import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# إعدادات بوت تليجرام
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9248737447:AAHoRRUFLoMlzIeXao1ZhECW6Who_4gJjO4")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8395647613")

# ==========================================
# الأصول المالية المراقبة
# ==========================================
SYMBOLS = ["XAU/USD", "EUR/USD", "GBP/USD"]

# ==========================================
# معايير القناص النشط (Active Sniper Settings)
# ==========================================
ORDER_BOOK_DEPTH = 20

# عتبة OBI مرنة وسريعة لاقتناص الصفقات الحية بشكل مستمر
IMBALANCE_THRESHOLD = 0.15

# مضاعف جدار السيولة مرن لرصد تجمعات السيولة السريعة
LIQUIDITY_WALL_MULTIPLIER = 1.3

# الحد الأدنى لنسبة العائد إلى المخاطرة
MIN_RR_RATIO = 1.5

# هوامش الأمان خلف جدران السيولة
SL_BUFFER = {
    "XAU/USD": 1.2,
    "EUR/USD": 0.0005,
    "GBP/USD": 0.0006
}
