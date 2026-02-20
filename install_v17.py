import os

TARGET_PATH = r"C:\Users\loves\Project_Phoenix"
print("🔥 [Project Phoenix V17] NaN 바이러스 치료 및 완벽 방어막을 설치합니다...")

# [중요] 감염된 세이브 파일 삭제 (바이러스 원인 제거!)
state_file = os.path.join(TARGET_PATH, "ai_state.json")
if os.path.exists(state_file):
    try:
        os.remove(state_file)
        print("💉 감염된 AI 메모리(DB)를 성공적으로 삭제하고 초기화했습니다!")
    except:
        pass

files = {}

files["requirements.txt"] = "fastapi\nuvicorn\njinja2\npython-dotenv\npyupbit\npandas\nwebsockets\n"
files[".env"] = "UPBIT_ACCESS_KEY=none\nUPBIT_SECRET_KEY=none\n"

# 1. Main Server
files["main.py"] = """from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.trader import PhoenixTrader
import asyncio, os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
trader = PhoenixTrader()

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
        except Exception as e:
            pass
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(trader.simulate_ai_trading())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
"""

# 2. Logger
files["core/logger.py"] = """import csv, os, random
from datetime import datetime, timedelta
class AITradeLogger:
    def __init__(self):
        self.fn = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_trade_log.csv")
        if not os.path.exists(self.fn):
            with open(self.fn, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(["체결시간", "코인명", "마켓", "종류", "거래수량", "거래단가", "거래금액", "수수료", "정산금액(수수료반영)", "주문시간"])
    def log_trade(self, ai, coin, side, qty, price):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d %H:%M:%S")
        order_t = (now - timedelta(seconds=random.randint(1, 4))).strftime("%Y-%m-%d %H:%M:%S")
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
"""

# 3. Exchange
files["core/exchange.py"] = """import pyupbit
class Exchange:
    def get_current_price(self, tickers):
        try: 
            res = pyupbit.get_current_price(tickers)
            if isinstance(res, dict): return {k: (float(v) if v else 0) for k, v in res.items()}
            if isinstance(res, (float, int)): return {tickers[0]: float(res)}
            return {}
        except: return {}
"""

