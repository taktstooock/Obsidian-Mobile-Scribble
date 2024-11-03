from git import Repo
import os

class GitSync:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
    
    def pull(self):
        self.repo.remotes.origin.pull()
    
    def push(self):
        self.repo.git.add('.')
        self.repo.index.commit("Update memo")
        self.repo.remotes.origin.push()