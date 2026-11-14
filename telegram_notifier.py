import requests
import logging
import sys
from institutional_engine import SwingTradeSignal
import config

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token: str = config.TELEGRAM_BOT_TOKEN, chat_id: str = config.TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_swing_signal(self, signal: SwingTradeSignal) -> bool:
        # استخدام HTML بدلاً من Markdown لمنع أي خطأ في الحروف الخاصة
        html_message = (
            f"👑 <b>صفقة سوينغ نخبوية متكاملة (Elite Institutional Confluence)</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <b>الأصل المالي:</b> <code>{signal.symbol}</code>\n"
            f"⚡ <b>نوع الصفقة:</b> <b>{signal.action}</b>\n"
            f"🎯 <b>نسبة نجاح الصفقة المركبة:</b> <b>{signal.win_probability}%</b> 🏆\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 <b>إجماع الخبراء والمؤشرات الفنية (26 مؤشراً):</b>\n"
            f"⭐ <b>تصنيف المحللين:</b> <b>{signal.expert_rating}</b>\n"
            f"🗳️ <b>تصويت المؤشرات:</b> <code>{signal.expert_votes}</code>\n"
            f"💵 <b>تأكيد مؤشر الدولار (DXY):</b> <i>{signal.dxy_confirmation}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>سعر الدخول المباشر:</b> <code>{signal.entry_price}</code>\n"
            f"🎯 <b>منطقة التمركز المؤسساتي (Zone):</b> <code>{signal.entry_zone[0]} ➔ {signal.entry_zone[1]}</code>\n\n"
            f"🛑 <b>وقف الخسارة المحمي (SL):</b> <code>{signal.stop_loss}</code>\n"
            f"   <i>(محمي خلف جدار السيولة المؤسساتي بـ Buffer أمان)</i>\n\n"
            f"🎯 <b>الهدف الأول (TP1):</b> <code>{signal.take_profit_1}</code> <i>(تحرك سوينغ +{signal.target_move_dollars}$ دولار)</i>\n"
            f"🚀 <b>الهدف الثاني (TP2):</b> <code>{signal.take_profit_2}</code> <i>(استهداف كتل السيولة حتى 4100$+)</i>\n"
            f"⚖️ <b>نسبة العائد/المخاطرة (R:R):</b> <code>1:{signal.risk_reward_ratio}</code>\n"
            f"🧲 <b>مناطق السيولة والفجوات السعرية (SMC/FVG):</b>\n<code>{signal.smc_target_zone}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔬 <b>عمق السوق وتدفق الأوامر (L2 Order Flow):</b>\n"
            f"🧱 <b>كتلة الحوت المؤسساتي:</b> <code>{signal.institutional_block_price}</code> (بحجم <code>{signal.institutional_volume:.0f}</code> عقد)\n"
            f"📊 <b>انحياز تدفق الأوامر (OBI):</b> <code>{signal.obi_score * 100:+.1f}%</code>\n\n"
            f"💡 <b>التحليل والرؤية الاستراتيجية:</b>\n<i>{signal.rationale}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <b>سيتابع البوت الصفقة ويرسل تنبيه Breakeven فور تحرك السعر لتأمين الأرباح.</b>"
        )
        return self.send_message(html_message, parse_mode="HTML")

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if self.bot_token == "YOUR_BOT_TOKEN_HERE" or self.chat_id == "YOUR_CHAT_ID_HERE":
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            res = requests.post(self.base_url, json=payload, timeout=10)
            if res.status_code == 200:
                print("Telegram HTML message sent successfully.")
                return True
            else:
                logger.error(f"Telegram API Error: {res.text}")
                return False
        except Exception:
            return False
