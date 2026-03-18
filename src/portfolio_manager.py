import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import requests
from git import Repo
import yfinance as yf
import statistics

class PortfolioManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.portfolio_file = os.path.join(data_dir, "portfolio.json")
        self.alarms_file = os.path.join(data_dir, "alarms.json")
        self.settings_file = os.path.join(data_dir, "settings.json")
        self.market_data_file = os.path.join(data_dir, "market_data.json")
        self.config_file = os.path.join("config", "bist_stocks.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load initial data
        self.portfolio_data = self._load_portfolio()
        self.alarms_data = self._load_alarms()
        self.settings_data = self._load_settings()
        self.market_data = self._load_market_data()
        self.bist_stocks = self._load_bist_stocks()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _load_portfolio(self) -> Dict:
        """Load portfolio data from file"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"users": {}, "last_updated": None}
        except Exception as e:
            self.logger.error(f"Error loading portfolio: {e}")
            return {"users": {}, "last_updated": None}

    def _load_alarms(self) -> Dict:
        """Load alarm data from file"""
        try:
            if os.path.exists(self.alarms_file):
                with open(self.alarms_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"alarms": {}, "last_updated": None}
        except Exception as e:
            self.logger.error(f"Error loading alarms: {e}")
            return {"alarms": {}, "last_updated": None}

    def _load_bist_stocks(self) -> List[str]:
        """Load BIST stock list from config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("bist_stocks", [])
            return []
        except Exception as e:
            self.logger.error(f"Error loading BIST stocks: {e}")
            return []

    def _load_settings(self) -> Dict:
        """Load user settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"users": {}, "default_settings": {
                    "notifications": {
                        "daily_report": True,
                        "closing_report": True,
                        "price_alerts": True,
                        "volatility_alerts": True
                    },
                    "report_time": "18:00",
                    "volatility_threshold": 5.0,
                    "price_change_threshold": 3.0
                }}
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return {"users": {}, "default_settings": {}}

    def _load_market_data(self) -> Dict:
        """Load market data from file"""
        try:
            if os.path.exists(self.market_data_file):
                with open(self.market_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"price_history": {}, "alerts_sent": {}, "last_updated": None}
        except Exception as e:
            self.logger.error(f"Error loading market data: {e}")
            return {"price_history": {}, "alerts_sent": {}, "last_updated": None}

    def _save_portfolio(self):
        """Save portfolio data to file"""
        try:
            self.portfolio_data["last_updated"] = datetime.now().isoformat()
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio_data, f, indent=2, ensure_ascii=False)
            self.logger.info("Portfolio data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving portfolio: {e}")

    def _save_alarms(self):
        """Save alarm data to file"""
        try:
            self.alarms_data["last_updated"] = datetime.now().isoformat()
            with open(self.alarms_file, 'w', encoding='utf-8') as f:
                json.dump(self.alarms_data, f, indent=2, ensure_ascii=False)
            self.logger.info("Alarm data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving alarms: {e}")

    def _save_settings(self):
        """Save settings data to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, indent=2, ensure_ascii=False)
            self.logger.info("Settings data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def _save_market_data(self):
        """Save market data to file"""
        try:
            self.market_data["last_updated"] = datetime.now().isoformat()
            with open(self.market_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.market_data, f, indent=2, ensure_ascii=False)
            self.logger.info("Market data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving market data: {e}")

    def get_stock_price(self, symbol: str) -> Optional[float]:
        """Get current stock price using yfinance"""
        try:
            # Add .IS suffix for Turkish stocks
            ticker_symbol = f"{symbol}.IS"
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return None

    def add_stock(self, user_id: int, symbol: str, quantity: int, price: float) -> str:
        """Add stock to user's portfolio"""
        try:
            symbol = symbol.upper()
            
            # Validate stock symbol
            if symbol not in self.bist_stocks:
                return f"❌ {symbol} BIST'te bulunamadı. Geçerli hisseler için /hisseler komutunu kullanın."
            
            if user_id not in self.portfolio_data["users"]:
                self.portfolio_data["users"][user_id] = {"stocks": {}}
            
            if symbol not in self.portfolio_data["users"][user_id]["stocks"]:
                self.portfolio_data["users"][user_id]["stocks"][symbol] = {
                    "quantity": 0,
                    "total_cost": 0.0,
                    "transactions": []
                }
            
            # Update portfolio
            portfolio = self.portfolio_data["users"][user_id]["stocks"][symbol]
            portfolio["quantity"] += quantity
            portfolio["total_cost"] += quantity * price
            
            # Add transaction record
            portfolio["transactions"].append({
                "type": "buy",
                "quantity": quantity,
                "price": price,
                "total": quantity * price,
                "date": datetime.now().isoformat()
            })
            
            self._save_portfolio()
            
            current_price = self.get_stock_price(symbol)
            current_value = portfolio["quantity"] * (current_price or price)
            profit_loss = current_value - portfolio["total_cost"]
            profit_loss_percent = (profit_loss / portfolio["total_cost"]) * 100 if portfolio["total_cost"] > 0 else 0
            
            return f"✅ {symbol} eklendi:\n" \
                   f"• Adet: {quantity}\n" \
                   f"• Alış Fiyatı: {price:.2f} TL\n" \
                   f"• Toplam Maliyet: {portfolio['total_cost']:.2f} TL\n" \
                   f"• Mevcut Değer: {current_value:.2f} TL\n" \
                   f"• Kar/Zarar: {profit_loss:.2f} TL ({profit_loss_percent:+.2f}%)"
        
        except Exception as e:
            self.logger.error(f"Error adding stock: {e}")
            return f"❌ Hata: {str(e)}"

    def remove_stock(self, user_id: int, symbol: str, quantity: int, price: float = None) -> str:
        """Remove stock from user's portfolio"""
        try:
            symbol = symbol.upper()
            
            if user_id not in self.portfolio_data["users"]:
                return "❌ Portföyünüz bulunamadı."
            
            if symbol not in self.portfolio_data["users"][user_id]["stocks"]:
                return f"❌ {symbol} portföyünüzde bulunmuyor."
            
            portfolio = self.portfolio_data["users"][user_id]["stocks"][symbol]
            
            if portfolio["quantity"] < quantity:
                return f"❌ Portföyünüzde sadece {portfolio['quantity']} adet {symbol} var."
            
            # Use provided price or get current price
            if price is None:
                price = self.get_stock_price(symbol) or 0
            
            # Update portfolio
            portfolio["quantity"] -= quantity
            sale_value = quantity * price
            
            # Adjust total cost proportionally
            cost_per_share = portfolio["total_cost"] / (portfolio["quantity"] + quantity)
            portfolio["total_cost"] -= cost_per_share * quantity
            
            # Add transaction record
            portfolio["transactions"].append({
                "type": "sell",
                "quantity": quantity,
                "price": price,
                "total": sale_value,
                "date": datetime.now().isoformat()
            })
            
            # Remove stock if quantity is 0
            if portfolio["quantity"] == 0:
                del self.portfolio_data["users"][user_id]["stocks"][symbol]
            
            self._save_portfolio()
            
            return f"✅ {symbol} satıldı:\n" \
                   f"• Adet: {quantity}\n" \
                   f"• Satış Fiyatı: {price:.2f} TL\n" \
                   f"• Satış Değeri: {sale_value:.2f} TL"
        
        except Exception as e:
            self.logger.error(f"Error removing stock: {e}")
            return f"❌ Hata: {str(e)}"

    def get_portfolio(self, user_id: int) -> str:
        """Get user's portfolio summary"""
        try:
            if user_id not in self.portfolio_data["users"]:
                return "📊 Portföyünüz boş."
            
            stocks = self.portfolio_data["users"][user_id]["stocks"]
            if not stocks:
                return "📊 Portföyünüz boş."
            
            total_value = 0
            total_cost = 0
            result = "📊 **Portföyünüz**\n\n"
            
            for symbol, data in stocks.items():
                current_price = self.get_stock_price(symbol) or 0
                current_value = data["quantity"] * current_price
                profit_loss = current_value - data["total_cost"]
                profit_loss_percent = (profit_loss / data["total_cost"]) * 100 if data["total_cost"] > 0 else 0
                
                total_value += current_value
                total_cost += data["total_cost"]
                
                result += f"📈 **{symbol}**\n" \
                         f"  Adet: {data['quantity']}\n" \
                         f"  Ort. Maliyet: {data['total_cost']/data['quantity']:.2f} TL\n" \
                         f"  Mevcut Fiyat: {current_price:.2f} TL\n" \
                         f"  Değer: {current_value:.2f} TL\n" \
                         f"  Kar/Zarar: {profit_loss:.2f} TL ({profit_loss_percent:+.2f}%)\n\n"
            
            total_profit_loss = total_value - total_cost
            total_profit_percent = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
            
            result += f"💰 **Toplam Özet**\n" \
                     f"Toplam Maliyet: {total_cost:.2f} TL\n" \
                     f"Toplam Değer: {total_value:.2f} TL\n" \
                     f"Toplam Kar/Zarar: {total_profit_loss:.2f} TL ({total_profit_percent:+.2f}%)"
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error getting portfolio: {e}")
            return f"❌ Hata: {str(e)}"

    def add_alarm(self, user_id: int, symbol: str, target_price: float, alarm_type: str) -> str:
        """Add price alarm for a stock"""
        try:
            symbol = symbol.upper()
            
            if symbol not in self.bist_stocks:
                return f"❌ {symbol} BIST'te bulunamadı."
            
            if user_id not in self.alarms_data["alarms"]:
                self.alarms_data["alarms"][user_id] = []
            
            alarm = {
                "symbol": symbol,
                "target_price": target_price,
                "type": alarm_type,  # "above" or "below"
                "created": datetime.now().isoformat(),
                "triggered": False
            }
            
            self.alarms_data["alarms"][user_id].append(alarm)
            self._save_alarms()
            
            alarm_text = "üzerine" if alarm_type == "above" else "altına"
            return f"🔔 Alarm ayarlandı: {symbol} {target_price:.2f} TL {alarm_text} ulaştığında bildirim alacaksınız."
        
        except Exception as e:
            self.logger.error(f"Error adding alarm: {e}")
            return f"❌ Hata: {str(e)}"

    def check_alarms(self) -> List[Dict]:
        """Check and return triggered alarms"""
        triggered_alarms = []
        
        try:
            for user_id, user_alarms in self.alarms_data["alarms"].items():
                for alarm in user_alarms:
                    if alarm["triggered"]:
                        continue
                    
                    current_price = self.get_stock_price(alarm["symbol"])
                    if current_price is None:
                        continue
                    
                    triggered = False
                    if alarm["type"] == "above" and current_price >= alarm["target_price"]:
                        triggered = True
                    elif alarm["type"] == "below" and current_price <= alarm["target_price"]:
                        triggered = True
                    
                    if triggered:
                        alarm["triggered"] = True
                        alarm["triggered_price"] = current_price
                        alarm["triggered_date"] = datetime.now().isoformat()
                        triggered_alarms.append({
                            "user_id": int(user_id),
                            "alarm": alarm
                        })
            
            if triggered_alarms:
                self._save_alarms()
            
            return triggered_alarms
        
        except Exception as e:
            self.logger.error(f"Error checking alarms: {e}")
            return []

    def get_alarms(self, user_id: int) -> str:
        """Get user's active alarms"""
        try:
            if user_id not in self.alarms_data["alarms"]:
                return "🔔 Aktif alarmınız bulunmuyor."
            
            alarms = self.alarms_data["alarms"][user_id]
            active_alarms = [a for a in alarms if not a["triggered"]]
            
            if not active_alarms:
                return "🔔 Aktif alarmınız bulunmuyor."
            
            result = "🔔 **Aktif Alarmlarınız**\n\n"
            for alarm in active_alarms:
                alarm_text = "üzeri" if alarm["type"] == "above" else "altı"
                result += f"📈 {alarm['symbol']} - {alarm['target_price']:.2f} TL {alarm_text}\n"
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error getting alarms: {e}")
            return f"❌ Hata: {str(e)}"

    def get_stock_info(self, symbol: str) -> str:
        """Get detailed information about a stock"""
        try:
            symbol = symbol.upper()
            
            if symbol not in self.bist_stocks:
                return f"❌ {symbol} BIST'te bulunamadı."
            
            ticker = yf.Ticker(f"{symbol}.IS")
            info = ticker.info
            
            result = f"📈 **{symbol} Hisse Bilgileri**\n\n"
            result += f"Fiyat: {info.get('currentPrice', 'N/A')} TL\n"
            result += f"Önceki Kapanış: {info.get('previousClose', 'N/A')} TL\n"
            result += f"Günlük Değişim: {info.get('regularMarketChangePercent', 'N/A'):.2f}%\n"
            result += f"Hacim: {info.get('volume', 'N/A'):,}\n"
            result += f"Piyasa Değeri: {info.get('marketCap', 'N/A'):,} TL\n"
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error getting stock info: {e}")
            return f"❌ Hata: {str(e)}"

    def get_bist_stocks(self) -> str:
        """Get list of available BIST stocks"""
        result = "📋 **BIST 30 Hisseleri**\n\n"
        for i, stock in enumerate(self.bist_stocks, 1):
            result += f"{i:2d}. {stock}\n"
        return result

    def update_price_history(self, symbol: str, price: float):
        """Update price history for a stock"""
        try:
            if symbol not in self.market_data["price_history"]:
                self.market_data["price_history"][symbol] = []
            
            # Add new price with timestamp
            price_entry = {
                "price": price,
                "timestamp": datetime.now().isoformat()
            }
            
            self.market_data["price_history"][symbol].append(price_entry)
            
            # Keep only last 100 entries per stock
            if len(self.market_data["price_history"][symbol]) > 100:
                self.market_data["price_history"][symbol] = self.market_data["price_history"][symbol][-100:]
            
            self._save_market_data()
            
        except Exception as e:
            self.logger.error(f"Error updating price history for {symbol}: {e}")

    def check_volatility_alerts(self, user_id: int) -> List[Dict]:
        """Check for volatility alerts for user's portfolio"""
        alerts = []
        
        try:
            if user_id not in self.portfolio_data["users"]:
                return alerts
            
            user_settings = self.settings_data["users"].get(str(user_id), self.settings_data["default_settings"])
            
            if not user_settings["notifications"]["volatility_alerts"]:
                return alerts
            
            threshold = user_settings["volatility_threshold"]
            stocks = self.portfolio_data["users"][user_id]["stocks"]
            
            for symbol in stocks:
                if symbol in self.market_data["price_history"]:
                    price_history = self.market_data["price_history"][symbol]
                    
                    if len(price_history) >= 2:
                        current_price = price_history[-1]["price"]
                        previous_price = price_history[-2]["price"]
                        
                        if previous_price > 0:
                            change_percent = abs((current_price - previous_price) / previous_price) * 100
                            
                            if change_percent >= threshold:
                                alert_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                                
                                if alert_key not in self.market_data["alerts_sent"]:
                                    self.market_data["alerts_sent"][alert_key] = True
                                    
                                    alerts.append({
                                        "symbol": symbol,
                                        "type": "volatility",
                                        "current_price": current_price,
                                        "previous_price": previous_price,
                                        "change_percent": change_percent,
                                        "direction": "artış" if current_price > previous_price else "düşüş"
                                    })
            
            if alerts:
                self._save_market_data()
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking volatility alerts: {e}")
            return []

    def generate_detailed_report(self, user_id: int) -> str:
        """Generate detailed portfolio report"""
        try:
            if user_id not in self.portfolio_data["users"]:
                return "📊 Portföyünüz bulunmamaktadır."
            
            stocks = self.portfolio_data["users"][user_id]["stocks"]
            if not stocks:
                return "📊 Portföyünüz boş."
            
            report = "📊 **DETAYLI PORTFÖY RAPORU**\n\n"
            report += f"📅 Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            
            total_value = 0
            total_cost = 0
            best_performer = None
            worst_performer = None
            
            for symbol, data in stocks.items():
                current_price = self.get_stock_price(symbol) or 0
                current_value = data["quantity"] * current_price
                profit_loss = current_value - data["total_cost"]
                profit_loss_percent = (profit_loss / data["total_cost"]) * 100 if data["total_cost"] > 0 else 0
                
                total_value += current_value
                total_cost += data["total_cost"]
                
                # Track best/worst performers
                if best_performer is None or profit_loss_percent > best_performer["percent"]:
                    best_performer = {"symbol": symbol, "percent": profit_loss_percent, "value": profit_loss}
                
                if worst_performer is None or profit_loss_percent < worst_performer["percent"]:
                    worst_performer = {"symbol": symbol, "percent": profit_loss_percent, "value": profit_loss}
                
                # Get historical data
                volatility = self._calculate_volatility(symbol)
                day_high = self._get_day_high(symbol)
                day_low = self._get_day_low(symbol)
                
                report += f"📈 **{symbol}**\n"
                report += f"  └─ Adet: {data['quantity']:,}\n"
                report += f"  └─ Ort. Maliyet: {data['total_cost']/data['quantity']:.2f} TL\n"
                report += f"  └─ Mevcut Fiyat: {current_price:.2f} TL\n"
                report += f"  └─ Gün En Yüksek: {day_high:.2f} TL\n"
                report += f"  └─ Gün En Düşük: {day_low:.2f} TL\n"
                report += f"  └─ Piyasa Değeri: {current_value:,.2f} TL\n"
                report += f"  └─ Kar/Zarar: {profit_loss:,.2f} TL ({profit_loss_percent:+.2f}%)\n"
                report += f"  └─ Oynaklık: {volatility:.2f}%\n"
                report += f"  └─ Portföy Ağırlığı: {(current_value/total_value)*100:.1f}%\n\n"
            
            total_profit_loss = total_value - total_cost
            total_profit_percent = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
            
            report += "💰 **TOPLAM ÖZET**\n"
            report += f"🔸 Toplam Maliyet: {total_cost:,.2f} TL\n"
            report += f"🔸 Toplam Değer: {total_value:,.2f} TL\n"
            report += f"🔸 Toplam Kar/Zarar: {total_profit_loss:,.2f} TL ({total_profit_percent:+.2f}%)\n\n"
            
            report += "🏆 **PERFORMANS ANALİZİ**\n"
            if best_performer:
                report += f"🥇 En İyi Performans: {best_performer['symbol']} (+{best_performer['percent']:.2f}%)\n"
            if worst_performer:
                report += f"📉 En Zayıf Performans: {worst_performer['symbol']} ({worst_performer['percent']:.2f}%)\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating detailed report: {e}")
            return f"❌ Rapor oluşturulurken hata: {str(e)}"

    def generate_closing_report(self, user_id: int) -> str:
        """Generate daily closing report"""
        try:
            if user_id not in self.portfolio_data["users"]:
                return "📊 Portföyünüz bulunmamaktadır."
            
            stocks = self.portfolio_data["users"][user_id]["stocks"]
            if not stocks:
                return "📊 Portföyünüz boş."
            
            report = "🌅 **GÜNLÜK KAPANIŞ RAPORU**\n\n"
            report += f"📅 {datetime.now().strftime('%d.%m.%Y')} - Piyasa Kapanışı\n\n"
            
            total_value = 0
            total_cost = 0
            daily_changes = []
            
            for symbol, data in stocks.items():
                current_price = self.get_stock_price(symbol) or 0
                current_value = data["quantity"] * current_price
                profit_loss = current_value - data["total_cost"]
                profit_loss_percent = (profit_loss / data["total_cost"]) * 100 if data["total_cost"] > 0 else 0
                
                total_value += current_value
                total_cost += data["total_cost"]
                
                # Calculate daily change
                daily_change = self._calculate_daily_change(symbol)
                daily_changes.append({
                    "symbol": symbol,
                    "change": daily_change,
                    "value": current_value
                })
                
                report += f"📈 {symbol}: {current_price:.2f} TL ({daily_change:+.2f}%)\n"
            
            # Sort by daily change
            daily_changes.sort(key=lambda x: x["change"], reverse=True)
            
            report += f"\n💰 **GÜNÜN ÖZETİ**\n"
            report += f"🔸 Portföy Değeri: {total_value:,.2f} TL\n"
            report += f"🔸 Toplam Kar/Zarar: {(total_value-total_cost):,.2f} TL\n\n"
            
            report += "📊 **GÜNÜN KAZANANLARI**\n"
            for i, change in enumerate(daily_changes[:3], 1):
                if change["change"] > 0:
                    report += f"{i}. {change['symbol']}: +{change['change']:.2f}%\n"
            
            report += "\n📉 **GÜNÜN KAYBEDENLERİ**\n"
            for i, change in enumerate(daily_changes[-3:], 1):
                if change["change"] < 0:
                    report += f"{i}. {change['symbol']}: {change['change']:.2f}%\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating closing report: {e}")
            return f"❌ Kapanış raporu oluşturulurken hata: {str(e)}"

    def _calculate_volatility(self, symbol: str, days: int = 20) -> float:
        """Calculate volatility for a stock"""
        try:
            if symbol not in self.market_data["price_history"]:
                return 0.0
            
            prices = [entry["price"] for entry in self.market_data["price_history"][symbol][-days:]]
            
            if len(prices) < 2:
                return 0.0
            
            returns = []
            for i in range(1, len(prices)):
                if prices[i-1] > 0:
                    returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            if not returns:
                return 0.0
            
            return statistics.stdev(returns) * 100  # Convert to percentage
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility for {symbol}: {e}")
            return 0.0

    def _get_day_high(self, symbol: str) -> float:
        """Get day's highest price"""
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            info = ticker.info
            return info.get('dayHigh') or 0.0
        except:
            return 0.0

    def _get_day_low(self, symbol: str) -> float:
        """Get day's lowest price"""
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            info = ticker.info
            return info.get('dayLow') or 0.0
        except:
            return 0.0

    def _calculate_daily_change(self, symbol: str) -> float:
        """Calculate daily price change percentage"""
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            info = ticker.info
            return info.get('regularMarketChangePercent', 0.0) or 0.0
        except:
            return 0.0

    def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        user_id_str = str(user_id)
        if user_id_str not in self.settings_data["users"]:
            # Initialize user settings with defaults
            self.settings_data["users"][user_id_str] = self.settings_data["default_settings"].copy()
            self._save_settings()
        
        return self.settings_data["users"][user_id_str]

    def update_user_settings(self, user_id: int, settings: Dict) -> str:
        """Update user settings"""
        try:
            user_id_str = str(user_id)
            self.settings_data["users"][user_id_str] = settings
            self._save_settings()
            return "✅ Ayarlarınız güncellendi."
        except Exception as e:
            self.logger.error(f"Error updating user settings: {e}")
            return "❌ Ayarlar güncellenirken hata oluştu."
