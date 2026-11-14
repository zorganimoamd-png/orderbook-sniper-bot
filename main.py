import time
import sys
import logging
from institutional_engine import InstitutionalOrderFlowEngine
from market_feed import MarketDataFeed
from telegram_notifier import TelegramNotifier
from market_hours import MarketHoursFilter
from trade_manager import LiveTradeManager
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("EliteSniper")

def run_sniper():
    print("""
    =======================================================================
       👑 ELITE INSTITUTIONAL ORDER FLOW & SMC SNIPER - GOLD & FOREX 👑
    =======================================================================
    🚀 البوت الآن يعمل بكامل طاقته النخبوية (DXY + SMC + Consensus + L2)...
    """)

    engine = InstitutionalOrderFlowEngine()
    feed = MarketDataFeed()
    notifier = TelegramNotifier()
    trade_manager = LiveTradeManager()

    cooldown = {}

    while True:
        try:
            # 1. صمام الأمان: إغلاق عطلة نهاية الأسبوع (السبت والأحد)
            if not MarketHoursFilter.is_market_open():
                logger.info("⏸️ السوق المالي مغلق حالياً (عطلة نهاية الأسبوع). البوت في وضع الاستعداد الصامت...")
                time.sleep(60)
                continue

            # 2. متابعة الصفقات المفتوحة مسبقاً وتأمين الأرباح (Breakeven Tracker)
            for symbol in config.SYMBOLS:
                current_price = feed.get_live_base_price(symbol)
                update_msg = trade_manager.check_trade_progress(symbol, current_price)
                if update_msg:
                    logger.info(f"🛡️ تم إرسال تنبيه تأمين الصفقة وحجز الأرباح على {symbol}")
                    notifier.send_message(update_msg)

            # 3. فحص اقتناص صفقات السوينغ النخبوية الجديدة
            for symbol in config.SYMBOLS:
                current_time = time.time()
                
                # تهدئة 4 ساعات على الأقل بين صفقات السوينغ لنفس الأصل
                if symbol in cooldown and (current_time - cooldown[symbol]) < 14400:
                    continue

                live_price = feed.get_live_base_price(symbol)
                signal = engine.generate_swing_opportunity(symbol, live_price)

                if signal:
                    logger.info(f"🎯 تم رصد صفقة سوينغ نخبوية متكاملة على {symbol}: {signal.action} @ {signal.entry_price}")
                    notifier.send_swing_signal(signal)
                    trade_manager.register_trade(signal)
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
