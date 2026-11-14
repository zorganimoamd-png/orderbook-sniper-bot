import requests
import time
import random
from typing import List, Tuple
from orderbook_engine import OrderLevel

class MarketDataFeed:
    """
    مزود بيانات الأسعار الحية لأسواق الذهب (XAU/USD) والفوركس (EUR/USD, GBP/USD).
    تم حذف الناسداك تماماً لتركيز كامل قوة البوت على الذهب والفوركس.
    """
    def __init__(self):
        self.cached_prices = {}
        self.last_cache_time = 0

    def get_live_base_price(self, symbol: str) -> float:
        now = time.time()
        if symbol in self.cached_prices and (now - self.last_cache_time) < 10:
            return self.cached_prices[symbol]

        price = 0.0
        # 1. الذهب XAU/USD
        if "XAU" in symbol or "GOLD" in symbol:
            try:
                res = requests.get("https://api.binance.com/api/v3/ticker/bookTicker?symbol=PAXGUSDT", timeout=3)
                if res.status_code == 200:
                    d = res.json()
                    price = round(float(d['bidPrice']) + 10.80, 2)
            except Exception:
                price = self.cached_prices.get(symbol, 4104.50)
            if price == 0.0:
                price = 4104.50

        # 2. اليورو والباوند
        elif "EUR" in symbol:
            try:
                res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=3)
                if res.status_code == 200:
                    rates = res.json().get('rates', {})
                    price = round(1.0 / rates.get('EUR', 0.897), 5)
            except Exception:
                price = self.cached_prices.get(symbol, 1.11485)
            if price == 0.0:
                price = 1.11485

        elif "GBP" in symbol:
            try:
                res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=3)
                if res.status_code == 200:
                    rates = res.json().get('rates', {})
                    price = round(1.0 / rates.get('GBP', 0.748), 5)
            except Exception:
                price = self.cached_prices.get(symbol, 1.33620)
            if price == 0.0:
                price = 1.33620

        self.cached_prices[symbol] = price
        self.last_cache_time = now
        return price

    def get_live_order_book(self, symbol: str, depth: int = 20) -> Tuple[List[OrderLevel], List[OrderLevel]]:
        current_price = self.get_live_base_price(symbol)
        
        is_gold = "XAU" in symbol or "GOLD" in symbol
        is_fx = "EUR" in symbol or "GBP" in symbol

        digits = 5 if is_fx else 2
        step = 0.00005 if is_fx else 0.25
        spread = 0.00010 if is_fx else 0.25

        best_bid = round(current_price - (spread / 2.0), digits)
        best_ask = round(current_price + (spread / 2.0), digits)

        bids: List[OrderLevel] = []
        asks: List[OrderLevel] = []

        # محاكاة تدفق سيولة مؤسساتية حقيقية
        whale_trigger = random.random() < 0.30
        whale_side = random.choice(["bid", "ask"]) if whale_trigger else None

        for i in range(depth):
            p_bid = round(best_bid - (i * step), digits)
            p_ask = round(best_ask + (i * step), digits)

            v_bid = round(random.uniform(15.0, 35.0) + (i * 1.5), 1)
            v_ask = round(random.uniform(15.0, 35.0) + (i * 1.5), 1)

            if whale_side == "bid" and i == 3:
                v_bid = round(v_bid * 3.5, 1) # جدار سيولة مؤسساتي
            elif whale_side == "ask" and i == 3:
                v_ask = round(v_ask * 3.5, 1)

            bids.append(OrderLevel(price=p_bid, volume=v_bid))
            asks.append(OrderLevel(price=p_ask, volume=v_ask))

        return bids, asks
