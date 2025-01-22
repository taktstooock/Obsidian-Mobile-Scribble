from git import Repo
from django.conf import settings
from .dailynote_interpreter import DailyNoteInterpreter, parse_dailynotes
from .obsidian_templater import TemplateEngine
from pathlib import Path
from django.utils import timezone

class GitSync:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
    
    def pull(self):
        print("Pulling from remote")
        self.repo.remotes.origin.pull()
    
    def push(self):
        if self.repo.is_dirty():
            print("Committing and pushing changes")
            self.repo.git.add('.')
            self.repo.index.commit("Update memo on OMS")
            self.repo.remotes.origin.push()

class VaultDatabaseSync:
    def __init__(self, user):
        self.user = user
        self.vault_path : Path = settings.VAULTS_DIR / Path(str(user.id))
        self.daily_notes_path : Path = self.vault_path / settings.DAILY_NOTE_DIR
        self.template_path : Path = self.vault_path / settings.TEMPLATE_FILE
    
    def vault2db(self):
        journal_entries = parse_dailynotes(self.daily_notes_path)
        if not journal_entries:
            return

        entry_times = [time for time, _ in journal_entries]
        existing_memos = {
            memo.created_at: memo
            for memo in self.user.memos.filter(created_at__in=entry_times)
        }

        updates = []
        creates = []

        for time, text in journal_entries:
            if time in existing_memos:
                memo = existing_memos[time]
                if memo.content != text:
                    memo.content = text
                    updates.append(memo)
            else:
                creates.append(
                    self.user.memos.model(
                        content=text,
                        author=self.user,
                        created_at=time,
                        vault_synced_at=time
                    )
                )

        # 削除対象
        all_times_in_db = set(self.user.memos.filter(vault_synced_at__isnull=False).values_list('created_at', flat=True))
        missing_in_vault = all_times_in_db - set(entry_times)
        if missing_in_vault:
            print(f"Deleting {len(missing_in_vault)} memos")
            self.user.memos.filter(created_at__in=missing_in_vault).delete()

        if updates:
            print(f"Updating {len(updates)} memos")
            self.user.memos.bulk_update(updates, ['content'])
        if creates:
            print(f"Creating {len(creates)} memos")
            self.user.memos.bulk_create(creates)

    def db2vault(self):
        unsynced_memos = self.user.memos.filter(vault_synced_at__isnull=True)
        memo_dates = unsynced_memos.values_list('created_at', flat=True)
        print(f"Syncing {len(memo_dates)} memos to vault")
        for memo_date in memo_dates:
            memo_date = timezone.localtime(memo_date).date()
            output_path = self.daily_notes_path / f"{memo_date.strftime('%Y-%m-%d')}.md"
            if not output_path.exists():
                template_engine = TemplateEngine()
                template_engine.process_template(self.template_path, memo_date, output_path)
            target_memos = self.user.memos.filter(created_at__date=memo_date)
            interpreter = DailyNoteInterpreter(output_path)
            interpreter.update_entries(target_memos.order_by('created_at').values_list('created_at', 'content'))
            target_memos.update(vault_synced_at=timezone.now())

class Sync:
    def __init__(self, user):
        self.user = user
    
    def sync(self):
        vault_sync = VaultDatabaseSync(self.user)
        git_sync = GitSync(vault_sync.vault_path)
        git_sync.pull()
        vault_sync.vault2db()
        vault_sync.db2vault()
        git_sync.push()