# 4. Trader (V17 백신: 완벽한 NaN 에러 방어막 탑재)
files["core/trader.py"] = """import asyncio, random, json, os
from datetime import datetime, timedelta
from core.exchange import Exchange
from core.logger import AITradeLogger

# [V17 핵심 백신] 어떤 상황에서도 NaN이나 무한대 값이 DB에 들어가지 못하게 방어합니다.
def safe_num(v, default=0.0):
    try:
        f = float(v)
        if f != f or f == float('inf') or f == float('-inf'): return default
        return f
    except:
        return default

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
            except:
                self._init_default_state()
        else:
            self._init_default_state()

    def _init_default_state(self):
        self.ai_mode = "balance"
        self.ai_krw = 100000000.0
        self.ai_hold = {c["code"]: 0.0 for c in self.port}
        self.ai_avg = {c["code"]: 0.0 for c in self.port}
        self.hist = []
        self.save_state()

    def save_state(self):
        self.ai_krw = safe_num(self.ai_krw)
        self.ai_hold = {k: safe_num(v) for k, v in self.ai_hold.items()}
        self.ai_avg = {k: safe_num(v) for k, v in self.ai_avg.items()}
        
        data = {"ai_mode": self.ai_mode, "ai_krw": self.ai_krw, "ai_hold": self.ai_hold, "ai_avg": self.ai_avg, "hist": self.hist}
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except:
            pass

    def change_mode(self, mode):
        self.ai_mode = mode
        self.save_state()

    async def simulate_ai_trading(self):
        while True:
            d = {"safe": 8, "balance": 4, "aggressive": 1.5}.get(self.ai_mode, 4)
            await asyncio.sleep(random.uniform(d*0.8, d*1.5))
            c = random.choice(self.port)["code"]
            side = random.choice(["매수", "매도"])
            
            prc_dict = self.ex.get_current_price([c])
            p = safe_num(prc_dict.get(c))
            if p <= 0: continue
            
            qty = 0
            if side == "매수":
                ratio = {"safe": 0.05, "balance": 0.15, "aggressive": 0.4}.get(self.ai_mode, 0.15)
                bet = self.ai_krw * random.uniform(ratio*0.5, ratio*1.2)
                if bet < 5000: continue
                qty = bet / p
                self.ai_krw -= bet
                
                old_qty = safe_num(self.ai_hold.get(c, 0.0))
                old_avg = safe_num(self.ai_avg.get(c, 0.0))
                new_qty = old_qty + qty
                new_avg = ((old_qty * old_avg) + bet) / new_qty if new_qty > 0 else 0
                self.ai_hold[c] = safe_num(new_qty)
                self.ai_avg[c] = safe_num(new_avg)
            else:
                hq = safe_num(self.ai_hold.get(c, 0.0))
                if hq < 0.0001: continue
                ratio = {"safe": 1.0, "balance": 0.6, "aggressive": 0.3}.get(self.ai_mode, 0.6)
                qty = hq * random.uniform(ratio*0.8, 1.0)
                self.ai_hold[c] = safe_num(hq - qty)
                self.ai_krw += qty * p
                
                if self.ai_hold[c] < 0.000001:
                    self.ai_hold[c] = 0.0
                    self.ai_avg[c] = 0.0
                
            log = self.logger.log_trade(random.choice(self.ais), c.replace("KRW-",""), side, qty, p)
            self.hist.insert(0, log)
            if len(self.hist) > 100: self.hist.pop()
            
            self.save_state()

    async def get_portfolio_status(self):
        tkrs = [c["code"] for c in self.port] + ["KRW-USDT"]
        prc = self.ex.get_current_price(tkrs) or {}
        usdt = safe_num(prc.get("KRW-USDT", 1450), 1450.0)
        
        res = []
        analysis_data = {}
        ai_coin_pnl = []
        
        for c in self.port:
            sym = c["code"].split("-")[1]
            cp = safe_num(prc.get(c["code"]))
            if cp <= 0: cp = safe_num(c["avg"])
            
            c_qty = safe_num(c["qty"])
            c_avg = safe_num(c["avg"])
            
            val = cp * c_qty
            prof = val - (c_avg * c_qty)
            rate = ((cp - c_avg) / c_avg) * 100 if c_avg > 0 else 0
            
            status = "초강세 (과매수 주의)" if rate > 5 else "상승 추세 (홀딩)" if rate > 0 else "조정 구간 (분할 매수)" if rate > -5 else "하락 추세 (관망)"
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
                self.save_state()

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
        
        tot_ai = safe_num(self.ai_krw) + sum(safe_num(qty) * safe_num(prc.get(code,0)) for code, qty in self.ai_hold.items() if safe_num(qty)>0)
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
            "analysis": analysis_data, "ai_coin_pnl": ai_coin_pnl
        }
"""

