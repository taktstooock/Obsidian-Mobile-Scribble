from git import Repo

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
    
    def vault2db(self):
        pass

    def db2vault(self):
        pass

class Sync:
    def __init__(self, user):
        self.user = user
    
    def sync(self):
        vault_sync = VaultDatabaseSync(self.user)
        git_sync = GitSync(self.user.vault_path)
        git_sync.pull()
        vault_sync.vault2db()
        vault_sync.db2vault()
        git_sync.push()