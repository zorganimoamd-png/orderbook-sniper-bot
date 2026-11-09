import requests
import logging
from orderbook_engine import TradeSignal
import config

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token: str = config.TELEGRAM_BOT_TOKEN, chat_id: str = config.TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_signal(self, signal: TradeSignal) -> bool:
        """
        إرسال إشارة التداول المحللة بعمق السوق بتنسيق فاخر
        """
        message = (
            f"🎯 *إشارة قناص عمق السوق (Market Depth Sniper)* 🎯\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 *الأصل المالي:* `{signal.symbol}`\n"
            f"⚡ *نوع الصفقة:* *{signal.action}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 *سعر الدخول المباشر:* `{signal.entry_price}`\n"
            f"🎯 *منطقة التمركز (Zone):* `{signal.entry_zone[0]} - {signal.entry_zone[1]}`\n\n"
            f"🛑 *وقف الخسارة (SL):* `{signal.stop_loss}`\n"
            f"   *(محمي خلف جدار السيولة المؤسساتي)*\n\n"
            f"🎯 *الهدف الأول (TP1):* `{signal.take_profit_1}`\n"
            f"🚀 *الهدف الثاني (TP2):* `{signal.take_profit_2}`\n"
            f"⚖️ *نسبة العائد/المخاطرة (R:R):* `1:{signal.risk_reward_ratio}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔬 *تحليل البنية الدقيقة لعمق السوق (L2 Analysis):*\n"
            f"📊 *مؤشر عدم التوازن (OBI):* `{signal.obi_score * 100:+.1f}%`\n"
            f"⚖️ *السعر العادل (Micro-Price):* `{signal.micro_price}`\n"
            f"🧱 *جدار السيولة المعتمد:* `{signal.wall_price}` (بحجم `{signal.wall_volume}` عقد)\n\n"
            f"💡 *أسباب الاقتناص المؤسساتي:*\n_{signal.rationale}_\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ *إدارة رأس المال الصارمة هي سر استمرار الأرباح.*"
        )

        return self.send_message(message)

    def send_message(self, text: str) -> bool:
        """
        إرسال رسالة نصية عادية إلى قناة أو مستخدم تليجرام
        """
        if self.bot_token == "YOUR_BOT_TOKEN_HERE" or self.chat_id == "YOUR_CHAT_ID_HERE":
            print("\n[تنبيه تليجرام] لم يتم تعيين Telegram Token أو Chat ID بعد.")
            print("الرسالة التي كانت ستُرسل إلى تليجرام:")
            print("--------------------------------------------------")
            print(text)
            print("--------------------------------------------------\n")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            res = requests.post(self.base_url, json=payload, timeout=10)
            if res.status_code == 200:
                print(f"[تليجرام] تم إرسال الإشارة بنجاح.")
                return True
            else:
                logger.error(f"Telegram API Error: {res.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send to Telegram: {e}")
            return False
