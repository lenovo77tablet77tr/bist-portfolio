import os
import json
import logging
from datetime import datetime
from git import Repo

class GitHubSync:
    def __init__(self):
        self.github_username = os.getenv('GITHUB_REPO_USERNAME')
        self.github_repo = os.getenv('GITHUB_REPO_NAME', 'bist-portfolio')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.local_repo_path = os.getcwd()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_github_repo(self):
        """Setup GitHub repository if not exists"""
        try:
            if not os.path.exists('.git'):
                # Initialize git repository
                repo = Repo.init(self.local_repo_path)
                self.logger.info("Git repository initialized")
                
                # Add remote
                remote_url = f"https://{self.github_token}@github.com/{self.github_username}/{self.github_repo}.git"
                repo.create_remote('origin', remote_url)
                self.logger.info(f"Remote added: {remote_url}")
            else:
                repo = Repo(self.local_repo_path)
                self.logger.info("Git repository already exists")
            
            return repo
            
        except Exception as e:
            self.logger.error(f"Error setting up GitHub repo: {e}")
            return None

    def commit_and_push(self, message="Auto sync"):
        """Commit changes and push to GitHub"""
        try:
            repo = self.setup_github_repo()
            if not repo:
                return False
            
            # Add all changes
            repo.git.add('--all')
            
            # Check if there are changes to commit
            if repo.is_dirty(untracked_files=True):
                # Commit changes
                repo.index.commit(message)
                
                # Push to GitHub
                origin = repo.remote(name='origin')
                origin.push()
                
                self.logger.info(f"Changes pushed to GitHub: {message}")
                return True
            else:
                self.logger.info("No changes to commit")
                return True
                
        except Exception as e:
            self.logger.error(f"Error committing and pushing: {e}")
            return False

    def pull_changes(self):
        """Pull latest changes from GitHub"""
        try:
            repo = Repo(self.local_repo_path)
            origin = repo.remote(name='origin')
            origin.pull()
            
            self.logger.info("Changes pulled from GitHub")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pulling changes: {e}")
            return False

    def sync_data(self):
        """Sync data files with GitHub"""
        try:
            # Pull latest changes first
            self.pull_changes()
            
            # Commit and push local changes
            return self.commit_and_push(f"Data sync - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error syncing data: {e}")
            return False
