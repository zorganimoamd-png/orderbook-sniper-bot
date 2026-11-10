import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# إعدادات بوت تليجرام
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9248737447:AAHoRRUFLoMlzIeXao1ZhECW6Who_4gJjO4")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8395647613")

# ==========================================
# الأصول المالية المراقبة (تمت إضافة الناسداك)
# ==========================================
SYMBOLS = ["XAU/USD", "USTEC", "EUR/USD", "GBP/USD"]

# ==========================================
# معايير القناص النشط (Active Sniper Settings)
# ==========================================
ORDER_BOOK_DEPTH = 20
IMBALANCE_THRESHOLD = 0.15
LIQUIDITY_WALL_MULTIPLIER = 1.3
MIN_RR_RATIO = 1.5

# هوامش الأمان خلف جدران السيولة
SL_BUFFER = {
    "XAU/USD": 1.2,    # 1.2 دولار للذهب
    "USTEC": 15.0,     # 15 نقطة للناسداك (حماية مؤسساتية ممتازة)
    "EUR/USD": 0.0005, # 5 نقاط
    "GBP/USD": 0.0006  # 6 نقاط
}
