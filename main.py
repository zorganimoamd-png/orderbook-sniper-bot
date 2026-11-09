import time
import sys
import logging
from orderbook_engine import OrderBookAnalyzer
from market_feed import MarketDataFeed
from telegram_notifier import TelegramNotifier
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("SniperBot")

def run_sniper():
    print("""
    ===============================================================
       ⚡ INSTITUTIONAL MARKET DEPTH (L2) SNIPER BOT - FOR XAU/FX ⚡
    ===============================================================
    🚀 البوت الآن يعمل ويبحث عن فرص السيولة المؤسساتية في عمق السوق...
    """)

    analyzer = OrderBookAnalyzer(depth=config.ORDER_BOOK_DEPTH)
    feed = MarketDataFeed()
    notifier = TelegramNotifier()

    # لتجنب تكرار إرسال نفس الإشارة في فترة قصيرة
    cooldown = {}

    while True:
        try:
            for symbol in config.SYMBOLS:
                current_time = time.time()
                # منع تكرار الإشارة لنفس الرمز إلا بعد دقيقتين
                if symbol in cooldown and (current_time - cooldown[symbol]) < 120:
                    continue

                # 1. جلب عمق السوق المباشر
                bids, asks = feed.get_live_order_book(symbol, depth=config.ORDER_BOOK_DEPTH)

                # 2. تقييم الفرصة واقتناصها
                signal = analyzer.evaluate_opportunity(symbol, bids, asks)

                if signal:
                    logger.info(f"🎯 تم اقتناص فرصة عالية الجودة على {symbol}: {signal.action} @ {signal.entry_price}")
                    # إرسال الإشعار لتليجرام
                    notifier.send_signal(signal)
                    cooldown[symbol] = current_time

            # فحص دوري كل ثانيتين لمتابعة تدفق الأوامر السريع
            time.sleep(2)

        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت بواسطة المستخدم.")
            break
        except Exception as e:
            logger.error(f"حدث خطأ غير متوقع: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    run_sniper()
