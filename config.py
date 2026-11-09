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
# معايير القناص الرياضية لعمق السوق (Order Book Settings)
# ==========================================
# عمق المستويات التي يتم تحليلها (Top N Levels)
ORDER_BOOK_DEPTH = 20

# عتبة عدم التوازن لاقتناص الصفقة (0.65 تعني 65% تفوق لأحد الطرفين)
IMBALANCE_THRESHOLD = 0.65

# مضاعف حجم جدار السيولة مقارنة بالمتوسط
LIQUIDITY_WALL_MULTIPLIER = 2.8

# الحد الأدنى لنسبة العائد إلى المخاطرة (Risk to Reward Ratio)
MIN_RR_RATIO = 2.0

# هوامش الأمان خلف جدران السيولة لوقف الخسارة
SL_BUFFER = {
    "XAU/USD": 1.5,    # 1.5 دولار خلف الجدار للذهب
    "EUR/USD": 0.0008, # 8 نقاط
    "GBP/USD": 0.0010  # 10 نقاط
}
