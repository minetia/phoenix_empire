import os
import shutil

TARGET_PATH = r"C:\Users\loves\Project_Phoenix"
print("🔥 [Project Phoenix V31] AI 장부 완벽 분리 및 소유자 이름표 부착 중...")

# 헷갈림을 유발했던 과거 AI 세이브 파일 완벽 소각
state_file = os.path.join(TARGET_PATH, "ai_state.json")
if os.path.exists(state_file):
    try: os.remove(state_file)
    except: pass

files = {}

# 1. Main Server
files["main.py"] = """from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from core.trader import PhoenixTrader
import asyncio, os, socket

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
        except: break
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="warning")
"""

# 2. Trader (V31: AI 장부에만 뜨도록 필터링 & 누가 샀는지 이름표 추가)
files["core/trader.py"] = """import asyncio, random, json, os
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
        # 이것은 사용자님의 기준 포트폴리오입니다.
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
        
        self.agents = {
            "전략 잼": {"profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0},
            "수집 잼": {"profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0},
            "정렬 잼": {"profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0},
            "타이밍 잼": {"profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0},
            "가디언 잼": {"profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0},
            "행동 잼": {"profit": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0}
        }
        self.ais = list(self.agents.keys())
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
                    self.agents = data.get("agents", self.agents)
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
        data = {
            "ai_mode": self.ai_mode, "ai_krw": self.ai_krw, 
            "ai_hold": self.ai_hold, "ai_avg": self.ai_avg, 
            "agents": self.agents, "hist": self.hist
        }
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
            profit_rate = ((p - old_avg) / old_avg * 100) if old_avg > 0 else 0

            side = None; bet_ratio = 0.0; sell_ratio = 0.0

            if ai_name == "전략 잼": 
                if profit_rate > 1.5: side = "매수"; bet_ratio = 0.1 
                elif profit_rate < -2.0 and bot_hold > 0: side = "매도"; sell_ratio = 0.8
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.2
            elif ai_name == "수집 잼": 
                if profit_rate < -2.0: side = "매수"; bet_ratio = 0.1
                elif bot_hold > 0 and profit_rate > 4.0: side = "매도"; sell_ratio = 0.5
                else: side = "매수"; bet_ratio = 0.02
            elif ai_name == "정렬 잼": 
                if bot_hold > 0 and profit_rate > 1.0: side = "매도"; sell_ratio = 0.5
                elif profit_rate < -1.0: side = "매수"; bet_ratio = 0.05
                else: continue
            elif ai_name == "타이밍 잼": 
                if profit_rate < -7.0 or random.random() < 0.02: side = "매수"; bet_ratio = 0.3 
                elif bot_hold > 0 and profit_rate > 6.0: side = "매도"; sell_ratio = 1.0
                else: continue
            elif ai_name == "가디언 잼": 
                if bot_hold > 0 and profit_rate < -3.0: side = "매도"; sell_ratio = 1.0 
                elif bot_hold > 0 and profit_rate > 3.0: side = "매도"; sell_ratio = 1.0 
                elif profit_rate < -10.0: side = "매수"; bet_ratio = 0.2 
                else: continue
            elif ai_name == "행동 잼": 
                if bot_hold > 0 and profit_rate > 0.4: side = "매도"; sell_ratio = 1.0 
                elif bot_hold > 0 and profit_rate < -0.8: side = "매도"; sell_ratio = 1.0 
                else: side = "매수"; bet_ratio = 0.03

            if not side: continue
            
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
                
                self.agents[ai_name]["holds"][c] = bot_hold + qty

            else:
                if bot_hold < 0.0001: continue
                qty = bot_hold * sell_ratio
                sell_amount = qty * p
                buy_amount = qty * old_avg
                
                self.ai_hold[c] = safe_num(old_qty - qty)
                self.ai_krw += sell_amount
                if self.ai_hold.get(c, 0.0) < 0.000001:
                    self.ai_hold[c] = 0.0
                    self.ai_avg[c] = 0.0
                
                self.agents[ai_name]["holds"][c] = bot_hold - qty
                
                trade_profit = sell_amount - buy_amount
                self.agents[ai_name]["profit"] += trade_profit
                if trade_profit > 0: self.agents[ai_name]["wins"] = self.agents[ai_name].get("wins", 0) + 1
                else: self.agents[ai_name]["losses"] = self.agents[ai_name].get("losses", 0) + 1
                
            log = self.logger.log_trade(ai_name, c.replace("KRW-",""), side, qty, p)
            self.hist.insert(0, log)
            if len(self.hist) > 100: self.hist.pop()
            
            self.save_state()

    async def get_portfolio_status(self):
        usdt = safe_num(self.prc_cache.get("KRW-USDT", 1450), 1450.0)
        res = []
        analysis_data = {}
        ai_coin_pnl = []
        
        # 1. 내 장부 (사용자 원본 데이터) - r.data
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
            rec_jam = random.choice(self.ais)
            rsi_sim = round(random.uniform(20, 80), 1)
            
            analysis_data[sym] = {"status": status, "rec": rec_jam, "rsi": rsi_sim}
            res.append({
                "name": c["name"], "code": sym, "qty": c_qty, "avg": c_avg, 
                "cur_krw": cp, "cur_usd": cp/usdt, "val": val, "prof": prof, "rate": rate
            })

            # 2. AI 장부 (AI가 실제로 보유한 것만 필터링) - r.ai_coin_pnl
            ai_qty = safe_num(self.ai_hold.get(c["code"], 0.0))
            if ai_qty > 0.00001:  # [V31 핵심] 보유량이 0인 코인은 AI 장부에 안 띄움!
                ai_avg_price = safe_num(self.ai_avg.get(c["code"], 0.0))
                if ai_avg_price <= 0: ai_avg_price = cp

                ai_invested = ai_qty * ai_avg_price
                ai_valuation = ai_qty * cp
                ai_profit = ai_valuation - ai_invested
                ai_coin_rate = ((cp - ai_avg_price) / ai_avg_price) * 100 if ai_avg_price > 0 else 0
                
                # 누가 보유중인지 이름표 생성
                owners = []
                for a_name, a_data in self.agents.items():
                    hq = safe_num(a_data["holds"].get(c["code"], 0.0))
                    if hq > 0.00001:
                        owners.append(f"{a_name}({hq:.4f})")
                owners_str = " / ".join(owners)

                ai_coin_pnl.append({
                    "name": c["name"], "code": sym, 
                    "qty": ai_qty, "avg": ai_avg_price,
                    "invested": ai_invested, "valuation": ai_valuation,
                    "profit": ai_profit, "rate": ai_coin_rate,
                    "owners": owners_str  # 이름표 추가
                })
        
        tot_ai_coins = sum(safe_num(qty) * safe_num(self.prc_cache.get(code, 0.0)) for code, qty in self.ai_hold.items() if safe_num(qty)>0)
        tot_ai = safe_num(self.ai_krw) + tot_ai_coins
        ai_prof = tot_ai - self.ai_seed
        ai_rate = (ai_prof / self.ai_seed) * 100

        ranking = []
        for name, data in self.agents.items():
            holds_list = []
            for code, q in data["holds"].items():
                if q > 0.0001:
                    sym = code.replace("KRW-", "")
                    holds_list.append(f"{sym}({q:.3f})")
            holds_str = ", ".join(holds_list) if holds_list else "관망 중 (보유없음)"
            
            wins = data.get("wins", 0)
            losses = data.get("losses", 0)
            total_trades = wins + losses
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
            
            ranking.append({
                "name": name, "profit": data["profit"],
                "win_rate": win_rate, "wins": wins, "losses": losses, "holds_str": holds_str
            })
        ranking.sort(key=lambda x: x["profit"], reverse=True)

        return {
            "usdt": usdt, "data": res, "hist": self.hist, 
            "ai_krw": safe_num(self.ai_krw), "ai_tot": tot_ai, 
            "ai_prof": ai_prof, "ai_rate": ai_rate,
            "analysis": analysis_data, "ai_coin_pnl": ai_coin_pnl,
            "ranking": ranking
        }
"""

