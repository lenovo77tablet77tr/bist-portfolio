import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from portfolio_manager import PortfolioManager

# Load environment variables
load_dotenv()

class BistPortfolioBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_id = int(os.getenv('ADMIN_USER_ID', 0))
        self.portfolio_manager = PortfolioManager()
        
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "👋 **Bist Portföy Yönetim Botuna Hoş Geldiniz!**\n\n"
            "📊 **Komutlar:**\n"
            "/yardım - Bu yardım mesajını gösterir\n"
            "/portföy - Portföyünüzü görüntüler\n"
            "/detaylı_rapor - Detaylı portföy raporu\n"
            "/kapanış_raporu - Günlük kapanış raporu\n"
            "/ekle <hisse> <adet> <fiyat> - Hisse ekler\n"
            "/sat <hisse> <adet> [fiyat] - Hisse satar\n"
            "/alarm <hisse> <fiyat> <tip> - Alarm kurar\n"
            "/alarmlar - Aktif alarmlarınızı gösterir\n"
            "/ayarlar - Bildirim ayarlarınızı gösterir\n"
            "/ayarla <özellik> <değer> - Ayarları değiştirir\n"
            "/bilgi <hisse> - Hisse bilgilerini gösterir\n"
            "/hisseler - BIST 30 listesini gösterir\n"
            "/fiyat <hisse> - Hisse fiyatını gösterir\n\n"
            "💡 **Alarm tipler:** 'üstü' veya 'altı'\n"
            "📝 **Örnek:** /ekle GARAN 100 45.50\n"
            "⚙️ **Ayarlar:** /ayarla günlük_rapor evet"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /yardım command"""
        await self.start(update, context)

    async def portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portföy command"""
        user_id = update.effective_user.id
        portfolio_text = self.portfolio_manager.get_portfolio(user_id)
        await update.message.reply_text(portfolio_text, parse_mode='Markdown')

    async def add_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ekle command"""
        user_id = update.effective_user.id
        
        try:
            args = context.args
            if len(args) != 3:
                await update.message.reply_text(
                    "❌ Kullanım: /ekle <hisse> <adet> <fiyat>\n"
                    "📝 Örnek: /ekle GARAN 100 45.50"
                )
                return
            
            symbol = args[0].upper()
            quantity = int(args[1])
            price = float(args[2])
            
            if quantity <= 0 or price <= 0:
                await update.message.reply_text("❌ Adet ve fiyat pozitif sayılar olmalıdır.")
                return
            
            result = self.portfolio_manager.add_stock(user_id, symbol, quantity, price)
            await update.message.reply_text(result, parse_mode='Markdown')
            
        except ValueError:
            await update.message.reply_text("❌ Geçersiz sayı formatı. Lütfen kontrol edin.")
        except Exception as e:
            self.logger.error(f"Error in add_stock: {e}")
            await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

    async def sell_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sat command"""
        user_id = update.effective_user.id
        
        try:
            args = context.args
            if len(args) < 2 or len(args) > 3:
                await update.message.reply_text(
                    "❌ Kullanım: /sat <hisse> <adet> [fiyat]\n"
                    "📝 Örnek: /sat GARAN 50 46.00\n"
                    "💡 Fiyat belirtilmezse güncel fiyat kullanılır."
                )
                return
            
            symbol = args[0].upper()
            quantity = int(args[1])
            price = float(args[2]) if len(args) == 3 else None
            
            if quantity <= 0:
                await update.message.reply_text("❌ Adet pozitif sayı olmalıdır.")
                return
            
            if price is not None and price <= 0:
                await update.message.reply_text("❌ Fiyat pozitif sayı olmalıdır.")
                return
            
            result = self.portfolio_manager.remove_stock(user_id, symbol, quantity, price)
            await update.message.reply_text(result, parse_mode='Markdown')
            
        except ValueError:
            await update.message.reply_text("❌ Geçersiz sayı formatı. Lütfen kontrol edin.")
        except Exception as e:
            self.logger.error(f"Error in sell_stock: {e}")
            await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

    async def add_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alarm command"""
        user_id = update.effective_user.id
        
        try:
            args = context.args
            if len(args) != 3:
                await update.message.reply_text(
                    "❌ Kullanım: /alarm <hisse> <fiyat> <tip>\n"
                    "📝 Örnek: /alarm GARAN 50.00 üstü\n"
                    "💡 Tipler: 'üstü' veya 'altı'"
                )
                return
            
            symbol = args[0].upper()
            target_price = float(args[1])
            alarm_type = args[2].lower()
            
            if alarm_type not in ['üstü', 'altı']:
                await update.message.reply_text("❌ Alarm tipi 'üstü' veya 'altı' olmalıdır.")
                return
            
            if target_price <= 0:
                await update.message.reply_text("❌ Fiyat pozitif sayı olmalıdır.")
                return
            
            # Convert to English
            alarm_type_en = 'above' if alarm_type == 'üstü' else 'below'
            
            result = self.portfolio_manager.add_alarm(user_id, symbol, target_price, alarm_type_en)
            await update.message.reply_text(result, parse_mode='Markdown')
            
        except ValueError:
            await update.message.reply_text("❌ Geçersiz sayı formatı. Lütfen kontrol edin.")
        except Exception as e:
            self.logger.error(f"Error in add_alarm: {e}")
            await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

    async def get_alarms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alarmlar command"""
        user_id = update.effective_user.id
        alarms_text = self.portfolio_manager.get_alarms(user_id)
        await update.message.reply_text(alarms_text, parse_mode='Markdown')

    async def stock_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /bilgi command"""
        try:
            args = context.args
            if len(args) != 1:
                await update.message.reply_text(
                    "❌ Kullanım: /bilgi <hisse>\n"
                    "📝 Örnek: /bilgi GARAN"
                )
                return
            
            symbol = args[0].upper()
            info_text = self.portfolio_manager.get_stock_info(symbol)
            await update.message.reply_text(info_text, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in stock_info: {e}")
            await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

    async def get_stocks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /hisseler command"""
        stocks_text = self.portfolio_manager.get_bist_stocks()
        await update.message.reply_text(stocks_text, parse_mode='Markdown')

    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fiyat command"""
        try:
            args = context.args
            if len(args) != 1:
                await update.message.reply_text(
                    "❌ Kullanım: /fiyat <hisse>\n"
                    "📝 Örnek: /fiyat GARAN"
                )
                return
            
            symbol = args[0].upper()
            price = self.portfolio_manager.get_stock_price(symbol)
            
            if price is None:
                await update.message.reply_text(f"❌ {symbol} için fiyat bilgisi alınamadı.")
            else:
                await update.message.reply_text(f"💰 {symbol}: {price:.2f} TL")
            
        except Exception as e:
            self.logger.error(f"Error in get_price: {e}")
            await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

    async def detailed_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /detaylı_rapor command"""
        user_id = update.effective_user.id
        report_text = self.portfolio_manager.generate_detailed_report(user_id)
        await update.message.reply_text(report_text, parse_mode='Markdown')

    async def closing_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /kapanış_raporu command"""
        user_id = update.effective_user.id
        report_text = self.portfolio_manager.generate_closing_report(user_id)
        await update.message.reply_text(report_text, parse_mode='Markdown')

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ayarlar command"""
        user_id = update.effective_user.id
        user_settings = self.portfolio_manager.get_user_settings(user_id)
        
        settings_text = (
            "⚙️ **BİLDİRİM AYARLARINIZ**\n\n"
            f"📊 Günlük Rapor: {'✅' if user_settings['notifications']['daily_report'] else '❌'}\n"
            f"🌅 Kapanış Raporu: {'✅' if user_settings['notifications']['closing_report'] else '❌'}\n"
            f"🔔 Fiyat Alarmları: {'✅' if user_settings['notifications']['price_alerts'] else '❌'}\n"
            f"📈 Oynaklık Alarmları: {'✅' if user_settings['notifications']['volatility_alerts'] else '❌'}\n\n"
            f"⏰ Rapor Saati: {user_settings['report_time']}\n"
            f"📊 Oynaklık Eşiği: %{user_settings['volatility_threshold']}\n"
            f"💰 Fiyat Değişim Eşiği: %{user_settings['price_change_threshold']}\n\n"
            "💡 Ayarları değiştirmek için: /ayarla <özellik> <değer>"
        )
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')

    async def update_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ayarla command"""
        user_id = update.effective_user.id
        
        try:
            args = context.args
            if len(args) != 2:
                await update.message.reply_text(
                    "❌ Kullanım: /ayarla <özellik> <değer>\n\n"
                    "📝 Örnekler:\n"
                    "/ayarla günlük_rapor evet\n"
                    "/ayarla oynaklık_eşiği 3.0\n"
                    "/ayarla rapor_saati 17:30\n\n"
                    "⚙️ Özellikler: günlük_rapor, kapanış_raporu, fiyat_alarmları, "
                    "oynaklık_alarmları, oynaklık_eşiği, fiyat_değişim_eşiği, rapor_saati"
                )
                return
            
            feature = args[0].lower()
            value = args[1].lower()
            
            user_settings = self.portfolio_manager.get_user_settings(user_id)
            
            # Update settings based on feature
            if feature == "günlük_rapor":
                user_settings['notifications']['daily_report'] = value in ['evet', 'açık', 'true', '1']
            elif feature == "kapanış_raporu":
                user_settings['notifications']['closing_report'] = value in ['evet', 'açık', 'true', '1']
            elif feature == "fiyat_alarmları":
                user_settings['notifications']['price_alerts'] = value in ['evet', 'açık', 'true', '1']
            elif feature == "oynaklık_alarmları":
                user_settings['notifications']['volatility_alerts'] = value in ['evet', 'açık', 'true', '1']
            elif feature == "oynaklık_eşiği":
                try:
                    user_settings['volatility_threshold'] = float(value)
                except ValueError:
                    await update.message.reply_text("❌ Oynaklık eşiği sayı olmalıdır.")
                    return
            elif feature == "fiyat_değişim_eşiği":
                try:
                    user_settings['price_change_threshold'] = float(value)
                except ValueError:
                    await update.message.reply_text("❌ Fiyat değişim eşiği sayı olmalıdır.")
                    return
            elif feature == "rapor_saati":
                # Validate time format HH:MM
                try:
                    hour, minute = value.split(':')
                    int(hour), int(minute)  # Validate numbers
                    user_settings['report_time'] = value
                except:
                    await update.message.reply_text("❌ Saat formatı HH:MM olmalıdır.")
                    return
            else:
                await update.message.reply_text("❌ Geçersiz özellik.")
                return
            
            result = self.portfolio_manager.update_user_settings(user_id, user_settings)
            await update.message.reply_text(result)
            
        except Exception as e:
            self.logger.error(f"Error in update_settings: {e}")
            await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin statistics command"""
        user_id = update.effective_user.id
        
        if user_id != self.admin_id:
            await update.message.reply_text("❌ Bu komut sadece admin kullanabilir.")
            return
        
        try:
            # Get basic stats
            portfolio_data = self.portfolio_manager._load_portfolio()
            alarms_data = self.portfolio_manager._load_alarms()
            
            total_users = len(portfolio_data.get("users", {}))
            total_alarms = sum(len(alarms) for alarms in alarms_data.get("alarms", {}).values())
            
            stats_text = (
                f"📊 **Bot İstatistikleri**\n\n"
                f"👥 Toplam Kullanıcı: {total_users}\n"
                f"🔔 Toplam Alarm: {total_alarms}\n"
                f"📅 Son Güncelleme: {portfolio_data.get('last_updated', 'Bilinmiyor')}\n"
                f"🔄 Alarm Kontrol: {alarms_data.get('last_updated', 'Bilinmiyor')}"
            )
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in admin_stats: {e}")
            await update.message.reply_text("❌ İstatistikler alınamadı.")

    async def check_volatility_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Background job to check volatility alerts"""
        try:
            # Get all users with portfolios
            for user_id_str in self.portfolio_manager.portfolio_data.get("users", {}):
                user_id = int(user_id_str)
                volatility_alerts = self.portfolio_manager.check_volatility_alerts(user_id)
                
                for alert in volatility_alerts:
                    message = (
                        f"🚨 **OYNAKLIK ALARMI!**\n\n"
                        f"📈 {alert['symbol']} anlı {alert['direction']} yaşandı!\n"
                        f"📊 Değişim: %{alert['change_percent']:.2f}\n"
                        f"💰 Önceki Fiyat: {alert['previous_price']:.2f} TL\n"
                        f"💰 Mevcut Fiyat: {alert['current_price']:.2f} TL"
                    )
                    
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        self.logger.error(f"Error sending volatility alert to {user_id}: {e}")
            
            if volatility_alerts:
                self.logger.info(f"Processed {len(volatility_alerts)} volatility alerts")
                
        except Exception as e:
            self.logger.error(f"Error in check_volatility_job: {e}")

    async def daily_report_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Background job to send daily reports"""
        try:
            for user_id_str in self.portfolio_manager.portfolio_data.get("users", {}):
                user_id = int(user_id_str)
                user_settings = self.portfolio_manager.get_user_settings(user_id)
                
                if user_settings['notifications']['daily_report']:
                    report = self.portfolio_manager.generate_detailed_report(user_id)
                    
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=report,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        self.logger.error(f"Error sending daily report to {user_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error in daily_report_job: {e}")

    async def closing_report_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Background job to send closing reports"""
        try:
            for user_id_str in self.portfolio_manager.portfolio_data.get("users", {}):
                user_id = int(user_id_str)
                user_settings = self.portfolio_manager.get_user_settings(user_id)
                
                if user_settings['notifications']['closing_report']:
                    report = self.portfolio_manager.generate_closing_report(user_id)
                    
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=report,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        self.logger.error(f"Error sending closing report to {user_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error in closing_report_job: {e}")

    async def check_alarms_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Background job to check alarms"""
        try:
            triggered_alarms = self.portfolio_manager.check_alarms()
            
            for alarm_data in triggered_alarms:
                user_id = alarm_data["user_id"]
                alarm = alarm_data["alarm"]
                
                alarm_text = "üzerine çıktı" if alarm["type"] == "above" else "altına düştü"
                message = (
                    f"🔔 **ALARM!**\n\n"
                    f"📈 {alarm['symbol']} hedef fiyata {alarm_text}!\n"
                    f"🎯 Hedef Fiyat: {alarm['target_price']:.2f} TL\n"
                    f"💰 Mevcut Fiyat: {alarm['triggered_price']:.2f} TL"
                )
                
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    self.logger.error(f"Error sending alarm notification to {user_id}: {e}")
            
            if triggered_alarms:
                self.logger.info(f"Processed {len(triggered_alarms)} triggered alarms")
                
        except Exception as e:
            self.logger.error(f"Error in check_alarms_job: {e}")

    def run(self):
        """Start the bot"""
        if not self.token:
            self.logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        application = Application.builder().token(self.token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("yardım", self.help_command))
        application.add_handler(CommandHandler("portföy", self.portfolio))
        application.add_handler(CommandHandler("portfolio", self.portfolio))
        application.add_handler(CommandHandler("ekle", self.add_stock))
        application.add_handler(CommandHandler("sat", self.sell_stock))
        application.add_handler(CommandHandler("alarm", self.add_alarm))
        application.add_handler(CommandHandler("alarmlar", self.get_alarms))
        application.add_handler(CommandHandler("bilgi", self.stock_info))
        application.add_handler(CommandHandler("hisseler", self.get_stocks))
        application.add_handler(CommandHandler("fiyat", self.get_price))
        application.add_handler(CommandHandler("detaylı_rapor", self.detailed_report))
        application.add_handler(CommandHandler("kapanış_raporu", self.closing_report))
        application.add_handler(CommandHandler("ayarlar", self.settings))
        application.add_handler(CommandHandler("ayarla", self.update_settings))
        application.add_handler(CommandHandler("admin_stats", self.admin_stats))
        
        # Add alarm check job (every 5 minutes)
        job_queue = application.job_queue
        job_queue.run_repeating(self.check_alarms_job, interval=300, first=10)
        
        # Add volatility check job (every 2 minutes during market hours)
        job_queue.run_repeating(self.check_volatility_job, interval=120, first=30)
        
        # Add daily report job (every day at user's preferred time)
        job_queue.run_daily(self.daily_report_job, time=datetime.time(hour=9, minute=0))
        
        # Add closing report job (every day at 18:00)
        job_queue.run_daily(self.closing_report_job, time=datetime.time(hour=18, minute=0))
        
        self.logger.info("BIST Portfolio Bot started successfully")
        
        # Start the bot
        application.run_polling()

if __name__ == '__main__':
    bot = BistPortfolioBot()
    bot.run()
