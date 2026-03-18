#!/usr/bin/env python3
import sys
import os
sys.path.append('src')

from telegram_bot import BistPortfolioBot
from github_sync import GitHubSync

def main():
    bot = BistPortfolioBot()
    github_sync = GitHubSync()

    # Send daily reports to all users
    for user_id_str in bot.portfolio_manager.portfolio_data.get("users", {}):
        user_id = int(user_id_str)
        user_settings = bot.portfolio_manager.get_user_settings(user_id)
        
        if user_settings['notifications']['daily_report']:
            report = bot.portfolio_manager.generate_detailed_report(user_id)
            
            try:
                import telegram
                application = telegram.ext.Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
                application.bot.send_message(
                    chat_id=user_id,
                    text=report,
                    parse_mode='Markdown'
                )
                print(f'Daily report sent to user {user_id}')
            except Exception as e:
                print(f'Error sending daily report to {user_id}: {e}')

    # Sync data
    github_sync.sync_data()
    print('Daily reports completed and data synced')

if __name__ == '__main__':
    main()
