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

    cooldown = {}

    while True:
        try:
            for symbol in config.SYMBOLS:
                current_time = time.time()
                # تهدئة 25 ثانية فقط بين الصفقات لنفس الزوج
                if symbol in cooldown and (current_time - cooldown[symbol]) < 25:
                    continue

                bids, asks = feed.get_live_order_book(symbol, depth=config.ORDER_BOOK_DEPTH)
                signal = analyzer.evaluate_opportunity(symbol, bids, asks)

                if signal:
                    logger.info(f"🎯 تم اقتناص فرصة عالية الجودة على {symbol}: {signal.action} @ {signal.entry_price}")
                    notifier.send_signal(signal)
                    cooldown[symbol] = current_time

            time.sleep(2)

        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت بواسطة المستخدم.")
            break
        except Exception as e:
            logger.error(f"حدث خطأ غير متوقع: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    run_sniper()
