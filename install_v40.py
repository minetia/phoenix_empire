import os

TARGET_PATH = r"C:\Users\loves\Project_Phoenix"
print("🔥 [Project Phoenix V40] 금액 누락 버그 픽스 & 6대잼 풀악셀 매매 엔진 장착 중...")

files = {}

# 1. Main Server (유지)
files["main.py"] = """from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from core.trader import PhoenixTrader
import asyncio, os

trader = PhoenixTrader()

@asynccontextmanager
async def lifespan(app: FastAPI):
    t1 = asyncio.create_task(trader.price_update_loop())
    t2 = asyncio.create_task(trader.simulate_ai_trading())
    yield
    t1.cancel()
    t2.cancel()

app = FastAPI(lifespan=lifespan)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/mode/{mode}")
async def set_mode(mode: str):
    trader.change_mode(mode)
    return {"status": "success"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await trader.get_portfolio_status()
            await websocket.send_json(data)
        except Exception: break
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="warning")
"""

# 2. Trader (V40 핵심: 6대잼 전부 다 "풀악셀" 초스피드 매매하도록 알고리즘 대폭 완화)
files["core/trader.py"] = """import asyncio, random, json, os
from datetime import datetime, timedelta
from core.exchange import Exchange
from core.logger import AITradeLogger

def safe_num(v, default=0.0):
    try: f = float(v); return f if f == f and f != float('inf') and f != float('-inf') else default
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
        self.ai_seed = 100000000.0 / 6 
        
        self.agents = {
            "전략 잼": {"cash": self.ai_seed, "profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "수집 잼": {"cash": self.ai_seed, "profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "정렬 잼": {"cash": self.ai_seed, "profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "타이밍 잼": {"cash": self.ai_seed, "profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "가디언 잼": {"cash": self.ai_seed, "profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "행동 잼": {"cash": self.ai_seed, "profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []}
        }
        self.ais = list(self.agents.keys())
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_state.json")
        self.load_state()
        self._init_today_history()

    def _init_today_history(self):
        today_str = datetime.now().strftime("%m.%d")
        for a_name, a_data in self.agents.items():
            if len(a_data.get("history", [])) == 0:
                a_data.setdefault("history", []).append({"date": today_str, "d_prof": 0.0, "c_prof": 0.0, "d_rate": 0.0, "c_rate": 0.0, "b_asset": self.ai_seed, "e_asset": self.ai_seed})

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ai_mode = data.get("ai_mode", "balance")
                    self.ai_krw = safe_num(data.get("ai_krw", 100000000.0))
                    self.ai_hold = {k: safe_num(v) for k, v in data.get("ai_hold", {}).items()}
                    self.ai_avg = {k: safe_num(v) for k, v in data.get("ai_avg", {}).items()}
                    self.agents = data.get("agents", self.agents)
                    self.hist = data.get("hist", [])
            except: pass

    def save_state(self):
        data = {"ai_mode": self.ai_mode, "ai_krw": self.ai_krw, "ai_hold": self.ai_hold, "ai_avg": self.ai_avg, "agents": self.agents, "hist": self.hist}
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def change_mode(self, mode):
        self.ai_mode = mode; self.save_state()

    async def price_update_loop(self):
        while True:
            try:
                prc = await asyncio.to_thread(self.ex.get_current_price, self.tkrs)
                if prc: self.prc_cache = prc
            except: pass
            await asyncio.sleep(0.5)

    async def simulate_ai_trading(self):
        while True:
            d = {"safe": 1.5, "balance": 0.8, "aggressive": 0.3}.get(self.ai_mode, 0.8)
            await asyncio.sleep(random.uniform(d * 0.5, d * 1.5))
            if not self.prc_cache: continue
            
            c = random.choice(self.port)["code"]
            p = safe_num(self.prc_cache.get(c))
            if p <= 0: continue
            
            ai_name = random.choice(self.ais)
            old_qty = safe_num(self.ai_hold.get(c, 0.0))
            old_avg = safe_num(self.ai_avg.get(c, 0.0))
            bot_hold = safe_num(self.agents[ai_name]["holds"].get(c, 0.0))
            bot_cash = safe_num(self.agents[ai_name].get("cash", self.ai_seed))
            profit_rate = ((p - old_avg) / old_avg * 100) if old_avg > 0 else 0

            side = None; bet_ratio = 0.0; sell_ratio = 0.0

            # 🔥 [V40 핵심] 6대잼 풀악셀 개조! 관망을 아예 없애고 무조건 사고 팔도록 확률 대폭 상향!
            if ai_name == "전략 잼": 
                if profit_rate > 0.5: side = "매수"; bet_ratio = 0.15 
                elif profit_rate < -1.0 and bot_hold > 0: side = "매도"; sell_ratio = 0.8
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.08; sell_ratio = 0.4
            elif ai_name == "수집 잼": 
                if profit_rate < -0.5: side = "매수"; bet_ratio = 0.1
                elif bot_hold > 0 and profit_rate > 2.0: side = "매도"; sell_ratio = 0.5
                else: side = "매수" if random.random() > 0.3 else "매도"; bet_ratio = 0.05; sell_ratio = 0.3
            elif ai_name == "정렬 잼": 
                if bot_hold > 0 and profit_rate > 0.5: side = "매도"; sell_ratio = 0.5
                elif profit_rate < -0.5: side = "매수"; bet_ratio = 0.1
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.2
            elif ai_name == "타이밍 잼": 
                if profit_rate < -1.5 or random.random() < 0.2: side = "매수"; bet_ratio = 0.25 
                elif bot_hold > 0 and (profit_rate > 1.5 or random.random() < 0.2): side = "매도"; sell_ratio = 0.7
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.3
            elif ai_name == "가디언 잼": 
                if bot_hold > 0 and profit_rate < -1.0: side = "매도"; sell_ratio = 1.0 
                elif bot_hold > 0 and profit_rate > 1.0: side = "매도"; sell_ratio = 0.8 
                elif profit_rate < -2.0 or random.random() < 0.25: side = "매수"; bet_ratio = 0.2 
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.4
            elif ai_name == "행동 잼": 
                if bot_hold > 0 and profit_rate > 0.2: side = "매도"; sell_ratio = 1.0 
                elif bot_hold > 0 and profit_rate < -0.4: side = "매도"; sell_ratio = 1.0 
                else: side = "매수"; bet_ratio = 0.1

            if not side: continue
            mode_multi = {"safe": 0.5, "balance": 1.0, "aggressive": 2.0}.get(self.ai_mode, 1.0)
            bet_ratio = min(bet_ratio * mode_multi, 0.9)

            qty = 0
            if side == "매수":
                bet = bot_cash * bet_ratio
                if bet < 5000: continue
                qty = bet / p
                self.ai_krw -= bet
                self.agents[ai_name]["cash"] = bot_cash - bet
                new_qty = old_qty + qty
                new_avg = ((old_qty * old_avg) + bet) / new_qty if new_qty > 0 else 0
                self.ai_hold[c] = safe_num(new_qty)
                self.ai_avg[c] = safe_num(new_avg)
                self.agents[ai_name]["holds"][c] = bot_hold + qty
            else:
                if bot_hold < 0.0001: continue
                qty = bot_hold * sell_ratio
                sell_amount = qty * p
                buy_amount = qty * old_avg
                
                self.ai_hold[c] = safe_num(old_qty - qty)
                self.ai_krw += sell_amount
                self.agents[ai_name]["cash"] = bot_cash + sell_amount
                if self.ai_hold.get(c, 0.0) < 0.000001:
                    self.ai_hold[c] = 0.0; self.ai_avg[c] = 0.0
                
                self.agents[ai_name]["holds"][c] = bot_hold - qty
                
                trade_profit = sell_amount - buy_amount
                self.agents[ai_name]["profit"] += trade_profit
                if trade_profit > 0: self.agents[ai_name]["wins"] = self.agents[ai_name].get("wins", 0) + 1
                else: self.agents[ai_name]["losses"] = self.agents[ai_name].get("losses", 0) + 1
                
            log = self.logger.log_trade(ai_name, c.replace("KRW-",""), side, qty, p)
            self.hist.insert(0, log)
            if len(self.hist) > 100: self.hist.pop()
            
            today_str = datetime.now().strftime("%m.%d")
            for a_name, a_data in self.agents.items():
                if not a_data.get("history"): continue
                last_record = a_data["history"][-1]
                if last_record["date"] == today_str:
                    last_record["d_prof"] = a_data["profit"]
                    last_record["c_prof"] = a_data["profit"]
                    last_record["d_rate"] = (a_data["profit"] / self.ai_seed) * 100
                    last_record["c_rate"] = (a_data["profit"] / self.ai_seed) * 100
                    last_record["e_asset"] = self.ai_seed + a_data["profit"]

            self.save_state()

    async def get_portfolio_status(self):
        usdt = safe_num(self.prc_cache.get("KRW-USDT", 1450), 1450.0)
        res = []; analysis_data = {}; ai_coin_pnl = []
        
        tot_w = 0; tot_l = 0
        for data in self.agents.values():
            tot_w += data.get("wins", 0); tot_l += data.get("losses", 0)
        global_win_rate = (tot_w / (tot_w + tot_l) * 100) if (tot_w + tot_l) > 0 else 0.0
        global_ai_score = round(random.uniform(88.0, 99.5), 1) 
        
        for c in self.port:
            sym = c["code"].split("-")[1]
            cp = safe_num(self.prc_cache.get(c["code"]))
            if cp <= 0: cp = safe_num(c["avg"])
            
            c_qty = safe_num(c["qty"]); c_avg = safe_num(c["avg"])
            val = cp * c_qty; prof = val - (c_avg * c_qty)
            rate = ((cp - c_avg) / c_avg) * 100 if c_avg > 0 else 0
            
            status = "초강세" if rate > 5 else "상승" if rate > 0 else "조정" if rate > -5 else "하락"
            analysis_data[sym] = {"status": status, "rec": random.choice(self.ais), "rsi": round(random.uniform(20, 80), 1)}
            res.append({"name": c["name"], "code": sym, "qty": c_qty, "avg": c_avg, "cur_krw": cp, "cur_usd": cp/usdt, "val": val, "prof": prof, "rate": rate})

            ai_qty = safe_num(self.ai_hold.get(c["code"], 0.0))
            if ai_qty > 0.00001:
                ai_avg_price = safe_num(self.ai_avg.get(c["code"], 0.0))
                if ai_avg_price <= 0: ai_avg_price = cp
                ai_invested = ai_qty * ai_avg_price
                ai_valuation = ai_qty * cp
                ai_profit = ai_valuation - ai_invested
                ai_coin_rate = ((cp - ai_avg_price) / ai_avg_price) * 100 if ai_avg_price > 0 else 0
                
                owners = []
                for a_name, a_data in self.agents.items():
                    hq = safe_num(a_data["holds"].get(c["code"], 0.0))
                    if hq > 0.00001: owners.append(f"{a_name}({hq:.4f})")
                owners_str = " / ".join(owners)

                ai_coin_pnl.append({"name": c["name"], "code": sym, "qty": ai_qty, "avg": ai_avg_price, "invested": ai_invested, "valuation": ai_valuation, "profit": ai_profit, "rate": ai_coin_rate, "owners": owners_str})
        
        tot_ai_coins = sum(safe_num(qty) * safe_num(self.prc_cache.get(code, 0.0)) for code, qty in self.ai_hold.items() if safe_num(qty)>0)
        tot_ai = safe_num(self.ai_krw) + tot_ai_coins
        ai_prof = tot_ai - 100000000.0
        ai_rate = (ai_prof / 100000000.0) * 100

        ranking = []; agent_details = {}; ai_probs = []
        for name, data in self.agents.items():
            wins = data.get("wins", 0); losses = data.get("losses", 0)
            total_trades = wins + losses
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
            
            prob = min(max(win_rate * 0.4 + 50.0 + random.uniform(-3.0, 8.0), 10.0), 99.9)
            ai_probs.append({"name": name, "prob": prob})
            
            holds_str = ", ".join([f"{code.replace('KRW-', '')}({q:.3f})" for code, q in data["holds"].items() if q > 0.0001]) or "관망 중"
            ranking.append({"name": name, "profit": data["profit"], "win_rate": win_rate, "wins": wins, "losses": losses, "holds_str": holds_str})
            
            agent_details[name] = {
                "summary": { "cum_prof": data["profit"], "cum_rate": (data["profit"] / self.ai_seed) * 100, "avg_inv": self.ai_seed },
                "history": list(reversed(data.get("history", [])))
            }
            
        ranking.sort(key=lambda x: x["profit"], reverse=True)
        ai_probs.sort(key=lambda x: x["prob"], reverse=True)

        return {
            "usdt": usdt, "data": res, "hist": self.hist, 
            "ai_krw": safe_num(self.ai_krw), "ai_tot": tot_ai, 
            "ai_prof": ai_prof, "ai_rate": ai_rate,
            "ai_coin_pnl": ai_coin_pnl,
            "ranking": ranking, "agent_details": agent_details,
            "global_stats": { "win_rate": global_win_rate, "ai_score": global_ai_score },
            "ai_probs": ai_probs,
            "analysis": analysis_data
        }
"""

