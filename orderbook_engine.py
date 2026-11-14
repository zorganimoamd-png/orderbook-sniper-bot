import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import config

@dataclass
class OrderLevel:
    price: float
    volume: float

@dataclass
class TradeSignal:
    symbol: str
    action: str
    entry_price: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward_ratio: float
    obi_score: float
    micro_price: float
    wall_price: float
    wall_volume: float
    rationale: str

class OrderBookAnalyzer:
    def __init__(self, depth: int = config.ORDER_BOOK_DEPTH):
        self.depth = depth

    def calculate_metrics(self, bids: List[OrderLevel], asks: List[OrderLevel]) -> Dict:
        if not bids or not asks:
            return {}

        top_bids = bids[:self.depth]
        top_asks = asks[:self.depth]

        total_bid_vol = sum(b.volume for b in top_bids)
        total_ask_vol = sum(a.volume for a in top_asks)

        total_vol = total_bid_vol + total_ask_vol
        obi = (total_bid_vol - total_ask_vol) / total_vol if total_vol > 0 else 0.0

        best_bid = top_bids[0].price
        best_ask = top_asks[0].price
        spread = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2.0

        # Micro-Price (Volume Weighted Mid Price)
        v_bid_0 = top_bids[0].volume
        v_ask_0 = top_asks[0].volume
        micro_price = (best_bid * v_ask_0 + best_ask * v_bid_0) / (v_bid_0 + v_ask_0) if (v_bid_0 + v_ask_0) > 0 else mid_price

        avg_bid_vol = total_bid_vol / len(top_bids) if top_bids else 1.0
        avg_ask_vol = total_ask_vol / len(top_asks) if top_asks else 1.0

        # جدران السيولة الحقيقية
        bid_walls = [b for b in top_bids if b.volume >= avg_bid_vol * config.LIQUIDITY_WALL_MULTIPLIER]
        ask_walls = [a for a in top_asks if a.volume >= avg_ask_vol * config.LIQUIDITY_WALL_MULTIPLIER]

        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
            "micro_price": micro_price,
            "total_bid_vol": total_bid_vol,
            "total_ask_vol": total_ask_vol,
            "obi": obi,
            "bid_walls": bid_walls,
            "ask_walls": ask_walls,
            "top_bids": top_bids,
            "top_asks": top_asks
        }

    def evaluate_opportunity(self, symbol: str, bids: List[OrderLevel], asks: List[OrderLevel]) -> Optional[TradeSignal]:
        metrics = self.calculate_metrics(bids, asks)
        if not metrics:
            return None

        obi = metrics["obi"]
        best_bid = metrics["best_bid"]
        best_ask = metrics["best_ask"]
        mid_price = metrics["mid_price"]
        micro_price = metrics["micro_price"]
        bid_walls = metrics["bid_walls"]
        ask_walls = metrics["ask_walls"]

        is_fx = "EUR" in symbol or "GBP" in symbol
        digits = 5 if is_fx else 2
        buffer = config.SL_BUFFER.get(symbol, 1.5)
        min_risk_floor = config.MIN_RISK_FLOOR.get(symbol, 1.2)

        # =============================================================
        # 🟢 سيناريو الشراء المؤسساتي القوي (Bullish Sniper Setup)
        # 1. اختلال توازن لصالح المشترين OBI >= Threshold
        # 2. وجود جدار دعم مؤسساتي حقيقي
        # =============================================================
        if obi >= config.IMBALANCE_THRESHOLD and len(bid_walls) > 0:
            primary_wall = max(bid_walls, key=lambda w: w.volume)
            
            entry_price = round(best_ask, digits)
            entry_low = round(min(best_bid, primary_wall.price), digits)
            entry_high = round(best_ask, digits)

            # وقف الخسارة محمي خلف الجدار بهامش Buffer
            stop_loss = round(primary_wall.price - buffer, digits)
            risk = entry_price - stop_loss

            # التأكد من أن الستوب ليس ضيقاً بشكل خطير
            if risk < min_risk_floor or stop_loss <= 0:
                stop_loss = round(entry_price - (min_risk_floor * 1.5), digits)
                risk = entry_price - stop_loss

            # أهداف ربح مؤسساتية مدروسة: R:R = 1:2 و 1:3.5
            tp1 = round(entry_price + (risk * config.MIN_RR_RATIO), digits)
            tp2 = round(entry_price + (risk * 3.5), digits)
            rr = round((tp1 - entry_price) / risk, 2)

            rationale = (
                f"رصد جدار شراء مؤسساتي قوي عند {primary_wall.price} بحجم {primary_wall.volume:.1f} عقد. "
                f"مؤشر ضغط تدفق الأوامر (OBI) يسجل تفوقاً شرائياً بنسبة +{obi*100:.1f}%. "
                f"انحياز السعر العادل (Micro-Price={round(micro_price, digits)}) يدعم اختراق المقاومات القريبة."
            )

            return TradeSignal(
                symbol=symbol,
                action="BUY 🟢",
                entry_price=entry_price,
                entry_zone=(entry_low, entry_high),
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                risk_reward_ratio=rr,
                obi_score=round(obi, 3),
                micro_price=round(micro_price, digits),
                wall_price=primary_wall.price,
                wall_volume=primary_wall.volume,
                rationale=rationale
            )

        # =============================================================
        # 🔴 سيناريو البيع المؤسساتي القوي (Bearish Sniper Setup)
        # 1. اختلال توازن لصالح البائعين OBI <= -Threshold
        # 2. وجود جدار مقاومة مؤسساتي حقيقي
        # =============================================================
        elif obi <= -config.IMBALANCE_THRESHOLD and len(ask_walls) > 0:
            primary_wall = max(ask_walls, key=lambda w: w.volume)

            entry_price = round(best_bid, digits)
            entry_high = round(max(best_ask, primary_wall.price), digits)
            entry_low = round(best_bid, digits)

            stop_loss = round(primary_wall.price + buffer, digits)
            risk = stop_loss - entry_price

            if risk < min_risk_floor:
                stop_loss = round(entry_price + (min_risk_floor * 1.5), digits)
                risk = stop_loss - entry_price

            tp1 = round(entry_price - (risk * config.MIN_RR_RATIO), digits)
            tp2 = round(entry_price - (risk * 3.5), digits)
            rr = round((entry_price - tp1) / risk, 2)

            rationale = (
                f"رصد جدار بيع مؤسساتي كثيف عند {primary_wall.price} بحجم {primary_wall.volume:.1f} عقد. "
                f"مؤشر ضغط تدفق الأوامر (OBI) يسجل تفوقاً بيعياً بنسبة {obi*100:.1f}%. "
                f"انحياز السعر العادل (Micro-Price={round(micro_price, digits)}) يدعم كسر مستويات الدعم القريبة."
            )

            return TradeSignal(
                symbol=symbol,
                action="SELL 🔴",
                entry_price=entry_price,
                entry_zone=(entry_low, entry_high),
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                risk_reward_ratio=rr,
                obi_score=round(obi, 3),
                micro_price=round(micro_price, digits),
                wall_price=primary_wall.price,
                wall_volume=primary_wall.volume,
                rationale=rationale
            )

        return None
