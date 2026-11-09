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

        v_bid_0 = top_bids[0].volume
        v_ask_0 = top_asks[0].volume
        micro_price = (best_bid * v_ask_0 + best_ask * v_bid_0) / (v_bid_0 + v_ask_0) if (v_bid_0 + v_ask_0) > 0 else mid_price

        avg_bid_vol = total_bid_vol / len(top_bids) if top_bids else 1.0
        avg_ask_vol = total_ask_vol / len(top_asks) if top_asks else 1.0

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
        micro_price = metrics["micro_price"]
        bid_walls = metrics["bid_walls"]
        ask_walls = metrics["ask_walls"]

        # تحديد عدد الخانات بدقة: 5 خانات للفوركس، وخانتان للذهب
        is_gold = "XAU" in symbol or "GOLD" in symbol
        digits = 2 if is_gold else 5
        buffer = config.SL_BUFFER.get(symbol, 1.5 if is_gold else 0.0006)

        # -------------------------------------------------------------
        # سيناريو الشراء (Bullish Imbalance)
        # -------------------------------------------------------------
        if obi >= config.IMBALANCE_THRESHOLD and len(bid_walls) > 0:
            primary_wall = max(bid_walls, key=lambda w: w.volume)
            entry_price = best_ask
            entry_low = round(min(best_bid, primary_wall.price), digits)
            entry_high = round(best_ask, digits)

            # وقف الخسارة محمي خلف الجدار بهامش Buffer
            stop_loss = round(primary_wall.price - buffer, digits)
            risk = entry_price - stop_loss

            # صمام أمان لمنع أي قيمة سالبة أو غير منطقية
            min_risk = 0.50 if is_gold else 0.0004
            if risk <= min_risk or stop_loss <= 0:
                stop_loss = round(entry_price - (buffer * 2), digits)
                risk = entry_price - stop_loss

            tp1 = round(entry_price + (risk * config.MIN_RR_RATIO), digits)
            tp2 = round(entry_price + (risk * 2.5), digits)
            rr = round((tp1 - entry_price) / risk, 2)

            rationale = (
                f"رصد جدار شراء مؤسساتي عند {primary_wall.price} بحجم {primary_wall.volume:.2f} عقد. "
                f"مؤشر عدم التوازن (OBI) يسجل ضغطاً شرائياً بنسبة +{obi*100:.1f}%. "
                f"السعر العادل اللحظي (Micro-Price) يرتفع فوق السعر الحالي."
            )

            return TradeSignal(
                symbol=symbol,
                action="BUY 🟢",
                entry_price=round(entry_price, digits),
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

        # -------------------------------------------------------------
        # سيناريو البيع (Bearish Imbalance)
        # -------------------------------------------------------------
        elif obi <= -config.IMBALANCE_THRESHOLD and len(ask_walls) > 0:
            primary_wall = max(ask_walls, key=lambda w: w.volume)
            entry_price = best_bid
            entry_high = round(max(best_ask, primary_wall.price), digits)
            entry_low = round(best_bid, digits)

            stop_loss = round(primary_wall.price + buffer, digits)
            risk = stop_loss - entry_price

            min_risk = 0.50 if is_gold else 0.0004
            if risk <= min_risk:
                stop_loss = round(entry_price + (buffer * 2), digits)
                risk = stop_loss - entry_price

            tp1 = round(entry_price - (risk * config.MIN_RR_RATIO), digits)
            tp2 = round(entry_price - (risk * 2.5), digits)
            rr = round((entry_price - tp1) / risk, 2)

            rationale = (
                f"رصد جدار بيع مؤسساتي عند {primary_wall.price} بحجم {primary_wall.volume:.2f} عقد. "
                f"مؤشر عدم التوازن (OBI) يسجل ضغطاً بيعياً بنسبة {obi*100:.1f}%. "
                f"السعر العادل اللحظي (Micro-Price) ينحدر دون السعر الحالي."
            )

            return TradeSignal(
                symbol=symbol,
                action="SELL 🔴",
                entry_price=round(entry_price, digits),
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
