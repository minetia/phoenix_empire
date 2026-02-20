import os

TARGET_PATH = r"C:\Users\loves\Project_Phoenix"
print("🔥 [Project Phoenix V6] 버그 픽스 및 투자내역 완벽 복구 중...")

files = {}

# 1. 의존성 및 환경변수
files["requirements.txt"] = "fastapi\nuvicorn\njinja2\npython-dotenv\npyupbit\npandas\nwebsockets\n"
files[".env"] = "UPBIT_ACCESS_KEY=none\nUPBIT_SECRET_KEY=none\n"

# 2. 메인 서버 (main.py)
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
    trader.ai_mode = mode
    return {"status": "success"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await trader.get_portfolio_status()
            await websocket.send_json(data)
        except Exception as e:
            print("WS Error:", e)
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(trader.simulate_ai_trading())

if __name__ == "__main__":
    import uvicorn
    # 반드시 127.0.0.1 로 실행하여 지갑 경고 회피
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
"""

# 3. 로거
files["core/logger.py"] = """import csv, os
from datetime import datetime
class AITradeLogger:
    def __init__(self):
        self.fn = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_trade_log.csv")
        if not os.path.exists(self.fn):
            with open(self.fn, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(["체결시간", "담당 AI", "마켓", "종류", "수량", "단가", "금액"])
    def log_trade(self, ai, coin, side, qty, price):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tot = qty * price
        with open(self.fn, 'a', newline='', encoding='utf-8-sig') as f:
            csv.writer(f).writerow([t, ai, coin, side, f"{qty:.8f}", f"{price:,.0f}", f"{tot:,.0f}"])
        return {"time": t[11:], "ai": ai, "coin": coin, "side": side, "qty": round(qty,4), "price": price}
"""

# 4. 거래소 API (NaN 방지용 안전 장치 추가)
files["core/exchange.py"] = """import pyupbit
class Exchange:
    def get_current_price(self, tickers):
        try: 
            res = pyupbit.get_current_price(tickers)
            # 단일 코인 조회시 float 반환 버그 픽스
            if isinstance(res, (float, int)): 
                return {tickers[0]: float(res)}
            elif isinstance(res, dict):
                return res
            return {}
        except: return {}
"""

# 5. 트레이더 로직 (모드별 딜레이/비중 완벽 적용)
files["core/trader.py"] = """import asyncio, random
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
            # [기능 적용] 모드에 따른 딜레이 적용 (공격형일수록 빠름)
            d = {"safe": 8, "balance": 4, "aggressive": 1.5}.get(self.ai_mode, 4)
            await asyncio.sleep(random.uniform(d*0.8, d*1.5))
            
            c = random.choice(self.port)["code"]
            side = random.choice(["매수", "매도"])
            
            prc_dict = self.ex.get_current_price([c])
            p = prc_dict.get(c, 0) if prc_dict else 0
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
            if len(self.hist) > 100: self.hist.pop()

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
            res.append({
                "name": c["name"], "code": c["code"].split("-")[1], 
                "qty": c["qty"], "avg": c["avg"], 
                "cur_krw": cp, "cur_usd": cp/usdt, 
                "val": val, "prof": prof, "rate": rate
            })
        
        tot_ai = self.ai_krw + sum(qty * prc.get(code,0) for code, qty in self.ai_hold.items() if qty>0)
        return {"usdt": usdt, "data": res, "hist": self.hist, "ai_tot": tot_ai}
"""

# 6. HTML (NaN 완벽 방어 + 투자내역 복구)
html_part1 = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8"><title>Phoenix PRO - AI Trading V6</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background:#0b1016; color:#c8ccce; font-family:-apple-system,sans-serif; overflow:hidden; }
        .bg-panel { background:#12161f; } .border-line { border-color:#2b303b; }
        .up-red { color:#c84a31; } .down-blue { color:#1261c4; } .num-font { font-family:'Roboto',sans-serif; }
        ::-webkit-scrollbar { width:4px; height:4px; } ::-webkit-scrollbar-track { background:#0b1016; } ::-webkit-scrollbar-thumb { background:#2b303b; }
        .t-act { font-weight:bold; color:#fff; } .t-inact { color:#666; cursor:pointer; }
        .o-buy { background:rgba(200,74,49,0.2); color:#c84a31; border-top:2px solid #c84a31; font-weight:bold; }
        .o-sell { background:rgba(18,97,196,0.2); color:#1261c4; border-top:2px solid #1261c4; font-weight:bold; }
        .o-hist { background:#1b2029; color:#fff; border-top:2px solid #fff; font-weight:bold; }
    </style>
</head>
<body class="h-screen flex flex-col select-none">
    <header class="h-12 bg-panel border-b border-line flex justify-between items-center px-4 shrink-0">
        <div class="flex items-center space-x-6">
            <h1 class="text-lg font-bold text-white tracking-wider">UPBIT <span class="text-yellow-500 text-sm border border-yellow-500 px-1 rounded ml-1">AI PRO V6</span></h1>
            <nav class="flex space-x-4 text-sm font-bold">
                <a id="n-trd" onclick="setTab('trd')" class="text-white border-b-2 border-white pb-[14px] pt-4 cursor-pointer">거래소</a>
                <a id="n-port" onclick="setTab('port')" class="text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer">투자내역</a>
                <a onclick="setTab('trd')" class="text-yellow-400 pt-4 cursor-pointer">🤖 AI 자동매매</a>
            </nav>
        </div>
        <div class="flex gap-4 items-center text-xs text-gray-400">
            <div>총 평가손익: <span id="g-prof" class="font-bold text-sm num-font text-white">0 KRW</span></div>
            <div>환율: <span id="usdt" class="text-yellow-500">0</span> KRW</div>
        </div>
    </header>
"""

html_part2 = """
    <main id="v-trd" class="flex-1 flex overflow-hidden p-1 space-x-1">
        <div class="flex-1 flex flex-col space-y-1 overflow-hidden min-w-[600px]">
            <div class="h-16 bg-panel flex items-center px-4 shrink-0">
                <img src="https://static.upbit.com/logos/BTC.png" class="w-6 h-6 rounded-full mr-2">
                <h2 class="text-xl font-bold text-white">비트코인 <span class="text-xs text-gray-500">BTC/KRW</span></h2>
                <div class="ml-6 flex flex-col"><span id="m-prc" class="text-2xl font-bold up-red num-font">0</span><span id="m-rt" class="text-xs up-red font-bold num-font">0.00%</span></div>
                <div class="ml-auto flex items-center gap-2 border border-yellow-600/50 bg-yellow-900/20 px-3 py-1 rounded"><div class="animate-pulse w-2 h-2 bg-yellow-400 rounded-full"></div><span class="text-xs text-yellow-500 font-bold">AI 트레이딩 가동중</span></div>
            </div>
            <div class="flex-[3] bg-panel"><div id="tv_chart" style="height:100%;width:100%"></div></div>
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
                    <div id="ai-log" class="flex-1 p-2 space-y-2 text-[11px] overflow-y-auto font-mono text-gray-400"></div>
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
            <div class="p-2 border-b border-line"><input type="text" placeholder="검색" class="w-full bg-[#0b1016] border border-line text-white text-xs p-1.5 outline-none"></div>
            <div class="flex text-[10px] text-gray-400 py-1.5 px-2 border-b border-line bg-[#0b1016]"><div class="flex-[1.5]">코인</div><div class="flex-[1.5] text-right">수량/평단</div><div class="flex-[1.5] text-right">현재가</div><div class="flex-[1.5] text-right">손익/수익률</div></div>
            <div id="c-list" class="flex-1 overflow-y-auto divide-y divide-[#1b2029]"></div>
        </div>
    </main>
"""

html_part3 = """
    <main id="v-port" class="flex-1 hidden bg-[#0b1016] p-4 overflow-y-auto w-full">
        <div class="max-w-5xl mx-auto mt-4">
            <h2 class="text-2xl font-bold mb-6 text-white border-b border-gray-800 pb-2">나의 투자내역</h2>
            <div class="bg-panel rounded-lg p-6 mb-6 border border-gray-800 shadow-lg flex justify-between">
                <div>
                    <p class="text-sm text-gray-400 mb-1">총 보유자산</p>
                    <p id="p-tot-val" class="text-3xl font-bold num-font text-white">0 KRW</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-400 mb-1">총 평가손익</p>
                    <p id="p-tot-prof" class="text-3xl font-bold num-font">0 KRW</p>
                </div>
            </div>
            
            <div class="bg-panel rounded-lg border border-gray-800 overflow-hidden w-full">
                <div class="flex text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016]">
                    <div class="flex-[1.5]">보유코인</div>
                    <div class="flex-[1] text-right">보유수량</div>
                    <div class="flex-[1] text-right">매수평균가</div>
                    <div class="flex-[1] text-right">현재가</div>
                    <div class="flex-[1.5] text-right">평가손익 / 수익률</div>
                </div>
                <div id="p-list" class="divide-y divide-gray-800"></div>
            </div>
        </div>
    </main>

    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
        new TradingView.widget({"autosize":true,"symbol":"UPBIT:BTCKRW","interval":"15","theme":"dark","style":"1","locale":"kr","backgroundColor":"#12161f","container_id":"tv_chart"});
        let gh = []; let co = 'history';
        async function changeMode(m) { await fetch(`/api/mode/${m}`, {method:'POST'}); const b=document.getElementById('ai-log'); b.innerHTML+=`<div class="text-yellow-400">>> AI 모드 변경됨</div>`; b.scrollTop=b.scrollHeight; }
        
        function setTab(t) { 
            document.getElementById('v-trd').className = t==='trd' ? "flex-1 flex overflow-hidden p-1 space-x-1" : "hidden"; 
            document.getElementById('v-port').className = t==='port' ? "flex-1 bg-[#0b1016] p-4 overflow-y-auto w-full" : "hidden"; 
            if(t==='trd') { document.getElementById('n-trd').className="text-white border-b-2 border-white pb-[14px] pt-4 cursor-pointer"; document.getElementById('n-port').className="text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer"; }
            else { document.getElementById('n-port').className="text-white border-b-2 border-white pb-[14px] pt-4 cursor-pointer"; document.getElementById('n-trd').className="text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer"; }
        }
        
        function setOrd(t) { co=t; ['buy','sell','hist'].forEach(x=>document.getElementById(`t-${x}`).className="flex-1 text-center py-2 t-inact hover:text-gray-300"); document.getElementById(`t-${t==='history'?'hist':t}`).className=`flex-1 text-center py-2 o-${t==='history'?'hist':t}`; drawH(); }
        
        function drawH() { 
            let f=gh; if(co==='buy') f=gh.filter(x=>x.side==='매수'); if(co==='sell') f=gh.filter(x=>x.side==='매도'); 
            let h=""; f.forEach(x=>{ const c=x.side==='매수'?'up-red':'down-blue'; h+=`<div class="flex py-1.5 px-2 hover:bg-gray-800"><div class="w-1/5 text-gray-500">${x.time}</div><div class="w-1/4 font-bold text-gray-300 truncate">${x.ai}</div><div class="w-1/5 ${c} font-bold text-[10px]">${x.coin} ${x.side}</div><div class="w-1/3 text-right font-bold ${c}">${x.price.toLocaleString()}</div></div>`}); 
            document.getElementById('h-list').innerHTML=h; 
        }
        
        function drawOB(p) { let h=""; let bp=p+5000; for(let i=0;i<5;i++){ h+=`<div class="flex justify-between bg-[rgba(18,97,196,0.1)] px-2 mb-[1px]"><span class="down-blue">${bp.toLocaleString()}</span><span class="text-gray-400">1.2</span></div>`; bp-=1000; } h+=`<div class="flex justify-between bg-gray-800 border border-gray-600 px-2 py-1 my-1"><span class="up-red font-bold text-xs">${p.toLocaleString()}</span><span class="text-gray-200">3.4</span></div>`; bp=p-1000; for(let i=0;i<5;i++){ h+=`<div class="flex justify-between bg-[rgba(200,74,49,0.1)] px-2 mt-[1px]"><span class="up-red">${bp.toLocaleString()}</span><span class="text-gray-400">0.5</span></div>`; bp-=1000; } document.getElementById('ob').innerHTML=h; }
        
        const ws = new WebSocket("ws://"+location.host+"/ws");
        ws.onmessage = e => { 
            const r=JSON.parse(e.data); 
            // NaN 방지: 값이 없으면 기본값 0 처리
            document.getElementById('usdt').innerText=Math.round(r.usdt || 1450).toLocaleString(); 
            if(r.ai_tot) document.getElementById('ai-tot').innerText=Math.round(r.ai_tot).toLocaleString()+" KRW"; 
            
            let lh="", ph="", tp=0, tv=0; 
            r.data.forEach(c => { 
                const prof = c.prof || 0; const val = c.val || 0; const rate = c.rate || 0;
                const cur_krw = c.cur_krw || c.avg; const avg = c.avg || 0; const qty = c.qty || 0;
                
                tp += prof; tv += val;
                const cl = rate >= 0 ? 'up-red' : 'down-blue', s = rate >= 0 ? '+' : ''; 
                
                if(c.code === 'BTC'){ 
                    document.getElementById('m-prc').innerText=Math.round(cur_krw).toLocaleString(); 
                    document.getElementById('m-rt').innerText=`${s}${rate.toFixed(2)}%`; 
                    document.getElementById('m-prc').className=`text-2xl font-bold num-font ${cl}`; 
                    document.getElementById('m-rt').className=`text-xs font-bold num-font ${cl}`; 
                    drawOB(Math.round(cur_krw)); 
                } 
                
                // 우측 거래소 리스트
                lh+=`<div class="flex text-[11px] py-1.5 px-2 hover:bg-[#1b2029] items-center">
                    <div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200">${c.name}</span><span class="text-[9px] text-gray-500">${c.code}/KRW</span></div>
                    <div class="flex-[1.5] text-right flex flex-col"><span class="text-gray-300 num-font">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</span><span class="text-gray-500 text-[9px] num-font">${Math.round(avg).toLocaleString()}</span></div>
                    <div class="flex-[1.5] text-right font-bold num-font ${cl}">${Math.round(cur_krw).toLocaleString()}</div>
                    <div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font">${s}${rate.toFixed(2)}%</span><span class="${cl} text-[9px] num-font">${Math.round(prof).toLocaleString()}</span></div>
                </div>`; 
                
                // 복구된 포트폴리오(투자내역) 리스트
                ph+=`<div class="flex text-sm py-4 px-4 items-center hover:bg-gray-800 transition border-b border-gray-800">
                    <div class="flex-[1.5] flex flex-col"><span class="font-bold text-gray-200 text-base">${c.name}</span><span class="text-xs text-gray-500">${c.code}</span></div>
                    <div class="flex-[1] text-right num-font text-gray-300">${qty.toLocaleString(undefined,{maximumFractionDigits:4})}</div>
                    <div class="flex-[1] text-right num-font text-gray-400">${Math.round(avg).toLocaleString()} KRW</div>
                    <div class="flex-[1] text-right font-bold num-font ${cl}">${Math.round(cur_krw).toLocaleString()} KRW</div>
                    <div class="flex-[1.5] text-right flex flex-col"><span class="${cl} font-bold num-font text-base">${Math.round(prof).toLocaleString()} KRW</span><span class="${cl} text-xs num-font">${s}${rate.toFixed(2)}%</span></div>
                </div>`;
            }); 
            
            document.getElementById('c-list').innerHTML=lh; 
            document.getElementById('p-list').innerHTML=ph; 
            
            document.getElementById('g-prof').innerText=Math.round(tp).toLocaleString()+" KRW"; 
            document.getElementById('g-prof').className=`font-bold text-sm num-font ${tp>=0?'up-red':'down-blue'}`; 
            
            document.getElementById('p-tot-val').innerText=Math.round(tv).toLocaleString()+" KRW";
            document.getElementById('p-tot-prof').innerText=Math.round(tp).toLocaleString()+" KRW";
            document.getElementById('p-tot-prof').className=`text-3xl font-bold num-font ${tp>=0?'up-red':'down-blue'}`;

            if(r.hist){ gh=r.hist; drawH(); } 
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
        print(f"✅ 파일 생성 성공: {path}")
    print("\n🎉 완벽하게 패치되었습니다!")

if __name__ == "__main__":
    install()