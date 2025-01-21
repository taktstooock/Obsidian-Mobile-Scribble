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
        self.repo.remotes.origin.pull()
    
    def push(self):
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
        print(journal_entries)
        for time, text in journal_entries:
            if self.user.memos.filter(created_at=time).exists():
                existing_memo = self.user.memos.get(created_at=time)
                if existing_memo.content != text:
                    existing_memo.content = text
                    existing_memo.save()                
                continue
            self.user.memos.create(
                content=text,
                author=self.user,
                created_at=time,
                vault_synced_at=time
                )

    def db2vault(self):
        unsynced_memos = self.user.memos.filter(vault_synced_at__isnull=True)
        memo_dates = unsynced_memos.values_list('created_at', flat=True)
        for memo_date in memo_dates:
            memo_date = timezone.localtime(memo_date).date()
            output_path = self.daily_notes_path / f"{memo_date.strftime('%Y-%m-%d')}.md"
            if not output_path.exists():
                template_engine = TemplateEngine()
                template_engine.process_template(self.template_path, memo_date, output_path)
            target_memos = self.user.memos.filter(created_at__date=memo_date)
            interpreter = DailyNoteInterpreter(output_path)
            interpreter.update_entries(target_memos.values_list('created_at', 'content'))
            target_memos.update(vault_synced_at=timezone.now())

class Sync:
    def __init__(self, user):
        self.user = user
    
    def sync(self):
        vault_sync = VaultDatabaseSync(self.user)
        git_sync = GitSync(vault_sync.vault_path)
        # git_sync.pull()
        vault_sync.vault2db()
        vault_sync.db2vault()
        # git_sync.push()