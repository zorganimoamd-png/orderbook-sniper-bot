import time
import sys
import logging
from orderbook_engine import OrderBookAnalyzer
from market_feed import MarketDataFeed
from telegram_notifier import TelegramNotifier
from market_hours import MarketHoursFilter
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
       ⚡ INSTITUTIONAL MARKET DEPTH & DAY-TRADER SNIPER (XAU/FX) ⚡
    ===============================================================
    🚀 البوت الآن في وضع المراقبة الدقيقة لأسواق الذهب والفوركس...
    """)

    analyzer = OrderBookAnalyzer(depth=config.ORDER_BOOK_DEPTH)
    feed = MarketDataFeed()
    notifier = TelegramNotifier()

    cooldown = {}

    while True:
        try:
            # 1. صمام الأمان الأول: هل السوق المالي مفتوح اليوم؟
            if not MarketHoursFilter.is_market_open():
                logger.info("⏸️ السوق المالي (الذهب والفوركس) مغلق حالياً لعطلة نهاية الأسبوع (Weekend). البوت في وضع الاستعداد الصامت...")
                time.sleep(60) # فحص كل دقيقة بهدوء دون أي إرسال
                continue

            # 2. فحص الأصول المعتمدة (الذهب والفوركس فقط)
            for symbol in config.SYMBOLS:
                current_time = time.time()
                
                # صمام الأمان الثاني: منع السبام وتهدئة 30 دقيقة على الأقل لنفس الأصل
                if symbol in cooldown and (current_time - cooldown[symbol]) < config.SIGNAL_COOLDOWN_SECONDS:
                    continue

                bids, asks = feed.get_live_order_book(symbol, depth=config.ORDER_BOOK_DEPTH)
                signal = analyzer.evaluate_opportunity(symbol, bids, asks)

                if signal:
                    logger.info(f"🎯 تم اقتناص صفقة قناص مؤكدة على {symbol}: {signal.action} @ {signal.entry_price}")
                    notifier.send_signal(signal)
                    cooldown[symbol] = current_time

            # فحص تدفق الأوامر كل 5 ثوانٍ
            time.sleep(5)

        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت بواسطة المستخدم.")
            break
        except Exception as e:
            logger.error(f"حدث خطأ غير متوقع: {e}", exc_info=True)
            time.sleep(10)

if __name__ == "__main__":
    run_sniper()
