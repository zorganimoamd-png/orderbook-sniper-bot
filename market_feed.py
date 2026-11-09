import random
import time
from typing import List, Tuple
from orderbook_engine import OrderLevel

class MarketDataFeed:
    """
    محرك تدفق بيانات عمق السوق (Level 2 Order Book Feed)
    يدعم تغذية الذهب (XAU/USD) والعملات الأجنبية.
    """
    def __init__(self):
        # أسعار مرجعية أولية
        self.base_prices = {
            "XAU/USD": 2685.50,
            "EUR/USD": 1.08500,
            "GBP/USD": 1.29400
        }

    def get_live_order_book(self, symbol: str, depth: int = 20) -> Tuple[List[OrderLevel], List[OrderLevel]]:
        """
        جلب دفتر الأوامر (Bids & Asks).
        هنا يتم محاكاة ديناميكية عمق السوق مع حقن عشوائي واقعي لجدران السيولة وعدم التوازن (Imbalance)
        لمحاكاة دخول الحيتان وصناع السوق المؤسساتيين بدقة.
        """
        center_price = self.base_prices.get(symbol, 2685.50)
        # تذبذب طفيف للسعر المرجعي
        step = 0.10 if "XAU" in symbol else 0.0001
        center_price += random.choice([-step, 0, step])
        self.base_prices[symbol] = center_price

        spread = step * random.randint(1, 3)
        best_bid = round(center_price - spread / 2.0, 2 if "XAU" in symbol else 5)
        best_ask = round(center_price + spread / 2.0, 2 if "XAU" in symbol else 5)

        # احتمالية ظهور جدار مؤسساتي (Institutional Wall) في هذه اللحظة
        has_whale = random.random() < 0.35  # 35% احتمال ظهور سيناريو تدفق أوامر حاد
        whale_side = random.choice(["bid", "ask"]) if has_whale else None

        bids: List[OrderLevel] = []
        for i in range(depth):
            p = round(best_bid - (i * step), 2 if "XAU" in symbol else 5)
            # أحجام طبيعية من 5 إلى 35 عقد
            vol = round(random.uniform(5.0, 35.0), 1)
            # إذا كان هناك حوت شرائي
            if whale_side == "bid" and i in [3, 4, 5]:
                vol = round(random.uniform(150.0, 300.0), 1)  # جدار سيولة ضخم
            bids.append(OrderLevel(price=p, volume=vol))

        asks: List[OrderLevel] = []
        for i in range(depth):
            p = round(best_ask + (i * step), 2 if "XAU" in symbol else 5)
            vol = round(random.uniform(5.0, 35.0), 1)
            # إذا كان هناك حوت بيعي
            if whale_side == "ask" and i in [3, 4, 5]:
                vol = round(random.uniform(150.0, 300.0), 1)  # جدار سيولة ضخم
            asks.append(OrderLevel(price=p, volume=vol))

        return bids, asks
