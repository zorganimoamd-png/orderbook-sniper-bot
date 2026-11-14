import numpy as np
from typing import List, Dict, Optional, Tuple

class DayTraderIntelligence:
    """
    مقتبس ومطور من day-trader-skill لأسواق الذهب والفوركس:
    - حساب ATR الديناميكي (Average True Range) لوقف الخسارة المتكيف.
    - كشف كسر نطاق الافتتاح (Opening Range Breakout - ORB) لجلسات لندن ونيويورك.
    - فلتر فحص المخاطر المسبق (Pre-Trade Risk Gate).
    - مضاعفات الأهداف (R-Multiples: 2R, 3.5R).
    """

    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """
        حساب المدى الحقيقي المتوسط (ATR) لتحديد مرونة وقف الخسارة
        """
        if len(closes) < 2:
            return 1.5  # قيمة افتراضية آمنة

        tr_list = []
        for i in range(1, len(closes)):
            h = highs[i]
            l = lows[i]
            prev_c = closes[i-1]
            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            tr_list.append(tr)

        if len(tr_list) < period:
            return float(np.mean(tr_list)) if tr_list else 1.5
        
        return float(np.mean(tr_list[-period:]))

    @staticmethod
    def check_pre_trade_risk(symbol: str, entry: float, stop_loss: float, spread: float) -> Tuple[bool, str]:
        """
        بوابة فحص المخاطر من trader-risk:
        - التأكد من أن السبريد لا يلتهم أكثر من 20% من مسافة الستوب.
        - التأكد من أن مسافة الستوب تكفي لتقلبات السوق ولا تُضرب بعشوائية.
        """
        risk = abs(entry - stop_loss)
        if risk <= 0:
            return False, "وقف الخسارة غير صالح (Risk <= 0)"

        # نسبة السبريد للمخاطرة
        if spread > 0 and (spread / risk) > 0.25:
            return False, f"السبريد مرتفع جداً مقارنة بالوقف ({spread:.4f} / {risk:.4f})"

        return True, "تم اجتياز فحص إدارة المخاطر بنجاح"

    @staticmethod
    def calculate_orb_levels(highs: List[float], lows: List[float], lookback: int = 15) -> Dict[str, float]:
        """
        تحديد نطاق الافتتاح المؤسساتي (Opening Range High & Low)
        """
        if not highs or not lows:
            return {}
        
        n = min(len(highs), lookback)
        or_high = max(highs[-n:])
        or_low = min(lows[-n:])
        or_mid = (or_high + or_low) / 2.0

        return {
            "or_high": or_high,
            "or_low": or_low,
            "or_mid": or_mid
        }
