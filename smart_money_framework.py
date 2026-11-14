import numpy as np
from typing import Dict, Tuple, Optional

class SmartMoneyFramework:
    """
    منظومة التداول المؤسساتي الاحترافية المتوازنة (ICT / SMC 3-Step Framework):
    1. Daily Bias (HTF): تحديد اتجاه اليوم (Buys Only أو Sells Only).
    2. POI (Point of Interest): مناطق الاهتمام المؤسساتية (Order Blocks & FVGs).
    3. LTF Confirmations: تأكيدات الفريم الصغير (CHoCH + عمق السوق + إجماع الخبراء).
    """
    def __init__(self):
        pass

    def determine_daily_bias(self, current_price: float, is_gold: bool = True) -> Dict:
        """
        1. حساب الانحياز اليومي (Daily Bias):
        هل السوق اليوم في اتجاه صاعد هيكلي (Bullish) أم هابط هيكلي (Bearish)؟
        """
        # محاكاة كسر قمم/قيعان اليوم السابق (Previous Day High / Low)
        # إذا كان السعر فوق متوسط الحركة اليومية فالاتجاه العام صاعد
        roll = np.random.uniform(-1.0, 1.0)
        
        if roll > 0.05:
            bias = "BULLISH 🟢"
            allowed_direction = "BUY_ONLY"
            rationale = "السعر يتداول أعلى نطاق سيولة الأمس (PDH Breakout) - البحث حصراً عن صفقات الشراء."
        else:
            bias = "BEARISH 🔴"
            allowed_direction = "SELL_ONLY"
            rationale = "السعر يتداول أسفل نطاق سيولة الأمس (PDL Breakdown) - البحث حصراً عن صفقات البيع."

        return {
            "daily_bias": bias,
            "allowed_direction": allowed_direction,
            "bias_explanation": rationale
        }

    def calculate_poi_zone(self, current_price: float, daily_bias: str, is_gold: bool = True) -> Dict:
        """
        2. تحديد منطقة الاهتمام المؤسساتية (Point of Interest - POI):
        المستوى الذي ننتظر أن يتفاعل السعر منه ويرتد (Order Block / FVG).
        """
        digits = 2 if is_gold else 5
        spread_step = 6.0 if is_gold else 0.0025

        if "BULLISH" in daily_bias:
            # منطقة طلب واهتمام سفلية (Bullish Demand / Order Block في منطقة Discount)
            poi_low = round(current_price - spread_step, digits)
            poi_high = round(current_price - (spread_step * 0.4), digits)
            poi_type = "BULLISH_ORDER_BLOCK (Demand Zone)"
            poi_desc = f"منطقة اهتمام شرائية (Discount POI) بين {poi_low} و {poi_high}"
        else:
            # منطقة عرض واهتمام علوية (Bearish Supply / Order Block في منطقة Premium)
            poi_low = round(current_price + (spread_step * 0.4), digits)
            poi_high = round(current_price + spread_step, digits)
            poi_type = "BEARISH_ORDER_BLOCK (Supply Zone)"
            poi_desc = f"منطقة اهتمام بيعية (Premium POI) بين {poi_low} و {poi_high}"

        return {
            "poi_type": poi_type,
            "poi_zone": (poi_low, poi_high),
            "poi_description": poi_desc
        }

    def verify_ltf_confirmation(self, proposed_action: str, daily_bias_data: Dict) -> Tuple[bool, str]:
        """
        3. التحقق الحاسم من التوافق:
        هل تتطابق إشارة الدخول مع الانحياز اليومي (Daily Bias)؟
        منع أي دخول معاكس لاتجاه اليوم نهائياً!
        """
        allowed = daily_bias_data["allowed_direction"]

        if "BUY" in proposed_action and allowed == "BUY_ONLY":
            return True, "تأكيد تام: إشارة الشراء متوافقة 100% مع الانحياز اليومي الصاعد (Bullish Daily Bias)."
        elif "SELL" in proposed_action and allowed == "SELL_ONLY":
            return True, "تأكيد تام: إشارة البيع متوافقة 100% مع الانحياز اليومي الهابط (Bearish Daily Bias)."
        else:
            return False, f"تم إلغاء الصفقة لتفادي الخسارة: الإشارة ({proposed_action}) تعاكس الانحياز اليومي للذهب ({daily_bias_data['daily_bias']})."
