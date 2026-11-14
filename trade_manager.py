import time
from typing import Dict, Optional
from institutional_engine import SwingTradeSignal

class LiveTradeManager:
    """
    نظام المتابعة الحية للصفقات وإدارة الأرباح وتأمين الدخول (Breakeven & Trailing):
    يرسل تنبيهات متابعة على تليجرام عند تحرك السعر بنجاح نحو الهدف.
    """
    def __init__(self):
        self.active_trades: Dict[str, Dict] = {}

    def register_trade(self, signal: SwingTradeSignal):
        """
        تسجيل الصفقة المفتوحة للمتابعة الحية
        """
        self.active_trades[signal.symbol] = {
            "action": signal.action,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "tp1": signal.take_profit_1,
            "tp2": signal.take_profit_2,
            "breakeven_triggered": False,
            "tp1_triggered": False,
            "opened_at": time.time()
        }

    def check_trade_progress(self, symbol: str, current_price: float) -> Optional[str]:
        """
        فحص تقدم الصفقة الحية وتوليد إشعار تأمين الأرباح ونقل الستوب لنقطة الدخول
        """
        if symbol not in self.active_trades:
            return None

        trade = self.active_trades[symbol]
        entry = trade["entry_price"]
        action = trade["action"]
        tp1 = trade["tp1"]

        # حساب المسافة المقطوعة
        if "BUY" in action:
            profit_distance = current_price - entry
            target_half_distance = (tp1 - entry) * 0.40 # عند تحقيق 40% من الهدف

            if profit_distance >= target_half_distance and not trade["breakeven_triggered"]:
                trade["breakeven_triggered"] = True
                return (
                    f"🛡️ *تنبيه تأمين الصفقة وحجز الأرباح (Breakeven Alert)* 🛡️\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💎 *الأصل المالي:* `{symbol}` ({action})\n"
                    f"📈 *السعر الحالي:* `{current_price}` (ربح محقق +{profit_distance:.2f}$)\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ *التعليمات المؤسساتية الآن:*\n"
                    f"1️⃣ *انقل وقف الخسارة (Stop Loss) فوراً إلى سعر الدخول `{entry}`*.\n"
                    f"2️⃣ أصبحت الصفقة الآن *خالية تماماً من المخاطر بنسبة 100%*.\n"
                    f"3️⃣ احجز 30% إلى 50% من الأرباح واترك الباقي ينطلق نحو TP1 و TP2."
                )

        elif "SELL" in action:
            profit_distance = entry - current_price
            target_half_distance = (entry - tp1) * 0.40

            if profit_distance >= target_half_distance and not trade["breakeven_triggered"]:
                trade["breakeven_triggered"] = True
                return (
                    f"🛡️ *تنبيه تأمين الصفقة وحجز الأرباح (Breakeven Alert)* 🛡️\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💎 *الأصل المالي:* `{symbol}` ({action})\n"
                    f"📉 *السعر الحالي:* `{current_price}` (ربح محقق +{profit_distance:.2f}$)\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ *التعليمات المؤسساتية الآن:*\n"
                    f"1️⃣ *انقل وقف الخسارة (Stop Loss) فوراً إلى سعر الدخول `{entry}`*.\n"
                    f"2️⃣ أصبحت الصفقة الآن *خالية تماماً من المخاطر بنسبة 100%*.\n"
                    f"3️⃣ احجز 30% إلى 50% من الأرباح واترك الباقي ينطلق نحو الأهداف."
                )

        return None
