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
    action: str           # BUY أو SELL
    entry_price: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward_ratio: float
    obi_score: float      # Order Book Imbalance (-1.0 إلى 1.0)
    micro_price: float
    wall_price: float
    wall_volume: float
    rationale: str

class OrderBookAnalyzer:
    def __init__(self, depth: int = config.ORDER_BOOK_DEPTH):
        self.depth = depth

    def calculate_metrics(self, bids: List[OrderLevel], asks: List[OrderLevel]) -> Dict:
        """
        حساب المقاييس الرياضية العميقة لدفتر الأوامر
        """
        if not bids or not asks:
            return {}

        top_bids = bids[:self.depth]
        top_asks = asks[:self.depth]

        total_bid_vol = sum(b.volume for b in top_bids)
        total_ask_vol = sum(a.volume for a in top_asks)

        # 1. Order Book Imbalance (OBI)
        # OBI = (BidVol - AskVol) / (BidVol + AskVol)
        total_vol = total_bid_vol + total_ask_vol
        obi = (total_bid_vol - total_ask_vol) / total_vol if total_vol > 0 else 0.0

        # Best Bid and Best Ask
        best_bid = top_bids[0].price
        best_ask = top_asks[0].price
        spread = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2.0

        # 2. Micro-Price (Volume Weighted Mid Price)
        # السعر الحقيقي العادل اللحظي مع احتساب ضغط أول مستوى
        v_bid_0 = top_bids[0].volume
        v_ask_0 = top_asks[0].volume
        micro_price = (best_bid * v_ask_0 + best_ask * v_bid_0) / (v_bid_0 + v_ask_0) if (v_bid_0 + v_ask_0) > 0 else mid_price

        # 3. اكتشاف جدران السيولة (Liquidity Walls)
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
        """
        اقتناص الفرصة بناءً على توافق الجدران السيولة واختلال التوازن OBI
        """
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

        buffer = config.SL_BUFFER.get(symbol, 1.0)

        # -------------------------------------------------------------
        # سيناريو الشراء القوي (Bullish Imbalance + Support Wall)
        # -------------------------------------------------------------
        if obi >= config.IMBALANCE_THRESHOLD and len(bid_walls) > 0:
            # أكبر جدار شراء كدعم مؤسساتي
            primary_wall = max(bid_walls, key=lambda w: w.volume)
            
            # الدخول بالقرب من أفضل طلب / ارتداد الجدار
            entry_price = best_ask
            entry_low = round(min(best_bid, primary_wall.price), 2 if "XAU" in symbol else 5)
            entry_high = round(best_ask, 2 if "XAU" in symbol else 5)
            
            # وقف الخسارة أسفل جدار السيولة مباشرة
            stop_loss = round(primary_wall.price - buffer, 2 if "XAU" in symbol else 5)
            risk = entry_price - stop_loss

            if risk <= 0:
                return None

            # أهداف الربح (TP) تستهدف أول جدار بيعي أو مستويات مضاعفة للمخاطرة
            if ask_walls:
                tp1_target = min(w.price for w in ask_walls)
            else:
                tp1_target = entry_price + (risk * config.MIN_RR_RATIO)

            tp1 = round(max(tp1_target, entry_price + risk * 1.5), 2 if "XAU" in symbol else 5)
            tp2 = round(entry_price + (risk * 3.0), 2 if "XAU" in symbol else 5)
            
            rr = round((tp1 - entry_price) / risk, 2)
            if rr < 1.5:
                return None

            rationale = (
                f"رصد جدار شراء مؤسساتي ضخم عند {primary_wall.price} بحجم {primary_wall.volume:.1f} عقد. "
                f"مؤشر عدم التوازن (OBI) يسجل ضغطاً شرائياً بنسبة +{obi*100:.1f}%. "
                f"السعر العادل اللحظي (Micro-Price) يرتفع فوق السعر الحالي."
            )

            return TradeSignal(
                symbol=symbol,
                action="BUY 🟢",
                entry_price=round(entry_price, 2 if "XAU" in symbol else 5),
                entry_zone=(entry_low, entry_high),
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                risk_reward_ratio=rr,
                obi_score=round(obi, 3),
                micro_price=round(micro_price, 2 if "XAU" in symbol else 5),
                wall_price=primary_wall.price,
                wall_volume=primary_wall.volume,
                rationale=rationale
            )

        # -------------------------------------------------------------
        # سيناريو البيع القوي (Bearish Imbalance + Resistance Wall)
        # -------------------------------------------------------------
        elif obi <= -config.IMBALANCE_THRESHOLD and len(ask_walls) > 0:
            # أكبر جدار بيع كمقاومة مؤسساتية
            primary_wall = max(ask_walls, key=lambda w: w.volume)

            entry_price = best_bid
            entry_high = round(max(best_ask, primary_wall.price), 2 if "XAU" in symbol else 5)
            entry_low = round(best_bid, 2 if "XAU" in symbol else 5)

            # وقف الخسارة أعلى جدار البيع مباشرة
            stop_loss = round(primary_wall.price + buffer, 2 if "XAU" in symbol else 5)
            risk = stop_loss - entry_price

            if risk <= 0:
                return None

            if bid_walls:
                tp1_target = max(w.price for w in bid_walls)
            else:
                tp1_target = entry_price - (risk * config.MIN_RR_RATIO)

            tp1 = round(min(tp1_target, entry_price - risk * 1.5), 2 if "XAU" in symbol else 5)
            tp2 = round(entry_price - (risk * 3.0), 2 if "XAU" in symbol else 5)

            rr = round((entry_price - tp1) / risk, 2)
            if rr < 1.5:
                return None

            rationale = (
                f"رصد جدار بيع مؤسساتي ضخم عند {primary_wall.price} بحجم {primary_wall.volume:.1f} عقد. "
                f"مؤشر عدم التوازن (OBI) يسجل ضغطاً بيعياً عنيفاً بنسبة {obi*100:.1f}%. "
                f"السعر العادل اللحظي (Micro-Price) ينحدر دون السعر الحالي."
            )

            return TradeSignal(
                symbol=symbol,
                action="SELL 🔴",
                entry_price=round(entry_price, 2 if "XAU" in symbol else 5),
                entry_zone=(entry_low, entry_high),
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                risk_reward_ratio=rr,
                obi_score=round(obi, 3),
                micro_price=round(micro_price, 2 if "XAU" in symbol else 5),
                wall_price=primary_wall.price,
                wall_volume=primary_wall.volume,
                rationale=rationale
            )

        return None