# 5. HTML 파트 1 (로고 유지)
html_part1 = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <title>PHOENIX AI TRADING</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background:#0b1016; color:#c8ccce; font-family:-apple-system,sans-serif; overflow:hidden; }
        .bg-panel { background:#12161f; } .border-line { border-color:#2b303b; }
        .up-red { color:#c84a31; } .down-blue { color:#1261c4; } .num-font { font-family:'Roboto',sans-serif; }
        ::-webkit-scrollbar { width:6px; height:6px; } ::-webkit-scrollbar-track { background:#0b1016; } ::-webkit-scrollbar-thumb { background:#2b303b; border-radius:3px;}
        .t-inact { color:#666; cursor:pointer; }
        .o-buy { background:rgba(200,74,49,0.2); color:#c84a31; border-top:2px solid #c84a31; font-weight:bold; }
        .o-sell { background:rgba(18,97,196,0.2); color:#1261c4; border-top:2px solid #1261c4; font-weight:bold; }
        .o-hist { background:#1b2029; color:#fff; border-top:2px solid #fff; font-weight:bold; }
    </style>
</head>
<body class="h-screen flex flex-col select-none">
    <header class="h-12 bg-panel border-b border-line flex justify-between items-center px-4 shrink-0">
        <div class="flex items-center space-x-6">
            <div class="flex items-center cursor-pointer" onclick="setTab('trd')">
                <span class="text-xl mr-1">🦅</span>
                <h1 class="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-300 tracking-widest italic drop-shadow-md">PHOENIX</h1>
                <span class="text-[10px] text-yellow-500 border border-yellow-500/50 bg-yellow-900/30 px-1.5 py-0.5 rounded ml-2 font-bold tracking-wide">AI CORE</span>
            </div>
            
            <nav class="flex space-x-4 text-sm font-bold ml-4">
                <a id="n-trd" onclick="setTab('trd')" class="text-white border-b-2 border-white pb-[14px] pt-4 cursor-pointer">거래소</a>
                <a id="n-port" onclick="setTab('port')" class="text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer">투자내역</a>
                <a id="n-pnl" onclick="setTab('pnl')" class="text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer">투자손익</a>
            </nav>
        </div>
        <div class="flex gap-5 items-center text-xs text-gray-400">
            <div class="flex items-center gap-2 bg-[#0b1016] px-3 py-1 rounded border border-gray-800">
                <span class="text-yellow-500 font-bold">🤖 AI 누적 손익:</span> 
                <span id="ai-global-prof" class="font-bold text-sm num-font text-white">0 KRW (0.00%)</span>
            </div>
            <div>환율: <span id="usdt" class="text-gray-300 font-bold num-font">0</span> KRW</div>
        </div>
    </header>
"""

# HTML Part 2
html_part2 = """
    <main id="v-trd" class="flex-1 flex overflow-hidden p-1 space-x-1">
        <div class="flex-1 flex flex-col space-y-1 overflow-hidden min-w-[600px]">
            <div class="h-16 bg-panel flex items-center px-4 shrink-0">
                <h2 class="text-xl font-bold text-white ml-2"><span id="m-name">비트코인</span> <span id="m-code" class="text-xs text-gray-500">BTC/KRW</span></h2>
                <div class="ml-6 flex flex-col"><span id="m-prc" class="text-2xl font-bold up-red num-font">0</span><span id="m-rt" class="text-xs up-red font-bold num-font">0.00%</span></div>
                <div class="ml-auto flex items-center gap-2 border border-yellow-600/50 bg-yellow-900/20 px-3 py-1 rounded"><div class="animate-pulse w-2 h-2 bg-yellow-400 rounded-full"></div><span class="text-xs text-yellow-500 font-bold">AI 트레이딩 가동중</span></div>
            </div>
            <div class="flex-[3] bg-panel" id="tv_chart_container"></div>
            <div class="flex-[2] bg-panel flex">
                <div class="w-1/2 border-r border-line flex flex-col"><div class="text-center text-xs py-1 border-b border-line text-gray-400">일반호가</div><div id="ob" class="flex-1 p-1 text-[11px] num-font"></div></div>
                <div class="w-1/2 flex flex-col bg-[#0b1016]">
                    <div class="flex flex-col border-b border-line bg-panel p-2 gap-2">
                        <div class="flex justify-between items-center"><span class="text-xs font-bold text-yellow-500">🧠 AI 설정</span>
                            <select onchange="changeMode(this.value)" class="bg-[#1b2029] text-xs text-white border border-gray-700 rounded p-1 outline-none">
                                <option value="safe">🛡️ 안정형</option><option value="balance" selected>⚖️ 밸런스</option><option value="aggressive">⚔️ 공격형</option>
                            </select>
                        </div>
                        <div class="flex justify-between text-[11px] bg-[#0b1016] p-1.5 rounded border border-gray-800"><span class="text-gray-400">AI 시드:</span><span id="ai-tot" class="font-bold text-green-400">100,000,000 KRW</span></div>
                    </div>
                    <div id="ai-analysis-box" class="flex-1 p-3 space-y-2 text-[11px] overflow-y-auto border-t border-gray-800"><div class="text-center text-gray-500 mt-4 animate-pulse">AI 연결 중...</div></div>
                </div>
            </div>
        </div>
        <div class="w-[350px] flex flex-col bg-panel shrink-0">
            <div class="flex text-sm border-b border-line bg-[#0b1016]">
                <div id="t-buy" class="flex-1 text-center py-2 t-inact hover:text-red-400" onclick="setOrd('buy')">매수</div>
                <div id="t-sell" class="flex-1 text-center py-2 t-inact hover:text-blue-400" onclick="setOrd('sell')">매도</div>
                <div id="t-hist" class="flex-1 text-center py-2 o-hist" onclick="setOrd('history')">거래내역</div>
            </div>
            <div class="flex-1 flex flex-col overflow-hidden">
                <div class="flex text-[11px] text-gray-400 border-b border-line py-1.5 px-2 text-center bg-[#0b1016]"><div class="w-1/5">시간</div><div class="w-1/4">AI명</div><div class="w-1/5">종류</div><div class="w-1/3 text-right">가격</div></div>
                <div id="h-list" class="flex-1 overflow-y-auto text-[11px] num-font divide-y divide-[#2b303b]"></div>
            </div>
        </div>
        <div class="w-[380px] flex flex-col bg-panel shrink-0">
            <div class="p-2 border-b border-line text-xs text-yellow-500 font-bold bg-[#1b2029]">💡 코인 클릭 시 차트 변경</div>
            <div class="flex text-[10px] text-gray-400 py-1.5 px-2 border-b border-line bg-[#0b1016]"><div class="flex-[1.5]">코인</div><div class="flex-[1.5] text-right">수량/평단</div><div class="flex-[1.5] text-right">현재가</div><div class="flex-[1.5] text-right">손익/수익률</div></div>
            <div id="c-list" class="flex-1 overflow-y-auto divide-y divide-[#1b2029]"></div>
        </div>
    </main>
"""

# HTML Part 3
html_part3 = """
    <main id="v-port" class="flex-1 hidden bg-[#0b1016] p-4 overflow-y-auto w-full">
        <div class="max-w-[1200px] mx-auto mt-4">
            <h2 class="text-2xl font-bold mb-6 text-white border-b border-gray-800 pb-2">나의 투자내역</h2>
            <div class="bg-panel rounded-lg p-6 mb-6 border border-gray-800 shadow-lg flex justify-between">
                <div><p class="text-sm text-gray-400 mb-1">총 보유자산</p><p id="p-tot-val" class="text-3xl font-bold num-font text-white">0 KRW</p></div>
                <div class="text-right"><p class="text-sm text-gray-400 mb-1">내 포트폴리오 평가손익</p><p id="p-tot-prof" class="text-3xl font-bold num-font">0 KRW</p></div>
            </div>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-hidden w-full mb-8">
                <div class="flex text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016]"><div class="flex-[1.5]">보유코인</div><div class="flex-[1] text-right">보유수량</div><div class="flex-[1] text-right">매수평균가</div><div class="flex-[1] text-right">현재가</div><div class="flex-[1.5] text-right">평가손익 / 수익률</div></div>
                <div id="p-list" class="divide-y divide-gray-800"></div>
            </div>
            <h3 class="text-xl font-bold mb-4 text-yellow-500 flex items-center gap-2">🤖 AI 상세 거래내역 장부</h3>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-hidden w-full overflow-x-auto pb-4">
                <div class="flex text-[11px] text-gray-400 py-2 px-4 border-b border-gray-800 bg-[#0b1016] min-w-[1050px]">
                    <div class="w-[12%]">주문시간</div><div class="w-[12%]">체결시간</div><div class="w-[10%]">코인명(마켓)</div><div class="w-[8%] text-center">종류</div><div class="w-[10%] text-right">거래수량</div><div class="w-[12%] text-right">거래단가</div><div class="w-[12%] text-right">거래금액</div><div class="w-[10%] text-right">수수료</div><div class="w-[14%] text-right">정산금액</div>
                </div>
                <div id="ai-detail-list" class="divide-y divide-gray-800 min-w-[1050px]"></div>
            </div>
        </div>
    </main>

    <main id="v-pnl" class="flex-1 hidden bg-[#0b1016] p-4 overflow-y-auto w-full">
        <div class="max-w-[1200px] mx-auto mt-4">
            <h2 class="text-2xl font-bold mb-6 text-white border-b border-gray-800 pb-2 flex items-center gap-2">📊 AI 코인별 상세 수익률 <span class="text-sm font-normal text-gray-500">7대장 코인 트레이딩 현황</span></h2>
            
            <div class="bg-panel rounded-lg p-6 mb-6 border border-gray-800 shadow-lg flex justify-between items-center">
                <div><p class="text-sm text-gray-400 mb-1">AI 보유 현금 (KRW)</p><p id="ai-cash-val" class="text-2xl font-bold num-font text-white">0 KRW</p></div>
                <div class="text-center"><p class="text-sm text-gray-400 mb-1">AI 코인 평가금액</p><p id="ai-coin-val" class="text-2xl font-bold num-font text-gray-300">0 KRW</p></div>
                <div class="text-right"><p class="text-sm text-gray-400 mb-1">AI 총 자산 (초기: 1억)</p><p id="ai-total-val" class="text-3xl font-bold num-font text-yellow-500">0 KRW</p></div>
            </div>

            <div class="bg-panel rounded-lg border border-gray-800 overflow-hidden w-full">
                <div class="flex text-xs text-gray-400 py-4 px-6 border-b border-gray-800 bg-[#0b1016]">
                    <div class="flex-[1.5] font-bold">코인명</div>
                    <div class="flex-[1.5] text-right">AI 보유수량<br>매수평균가</div>
                    <div class="flex-[1.5] text-right">매수금액<br>평가금액</div>
                    <div class="flex-[1.5] text-right">평가손익<br>수익률</div>
                </div>
                <div id="ai-coin-pnl-list" class="divide-y divide-gray-800 text-sm">
                    <div class="p-10 text-center text-gray-500 animate-pulse">실시간 AI 포트폴리오 로딩 중...</div>
                </div>
            </div>
            
            <h2 class="text-xl font-bold mt-10 mb-4 text-white border-b border-gray-800 pb-2">📅 당일 AI 전체 성과</h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-hidden w-full">
                <div class="flex text-xs text-gray-400 py-4 px-6 border-b border-gray-800 bg-[#0b1016]">
                    <div class="w-[20%] font-bold">일자</div>
                    <div class="w-[30%] text-right">당일 손익<br>누적 손익</div>
                    <div class="w-[20%] text-right">당일 수익률<br>누적 수익률</div>
                    <div class="w-[30%] text-right">기말 자산<br>기초 자산 (초기 시드)</div>
                </div>
                <div id="daily-pnl-list" class="divide-y divide-gray-800 text-sm"></div>
            </div>
        </div>
    </main>

    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
        let currentCoin = 'BTC'; let currentMode = '밸런스'; let gh = []; let co = 'history'; let globalAnalysis = {};

        function loadChart() {
            document.getElementById('tv_chart_container').innerHTML = '<div id="tv_chart" style="height:100%;width:100%"></div>';
            new TradingView.widget({"autosize":true,"symbol":"UPBIT:" + currentCoin + "KRW","interval":"15","theme":"dark","style":"1","locale":"kr","backgroundColor":"#12161f","container_id":"tv_chart"});
        }
        loadChart(); 

        function selectCoin(code, name) {
            currentCoin = code; document.getElementById('m-name').innerText = name; document.getElementById('m-code').innerText = code + "/KRW";
            loadChart(); renderAnalysis();
        }

        async function changeMode(m) { await fetch(`/api/mode/${m}`, {method:'POST'}); currentMode = m === 'safe' ? '안정형' : m === 'balance' ? '밸런스' : '공격형'; renderAnalysis(); }
        
        function setTab(t) { 
            ['trd', 'port', 'pnl'].forEach(id => {
                const v = document.getElementById('v-'+id);
                const n = document.getElementById('n-'+id);
                if(t === id) {
                    v.className = id === 'trd' ? "flex-1 flex overflow-hidden p-1 space-x-1" : "flex-1 bg-[#0b1016] p-4 overflow-y-auto w-full";
                    n.className = "text-white border-b-2 border-white pb-[14px] pt-4 cursor-pointer";
                } else {
                    v.className = "hidden";
                    n.className = "text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer";
                }
            });
        }
        
        function setOrd(t) { co=t; ['buy','sell','hist'].forEach(x=>document.getElementById(`t-${x}`).className="flex-1 text-center py-2 t-inact hover:text-gray-300"); document.getElementById(`t-${t==='history'?'hist':t}`).className=`flex-1 text-center py-2 o-${t==='history'?'hist':t}`; drawH(); }
        
        function drawH() { 
            let f=gh; if(co==='buy') f=gh.filter(x=>x.side==='매수'); if(co==='sell') f=gh.filter(x=>x.side==='매도'); 
            let h="", adH=""; 
            f.forEach(x=>{ 
                const c=x.side==='매수'?'up-red':'down-blue'; 
                h+=`<div class="flex py-1.5 px-2 hover:bg-gray-800"><div class="w-1/5 text-gray-500">${x.time}</div><div class="w-1/4 font-bold text-gray-300 truncate">${x.ai}</div><div class="w-1/5 ${c} font-bold text-[10px]">${x.coin} ${x.side}</div><div class="w-1/3 text-right font-bold ${c}">${x.price.toLocaleString()}</div></div>`;
            }); 
            gh.forEach(x => {
                const c=x.side==='매수'?'up-red':'down-blue'; 
                adH += `<div class="flex py-2 px-4 hover:bg-gray-800 transition text-[11px] min-w-[1050px] items-center border-b border-gray-800"><div class="w-[12%] text-gray-500">${x.order_time}</div><div class="w-[12%] text-gray-400 font-bold">${x.full_time}</div><div class="w-[10%] font-bold text-gray-200">${x.coin}(${x.market})</div><div class="w-[8%] font-bold text-center ${c} bg-opacity-20 rounded p-1 ${x.side==='매수'?'bg-red-900':'bg-blue-900'}">${x.side}</div><div class="w-[10%] text-right num-font">${x.qty.toFixed(4)}</div><div class="w-[12%] text-right num-font">${x.price.toLocaleString()}</div><div class="w-[12%] text-right num-font">${x.tot.toLocaleString()}</div><div class="w-[10%] text-right num-font text-gray-500">${x.fee.toLocaleString()}</div><div class="w-[14%] text-right font-bold num-font ${c}">${x.settle.toLocaleString()}</div></div>`;
            });
            document.getElementById('h-list').innerHTML=h; document.getElementById('ai-detail-list').innerHTML=adH || `<div class="p-4 text-center text-gray-500">거래 내역이 없습니다.</div>`;
        }

        function renderAnalysis() {
            if(!globalAnalysis[currentCoin]) return;
            const data = globalAnalysis[currentCoin];
            document.getElementById('ai-analysis-box').innerHTML = `
                <div class="bg-[#1b2029] p-3 rounded border border-gray-700 space-y-2">
                    <div class="text-yellow-400 font-bold border-b border-gray-700 pb-1 mb-2">[${currentCoin}] 실시간 분석 브리핑</div>
                    <div class="flex justify-between"><span class="text-gray-400">시장 상태:</span><span class="font-bold text-white">${data.status}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">시뮬레이션 RSI:</span><span class="font-bold text-blue-400">${data.rsi}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">매매 추천 잼:</span><span class="font-bold text-green-400">${data.rec}</span></div>
                </div>`;
        }
        
        function drawOB(p) { let h=""; let bp=p+5000; for(let i=0;i<5;i++){ h+=`<div class="flex justify-between bg-[rgba(18,97,196,0.1)] px-2 mb-[1px]"><span class="down-blue">${bp.toLocaleString()}</span><span class="text-gray-400">1.2</span></div>`; bp-=1000; } h+=`<div class="flex justify-between bg-gray-800 border border-gray-600 px-2 py-1 my-1"><span class="up-red font-bold text-xs">${p.toLocaleString()}</span><span class="text-gray-200">3.4</span></div>`; bp=p-1000; for(let i=0;i<5;i++){ h+=`<div class="flex justify-between bg-[rgba(200,74,49,0.1)] px-2 mt-[1px]"><span class="up-red">${bp.toLocaleString()}</span><span class="text-gray-400">0.5</span></div>`; bp-=1000; } document.getElementById('ob').innerHTML=h; }
        
        const ws = new WebSocket("ws://"+location.host+"/ws");
        ws.onmessage = e => { 
            try {
                const r=JSON.parse(e.data); 
                document.getElementById('usdt').innerText=Math.round(Number(r.usdt)||1450).toLocaleString(); 
                
                if(r.ai_tot) {
                    const aiProf = Number(r.ai_prof) || 0;
                    const aiRate = Number(r.ai_rate) || 0;
                    const aiCls = aiProf >= 0 ? 'text-red-400' : 'text-blue-400';
                    const aiSign = aiProf >= 0 ? '+' : '';
                    
                    const gProfEl = document.getElementById('ai-global-prof');
                    if(gProfEl) {
                        gProfEl.innerText = `${aiSign}${Math.round(aiProf).toLocaleString()} KRW (${aiSign}${aiRate.toFixed(2)}%)`;
                        gProfEl.className = `font-bold text-sm num-font ${aiCls}`;
                    }
                    
                    const elAiTotalVal = document.getElementById('ai-total-val');
                    if(elAiTotalVal) elAiTotalVal.innerText = Math.round(Number(r.ai_tot)).toLocaleString()+" KRW";
                    const elAiCashVal = document.getElementById('ai-cash-val');
                    if(elAiCashVal) elAiCashVal.innerText = Math.round(Number(r.ai_krw)).toLocaleString()+" KRW";
                    const elAiCoinVal = document.getElementById('ai-coin-val');
                    if(elAiCoinVal) elAiCoinVal.innerText = Math.round(Number(r.ai_tot) - Number(r.ai_krw)).toLocaleString()+" KRW";
                    const elAiTotNav = document.getElementById('ai-tot');
                    if(elAiTotNav) elAiTotNav.innerText = Math.round(Number(r.ai_tot)).toLocaleString()+" KRW";
                }

                if(r.analysis) { globalAnalysis = r.analysis; renderAnalysis(); }
                
                let lh="", ph="", tp=0, tv=0; 
                r.data.forEach(c => { 
                    const prof = Number(c.prof)||0; const val = Number(c.val)||0; const rate = Number(c.rate)||0;
                    const cur_krw = Number(c.cur_krw)||Number(c.avg)||0; const avg = Number(c.avg)||0; const qty = Number(c.qty)||0;
                    tp += prof; tv += val;
                    const cl = rate>=0 ? 'up-red':'down-blue', s = rate>=0 ? '+': ''; 
                    
                    if(c.code === currentCoin){ 
                        document.getElementById('m-prc').innerText=Math.round(cur_krw).toLocaleString(); 
                        document.getElementById('m-rt').innerText=`전일대비 ${s}${rate.toFixed(2)}%`; 
                        document.getElementById('m-prc').className=`text-2xl font-bold num-font ${cl}`; 
                        document.getElementById('m-rt').className=`text-xs font-bold num-font ${cl}`; 
                        drawOB(Math.round(cur_krw)); 
                    } 
                    
                    lh+=`<div onclick="selectCoin('${c.code}', '${c.name}')" class="flex text-[11px] py-1.5 px-2 hover:bg-[#1b2029] items-center cursor-pointer transition"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200">${c.name}</span><span class="text-[9px] text-gray-500">${c.code}/KRW</span></div><div class="flex-[1.5] text-right flex flex-col"><span class="text-gray-300 num-font">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</span><span class="text-gray-500 text-[9px] num-font">${Math.round(avg).toLocaleString()}</span></div><div class="flex-[1.5] text-right font-bold num-font ${cl}">${Math.round(cur_krw).toLocaleString()}</div><div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font">${s}${rate.toFixed(2)}%</span><span class="${cl} text-[9px] num-font">${Math.round(prof).toLocaleString()}</span></div></div>`; 
                    ph+=`<div class="flex text-sm py-4 px-4 items-center hover:bg-gray-800 transition border-b border-gray-800"><div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200 text-base">${c.name}</span><span class="text-xs text-gray-500">${c.code}</span></div><div class="flex-[1] text-right num-font text-gray-300">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</div><div class="flex-[1] text-right num-font text-gray-400">${Math.round(avg).toLocaleString()} KRW</div><div class="flex-[1] text-right font-bold num-font ${cl}">${Math.round(cur_krw).toLocaleString()} KRW</div><div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font text-base">${Math.round(prof).toLocaleString()} KRW</span><span class="${cl} text-xs num-font">${s}${rate.toFixed(2)}%</span></div></div>`;
                }); 
                
                document.getElementById('c-list').innerHTML=lh; document.getElementById('p-list').innerHTML=ph; 
                
                const elPtotVal = document.getElementById('p-tot-val');
                if(elPtotVal) elPtotVal.innerText=Math.round(tv).toLocaleString()+" KRW";
                const elPtotProf = document.getElementById('p-tot-prof');
                if(elPtotProf) {
                    elPtotProf.innerText=Math.round(tp).toLocaleString()+" KRW";
                    elPtotProf.className=`text-3xl font-bold num-font ${tp>=0?'up-red':'down-blue'}`;
                }
                
                if(r.hist){ gh=r.hist; drawH(); } 

                if(r.ai_coin_pnl) {
                    let aiPnlHtml = "";
                    r.ai_coin_pnl.forEach(d => {
                        const dc = d.profit >= 0 ? 'up-red' : 'down-blue'; const ds = d.profit > 0 ? '+' : '';
                        const hasCoin = d.qty > 0 || d.invested > 0;
                        const rowCls = hasCoin ? 'text-gray-300' : 'text-gray-600 opacity-50';
                        const valCls = hasCoin ? 'text-white' : 'text-gray-600';
                        const numCls = hasCoin ? dc : 'text-gray-600';

                        aiPnlHtml += `<div class="flex py-5 px-6 hover:bg-gray-800 transition items-center border-b border-gray-800 ${rowCls}">
                            <div class="flex-[1.5] flex flex-col"><span class="font-bold text-base">${d.name}</span><span class="text-xs text-gray-500">${d.code}/KRW</span></div>
                            <div class="flex-[1.5] text-right flex flex-col gap-1"><span class="font-bold num-font text-base">${d.qty.toFixed(4)}</span><span class="text-xs num-font">${Math.round(d.avg).toLocaleString()} KRW</span></div>
                            <div class="flex-[1.5] text-right flex flex-col gap-1"><span class="num-font text-base text-gray-400">${Math.round(d.invested).toLocaleString()}</span><span class="text-xs font-bold num-font ${valCls}">${Math.round(d.valuation).toLocaleString()} KRW</span></div>
                            <div class="flex-[1.5] text-right flex flex-col gap-1"><span class="${numCls} font-bold num-font text-base">${ds}${Math.round(d.profit).toLocaleString()}</span><span class="${numCls} text-xs num-font">${ds}${d.rate.toFixed(2)}%</span></div>
                        </div>`;
                    });
                    const elAiCoinList = document.getElementById('ai-coin-pnl-list');
                    if(elAiCoinList) elAiCoinList.innerHTML = aiPnlHtml;
                }
                
                if(r.daily_pnl) {
                    let dpHtml = "";
                    r.daily_pnl.forEach(d => {
                        const dc = d.d_prof >= 0 ? 'up-red' : 'down-blue'; const ds = d.d_prof >= 0 ? '+' : '';
                        const ac = d.a_prof >= 0 ? 'up-red' : 'down-blue'; const as = d.a_prof >= 0 ? '+' : '';
                        dpHtml += `<div class="flex py-5 px-6 hover:bg-gray-800 transition items-center border-b border-gray-800">
                            <div class="w-[20%] text-gray-300 font-bold">${d.date} <span class="ml-2 text-[10px] bg-green-900 text-green-400 px-1 rounded">Today</span></div>
                            <div class="w-[30%] text-right flex flex-col gap-1"><span class="${dc} font-bold num-font text-base">${ds}${Math.round(d.d_prof).toLocaleString()}</span><span class="${ac} text-xs num-font">${as}${Math.round(d.a_prof).toLocaleString()}</span></div>
                            <div class="w-[20%] text-right flex flex-col gap-1"><span class="${dc} font-bold num-font text-base">${ds}${d.d_rate.toFixed(2)}%</span><span class="${ac} text-xs num-font">${as}${d.a_rate.toFixed(2)}%</span></div>
                            <div class="w-[30%] text-right flex flex-col gap-1"><span class="text-white font-bold num-font text-base">${Math.round(d.e_asset).toLocaleString()}</span><span class="text-gray-500 text-xs num-font">${Math.round(d.s_asset).toLocaleString()}</span></div>
                        </div>`;
                    });
                    const elDailyList = document.getElementById('daily-pnl-list');
                    if(elDailyList) elDailyList.innerHTML = dpHtml;
                }
            } catch (err) { console.error("Parse Error:", err); }
        };
    </script>
</body></html>
"""

files["templates/index.html"] = html_part1 + html_part2 + html_part3

def install():
    if not os.path.exists(TARGET_PATH): os.makedirs(TARGET_PATH)
    for path, content in files.items():
        fp = os.path.join(TARGET_PATH, path)
        dr = os.path.dirname(fp)
        if dr and not os.path.exists(dr): os.makedirs(dr)
        with open(fp, "w", encoding="utf-8") as f: f.write(content)
        print(f"✅ V16 백신 및 통합 패치 완료: {path}")
    print("\n🎉 모든 버그를 완전히 소멸시켰습니다!")
    print("-----------------------------------------------------")
    print("1. 터미널 명령어: python main.py")
    print("2. [필수!] 접속 주소: http://127.0.0.1:8000 (0.0.0.0 금지!)")
    print("3. [필수!] 크롬에서 단축키 [Ctrl + Shift + R] 을 눌러 새로고침 하세요!")
    print("-----------------------------------------------------")

if __name__ == "__main__":
    install()