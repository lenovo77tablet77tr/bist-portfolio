#!/usr/bin/env python3
import sys
import os
sys.path.append('src')

from telegram_bot import BistPortfolioBot
from github_sync import GitHubSync

def main():
    bot = BistPortfolioBot()
    github_sync = GitHubSync()

    # Check alarms
    triggered_alarms = bot.portfolio_manager.check_alarms()
    
    # Send notifications
    for alarm_data in triggered_alarms:
        user_id = alarm_data['user_id']
        alarm = alarm_data['alarm']
        
        alarm_text = 'üzerine çıktı' if alarm['type'] == 'above' else 'altına düştü'
        message = (
            f'🔔 **ALARM!**\n\n'
            f'📈 {alarm["symbol"]} hedef fiyata {alarm_text}!\n'
            f'🎯 Hedef Fiyat: {alarm["target_price"]:.2f} TL\n'
            f'💰 Mevcut Fiyat: {alarm["triggered_price"]:.2f} TL'
        )
        
        try:
            import telegram
            application = telegram.ext.Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
            application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            print(f'Alarm sent to user {user_id} for {alarm["symbol"]}')
        except Exception as e:
            print(f'Error sending alarm to {user_id}: {e}')

    # Sync data if there were changes
    if triggered_alarms:
        github_sync.sync_data()
        print(f'Synced data after processing {len(triggered_alarms)} alarms')

if __name__ == '__main__':
    main()
