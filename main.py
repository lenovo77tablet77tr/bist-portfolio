#!/usr/bin/env python3
"""
BIST Portfolio Management Bot
A Telegram bot for managing Turkish stock portfolios with price alarms
"""

import os
import sys
import logging
import schedule
import time
from threading import Thread
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot import BistPortfolioBot
from github_sync import GitHubSync
from portfolio_manager import PortfolioManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BistPortfolioApp:
    def __init__(self):
        self.bot = BistPortfolioBot()
        self.github_sync = GitHubSync()
        self.portfolio_manager = PortfolioManager()
        
    def sync_data_job(self):
        """Background job to sync data with GitHub"""
        try:
            logger.info("Starting GitHub sync...")
            success = self.github_sync.sync_data()
            if success:
                logger.info("GitHub sync completed successfully")
            else:
                logger.error("GitHub sync failed")
        except Exception as e:
            logger.error(f"Error in sync job: {e}")

    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        # Schedule data sync every 30 minutes
        schedule.every(30).minutes.do(self.sync_data_job)
        
        # Also sync at startup
        schedule.every().day.at("09:00").do(self.sync_data_job)
        schedule.every().day.at("18:00").do(self.sync_data_job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    def run(self):
        """Start the application"""
        logger.info("Starting BIST Portfolio Management Bot...")
        
        # Initial setup
        try:
            # Setup GitHub repository
            self.github_sync.setup_github_repo()
            
            # Initial sync
            self.sync_data_job()
            
            # Start scheduler thread
            scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
            scheduler_thread.start()
            
            # Start the bot (this will block)
            self.bot.run()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error starting application: {e}")

if __name__ == '__main__':
    app = BistPortfolioApp()
    app.run()
