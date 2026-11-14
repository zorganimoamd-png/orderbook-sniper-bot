import time
import sys
import logging
from institutional_engine import InstitutionalOrderFlowEngine
from market_feed import MarketDataFeed
from telegram_notifier import TelegramNotifier
from market_hours import MarketHoursFilter
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("InstitutionalSniper")

def run_sniper():
    print("""
    ===============================================================
       🦅 INSTITUTIONAL SWING ORDER FLOW SNIPER - GOLD & FOREX 🦅
    ===============================================================
    🚀 البوت الآن في وضع اقتناص كتل السيولة المؤسساتية وصفقات السوينغ...
    """)

    engine = InstitutionalOrderFlowEngine()
    feed = MarketDataFeed()
    notifier = TelegramNotifier()

    cooldown = {}

    while True:
        try:
            # 1. صمام الأمان: منع العمل في عطلة نهاية الأسبوع
            if not MarketHoursFilter.is_market_open():
                logger.info("⏸️ السوق المالي مغلق حالياً (عطلة السبت والأحد). البوت في وضع الاستعداد التام...")
                time.sleep(60)
                continue

            # 2. فحص الذهب والأصول المعتمدة
            for symbol in config.SYMBOLS:
                current_time = time.time()
                
                # تهدئة 4 ساعات على الأقل بين صفقات السوينغ لنفس الأصل (صفقات سوينغ عميقة لا تتكرر)
                if symbol in cooldown and (current_time - cooldown[symbol]) < 14400:
                    continue

                live_price = feed.get_live_base_price(symbol)
                signal = engine.generate_swing_opportunity(symbol, live_price)

                if signal:
                    logger.info(f"🎯 تم رصد صفقة سوينغ مؤسساتية على {symbol}: {signal.action} @ {signal.entry_price} باستهداف {signal.take_profit_1} و {signal.take_profit_2}")
                    notifier.send_swing_signal(signal)
                    cooldown[symbol] = current_time

            time.sleep(15)

        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت بواسطة المستخدم.")
            break
        except Exception as e:
            logger.error(f"حدث خطأ غير متوقع: {e}", exc_info=True)
            time.sleep(10)

if __name__ == "__main__":
    run_sniper()
