import os

TARGET_PATH = r"C:\Users\loves\Project_Phoenix\core\trader.py"
print("🔥 [Project Phoenix V26] 5대잼 AI 지능(고유 알고리즘) 이식 중...")

trader_content = """import asyncio, random, json, os
from datetime import datetime
from core.exchange import Exchange
from core.logger import AITradeLogger

def safe_num(v, default=0.0):
    try:
        f = float(v)
        if f != f or f == float('inf') or f == float('-inf'): return default
        return f
    except: return default

class PhoenixTrader:
    def __init__(self):
        self.ex = Exchange()
        self.logger = AITradeLogger()
        self.port = [
            {"code": "KRW-BTC", "name": "비트코인", "qty": 0.020129, "avg": 139647010},
            {"code": "KRW-ETH", "name": "이더리움", "qty": 0.613473, "avg": 4727629},
            {"code": "KRW-SOL", "name": "솔라나", "qty": 6.997309, "avg": 192965},
            {"code": "KRW-XRP", "name": "리플", "qty": 552.0696, "avg": 2913.0},
            {"code": "KRW-ZRX", "name": "제로엑스", "qty": 39624.97, "avg": 357.1},
            {"code": "KRW-SUI", "name": "수이", "qty": 522.1083, "avg": 2470.3},
            {"code": "KRW-ONDO", "name": "온도", "qty": 627.0825, "avg": 478.0}
        ]
        self.tkrs = [c["code"] for c in self.port] + ["KRW-USDT"]
        self.prc_cache = {} 
        self.ai_seed = 100000000.0 
        self.ais = ["스캘핑 잼", "추세추종 잼", "방패 잼", "스나이퍼 잼", "고래 잼"]
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_state.json")
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ai_mode = data.get("ai_mode", "balance")
                    self.ai_krw = safe_num(data.get("ai_krw", 100000000.0), 100000000.0)
                    self.ai_hold = {k: safe_num(v) for k, v in data.get("ai_hold", {}).items()}
                    self.ai_avg = {k: safe_num(v) for k, v in data.get("ai_avg", {}).items()}
                    self.hist = data.get("hist", [])
            except: self._init_default_state()
        else: self._init_default_state()

    def _init_default_state(self):
        self.ai_mode = "balance"
        self.ai_krw = 100000000.0
        self.ai_hold = {c["code"]: 0.0 for c in self.port}
        self.ai_avg = {c["code"]: 0.0 for c in self.port}
        self.hist = []
        self.save_state()

    def save_state(self):
        if not isinstance(self.ai_hold, dict): self.ai_hold = {}
        if not isinstance(self.ai_avg, dict): self.ai_avg = {}
        self.ai_krw = safe_num(self.ai_krw)
        self.ai_hold = {k: safe_num(v) for k, v in self.ai_hold.items()}
        self.ai_avg = {k: safe_num(v) for k, v in self.ai_avg.items()}
        data = {"ai_mode": self.ai_mode, "ai_krw": self.ai_krw, "ai_hold": self.ai_hold, "ai_avg": self.ai_avg, "hist": self.hist}
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def change_mode(self, mode):
        self.ai_mode = mode
        self.save_state()

    async def price_update_loop(self):
        while True:
            try:
                prc = await asyncio.to_thread(self.ex.get_current_price, self.tkrs)
                if prc: self.prc_cache = prc
            except: pass
            await asyncio.sleep(0.5)

    async def simulate_ai_trading(self):
        while True:
            d = {"safe": 8, "balance": 4, "aggressive": 1.5}.get(self.ai_mode, 4)
            await asyncio.sleep(random.uniform(d*0.8, d*1.5))
            if not self.prc_cache: continue
            
            c = random.choice(self.port)["code"]
            p = safe_num(self.prc_cache.get(c))
            if p <= 0: continue
            
            if not isinstance(self.ai_hold, dict): self.ai_hold = {}
            if not isinstance(self.ai_avg, dict): self.ai_avg = {}

            ai_name = random.choice(self.ais)
            old_qty = safe_num(self.ai_hold.get(c, 0.0))
            old_avg = safe_num(self.ai_avg.get(c, 0.0))
            profit_rate = ((p - old_avg) / old_avg * 100) if old_avg > 0 else 0

            side = None
            bet_ratio = 0.0
            sell_ratio = 0.0

            # 🧠 [V26 핵심] 5대잼 각자의 고유 트레이딩 알고리즘
            if ai_name == "스캘핑 잼":
                if old_qty > 0 and profit_rate > 0.5: side = "매도"; sell_ratio = 1.0 # 짧게 익절
                elif old_qty > 0 and profit_rate < -1.0: side = "매도"; sell_ratio = 0.5 # 칼손절
                else: side = "매수"; bet_ratio = 0.02 # 2%씩 짤짤이 매수

            elif ai_name == "추세추종 잼":
                if profit_rate > 1.5: side = "매수"; bet_ratio = 0.1 # 오를때 불타기
                elif profit_rate < -3.0 and old_qty > 0: side = "매도"; sell_ratio = 0.8
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.3

            elif ai_name == "방패 잼":
                if profit_rate < -5.0: side = "매수"; bet_ratio = 0.15 # 떡락시 줍줍
                elif old_qty > 0 and profit_rate > 2.0: side = "매도"; sell_ratio = 1.0
                else: continue # 평소엔 아무것도 안함 (관망)

            elif ai_name == "스나이퍼 잼":
                if profit_rate < -8.0 or random.random() < 0.05: side = "매수"; bet_ratio = 0.3 # 5% 확률로 큰거 한방
                elif old_qty > 0 and profit_rate > 5.0: side = "매도"; sell_ratio = 1.0
                else: continue

            elif ai_name == "고래 잼":
                if random.random() < 0.15: # 15% 확률로 묵직하게 움직임
                    side = random.choice(["매수", "매도"])
                    bet_ratio = 0.4; sell_ratio = 0.5
                else: continue

            if not side: continue

            # AI 모드(안정/밸런스/공격)에 따른 배율 부스트 적용
            mode_multi = {"safe": 0.5, "balance": 1.0, "aggressive": 2.0}.get(self.ai_mode, 1.0)
            bet_ratio = min(bet_ratio * mode_multi, 0.9)

            qty = 0
            if side == "매수":
                bet = self.ai_krw * bet_ratio
                if bet < 5000: continue
                qty = bet / p
                self.ai_krw -= bet
                new_qty = old_qty + qty
                new_avg = ((old_qty * old_avg) + bet) / new_qty if new_qty > 0 else 0
                self.ai_hold[c] = safe_num(new_qty)
                self.ai_avg[c] = safe_num(new_avg)
            else:
                if old_qty < 0.0001: continue
                qty = old_qty * sell_ratio
                self.ai_hold[c] = safe_num(old_qty - qty)
                self.ai_krw += qty * p
                if self.ai_hold.get(c, 0.0) < 0.000001:
                    self.ai_hold[c] = 0.0
                    self.ai_avg[c] = 0.0
                
            log = self.logger.log_trade(ai_name, c.replace("KRW-",""), side, qty, p)
            self.hist.insert(0, log)
            if len(self.hist) > 100: self.hist.pop()
            
            self.save_state()

    async def get_portfolio_status(self):
        usdt = safe_num(self.prc_cache.get("KRW-USDT", 1450), 1450.0)
        res = []
        analysis_data = {}
        ai_coin_pnl = []
        
        if not isinstance(self.ai_hold, dict): self.ai_hold = {}
        if not isinstance(self.ai_avg, dict): self.ai_avg = {}

        for c in self.port:
            sym = c["code"].split("-")[1]
            cp = safe_num(self.prc_cache.get(c["code"]))
            if cp <= 0: cp = safe_num(c["avg"])
            
            c_qty = safe_num(c["qty"])
            c_avg = safe_num(c["avg"])
            val = cp * c_qty
            prof = val - (c_avg * c_qty)
            rate = ((cp - c_avg) / c_avg) * 100 if c_avg > 0 else 0
            
            status = "초강세" if rate > 5 else "상승" if rate > 0 else "조정" if rate > -5 else "하락"
            rec_jam = "추세추종 잼" if rate > 0 else "방패 잼"
            rsi_sim = round(random.uniform(20, 80) if rate == 0 else min(max(50 + rate * 3, 10), 90), 1)
            
            analysis_data[sym] = {"status": status, "rec": rec_jam, "rsi": rsi_sim}
            res.append({
                "name": c["name"], "code": sym, "qty": c_qty, "avg": c_avg, 
                "cur_krw": cp, "cur_usd": cp/usdt, "val": val, "prof": prof, "rate": rate
            })

            ai_qty = safe_num(self.ai_hold.get(c["code"], 0.0))
            ai_avg_price = safe_num(self.ai_avg.get(c["code"], 0.0))
            
            if ai_qty > 0 and ai_avg_price <= 0:
                ai_avg_price = cp
                self.ai_avg[c["code"]] = cp

            ai_invested = ai_qty * ai_avg_price
            ai_valuation = ai_qty * cp
            ai_profit = ai_valuation - ai_invested
            ai_coin_rate = ((cp - ai_avg_price) / ai_avg_price) * 100 if ai_avg_price > 0 else 0

            ai_coin_pnl.append({
                "name": c["name"], "code": sym, 
                "qty": ai_qty, "avg": ai_avg_price,
                "invested": ai_invested, "valuation": ai_valuation,
                "profit": ai_profit, "rate": ai_coin_rate
            })
        
        tot_ai_coins = 0.0
        for code, qty in self.ai_hold.items():
            q = safe_num(qty)
            if q > 0:
                p = safe_num(self.prc_cache.get(code, 0.0))
                tot_ai_coins += (q * p)

        tot_ai = safe_num(self.ai_krw) + tot_ai_coins
        ai_prof = tot_ai - self.ai_seed
        ai_rate = (ai_prof / self.ai_seed) * 100

        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_pnl = [{
            "date": today_str, 
            "d_prof": ai_prof, "a_prof": ai_prof,
            "d_rate": ai_rate, "a_rate": ai_rate,
            "s_asset": self.ai_seed, "e_asset": tot_ai
        }]

        return {
            "usdt": usdt, "data": res, "hist": self.hist, 
            "ai_krw": safe_num(self.ai_krw), "ai_tot": tot_ai, 
            "ai_prof": ai_prof, "ai_rate": ai_rate,
            "analysis": analysis_data, "ai_coin_pnl": ai_coin_pnl,
            "daily_pnl": daily_pnl
        }
"""

with open(TARGET_PATH, "w", encoding="utf-8") as f:
    f.write(trader_content)

print("✅ 5대잼 고유 알고리즘 뇌 수술 성공!")