import csv, os, random
from datetime import datetime, timedelta
class AITradeLogger:
    def __init__(self):
        self.fn = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_trade_log.csv")
        if not os.path.exists(self.fn):
            with open(self.fn, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(["체결시간", "코인명", "마켓", "종류", "거래수량", "거래단가", "거래금액", "수수료", "정산금액", "주문시간"])
    def log_trade(self, ai, coin, side, qty, price):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d %H:%M:%S")
        order_t = (now - timedelta(seconds=random.randint(1, 2))).strftime("%Y-%m-%d %H:%M:%S")
        tot = qty * price
        fee = tot * 0.0005 
        settle = tot + fee if side == "매수" else tot - fee
        with open(self.fn, 'a', newline='', encoding='utf-8-sig') as f:
            csv.writer(f).writerow([t, coin, "KRW", side, f"{qty:.8f}", f"{price:,.0f}", f"{tot:,.0f}", f"{fee:,.0f}", f"{settle:,.0f}", order_t])
        return {
            "time": t[11:], "full_time": t, "order_time": order_t,
            "ai": ai, "coin": coin, "market": "KRW", "side": side,
            "qty": qty, "price": price, "tot": tot, "fee": fee, "settle": settle
        }
