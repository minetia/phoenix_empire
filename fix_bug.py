import os

# 수정할 파일 경로
TARGET_PATH = r"C:\Users\loves\Project_Phoenix\core\trader.py"

print("🔥 [버그 수정] 단일 코인 조회 오류(float) 패치 중...")

fixed_content = """import asyncio, random
from core.exchange import Exchange
from core.logger import AITradeLogger

class PhoenixTrader:
    def __init__(self):
        self.ex = Exchange()
        self.logger = AITradeLogger()
        self.hist = []
        self.port = [
            {"code": "KRW-BTC", "name": "비트코인", "qty": 0.020129, "avg": 139647010},
            {"code": "KRW-ETH", "name": "이더리움", "qty": 0.613473, "avg": 4727629},
            {"code": "KRW-SOL", "name": "솔라나", "qty": 6.997309, "avg": 192965},
            {"code": "KRW-XRP", "name": "리플", "qty": 552.0696, "avg": 2913.0},
            {"code": "KRW-ZRX", "name": "제로엑스", "qty": 39624.97, "avg": 357.1},
            {"code": "KRW-SUI", "name": "수이", "qty": 522.1083, "avg": 2470.3},
            {"code": "KRW-ONDO", "name": "온도", "qty": 627.0825, "avg": 478.0}
        ]
        self.ai_mode = "balance"
        self.ai_krw = 100000000.0
        self.ai_hold = {c["code"]: 0.0 for c in self.port}
        self.ais = ["스캘핑 잼", "추세추종 잼", "방패 잼", "스나이퍼 잼", "고래 잼"]

    async def simulate_ai_trading(self):
        while True:
            d = {"safe": 6, "balance": 3, "aggressive": 1.5}[self.ai_mode]
            await asyncio.sleep(random.uniform(d*0.8, d*1.5))
            c = random.choice(self.port)["code"]
            side = random.choice(["매수", "매도"])
            
            # [버그 수정 완료] pyupbit의 반환값이 숫자(float)인지 딕셔너리인지 자동 판별!
            raw_p = self.ex.get_current_price(c)
            if isinstance(raw_p, dict):
                p = raw_p.get(c, 0)
            elif isinstance(raw_p, (float, int)):
                p = float(raw_p)
            else:
                p = 0
                
            if p == 0: continue
            
            qty = 0
            if side == "매수":
                ratio = {"safe": 0.05, "balance": 0.15, "aggressive": 0.4}[self.ai_mode]
                bet = self.ai_krw * random.uniform(ratio*0.5, ratio*1.2)
                if bet < 5000: continue
                qty = bet / p
                self.ai_krw -= bet
                self.ai_hold[c] += qty
            else:
                hq = self.ai_hold[c]
                if hq < 0.0001: continue
                ratio = {"safe": 1.0, "balance": 0.6, "aggressive": 0.3}[self.ai_mode]
                qty = hq * random.uniform(ratio*0.8, 1.0)
                self.ai_hold[c] -= qty
                self.ai_krw += qty * p
                
            log = self.logger.log_trade(random.choice(self.ais), c.replace("KRW-",""), side, qty, p)
            self.hist.insert(0, log)
            if len(self.hist)>100: self.hist.pop()

    async def get_portfolio_status(self):
        tkrs = [c["code"] for c in self.port] + ["KRW-USDT"]
        prc = self.ex.get_current_price(tkrs) or {}
        usdt = prc.get("KRW-USDT", 1450)
        res = []
        for c in self.port:
            cp = prc.get(c["code"], c["avg"])
            val = cp * c["qty"]
            prof = val - (c["avg"] * c["qty"])
            rate = ((cp - c["avg"]) / c["avg"]) * 100 if c["avg"]>0 else 0
            res.append({"name": c["name"], "code": c["code"].split("-")[1], "qty": c["qty"], "avg": c["avg"], "cur_krw": cp, "cur_usd": cp/usdt, "val": val, "prof": prof, "rate": rate})
        
        tot_ai = self.ai_krw + sum(qty * prc.get(code,0) for code, qty in self.ai_hold.items() if qty>0)
        return {"usdt": usdt, "data": res, "hist": self.hist, "ai_tot": tot_ai}
"""

with open(TARGET_PATH, "w", encoding="utf-8") as f:
    f.write(fixed_content)

print("✅ 버그 수정 완료! 다시 python main.py 를 실행하세요.")