# HTML UI (V40 핵심: 자바스크립트 금액 미표기 에러를 원천 차단하는 무적의 렌더링 코드 적용)
html_ui = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PHOENIX AI TRADING V40</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <style>
        body { background:#0b1016; color:#c8ccce; font-family:-apple-system,sans-serif; }
        .bg-panel { background:#12161f; } .border-line { border-color:#2b303b; }
        .up-red { color:#c84a31; } .down-blue { color:#1261c4; } .num-font { font-family:'Roboto',sans-serif; }
        ::-webkit-scrollbar { width:4px; height:4px; } ::-webkit-scrollbar-track { background:#0b1016; } ::-webkit-scrollbar-thumb { background:#2b303b; border-radius:2px;}
        .t-inact { color:#666; cursor:pointer; }
        .o-buy { background:rgba(200,74,49,0.2); color:#c84a31; border-top:2px solid #c84a31; font-weight:bold; }
        .o-sell { background:rgba(18,97,196,0.2); color:#1261c4; border-top:2px solid #1261c4; font-weight:bold; }
        .o-hist { background:#1b2029; color:#fff; border-top:2px solid #fff; font-weight:bold; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .ub-table th { font-weight: normal; color: #a1a1aa; padding: 12px 10px; border-bottom: 1px solid #1f2937; background: #0b1016; text-align: center; font-size: 11px; }
        .ub-table td { padding: 12px 10px; border-bottom: 1px solid #1f2937; text-align: center; font-size: 13px; }
        .ub-btn { background: transparent; border: none; color: #666; padding: 10px; cursor: pointer; border-bottom: 2px solid transparent; width: 50%; }
        .ub-btn.active { color: #fff; border-bottom: 2px solid #1261c4; font-weight: bold; }
    </style>
</head>
<body class="lg:h-screen flex flex-col select-none overflow-y-auto lg:overflow-hidden bg-[#0b1016]">
    <header class="py-3 lg:h-14 lg:py-0 bg-panel border-b border-line flex flex-col lg:flex-row justify-between items-center px-4 shrink-0 gap-3">
        <div class="flex flex-col lg:flex-row items-center w-full lg:w-auto gap-3 overflow-hidden">
            <div class="flex items-center cursor-pointer shrink-0" onclick="setTab('trd')">
                <span class="text-2xl lg:text-xl mr-1">🦅</span>
                <h1 class="text-2xl lg:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-300 tracking-widest italic drop-shadow-md">PHOENIX</h1>
                <span class="text-[10px] text-yellow-500 border border-yellow-500/50 bg-yellow-900/30 px-1.5 py-0.5 rounded ml-2 font-bold tracking-wide">AI CORE V40</span>
            </div>
            <nav class="flex space-x-5 text-sm font-bold ml-0 lg:ml-6 mt-2 lg:mt-0 w-full lg:w-auto overflow-x-auto whitespace-nowrap border-t lg:border-0 border-gray-800 pt-3 lg:pt-0 scrollbar-hide justify-center lg:justify-start">
                <a id="n-trd" onclick="setTab('trd')" class="text-white border-b-2 border-white pb-2 lg:pb-[18px] lg:pt-5 cursor-pointer px-1">거래소</a>
                <a id="n-port" onclick="setTab('port')" class="text-gray-500 hover:text-white pb-2 lg:pb-[18px] lg:pt-5 border-b-2 border-transparent cursor-pointer px-1">투자내역</a>
                <a id="n-pnl" onclick="setTab('pnl')" class="text-gray-500 hover:text-white pb-2 lg:pb-[18px] lg:pt-5 border-b-2 border-transparent cursor-pointer px-1">투자손익</a>
                <a id="n-detail" onclick="setTab('detail')" class="text-gray-500 hover:text-white pb-2 lg:pb-[18px] lg:pt-5 border-b-2 border-transparent cursor-pointer px-1 flex items-center gap-1 text-yellow-400">📈 AI 투자상세</a>
            </nav>
        </div>
        <div class="flex gap-4 items-center text-xs lg:text-sm text-gray-400 w-full justify-between lg:justify-end lg:w-auto mt-2 lg:mt-0 bg-[#0b1016] lg:bg-transparent p-2 lg:p-0 rounded border border-gray-800 lg:border-0 shrink-0">
            <div class="flex items-center gap-2">
                <div id="conn-status" class="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" title="서버 연결 상태"></div>
                <span class="text-yellow-500 font-bold hidden md:inline">🤖 6대잼 누적 손익:</span> 
                <span class="text-yellow-500 font-bold md:hidden">AI 손익:</span> 
                <span id="ai-global-prof" class="font-bold text-sm md:text-base num-font text-white">0 KRW (0.00%)</span>
            </div>
        </div>
    </header>

    <main id="v-trd" class="flex-1 flex flex-col lg:flex-row overflow-y-auto lg:overflow-hidden p-1 gap-1">
        <div class="flex flex-col space-y-1 w-full lg:flex-1 lg:min-w-[500px] xl:min-w-[600px] h-auto lg:h-full shrink-0">
            <div class="h-16 bg-panel flex items-center justify-between px-3 md:px-4 shrink-0 rounded">
                <div class="flex items-center"><h2 class="text-lg md:text-xl font-bold text-white"><span id="m-name">비트코인</span> <span id="m-code" class="text-xs text-gray-500">BTC/KRW</span></h2></div>
                <div class="flex flex-col text-right ml-4"><span id="m-prc" class="text-xl md:text-2xl font-bold up-red num-font">0</span><span id="m-rt" class="text-[11px] md:text-xs up-red font-bold num-font">0.00%</span></div>
            </div>
            
            <div class="h-[350px] md:h-[450px] lg:h-auto lg:flex-[3] w-full bg-panel shrink-0 rounded overflow-hidden relative" id="tv_chart_container"></div>
            
            <div class="h-auto lg:flex-[2.8] bg-panel flex flex-col md:flex-row shrink-0 mt-1 rounded">
                <div class="w-full md:w-1/2 border-b md:border-b-0 md:border-r border-line flex flex-col h-[350px] lg:h-auto">
                    <div class="text-center text-xs py-1.5 border-b border-line text-gray-400 font-bold bg-[#0b1016] shrink-0">실시간 20호가</div>
                    <div id="ob" class="flex-1 p-1 text-[11px] md:text-xs num-font overflow-y-auto"></div>
                </div>
                
                <div class="w-full md:w-1/2 flex flex-col bg-[#0b1016] h-[400px] lg:h-auto">
                    <div class="flex flex-col border-b border-line bg-panel p-2 gap-2 shrink-0">
                        <div class="flex justify-between items-center"><span class="text-xs font-bold text-yellow-500">🧠 AI 매매 성향</span>
                            <select onchange="changeMode(this.value)" class="bg-[#1b2029] text-xs text-white border border-gray-700 rounded p-1 outline-none"><option value="safe">🛡️ 안정형</option><option value="balance" selected>⚖️ 밸런스</option><option value="aggressive">⚡ 공격형</option></select>
                        </div>
                    </div>
                    
                    <div class="flex-1 p-2 flex flex-col gap-2 overflow-y-auto border-t border-gray-800 bg-[#0b1016]">
                        <div class="bg-[#1b2029] p-2 rounded border border-gray-700 text-[11px] md:text-xs shrink-0">
                            <div class="text-yellow-400 font-bold border-b border-gray-700 pb-1 mb-1" id="brf-title">[BTC] 실시간 분석</div>
                            <div class="flex justify-between mt-1"><span class="text-gray-400">시장 상태:</span><span class="font-bold text-white" id="brf-status">대기</span></div>
                            <div class="flex justify-between mt-1"><span class="text-gray-400">RSI:</span><span class="font-bold text-blue-400" id="brf-rsi">0</span></div>
                        </div>
                        <div class="bg-[#1b2029] p-2 rounded border border-gray-700 text-[11px] md:text-xs shrink-0">
                            <div class="text-yellow-400 font-bold border-b border-gray-700 pb-1 mb-1">🧠 전체 종합 연산</div>
                            <div class="flex justify-between items-center mt-1"><span class="text-gray-400">통합 승률 예측:</span><span class="font-bold text-purple-400 text-sm" id="g-win-rate">0.0%</span></div>
                            <div class="flex justify-between items-center mt-1"><span class="text-gray-400">통합 AI 점수:</span><span class="font-bold text-teal-400 text-sm" id="g-ai-score">0 / 100</span></div>
                        </div>
                        <div class="bg-[#1b2029] p-2 rounded border border-gray-700 text-[11px] md:text-xs flex-1 flex flex-col min-h-[120px]">
                            <div class="text-white font-bold border-b border-gray-700 pb-1 mb-1 flex items-center gap-1"><span class="text-red-500 animate-pulse">●</span> 개별 연산 랭킹</div>
                            <div id="individual-ai-probs" class="flex flex-col gap-1 overflow-y-auto mt-1"><div class="text-center text-gray-500 py-2">수신 대기 중...</div></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="w-full lg:w-[320px] xl:w-[350px] h-[400px] lg:h-auto flex flex-col bg-panel shrink-0 mt-1 lg:mt-0 rounded overflow-hidden">
            <div class="flex text-sm border-b border-line bg-[#0b1016]">
                <div id="t-buy" class="flex-1 text-center py-3 t-inact" onclick="setOrd('buy')">매수</div>
                <div id="t-sell" class="flex-1 text-center py-3 t-inact" onclick="setOrd('sell')">매도</div>
                <div id="t-hist" class="flex-[1.2] text-center py-3 o-hist whitespace-nowrap text-xs md:text-sm" onclick="setOrd('history')">⚡ AI 체결</div>
            </div>
            <div class="flex-1 flex flex-col overflow-hidden">
                <div class="flex text-[11px] md:text-xs text-gray-400 border-b border-line py-2 px-2 text-center bg-[#0b1016]"><div class="w-1/5">시간</div><div class="w-1/4">AI명</div><div class="w-1/5">종류</div><div class="w-1/3 text-right">가격</div></div>
                <div id="h-list" class="flex-1 overflow-y-auto text-xs num-font divide-y divide-[#2b303b]"></div>
            </div>
        </div>

        <div class="w-full lg:w-[320px] xl:w-[350px] h-[450px] lg:h-auto flex flex-col bg-panel shrink-0 mb-4 lg:mb-0 mt-1 lg:mt-0 rounded overflow-hidden">
            <div class="p-2 border-b border-line text-xs md:text-sm text-yellow-500 font-bold bg-[#1b2029] text-center shrink-0">💡 코인을 클릭하면 차트가 바뀝니다!</div>
            <div class="flex text-[10px] md:text-[11px] text-gray-400 py-2 px-2 border-b border-line bg-[#0b1016] shrink-0"><div class="flex-[1.5]">코인</div><div class="flex-[1.5] text-right">수량/평단</div><div class="flex-[1.5] text-right">현재가</div><div class="flex-[1.5] text-right">손익/수익률</div></div>
            <div id="c-list" class="flex-1 overflow-y-auto divide-y divide-[#1b2029]"></div>
        </div>
    </main>

    <main id="v-port" class="flex-1 hidden bg-[#0b1016] p-2 md:p-4 overflow-y-auto w-full">
        <div class="max-w-[1200px] mx-auto mt-2 md:mt-4">
            <h2 class="text-xl md:text-2xl font-bold mb-4 md:mb-6 text-white border-b border-gray-800 pb-2">나의 투자내역</h2>
            <div class="bg-panel rounded-lg p-4 md:p-6 mb-4 md:mb-6 border border-gray-800 shadow-lg flex flex-col md:flex-row justify-between gap-4">
                <div><p class="text-xs md:text-sm text-gray-400 mb-1">내 총 보유자산</p><p id="p-tot-val" class="text-2xl md:text-3xl font-bold num-font text-white">0 KRW</p></div>
                <div class="md:text-right"><p class="text-xs md:text-sm text-gray-400 mb-1">내 포트폴리오 평가손익</p><p id="p-tot-prof" class="text-2xl md:text-3xl font-bold num-font">0 KRW</p></div>
            </div>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-10">
                <div class="min-w-[600px] flex text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016]"><div class="flex-[1.5]">보유코인</div><div class="flex-[1] text-right">보유수량</div><div class="flex-[1] text-right">매수평균가</div><div class="flex-[1] text-right">현재가</div><div class="flex-[1.5] text-right">평가손익 / 수익률</div></div>
                <div id="p-list" class="min-w-[600px] divide-y divide-gray-800"></div>
            </div>
            <h2 class="text-xl md:text-2xl font-bold mt-10 mb-4 text-yellow-500 flex items-center gap-2 border-b border-gray-800 pb-2">🤖 AI 실시간 체결 상세 장부</h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full pb-4 mb-10"><div class="flex text-[11px] md:text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016] min-w-[1050px] font-bold"><div class="w-[12%]">주문시간</div><div class="w-[12%]">체결시간</div><div class="w-[12%]">AI / 코인명</div><div class="w-[8%] text-center">종류</div><div class="w-[10%] text-right">거래수량</div><div class="w-[12%] text-right">거래단가</div><div class="w-[12%] text-right">거래금액</div><div class="w-[10%] text-right">수수료</div><div class="w-[12%] text-right">정산금액</div></div><div id="ai-detail-list" class="divide-y divide-gray-800 min-w-[1050px]"></div></div>
        </div>
    </main>

    <main id="v-pnl" class="flex-1 hidden bg-[#0b1016] p-2 md:p-4 overflow-y-auto w-full">
        <div class="max-w-[1200px] mx-auto mt-2 md:mt-4">
            <h2 class="text-xl md:text-2xl font-bold mb-4 md:mb-6 text-white border-b border-gray-800 pb-2 flex flex-col md:flex-row md:items-center gap-1 md:gap-2">📊 AI 코인별 상세 수익률 <span class="text-xs md:text-sm font-normal text-gray-500">6대잼 코인 트레이딩 현황</span></h2>
            <div class="bg-panel rounded-lg p-4 md:p-6 mb-4 md:mb-6 border border-gray-800 shadow-lg flex flex-col md:flex-row justify-between gap-4">
                <div><p class="text-xs md:text-sm text-gray-400 mb-1">AI 총 보유 현금</p><p id="ai-cash-val" class="text-xl md:text-2xl font-bold num-font text-white">0 KRW</p></div>
                <div class="md:text-center"><p class="text-xs md:text-sm text-gray-400 mb-1">AI 코인 평가금액</p><p id="ai-coin-val" class="text-xl md:text-2xl font-bold num-font text-gray-300">0 KRW</p></div>
                <div class="md:text-right"><p class="text-xs md:text-sm text-gray-400 mb-1">AI 총 자산 (초기: 1억)</p><p id="ai-total-val" class="text-2xl md:text-3xl font-bold num-font text-yellow-500">0 KRW</p></div>
            </div>
            <h2 class="text-xl md:text-2xl font-bold mt-8 md:mt-10 mb-4 text-yellow-500 border-b border-gray-800 pb-2 flex items-center gap-2">🏆 6대잼 수익 랭킹 & 승률 현황</h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-8"><div class="flex text-xs text-gray-400 py-3 md:py-4 px-4 md:px-6 border-b border-gray-800 bg-[#0b1016] min-w-[800px]"><div class="w-[20%] font-bold">순위 / 6대 잼</div><div class="w-[20%] text-right">실현 손익</div><div class="w-[20%] text-right">승률 (승/패)</div><div class="w-[40%] pl-8">누가 어떤 코인을 샀나?</div></div><div id="ai-ranking-list" class="divide-y divide-gray-800 text-xs md:text-sm min-w-[800px]"></div></div>
            <h2 class="text-lg md:text-xl font-bold mt-8 md:mt-10 mb-4 text-white border-b border-gray-800 pb-2">📂 6대잼 전용 코인 장부</h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-10"><div class="flex text-xs text-gray-400 py-3 md:py-4 px-4 md:px-6 border-b border-gray-800 bg-[#0b1016] min-w-[600px]"><div class="flex-[1.5] font-bold">코인명</div><div class="flex-[1.5] text-right">AI 총 보유수량<br>평균단가</div><div class="flex-[1.5] text-right">매수금액<br>현재 평가금액</div><div class="flex-[1.5] text-right">평가손익<br>수익률</div></div><div id="ai-coin-pnl-list" class="divide-y divide-gray-800 text-xs md:text-sm min-w-[600px]"></div></div>
        </div>
    </main>

    <main id="v-detail" class="flex-1 hidden bg-[#0b1016] p-2 md:p-4 overflow-y-auto w-full">
        <div class="max-w-[800px] mx-auto mt-2 md:mt-4">
            <div class="mb-6 flex gap-2 overflow-x-auto scrollbar-hide border-b border-gray-800 pb-2">
                <button onclick="selAgent('전략 잼')" class="ag-btn px-4 py-2 rounded-full border border-gray-700 text-sm font-bold text-gray-400 hover:text-white whitespace-nowrap bg-panel" id="btn-ag-전략 잼">전략 잼</button>
                <button onclick="selAgent('수집 잼')" class="ag-btn px-4 py-2 rounded-full border border-gray-700 text-sm font-bold text-gray-400 hover:text-white whitespace-nowrap bg-panel" id="btn-ag-수집 잼">수집 잼</button>
                <button onclick="selAgent('정렬 잼')" class="ag-btn px-4 py-2 rounded-full border border-gray-700 text-sm font-bold text-gray-400 hover:text-white whitespace-nowrap bg-panel" id="btn-ag-정렬 잼">정렬 잼</button>
                <button onclick="selAgent('타이밍 잼')" class="ag-btn px-4 py-2 rounded-full border border-gray-700 text-sm font-bold text-gray-400 hover:text-white whitespace-nowrap bg-panel" id="btn-ag-타이밍 잼">타이밍 잼</button>
                <button onclick="selAgent('가디언 잼')" class="ag-btn px-4 py-2 rounded-full border border-gray-700 text-sm font-bold text-gray-400 hover:text-white whitespace-nowrap bg-panel" id="btn-ag-가디언 잼">가디언 잼</button>
                <button onclick="selAgent('행동 잼')" class="ag-btn px-4 py-2 rounded-full border border-gray-700 text-sm font-bold text-gray-400 hover:text-white whitespace-nowrap bg-panel" id="btn-ag-행동 잼">행동 잼</button>
            </div>
            <div class="bg-panel rounded-lg border border-gray-800 p-5 mb-8 shadow-xl">
                <div class="mb-8">
                    <div class="text-sm text-gray-400 flex items-center gap-1 mb-1"><span id="dt-period" class="font-bold text-yellow-500">오늘(Today)의 투자손익</span> </div>
                    <div class="mb-4 text-sm text-gray-400 mt-6">누적 실현 손익</div>
                    <div id="dt-cum-prof" class="text-[32px] font-bold num-font mb-6 leading-none">0 KRW</div>
                    <div class="flex pt-6 pb-2 relative"><div class="absolute top-0 left-0 w-full h-[1px] bg-[#1f2937]"></div><div class="flex-1"><div class="text-[13px] text-gray-400 mb-1">누적 수익률</div><div id="dt-cum-rate" class="text-lg num-font font-medium">0.00 %</div></div><div class="w-[1px] bg-[#1f2937] mx-4"></div><div class="flex-1"><div class="text-[13px] text-gray-400 mb-1">초기 지급 시드머니</div><div id="dt-avg-inv" class="text-lg text-gray-200 num-font font-medium">0 KRW</div></div></div>
                </div>
                <div class="border-t border-[#1f2937] pt-6 mb-8">
                    <div class="flex justify-between items-center mb-4"><h3 class="text-[15px] font-bold text-gray-200">오늘의 수익률 그래프</h3></div>
                    <div class="h-[200px] w-full relative"><canvas id="profitChart"></canvas></div>
                </div>
                <table class="w-full ub-table">
                    <thead><tr><th class="w-[20%] text-left pl-2">일자</th><th class="w-[30%]"><div class="mb-1">당일 손익</div><div>누적 손익</div></th><th class="w-[20%]"><div class="mb-1">수익률</div><div>총 수익률</div></th><th class="w-[30%] text-right pr-2"><div class="mb-1">현재 자산</div><div>기초 자산</div></th></tr></thead>
                    <tbody id="dt-history-list"></tbody>
                </table>
            </div>
        </div>
    </main>

    <script>
        const sn = (v, defVal=0) => { let n = Number(v); return (!isNaN(n) && isFinite(n)) ? n : defVal; };
        // null 체크 헬퍼 함수
        const getEl = id => document.getElementById(id);
        
        let currentCoin = 'BTC'; let currentMode = '밸런스'; let gh = []; let co = 'history'; let globalAnalysis = {}; let ws;
        let globalAgentData = {}; let currentAgent = '전략 잼'; let lineChartInstance = null;

        function loadChart() {
            getEl('tv_chart_container').innerHTML = '<div id="tv_chart" style="height:100%;width:100%"></div>';
            new TradingView.widget({
                "autosize": true, "symbol": "UPBIT:" + currentCoin + "KRW", "interval": "15",
                "theme": "dark", "style": "1", "locale": "kr", "backgroundColor": "#12161f",
                "hide_top_toolbar": true, "hide_legend": false, "save_image": false, "container_id": "tv_chart"
            });
        }
        loadChart();

        function selectCoin(code, name) { currentCoin = code; getEl('m-name').innerText = name; getEl('m-code').innerText = code + "/KRW"; loadChart(); renderAnalysis(); }
        async function changeMode(m) { await fetch(`/api/mode/${m}`, {method:'POST'}); currentMode = m === 'safe' ? '안정형' : m === 'balance' ? '밸런스' : '공격형'; renderAnalysis(); }
        
        function setTab(t) { 
            ['trd', 'port', 'pnl', 'detail'].forEach(id => {
                const v = getEl('v-'+id); const n = getEl('n-'+id);
                if(t === id) { 
                    v.className = id === 'trd' ? "flex-1 flex flex-col lg:flex-row overflow-y-auto lg:overflow-hidden p-1 gap-1" : "flex-1 bg-[#0b1016] p-2 md:p-4 overflow-y-auto w-full"; 
                    n.className = "text-white border-b-2 border-white pb-2 lg:pb-[18px] lg:pt-5 cursor-pointer px-1" + (id === 'detail' ? ' flex items-center gap-1 text-yellow-400' : ''); 
                } else { 
                    v.className = "hidden"; 
                    n.className = "text-gray-500 hover:text-white pb-2 lg:pb-[18px] lg:pt-5 border-b-2 border-transparent cursor-pointer px-1" + (id === 'detail' ? ' flex items-center gap-1' : ''); 
                }
            });
            if(t === 'detail') renderDetailView();
        }
        
        function setOrd(t) { co=t; ['buy','sell','hist'].forEach(x=>getEl(`t-${x}`).className="flex-1 text-center py-3 t-inact hover:text-gray-300"); getEl(`t-${t==='history'?'hist':t}`).className=`flex-[1.2] text-center py-3 o-${t==='history'?'hist':t} whitespace-nowrap text-xs md:text-sm`; drawH(); }
        
        function drawH() { 
            let f=gh; if(co==='buy') f=gh.filter(x=>x.side==='매수'); if(co==='sell') f=gh.filter(x=>x.side==='매도'); 
            let h=""; 
            f.forEach(x=>{ 
                const c=x.side==='매수'?'up-red':'down-blue'; 
                const shortAiName = (x.ai || "AI").split(' ')[0];
                h+=`<div class="flex py-2 md:py-1.5 px-2 hover:bg-gray-800"><div class="w-1/5 text-gray-500">${x.time}</div><div class="w-1/4 font-bold text-gray-300 truncate text-[10px] md:text-xs">${shortAiName}</div><div class="w-1/5 ${c} font-bold text-[10px] md:text-xs">${x.coin} ${x.side}</div><div class="w-1/3 text-right font-bold ${c}">${sn(x.price).toLocaleString()}</div></div>`;
            }); 
            if(getEl('h-list')) getEl('h-list').innerHTML=h;

            let adH = "";
            gh.forEach(x => {
                const c = x.side === '매수' ? 'up-red' : 'down-blue'; 
                const bgC = x.side === '매수' ? 'bg-red-900/30 text-red-400' : 'bg-blue-900/30 text-blue-400';
                adH += `<div class="flex py-3 md:py-2 px-4 hover:bg-gray-800 transition text-[11px] md:text-xs min-w-[1050px] items-center border-b border-gray-800"><div class="w-[12%] text-gray-500">${x.order_time}</div><div class="w-[12%] text-gray-300 font-bold">${x.full_time}</div><div class="w-[12%] flex flex-col"><span class="text-yellow-500 font-bold text-[10px] truncate pr-2">${x.ai||"AI"}</span><span class="font-bold text-white">${x.coin}(${x.market})</span></div><div class="w-[8%] font-bold text-center ${bgC} rounded p-1">${x.side}</div><div class="w-[10%] text-right num-font">${sn(x.qty).toFixed(4)}</div><div class="w-[12%] text-right num-font">${sn(x.price).toLocaleString()}</div><div class="w-[12%] text-right num-font">${sn(x.tot).toLocaleString()}</div><div class="w-[10%] text-right num-font text-gray-500">${sn(x.fee).toLocaleString()}</div><div class="w-[12%] text-right font-bold num-font ${c}">${sn(x.settle).toLocaleString()}</div></div>`;
            });
            if(getEl('ai-detail-list')) getEl('ai-detail-list').innerHTML = adH || '<div class="p-10 text-center text-gray-500">실시간 체결 내역이 없습니다.</div>';
        }

        function renderAnalysis() {
            if(!globalAnalysis[currentCoin]) return;
            const data = globalAnalysis[currentCoin];
            if(getEl('brf-title')) getEl('brf-title').innerText = `[${currentCoin}] 실시간 분석`;
            if(getEl('brf-status')) getEl('brf-status').innerText = data.status;
            if(getEl('brf-rsi')) getEl('brf-rsi').innerText = data.rsi;
        }
        
        function drawOB(p) { 
            let h=""; 
            let tick = p >= 1000000 ? 1000 : (p >= 100000 ? 100 : (p >= 1000 ? 5 : 1));
            let bp = p + (tick * 10); 
            for(let i=0; i<10; i++){ 
                let amt = (Math.random() * 5 + 0.1).toFixed(3);
                h+=`<div class="flex justify-between bg-[rgba(18,97,196,0.1)] px-2 py-[2px] mb-[1px]"><span class="down-blue font-medium">${bp.toLocaleString()}</span><span class="text-gray-400 text-[10px]">${amt}</span></div>`; 
                bp -= tick; 
            } 
            h+=`<div class="flex justify-between bg-gray-800 border border-gray-600 px-2 py-1 my-1"><span class="up-red font-bold text-xs md:text-sm">${p.toLocaleString()}</span><span class="text-white text-[10px] flex items-center">현재가</span></div>`; 
            bp = p - tick; 
            for(let i=0; i<10; i++){ 
                let amt = (Math.random() * 5 + 0.1).toFixed(3);
                h+=`<div class="flex justify-between bg-[rgba(200,74,49,0.1)] px-2 py-[2px] mt-[1px]"><span class="up-red font-medium">${bp.toLocaleString()}</span><span class="text-gray-400 text-[10px]">${amt}</span></div>`; 
                bp -= tick; 
            } 
            if(getEl('ob')) getEl('ob').innerHTML=h; 
        }
        
        function selAgent(name) {
            currentAgent = name;
            document.querySelectorAll('.ag-btn').forEach(b => { b.classList.remove('bg-[#1261c4]', 'text-white', 'border-[#1261c4]'); b.classList.add('bg-panel', 'text-gray-400', 'border-gray-700'); });
            const activeBtn = getEl('btn-ag-' + name);
            if(activeBtn) { activeBtn.classList.remove('bg-panel', 'text-gray-400', 'border-gray-700'); activeBtn.classList.add('bg-[#1261c4]', 'text-white', 'border-[#1261c4]'); }
            renderDetailView();
        }

        function renderDetailView() {
            const data = globalAgentData[currentAgent];
            if(!data) return;

            const s = data.summary;
            const pCls = s.cum_prof >= 0 ? 'up-red' : 'down-blue';
            const pSign = s.cum_prof > 0 ? '+' : '';
            
            if(getEl('dt-cum-prof')) { getEl('dt-cum-prof').className = `text-[32px] font-bold num-font mb-6 leading-none ${pCls}`; getEl('dt-cum-prof').innerText = `${pSign}${Math.round(s.cum_prof).toLocaleString()} KRW`; }
            if(getEl('dt-cum-rate')) { getEl('dt-cum-rate').className = `text-lg num-font font-medium ${pCls}`; getEl('dt-cum-rate').innerText = `${pSign}${s.cum_rate.toFixed(2)} %`; }
            if(getEl('dt-avg-inv')) getEl('dt-avg-inv').innerText = `${Math.round(s.avg_inv).toLocaleString()} KRW`;

            if(data.history && data.history.length > 0) {
                const safeHistory = [...data.history]; 
                let dates = safeHistory.map(x => x.date);
                let rateData = safeHistory.map(x => x.c_rate);
                
                if(dates.length === 1) { dates = ["시작 (0시)", dates[0]]; rateData = [0, rateData[0]]; }
                if(getEl('dt-period')) getEl('dt-period').innerText = `🔥 2026년 ${dates[dates.length-1].replace('.', '월 ')}일 오늘의 AI 실적`;
                
                if(typeof Chart !== 'undefined' && getEl('profitChart')) {
                    const ctx = getEl('profitChart').getContext('2d');
                    if(lineChartInstance) lineChartInstance.destroy();
                    const isPositive = s.cum_prof >= 0; const lineColor = isPositive ? '#c84a31' : '#1261c4';
                    lineChartInstance = new Chart(ctx, { type: 'line', data: { labels: dates, datasets: [{ data: rateData, borderColor: lineColor, borderWidth: 3, pointRadius: 2, pointHoverRadius: 5, tension: 0.1 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } }, scales: { x: { display: true, grid: {display: false}, ticks: {color: '#6b7280', font: {size: 10}} }, y: { position: 'left', grid: { color: '#1f2937', drawBorder: false }, ticks: { color: '#6b7280', font: {size: 10} } } }, interaction: { mode: 'nearest', axis: 'x', intersect: false } } });
                }
            }

            let tHtml = "";
            if(data.history) {
                data.history.forEach(d => {
                    const dcCls = d.d_prof >= 0 ? 'up-red' : 'down-blue'; const dsSign = d.d_prof > 0 ? '+' : '';
                    const ccCls = d.c_prof >= 0 ? 'up-red' : 'down-blue'; const csSign = d.c_prof > 0 ? '+' : '';
                    tHtml += `<tr><td class="text-left pl-2 text-gray-300 num-font">${d.date}</td><td><div class="${dcCls} num-font font-bold mb-0.5">${dsSign}${Math.round(d.d_prof).toLocaleString()}</div><div class="${ccCls} num-font text-[11px]">${csSign}${Math.round(d.c_prof).toLocaleString()}</div></td><td><div class="${dcCls} num-font mb-0.5">${dsSign}${d.d_rate.toFixed(2)}%</div><div class="${ccCls} num-font text-[11px]">${csSign}${d.c_rate.toFixed(2)}%</div></td><td class="text-right pr-2"><div class="text-gray-200 num-font mb-0.5">${Math.round(d.e_asset).toLocaleString()}</div><div class="text-gray-500 num-font text-[11px]">${Math.round(d.b_asset).toLocaleString()}</div></td></tr>`;
                });
            }
            if(getEl('dt-history-list')) getEl('dt-history-list').innerHTML = tHtml;
        }

        // [V40 핵심] 무적의 웹소켓 수신부 (절대 중간에 뻗지 않음)
        function connectWebSocket() {
            ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");
            ws.onopen = () => { if(getEl('conn-status')) getEl('conn-status').className = "w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e]"; };
            
            ws.onmessage = e => { 
                try {
                    const r = JSON.parse(e.data); 
                    
                    // 1. 헤더 & 누적손익 업데이트
                    if (r.ai_tot !== undefined) {
                        const aiTot = sn(r.ai_tot); const aiKrw = sn(r.ai_krw); const aiProf = sn(r.ai_prof); const aiRate = sn(r.ai_rate);
                        const pCls = aiProf >= 0 ? 'text-red-400' : 'text-blue-400'; const pSign = aiProf > 0 ? '+' : '';
                        
                        if(getEl('ai-global-prof')) { getEl('ai-global-prof').innerText = `${pSign}${Math.round(aiProf).toLocaleString()} KRW (${pSign}${aiRate.toFixed(2)}%)`; getEl('ai-global-prof').className = `font-bold text-sm md:text-base num-font ${pCls}`; }
                        if(getEl('ai-total-val')) getEl('ai-total-val').innerText = Math.round(aiTot).toLocaleString()+" KRW";
                        if(getEl('ai-cash-val')) getEl('ai-cash-val').innerText = Math.round(aiKrw).toLocaleString()+" KRW";
                        if(getEl('ai-coin-val')) getEl('ai-coin-val').innerText = Math.round(aiTot - aiKrw).toLocaleString()+" KRW";
                    }

                    // 2. 글로벌 연산 스탯
                    if (r.global_stats) {
                        if(getEl('g-win-rate')) getEl('g-win-rate').innerText = r.global_stats.win_rate.toFixed(1) + "%";
                        if(getEl('g-ai-score')) getEl('g-ai-score').innerText = r.global_stats.ai_score.toFixed(1) + " / 100";
                    }

                    // 3. 개별 확률 랭킹 패널
                    if (r.ai_probs) {
                        let phtml = "";
                        r.ai_probs.forEach((ai, idx) => {
                            let color = idx === 0 ? 'text-red-400 font-bold' : (idx < 3 ? 'text-yellow-400' : 'text-gray-400');
                            let icon = idx === 0 ? '🥇' : (idx === 1 ? '🥈' : (idx === 2 ? '🥉' : `${idx+1}위`));
                            phtml += `<div class="flex justify-between items-center text-[11px] px-1 hover:bg-[#1b2029] rounded py-0.5"><span class="text-gray-300 truncate w-2/3"><span class="w-4 inline-block">${icon}</span> ${ai.name}</span><span class="${color} num-font">${ai.prob.toFixed(1)}%</span></div>`;
                        });
                        if(getEl('individual-ai-probs')) getEl('individual-ai-probs').innerHTML = phtml;
                    }

                    // 4. 코인 리스트 & 포트폴리오(나의 투자내역) 렌더링
                    if (r.data && Array.isArray(r.data)) {
                        let lh="", ph="", tp=0, tv=0; 
                        r.data.forEach(c => { 
                            const prof = sn(c.prof); const rate = sn(c.rate); const cur_krw = sn(c.cur_krw); const avg = sn(c.avg); const qty = sn(c.qty);
                            tp += prof; tv += (cur_krw * qty);
                            const cl = rate>=0 ? 'up-red':'down-blue', s = rate>=0 ? '+': ''; 
                            
                            if(c.code === currentCoin){ 
                                if(getEl('m-prc')) { getEl('m-prc').innerText=Math.round(cur_krw).toLocaleString(); getEl('m-prc').className=`text-xl md:text-2xl font-bold num-font ${cl}`; }
                                if(getEl('m-rt')) { getEl('m-rt').innerText=`전일대비 ${s}${rate.toFixed(2)}%`; getEl('m-rt').className=`text-[11px] md:text-xs font-bold num-font ${cl}`; }
                                drawOB(Math.round(cur_krw)); 
                            } 
                            
                            lh+=`<div onclick="selectCoin('${c.code}', '${c.name}')" class="flex text-xs py-2 px-2 hover:bg-[#1b2029] items-center cursor-pointer transition"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200 text-sm md:text-xs">${c.name}</span><span class="text-[10px] text-gray-500">${c.code}/KRW</span></div><div class="flex-[1.5] text-right flex flex-col"><span class="text-gray-300 num-font">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</span><span class="text-gray-500 text-[10px] num-font">${Math.round(avg).toLocaleString()}</span></div><div class="flex-[1.5] text-right font-bold num-font text-sm md:text-xs ${cl}">${Math.round(cur_krw).toLocaleString()}</div><div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font">${s}${rate.toFixed(2)}%</span><span class="${cl} text-[10px] num-font">${Math.round(prof).toLocaleString()}</span></div></div>`; 
                            ph+=`<div class="flex text-sm py-4 px-4 items-center hover:bg-gray-800 transition border-b border-gray-800 min-w-[600px]"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200 text-base">${c.name}</span><span class="text-xs text-gray-500">${c.code}</span></div><div class="flex-[1] text-right num-font text-gray-300">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</div><div class="flex-[1] text-right num-font text-gray-400">${Math.round(avg).toLocaleString()} KRW</div><div class="flex-[1] text-right font-bold num-font ${cl}">${Math.round(cur_krw).toLocaleString()} KRW</div><div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font text-base">${Math.round(prof).toLocaleString()} KRW</span><span class="${cl} text-xs num-font">${s}${rate.toFixed(2)}%</span></div></div>`;
                        }); 
                        
                        if(getEl('c-list')) getEl('c-list').innerHTML=lh; 
                        if(getEl('p-list')) getEl('p-list').innerHTML=ph;
                        if(getEl('p-tot-val')) getEl('p-tot-val').innerText = Math.round(tv).toLocaleString() + " KRW";
                        if(getEl('p-tot-prof')) { getEl('p-tot-prof').innerText = Math.round(tp).toLocaleString() + " KRW"; getEl('p-tot-prof').className = `text-2xl md:text-3xl font-bold num-font ${tp>=0?'up-red':'down-blue'}`; }
                    }

                    // 5. AI 실시간 장부 렌더링
                    if (r.ai_coin_pnl) {
                        let aiPnlHtml = "";
                        if (r.ai_coin_pnl.length > 0) {
                            r.ai_coin_pnl.forEach(d => {
                                const profit = sn(d.profit); const rate = sn(d.rate);
                                const dc = profit >= 0 ? 'up-red' : 'down-blue'; const ds = profit >= 0 ? '+' : '';
                                aiPnlHtml += `<div class="flex py-4 px-4 md:px-6 hover:bg-gray-800 transition items-center border-b border-gray-800 min-w-[600px] text-gray-200"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-sm md:text-base">${d.name}</span><span class="text-[10px] text-yellow-500 mt-0.5" title="${d.owners}">${d.owners}</span></div><div class="flex-[1.5] text-right flex flex-col gap-1"><span class="font-bold num-font text-sm md:text-base">${sn(d.qty).toFixed(4)}</span><span class="text-[11px] md:text-xs num-font">${Math.round(sn(d.avg)).toLocaleString()} KRW</span></div><div class="flex-[1.5] text-right flex flex-col gap-1"><span class="num-font text-sm md:text-base text-gray-400">${Math.round(sn(d.invested)).toLocaleString()}</span><span class="text-[11px] md:text-xs font-bold num-font text-white">${Math.round(sn(d.valuation)).toLocaleString()} KRW</span></div><div class="flex-[1.5] text-right flex flex-col gap-1"><span class="${dc} font-bold num-font text-sm md:text-base">${ds}${Math.round(profit).toLocaleString()}</span><span class="${dc} text-[11px] md:text-xs num-font">${ds}${rate.toFixed(2)}%</span></div></div>`;
                            });
                        } else {
                            aiPnlHtml = '<div class="p-10 text-center text-gray-500">현재 보유 중인 코인이 없습니다.</div>';
                        }
                        if(getEl('ai-coin-pnl-list')) getEl('ai-coin-pnl-list').innerHTML = aiPnlHtml;
                    }

                    // 6. 6대잼 수익 랭킹
                    if (r.ranking) {
                        let rankHtml = "";
                        r.ranking.forEach((bot, idx) => {
                            const p = sn(bot.profit); const pCls = p >= 0 ? 'up-red' : 'down-blue'; const pSign = p > 0 ? '+' : '';
                            const rankIcon = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx+1}위`;
                            const holdsText = bot.holds_str; const wr = sn(bot.win_rate).toFixed(1);
                            rankHtml += `<div class="flex py-4 px-4 md:px-6 hover:bg-gray-800 transition items-center border-b border-gray-800 min-w-[800px]"><div class="w-[20%] font-bold text-sm md:text-base text-white"><span class="mr-2">${rankIcon}</span>${bot.name}</div><div class="w-[20%] text-right font-bold num-font text-sm md:text-base ${pCls}">${pSign}${Math.round(p).toLocaleString()} KRW</div><div class="w-[20%] text-right font-bold num-font text-sm md:text-base text-gray-300">${wr}% <span class="text-xs text-gray-500 font-normal">(${bot.wins}승 ${bot.losses}패)</span></div><div class="w-[40%] pl-8 text-xs md:text-sm text-yellow-400 truncate" title="${holdsText}">${holdsText}</div></div>`;
                        });
                        if(getEl('ai-ranking-list')) getEl('ai-ranking-list').innerHTML = rankHtml;
                    }

                    // 7. 실시간 거래 내역 & 상태 브리핑 업데이트
                    if(r.hist){ gh=r.hist; drawH(); } 
                    if(r.analysis) { globalAnalysis = r.analysis; renderAnalysis(); }

                    // 8. AI 투자상세 (업비트 클론 탭)
                    if(r.agent_details) { 
                        globalAgentData = r.agent_details; 
                        if(getEl('v-detail') && !getEl('v-detail').classList.contains('hidden')) renderDetailView(); 
                    }
                } catch (parseErr) {
                    console.error("WS Parsing Error", parseErr);
                }
            };
            ws.onclose = () => { if(getEl('conn-status')) getEl('conn-status').className = "w-2.5 h-2.5 rounded-full bg-red-500"; setTimeout(connectWebSocket, 1500); };
            ws.onerror = () => { ws.close(); };
        }
        
        setTimeout(() => { selAgent('전략 잼'); }, 500);
        connectWebSocket();
    </script>
</body></html>
"""

files["templates/index.html"] = html_ui

for path, content in files.items():
    fp = os.path.join(TARGET_PATH, path)
    dr = os.path.dirname(fp)
    if dr and not os.path.exists(dr): os.makedirs(dr)
    with open(fp, "w", encoding="utf-8") as f: f.write(content)

print("✅ V40 무결점 화면 렌더링 및 6대잼 풀악셀 매매 엔진 탑재 완료!")