# HTML UI (V31: AI 코인 장부에 이름표 부착 & 깔끔한 구분)
html_ui = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PHOENIX AI TRADING</title>
    <script src="https://cdn.tailwindcss.com"></script>
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
    </style>
</head>
<body class="md:h-screen flex flex-col select-none overflow-y-auto md:overflow-hidden bg-[#0b1016]">
    <header class="py-3 md:h-14 md:py-0 bg-panel border-b border-line flex flex-col md:flex-row justify-between items-center px-4 shrink-0 gap-3">
        <div class="flex flex-col md:flex-row items-center w-full md:w-auto gap-3 overflow-hidden">
            <div class="flex items-center cursor-pointer shrink-0" onclick="setTab('trd')">
                <span class="text-2xl md:text-xl mr-1">🦅</span>
                <h1 class="text-2xl md:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-300 tracking-widest italic drop-shadow-md">PHOENIX</h1>
                <span class="text-[10px] text-yellow-500 border border-yellow-500/50 bg-yellow-900/30 px-1.5 py-0.5 rounded ml-2 font-bold tracking-wide">AI CORE V31</span>
            </div>
            <nav class="flex space-x-6 text-sm font-bold ml-0 md:ml-6 mt-2 md:mt-0 w-full md:w-auto overflow-x-auto whitespace-nowrap border-t md:border-0 border-gray-800 pt-3 md:pt-0 scrollbar-hide justify-center md:justify-start">
                <a id="n-trd" onclick="setTab('trd')" class="text-white border-b-2 border-white pb-2 md:pb-[18px] md:pt-5 cursor-pointer px-1">거래소</a>
                <a id="n-port" onclick="setTab('port')" class="text-gray-500 hover:text-white pb-2 md:pb-[18px] md:pt-5 border-b-2 border-transparent cursor-pointer px-1">투자내역</a>
                <a id="n-pnl" onclick="setTab('pnl')" class="text-gray-500 hover:text-white pb-2 md:pb-[18px] md:pt-5 border-b-2 border-transparent cursor-pointer px-1">투자손익</a>
            </nav>
        </div>
        <div class="flex gap-4 items-center text-xs md:text-sm text-gray-400 w-full justify-between md:justify-end md:w-auto mt-2 md:mt-0 bg-[#0b1016] md:bg-transparent p-2 md:p-0 rounded border border-gray-800 md:border-0 shrink-0">
            <div class="flex items-center gap-2">
                <div id="conn-status" class="w-2.5 h-2.5 md:w-2 md:h-2 rounded-full bg-green-500 animate-pulse" title="서버 연결 상태"></div>
                <span class="text-yellow-500 font-bold hidden md:inline">🤖 6대잼 누적 손익:</span> 
                <span class="text-yellow-500 font-bold md:hidden">AI 손익:</span> 
                <span id="ai-global-prof" class="font-bold text-sm md:text-base num-font text-white">0 KRW (0.00%)</span>
            </div>
        </div>
    </header>

    <main id="v-trd" class="flex-1 flex flex-col md:flex-row overflow-y-auto md:overflow-hidden p-1 gap-1">
        <div class="flex flex-col space-y-1 w-full md:flex-1 md:min-w-[600px] h-auto md:h-full shrink-0">
            <div class="h-16 bg-panel flex items-center justify-between px-3 md:px-4 shrink-0">
                <div class="flex items-center">
                    <h2 class="text-lg md:text-xl font-bold text-white"><span id="m-name">비트코인</span> <span id="m-code" class="text-xs text-gray-500">BTC/KRW</span></h2>
                </div>
                <div class="flex flex-col text-right ml-4">
                    <span id="m-prc" class="text-xl md:text-2xl font-bold up-red num-font">0</span>
                    <span id="m-rt" class="text-[11px] md:text-xs up-red font-bold num-font">0.00%</span>
                </div>
            </div>
            
            <div class="h-[450px] md:h-auto md:flex-[3] w-full bg-panel shrink-0" id="tv_chart_container"></div>
            
            <div class="h-auto md:flex-[2] bg-panel flex flex-col md:flex-row shrink-0">
                <div class="w-full md:w-1/2 border-b md:border-b-0 md:border-r border-line flex flex-col h-[200px] md:h-auto">
                    <div class="text-center text-xs py-1 border-b border-line text-gray-400 font-bold bg-[#0b1016]">일반호가</div>
                    <div id="ob" class="flex-1 p-1 text-[11px] md:text-xs num-font overflow-y-auto"></div>
                </div>
                <div class="w-full md:w-1/2 flex flex-col bg-[#0b1016] h-auto md:h-auto">
                    <div class="flex flex-col border-b border-line bg-panel p-2 gap-2">
                        <div class="flex justify-between items-center"><span class="text-xs font-bold text-yellow-500">🧠 AI 매매 속도 조절</span>
                            <select onchange="changeMode(this.value)" class="bg-[#1b2029] text-xs text-white border border-gray-700 rounded p-1 outline-none">
                                <option value="safe">🛡️ 안정형 (느림)</option><option value="balance" selected>⚖️ 밸런스 (보통)</option><option value="aggressive">⚡ 공격형 (초스피드)</option>
                            </select>
                        </div>
                        <div class="flex justify-between text-[11px] bg-[#0b1016] p-1.5 rounded border border-gray-800"><span class="text-gray-400">AI 전체 시드:</span><span id="ai-tot" class="font-bold text-green-400">100,000,000 KRW</span></div>
                    </div>
                    <div id="ai-analysis-box" class="flex-1 p-3 space-y-2 text-xs overflow-y-auto border-t border-gray-800 min-h-[120px]"><div class="text-center text-gray-500 mt-4 animate-pulse">데이터 수집 중...</div></div>
                </div>
            </div>
        </div>

        <div class="w-full md:w-[350px] h-[350px] md:h-auto flex flex-col bg-panel shrink-0 mt-1 md:mt-0">
            <div class="flex text-sm border-b border-line bg-[#0b1016]">
                <div id="t-buy" class="flex-1 text-center py-3 t-inact hover:text-red-400" onclick="setOrd('buy')">매수</div>
                <div id="t-sell" class="flex-1 text-center py-3 t-inact hover:text-blue-400" onclick="setOrd('sell')">매도</div>
                <div id="t-hist" class="flex-1 text-center py-3 o-hist" onclick="setOrd('history')">⚡ 실시간 거래내역</div>
            </div>
            <div class="flex-1 flex flex-col overflow-hidden">
                <div class="flex text-[11px] md:text-xs text-gray-400 border-b border-line py-2 px-2 text-center bg-[#0b1016]"><div class="w-1/5">시간</div><div class="w-1/4">AI명</div><div class="w-1/5">종류</div><div class="w-1/3 text-right">가격</div></div>
                <div id="h-list" class="flex-1 overflow-y-auto text-xs num-font divide-y divide-[#2b303b]"></div>
            </div>
        </div>

        <div class="w-full md:w-[380px] h-[450px] md:h-auto flex flex-col bg-panel shrink-0 mb-4 md:mb-0">
            <div class="p-2 border-b border-line text-xs md:text-sm text-yellow-500 font-bold bg-[#1b2029] text-center">💡 코인을 클릭하면 차트가 바뀝니다!</div>
            <div class="flex text-[10px] md:text-[11px] text-gray-400 py-2 px-2 border-b border-line bg-[#0b1016]"><div class="flex-[1.5]">코인</div><div class="flex-[1.5] text-right">수량/평단</div><div class="flex-[1.5] text-right">현재가</div><div class="flex-[1.5] text-right">손익/수익률</div></div>
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
            
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-8">
                <div class="min-w-[600px] flex text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016]"><div class="flex-[1.5]">보유코인</div><div class="flex-[1] text-right">보유수량</div><div class="flex-[1] text-right">매수평균가</div><div class="flex-[1] text-right">현재가</div><div class="flex-[1.5] text-right">평가손익 / 수익률</div></div>
                <div id="p-list" class="min-w-[600px] divide-y divide-gray-800"></div>
            </div>
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
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-8">
                <div class="flex text-xs text-gray-400 py-3 md:py-4 px-4 md:px-6 border-b border-gray-800 bg-[#0b1016] min-w-[800px]">
                    <div class="w-[20%] font-bold">순위 / 6대 잼</div>
                    <div class="w-[20%] text-right">실현 손익</div>
                    <div class="w-[20%] text-right">승률 (승/패)</div>
                    <div class="w-[40%] pl-8">누가 어떤 코인을 샀나?</div>
                </div>
                <div id="ai-ranking-list" class="divide-y divide-gray-800 text-xs md:text-sm min-w-[800px]">
                    <div class="p-10 text-center text-gray-500 animate-pulse">AI 실적 정산 중...</div>
                </div>
            </div>

            <h2 class="text-lg md:text-xl font-bold mt-8 md:mt-10 mb-4 text-white border-b border-gray-800 pb-2">📂 6대잼 전용 코인 장부 <span class="text-xs font-normal text-yellow-400 ml-2">※ AI가 실제로 매수한 코인만 표시됩니다.</span></h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-10">
                <div class="flex text-xs text-gray-400 py-3 md:py-4 px-4 md:px-6 border-b border-gray-800 bg-[#0b1016] min-w-[600px]">
                    <div class="flex-[1.5] font-bold">코인명 <span class="text-[10px] ml-1 text-gray-500">(소유 AI)</span></div>
                    <div class="flex-[1.5] text-right">AI 총 보유수량<br>평균단가</div>
                    <div class="flex-[1.5] text-right">매수금액<br>현재 평가금액</div>
                    <div class="flex-[1.5] text-right">평가손익<br>수익률</div>
                </div>
                <div id="ai-coin-pnl-list" class="divide-y divide-gray-800 text-xs md:text-sm min-w-[600px]">
                    <div class="p-10 text-center text-gray-500 animate-pulse">AI가 아직 코인을 매수하지 않았습니다. 매매 대기 중...</div>
                </div>
            </div>
        </div>
    </main>

    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
        const sn = (v, defVal=0) => { let n = Number(v); return (!isNaN(n) && isFinite(n)) ? n : defVal; };
        let currentCoin = 'BTC'; let currentMode = '밸런스'; let gh = []; let co = 'history'; let globalAnalysis = {}; let ws;

        function loadChart() {
            document.getElementById('tv_chart_container').innerHTML = '<div id="tv_chart" style="height:100%;width:100%"></div>';
            new TradingView.widget({
                "autosize": true, "symbol": "UPBIT:" + currentCoin + "KRW", "interval": "15",
                "theme": "dark", "style": "1", "locale": "kr", "backgroundColor": "#12161f",
                "hide_top_toolbar": true, "hide_legend": false, "save_image": false,
                "container_id": "tv_chart"
            });
        }
        loadChart(); 

        function selectCoin(code, name) { currentCoin = code; document.getElementById('m-name').innerText = name; document.getElementById('m-code').innerText = code + "/KRW"; loadChart(); renderAnalysis(); }
        async function changeMode(m) { await fetch(`/api/mode/${m}`, {method:'POST'}); currentMode = m === 'safe' ? '안정형' : m === 'balance' ? '밸런스' : '공격형'; renderAnalysis(); }
        
        function setTab(t) { 
            ['trd', 'port', 'pnl'].forEach(id => {
                const v = document.getElementById('v-'+id); const n = document.getElementById('n-'+id);
                if(t === id) { v.className = id === 'trd' ? "flex-1 flex flex-col md:flex-row overflow-y-auto md:overflow-hidden p-1 gap-1" : "flex-1 bg-[#0b1016] p-2 md:p-4 overflow-y-auto w-full"; n.className = "text-white border-b-2 border-white pb-2 md:pb-[18px] md:pt-5 cursor-pointer px-1"; } 
                else { v.className = "hidden"; n.className = "text-gray-500 hover:text-white pb-2 md:pb-[18px] md:pt-5 border-b-2 border-transparent cursor-pointer px-1"; }
            });
        }
        
        function setOrd(t) { co=t; ['buy','sell','hist'].forEach(x=>document.getElementById(`t-${x}`).className="flex-1 text-center py-3 t-inact hover:text-gray-300"); document.getElementById(`t-${t==='history'?'hist':t}`).className=`flex-1 text-center py-3 o-${t==='history'?'hist':t}`; drawH(); }
        
        function drawH() { 
            let f=gh; if(co==='buy') f=gh.filter(x=>x.side==='매수'); if(co==='sell') f=gh.filter(x=>x.side==='매도'); 
            let h=""; 
            f.forEach(x=>{ 
                const c=x.side==='매수'?'up-red':'down-blue'; 
                h+=`<div class="flex py-2 md:py-1.5 px-2 hover:bg-gray-800"><div class="w-1/5 text-gray-500">${x.time}</div><div class="w-1/4 font-bold text-gray-300 truncate">${x.ai}</div><div class="w-1/5 ${c} font-bold text-[10px] md:text-xs">${x.coin} ${x.side}</div><div class="w-1/3 text-right font-bold ${c}">${sn(x.price).toLocaleString()}</div></div>`;
            }); 
            document.getElementById('h-list').innerHTML=h;
        }

        function renderAnalysis() {
            if(!globalAnalysis[currentCoin]) return;
            const data = globalAnalysis[currentCoin];
            document.getElementById('ai-analysis-box').innerHTML = `
                <div class="bg-[#1b2029] p-3 rounded border border-gray-700 space-y-2 text-xs md:text-sm">
                    <div class="text-yellow-400 font-bold border-b border-gray-700 pb-1 mb-2">[${currentCoin}] 실시간 분석 브리핑</div>
                    <div class="flex justify-between"><span class="text-gray-400">시장 상태:</span><span class="font-bold text-white">${data.status}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">시뮬레이션 RSI:</span><span class="font-bold text-blue-400">${data.rsi}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">추천 6대잼:</span><span class="font-bold text-green-400">${data.rec}</span></div>
                </div>`;
        }
        
        function drawOB(p) { let h=""; let bp=p+5000; for(let i=0;i<5;i++){ h+=`<div class="flex justify-between bg-[rgba(18,97,196,0.1)] px-2 mb-[1px]"><span class="down-blue">${bp.toLocaleString()}</span><span class="text-gray-400">1.2</span></div>`; bp-=1000; } h+=`<div class="flex justify-between bg-gray-800 border border-gray-600 px-2 py-1.5 my-1"><span class="up-red font-bold text-xs md:text-sm">${p.toLocaleString()}</span><span class="text-gray-200">3.4</span></div>`; bp=p-1000; for(let i=0;i<5;i++){ h+=`<div class="flex justify-between bg-[rgba(200,74,49,0.1)] px-2 mt-[1px]"><span class="up-red">${bp.toLocaleString()}</span><span class="text-gray-400">0.5</span></div>`; bp-=1000; } document.getElementById('ob').innerHTML=h; }
        
        function connectWebSocket() {
            ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");
            ws.onopen = () => { document.getElementById('conn-status').className = "w-2.5 h-2.5 md:w-2 md:h-2 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e]"; };
            ws.onmessage = e => { 
                try {
                    const r=JSON.parse(e.data); 
                    
                    if(r.ai_tot !== undefined) {
                        const aiTot = sn(r.ai_tot); const aiKrw = sn(r.ai_krw); const aiProf = sn(r.ai_prof); const aiRate = sn(r.ai_rate);
                        const aiCls = aiProf >= 0 ? 'text-red-400' : 'text-blue-400'; const aiSign = aiProf >= 0 ? '+' : '';
                        
                        const gProfEl = document.getElementById('ai-global-prof');
                        if(gProfEl) { gProfEl.innerText = `${aiSign}${Math.round(aiProf).toLocaleString()} KRW (${aiSign}${aiRate.toFixed(2)}%)`; gProfEl.className = `font-bold text-sm md:text-base num-font ${aiCls}`; }
                        
                        const elAiTotalVal = document.getElementById('ai-total-val'); if(elAiTotalVal) elAiTotalVal.innerText = Math.round(aiTot).toLocaleString()+" KRW";
                        const elAiCashVal = document.getElementById('ai-cash-val'); if(elAiCashVal) elAiCashVal.innerText = Math.round(aiKrw).toLocaleString()+" KRW";
                        const elAiCoinVal = document.getElementById('ai-coin-val'); if(elAiCoinVal) elAiCoinVal.innerText = Math.round(aiTot - aiKrw).toLocaleString()+" KRW";
                        const elAiTotNav = document.getElementById('ai-tot'); if(elAiTotNav) elAiTotNav.innerText = Math.round(aiTot).toLocaleString()+" KRW";
                    }

                    if(r.analysis) { globalAnalysis = r.analysis; renderAnalysis(); }
                    
                    let lh="", ph="", tp=0, tv=0; 
                    
                    if(r.data && Array.isArray(r.data)) {
                        r.data.forEach(c => { 
                            const prof = sn(c.prof); const rate = sn(c.rate); const cur_krw = sn(c.cur_krw); const avg = sn(c.avg); const qty = sn(c.qty);
                            tp += prof; tv += (cur_krw * qty);
                            const cl = rate>=0 ? 'up-red':'down-blue', s = rate>=0 ? '+': ''; 
                            
                            if(c.code === currentCoin){ 
                                document.getElementById('m-prc').innerText=Math.round(cur_krw).toLocaleString(); 
                                document.getElementById('m-rt').innerText=`전일대비 ${s}${rate.toFixed(2)}%`; 
                                document.getElementById('m-prc').className=`text-xl md:text-2xl font-bold num-font ${cl}`; 
                                document.getElementById('m-rt').className=`text-[11px] md:text-xs font-bold num-font ${cl}`; 
                                drawOB(Math.round(cur_krw)); 
                            } 
                            
                            lh+=`<div onclick="selectCoin('${c.code}', '${c.name}')" class="flex text-xs py-2 px-2 hover:bg-[#1b2029] items-center cursor-pointer transition"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200 text-sm md:text-xs">${c.name}</span><span class="text-[10px] text-gray-500">${c.code}/KRW</span></div><div class="flex-[1.5] text-right flex flex-col"><span class="text-gray-300 num-font">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</span><span class="text-gray-500 text-[10px] num-font">${Math.round(avg).toLocaleString()}</span></div><div class="flex-[1.5] text-right font-bold num-font text-sm md:text-xs ${cl}">${Math.round(cur_krw).toLocaleString()}</div><div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font">${s}${rate.toFixed(2)}%</span><span class="${cl} text-[10px] num-font">${Math.round(prof).toLocaleString()}</span></div></div>`; 
                            ph+=`<div class="flex text-sm py-4 px-4 items-center hover:bg-gray-800 transition border-b border-gray-800 min-w-[600px]"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200 text-base">${c.name}</span><span class="text-xs text-gray-500">${c.code}</span></div><div class="flex-[1] text-right num-font text-gray-300">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</div><div class="flex-[1] text-right num-font text-gray-400">${Math.round(avg).toLocaleString()} KRW</div><div class="flex-[1] text-right font-bold num-font ${cl}">${Math.round(cur_krw).toLocaleString()} KRW</div><div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font text-base">${Math.round(prof).toLocaleString()} KRW</span><span class="${cl} text-xs num-font">${s}${rate.toFixed(2)}%</span></div></div>`;
                        }); 
                    }
                    
                    document.getElementById('c-list').innerHTML=lh; 
                    
                    const elPtotVal = document.getElementById('p-tot-val'); if(elPtotVal) elPtotVal.innerText=Math.round(tv).toLocaleString()+" KRW";
                    const elPtotProf = document.getElementById('p-tot-prof');
                    if(elPtotProf) { elPtotProf.innerText=Math.round(tp).toLocaleString()+" KRW"; elPtotProf.className=`text-2xl md:text-3xl font-bold num-font ${tp>=0?'up-red':'down-blue'}`; }
                    const elPlist = document.getElementById('p-list'); if(elPlist) elPlist.innerHTML=ph;
                    
                    if(r.hist){ gh=r.hist; drawH(); } 

                    // [V31 핵심] AI 장부 분리. 소유량이 0인 것은 숨기고 이름표를 붙인다!
                    if(r.ai_coin_pnl && r.ai_coin_pnl.length > 0) {
                        let aiPnlHtml = "";
                        r.ai_coin_pnl.forEach(d => {
                            const profit = sn(d.profit); const rate = sn(d.rate);
                            const dc = profit >= 0 ? 'up-red' : 'down-blue'; const ds = profit >= 0 ? '+' : '';
                            const valCls = 'text-white';
                            const numCls = dc;

                            aiPnlHtml += `<div class="flex py-4 px-4 md:px-6 hover:bg-gray-800 transition items-center border-b border-gray-800 min-w-[600px] text-gray-200">
                                <div class="flex-[1.5] flex flex-col"><span class="font-bold text-sm md:text-base">${d.name}</span><span class="text-[10px] text-yellow-500 mt-0.5" title="${d.owners}">${d.owners}</span></div>
                                <div class="flex-[1.5] text-right flex flex-col gap-1"><span class="font-bold num-font text-sm md:text-base">${sn(d.qty).toFixed(4)}</span><span class="text-[11px] md:text-xs num-font">${Math.round(sn(d.avg)).toLocaleString()} KRW</span></div>
                                <div class="flex-[1.5] text-right flex flex-col gap-1"><span class="num-font text-sm md:text-base text-gray-400">${Math.round(sn(d.invested)).toLocaleString()}</span><span class="text-[11px] md:text-xs font-bold num-font ${valCls}">${Math.round(sn(d.valuation)).toLocaleString()} KRW</span></div>
                                <div class="flex-[1.5] text-right flex flex-col gap-1"><span class="${numCls} font-bold num-font text-sm md:text-base">${ds}${Math.round(profit).toLocaleString()}</span><span class="${numCls} text-[11px] md:text-xs num-font">${ds}${rate.toFixed(2)}%</span></div>
                            </div>`;
                        });
                        const elAiCoinList = document.getElementById('ai-coin-pnl-list'); if(elAiCoinList) elAiCoinList.innerHTML = aiPnlHtml;
                    } else {
                        const elAiCoinList = document.getElementById('ai-coin-pnl-list'); 
                        if(elAiCoinList) elAiCoinList.innerHTML = '<div class="p-10 text-center text-gray-500">현재 AI가 보유중인 코인이 없습니다. 매수 타이밍을 엿보고 있습니다...</div>';
                    }
                    
                    if(r.ranking) {
                        let rankHtml = "";
                        r.ranking.forEach((bot, idx) => {
                            const p = sn(bot.profit);
                            const pCls = p >= 0 ? 'up-red' : 'down-blue';
                            const pSign = p > 0 ? '+' : '';
                            const rankIcon = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx+1}위`;
                            const holdsText = bot.holds_str;
                            const wr = sn(bot.win_rate).toFixed(1);
                            
                            rankHtml += `<div class="flex py-4 px-4 md:px-6 hover:bg-gray-800 transition items-center border-b border-gray-800 min-w-[800px]">
                                <div class="w-[20%] font-bold text-sm md:text-base text-white"><span class="mr-2">${rankIcon}</span>${bot.name}</div>
                                <div class="w-[20%] text-right font-bold num-font text-sm md:text-base ${pCls}">${pSign}${Math.round(p).toLocaleString()} KRW</div>
                                <div class="w-[20%] text-right font-bold num-font text-sm md:text-base text-gray-300">${wr}% <span class="text-xs text-gray-500 font-normal">(${bot.wins}승 ${bot.losses}패)</span></div>
                                <div class="w-[40%] pl-8 text-xs md:text-sm text-yellow-400 truncate" title="${holdsText}">${holdsText}</div>
                            </div>`;
                        });
                        const elRankList = document.getElementById('ai-ranking-list'); if(elRankList) elRankList.innerHTML = rankHtml;
                    }
                } catch (err) {}
            };
            ws.onclose = () => { document.getElementById('conn-status').className = "w-2.5 h-2.5 md:w-2 md:h-2 rounded-full bg-red-500"; setTimeout(connectWebSocket, 1500); };
            ws.onerror = () => { ws.close(); };
        }
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

print("✅ V31 6대잼 장부 완벽 분리 적용 성공!")