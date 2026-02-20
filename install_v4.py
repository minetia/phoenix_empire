import os

# ==========================================
# [설정] 설치 경로 지정
# ==========================================
TARGET_PATH = r"C:\Users\loves\Project_Phoenix"

print("🔥 [Project Phoenix V4] UI 활성화 및 5대잼 필터링 기능 탑재 중...")

files = {}

# 1. 의존성 패키지
files["requirements.txt"] = """fastapi
uvicorn
jinja2
python-dotenv
pyupbit
pandas
websockets
"""

# 2. 메인 서버 (main.py)
files["main.py"] = """from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.trader import PhoenixTrader
import asyncio
import os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

trader = PhoenixTrader()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await trader.get_portfolio_status()
        await websocket.send_json(data)
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(trader.simulate_ai_trading())

if __name__ == "__main__":
    import uvicorn
    print("🚀 PRO V4 서버 시작: http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
"""

# 3. Core - Logger (CSV 저장 유지)
files["core/logger.py"] = """import csv
import os
from datetime import datetime

class AITradeLogger:
    def __init__(self, filename="ai_trade_log.csv"):
        self.filename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["체결시간", "담당 AI", "마켓", "종류", "거래수량", "거래단가", "거래금액(KRW)"])

    def log_trade(self, ai_name, coin, side, qty, price):
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_amt = qty * price
        with open(self.filename, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([time_str, ai_name, coin, side, f"{qty:.8f}", f"{price:,.0f}", f"{total_amt:,.0f}"])
        
        return {
            "time": time_str[11:], 
            "ai": ai_name,
            "coin": coin,
            "side": side,
            "qty": round(qty, 4),
            "price": price,
            "total": total_amt
        }
"""

# 4. Core - Exchange
files["core/exchange.py"] = """import pyupbit
class Exchange:
    def get_current_price(self, tickers):
        try: return pyupbit.get_current_price(tickers)
        except: return {}
"""

# 5. Core - Trader (5대잼 로직 유지 & 확장)
files["core/trader.py"] = """import asyncio
import random
from core.exchange import Exchange
from core.logger import AITradeLogger

class PhoenixTrader:
    def __init__(self):
        self.exchange = Exchange()
        self.logger = AITradeLogger()
        self.trade_history = [] 
        
        # 실제 사용자 평단가/수량 적용
        self.portfolio = [
            {"code": "KRW-BTC",  "name": "비트코인",   "qty": 0.020129,   "avg": 139647010},
            {"code": "KRW-ETH",  "name": "이더리움",   "qty": 0.613473,   "avg": 4727629},
            {"code": "KRW-SOL",  "name": "솔라나",     "qty": 6.997309,   "avg": 192965},
            {"code": "KRW-XRP",  "name": "리플",       "qty": 552.0696,   "avg": 2913.0},
            {"code": "KRW-ZRX",  "name": "제로엑스",   "qty": 39624.97,   "avg": 357.1},
            {"code": "KRW-SUI",  "name": "수이",       "qty": 522.1083,   "avg": 2470.3},
            {"code": "KRW-ONDO", "name": "온도",       "qty": 627.0825,   "avg": 478.0}
        ]
        self.ai_names = ["스캘핑 잼", "추세추종 잼", "방패 잼", "스나이퍼 잼", "고래 잼"]

    async def simulate_ai_trading(self):
        while True:
            await asyncio.sleep(random.uniform(2, 6)) # 거래 빈도 증가
            coin_info = random.choice(self.portfolio)
            coin = coin_info["code"]
            ai = random.choice(self.ai_names)
            side = random.choice(["매수", "매도"])
            
            prices = self.exchange.get_current_price([coin])
            price = prices.get(coin, 0)
            if price > 0:
                qty_multiplier = 0.01 if price > 1000000 else 10
                qty = random.uniform(0.1, 5.0) * qty_multiplier
                
                log_data = self.logger.log_trade(ai, coin.replace("KRW-", ""), side, qty, price)
                self.trade_history.insert(0, log_data)
                
                # 프론트엔드 필터링을 위해 넉넉히 100개 유지
                if len(self.trade_history) > 100:
                    self.trade_history.pop()

    async def get_portfolio_status(self):
        tickers = [item["code"] for item in self.portfolio] + ["KRW-USDT"]
        prices = self.exchange.get_current_price(tickers) or {}
        usdt_rate = prices.get("KRW-USDT", 1450)
        
        response_data = []
        for coin in self.portfolio:
            current_price = prices.get(coin["code"], coin["avg"])
            valuation = current_price * coin["qty"]
            profit = valuation - (coin["avg"] * coin["qty"])
            rate = ((current_price - coin["avg"]) / coin["avg"]) * 100 if coin["avg"] > 0 else 0
            
            response_data.append({
                "name": coin["name"], "code": coin["code"].split("-")[1],
                "qty": coin["qty"], "avg": coin["avg"],
                "cur_price_krw": current_price, "cur_price_usd": current_price / usdt_rate,
                "valuation": valuation, "profit": profit, "rate": rate
            })

        return {
            "type": "update", 
            "usdt_rate": usdt_rate, 
            "data": response_data,
            "history": self.trade_history
        }
"""

# 6. Templates - Index.html (V4 전면 개편)
files["templates/index.html"] = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Phoenix PRO - AI Trading V4</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b1016; color: #c8ccce; font-family: -apple-system, sans-serif; overflow: hidden; }
        .bg-panel { background-color: #12161f; }
        .border-line { border-color: #2b303b; }
        
        .up-red { color: #c84a31; }
        .bg-up-red { background-color: rgba(200, 74, 49, 0.1); }
        .down-blue { color: #1261c4; }
        .bg-down-blue { background-color: rgba(18, 97, 196, 0.1); }
        
        .num-font { font-family: 'Roboto', Tahoma, sans-serif; letter-spacing: -0.5px; }
        
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0b1016; }
        ::-webkit-scrollbar-thumb { background: #2b303b; }
        ::-webkit-scrollbar-thumb:hover { background: #4a5568; }

        .tab-active { border-bottom: 2px solid #c8ccce; color: #fff; font-weight: bold; }
        .tab-inactive { border-bottom: 2px solid transparent; color: #666; cursor: pointer; }
        .tab-inactive:hover { color: #999; }
        
        /* 중앙 패널용 탭 색상 */
        .ord-buy-active { background-color: rgba(200, 74, 49, 0.2); color: #c84a31; font-weight: bold; border-top: 2px solid #c84a31; }
        .ord-sell-active { background-color: rgba(18, 97, 196, 0.2); color: #1261c4; font-weight: bold; border-top: 2px solid #1261c4; }
        .ord-hist-active { background-color: #1b2029; color: #fff; font-weight: bold; border-top: 2px solid #fff; }
    </style>
</head>
<body class="h-screen flex flex-col select-none">

    <header class="h-12 bg-panel border-b border-line flex justify-between items-center px-4 shrink-0">
        <div class="flex items-center space-x-6">
            <h1 class="text-lg font-bold text-white tracking-wider">UPBIT <span class="text-yellow-500 font-normal text-sm border border-yellow-500 px-1 rounded ml-1">AI PRO</span></h1>
            <nav class="flex space-x-4 text-sm font-bold">
                <a id="nav-trade" onclick="switchGlobalTab('trade')" class="text-white border-b-2 border-white pb-[14px] pt-4 cursor-pointer">거래소</a>
                <a id="nav-portfolio" onclick="switchGlobalTab('portfolio')" class="text-gray-500 hover:text-white pb-[14px] pt-4 border-b-2 border-transparent cursor-pointer">투자내역</a>
                <a onclick="switchGlobalTab('trade')" class="text-gray-500 hover:text-white pt-4 text-yellow-400 cursor-pointer">🤖 AI 자동매매</a>
            </nav>
        </div>
        <div class="flex gap-4 items-center">
            <div class="text-xs text-gray-400">총 평가손익: <span id="global-total-profit" class="font-bold text-sm num-font text-white">0 KRW</span></div>
            <div class="text-xs text-gray-400">환율: <span id="usdt-rate" class="text-yellow-500">0</span> KRW</div>
        </div>
    </header>

    <main id="view-trade" class="flex-1 flex overflow-hidden p-1 space-x-1">
        <div class="flex-1 flex flex-col space-y-1 overflow-hidden min-w-[600px]">
            <div class="h-16 bg-panel flex items-center px-4 shrink-0">
                <div class="flex items-center gap-2">
                    <img src="https://static.upbit.com/logos/BTC.png" class="w-6 h-6 rounded-full">
                    <h2 class="text-xl font-bold text-white">비트코인 <span class="text-xs text-gray-500 font-normal">BTC/KRW</span></h2>
                </div>
                <div class="ml-6 flex flex-col">
                    <span id="main-price" class="text-2xl font-bold up-red num-font">0</span>
                    <span id="main-rate" class="text-xs up-red font-bold num-font">전일대비 +0.00%</span>
                </div>
                <div class="ml-auto flex items-center gap-2 border border-yellow-600/50 bg-yellow-900/20 px-3 py-1.5 rounded">
                    <div class="animate-pulse w-2 h-2 bg-yellow-400 rounded-full"></div>
                    <span class="text-xs text-yellow-500 font-bold">잼 5대장 AI 트레이딩 가동 중</span>
                </div>
            </div>

            <div class="flex-[3] bg-panel relative">
                <div class="tradingview-widget-container" style="height:100%;width:100%">
                    <div id="tradingview_chart" style="height:100%;width:100%"></div>
                    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                    <script type="text/javascript">
                    new TradingView.widget({
                        "autosize": true, "symbol": "UPBIT:BTCKRW", "interval": "15",
                        "timezone": "Asia/Seoul", "theme": "dark", "style": "1",
                        "locale": "kr", "backgroundColor": "#12161f", "hide_top_toolbar": false,
                        "save_image": false, "container_id": "tradingview_chart"
                    });
                    </script>
                </div>
            </div>

            <div class="flex-[2] bg-panel flex">
                <div class="w-1/2 border-r border-line flex flex-col">
                    <div class="text-center text-xs py-1 border-b border-line text-gray-400 font-bold">일반호가</div>
                    <div class="flex-1 flex flex-col text-[11px] num-font p-1" id="orderbook"></div>
                </div>
                <div class="w-1/2 flex flex-col bg-[#0b1016]">
                    <div class="text-center text-xs py-1 border-b border-line text-yellow-500 font-bold bg-panel">🧠 AI 분석 엔진 로그</div>
                    <div id="ai-analysis" class="flex-1 p-2 space-y-2 text-[11px] overflow-y-auto font-mono text-gray-400">
                        <div class="text-yellow-600">>> 시스템 초기화 완료. 마켓 데이터 수신 중...</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="w-[350px] flex flex-col bg-panel shrink-0">
            <div class="flex text-sm border-b border-line bg-[#0b1016]">
                <div id="ord-tab-buy" class="flex-1 text-center py-2 tab-inactive hover:text-red-400" onclick="switchOrderTab('buy')">매수</div>
                <div id="ord-tab-sell" class="flex-1 text-center py-2 tab-inactive hover:text-blue-400" onclick="switchOrderTab('sell')">매도</div>
                <div id="ord-tab-hist" class="flex-1 text-center py-2 ord-hist-active" onclick="switchOrderTab('history')">거래내역 (AI)</div>
            </div>
            
            <div class="flex-1 flex flex-col overflow-hidden">
                <div class="flex text-[11px] text-gray-400 border-b border-line py-1.5 px-2 text-center bg-[#0b1016]">
                    <div class="w-1/5">시간</div>
                    <div class="w-1/4">AI명</div>
                    <div class="w-1/5">종류</div>
                    <div class="w-1/3 text-right">체결가격</div>
                </div>
                <div id="trade-history-list" class="flex-1 overflow-y-auto text-[11px] num-font divide-y divide-[#2b303b]">
                    </div>
            </div>
        </div>

        <div class="w-[380px] flex flex-col bg-panel shrink-0">
            <div class="p-2 border-b border-line">
                <input type="text" placeholder="코인명/심볼 검색" class="w-full bg-[#0b1016] border border-line text-white text-xs px-2 py-1.5 outline-none">
            </div>
            <div class="flex text-[10px] text-gray-400 py-1.5 px-2 border-b border-line bg-[#0b1016]">
                <div class="flex-[1.5]">코인명</div>
                <div class="flex-[1.5] text-right">보유수량/평단가</div>
                <div class="flex-[1.5] text-right">현재가</div>
                <div class="flex-[1.5] text-right">평가손익/수익률</div>
            </div>
            
            <div id="coin-list" class="flex-1 overflow-y-auto divide-y divide-[#1b2029]">
                <div class="text-center text-xs text-gray-500 py-10 animate-pulse">데이터 로딩중...</div>
            </div>
        </div>
    </main>

    <main id="view-portfolio" class="flex-1 hidden bg-[#0b1016] p-4 overflow-y-auto">
        <div class="max-w-4xl mx-auto mt-4">
            <h2 class="text-2xl font-bold mb-6 text-white border-b border-gray-800 pb-2">나의 투자내역</h2>
            <div class="bg-panel rounded-lg p-6 mb-6 border border-gray-800 shadow-lg">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-400 mb-1">총 평가금액</p>
                        <p id="port-total-val" class="text-3xl font-bold num-font text-white">0 KRW</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm text-gray-400 mb-1">총 평가손익</p>
                        <p id="port-total-profit" class="text-3xl font-bold num-font">0 KRW</p>
                    </div>
                </div>
            </div>
            
            <h3 class="text-lg font-bold mb-4 text-gray-300">보유 자산 상세</h3>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-hidden">
                <div class="flex text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016]">
                    <div class="w-1/4">자산명</div>
                    <div class="w-1/4 text-right">보유수량</div>
                    <div class="w-1/4 text-right">매수평균가</div>
                    <div class="w-1/4 text-right">평가손익 / 수익률</div>
                </div>
                <div id="portfolio-list" class="divide-y divide-gray-800">
                    </div>
            </div>
        </div>
    </main>

    <script>
        // 전역 변수
        let globalHistory = [];
        let currentOrderTab = 'history'; // buy, sell, history

        // 1. 글로벌 탭 전환 (거래소 <-> 투자내역)
        function switchGlobalTab(tab) {
            const vTrade = document.getElementById('view-trade');
            const vPort = document.getElementById('view-portfolio');
            const nTrade = document.getElementById('nav-trade');
            const nPort = document.getElementById('nav-portfolio');

            if(tab === 'trade') {
                vTrade.classList.remove('hidden'); vPort.classList.add('hidden');
                nTrade.classList.add('text-white', 'border-white');
                nTrade.classList.remove('text-gray-500', 'border-transparent');
                nPort.classList.add('text-gray-500', 'border-transparent');
                nPort.classList.remove('text-white', 'border-white');
            } else {
                vTrade.classList.add('hidden'); vPort.classList.remove('hidden');
                nPort.classList.add('text-white', 'border-white');
                nPort.classList.remove('text-gray-500', 'border-transparent');
                nTrade.classList.add('text-gray-500', 'border-transparent');
                nTrade.classList.remove('text-white', 'border-white');
            }
        }

        // 2. 중앙 패널 매수/매도 탭 전환 및 렌더링
        function switchOrderTab(tab) {
            currentOrderTab = tab;
            const tBuy = document.getElementById('ord-tab-buy');
            const tSell = document.getElementById('ord-tab-sell');
            const tHist = document.getElementById('ord-tab-hist');

            // 클래스 초기화
            [tBuy, tSell, tHist].forEach(el => {
                el.className = "flex-1 text-center py-2 tab-inactive hover:text-gray-300";
            });

            if(tab === 'buy') tBuy.className = "flex-1 text-center py-2 ord-buy-active";
            else if(tab === 'sell') tSell.className = "flex-1 text-center py-2 ord-sell-active";
            else tHist.className = "flex-1 text-center py-2 ord-hist-active";

            renderHistory();
        }

        function renderHistory() {
            let filtered = globalHistory;
            if(currentOrderTab === 'buy') filtered = globalHistory.filter(h => h.side === '매수');
            if(currentOrderTab === 'sell') filtered = globalHistory.filter(h => h.side === '매도');

            let histHtml = "";
            filtered.forEach(h => {
                const hColor = h.side === '매수' ? 'up-red' : 'down-blue';
                const aiColor = {
                    "스캘핑 잼": "text-blue-400", "추세추종 잼": "text-yellow-400",
                    "방패 잼": "text-green-400", "스나이퍼 잼": "text-purple-400", "고래 잼": "text-pink-400"
                }[h.ai] || "text-gray-400";

                histHtml += `
                <div class="flex py-1.5 px-2 items-center hover:bg-gray-800 transition">
                    <div class="w-1/5 text-gray-500">${h.time}</div>
                    <div class="w-1/4 font-bold ${aiColor} truncate">${h.ai}</div>
                    <div class="w-1/5 ${hColor} font-bold text-[10px]">${h.coin} ${h.side}</div>
                    <div class="w-1/3 text-right font-bold ${hColor}">${h.price.toLocaleString()}</div>
                </div>`;
            });
            document.getElementById('trade-history-list').innerHTML = histHtml || '<div class="text-center py-10 text-gray-500 text-xs">내역이 없습니다.</div>';
        }

        // 가짜 호가창
        function generateOrderbook(basePrice) {
            let html = ""; let p = basePrice + 5000;
            for(let i=0; i<5; i++) {
                html += `<div class="flex justify-between bg-down-blue px-2 py-0.5 mb-[1px]"><span class="down-blue">${p.toLocaleString()}</span><span class="text-gray-400">${(Math.random()*2).toFixed(3)}</span></div>`;
                p -= 1000;
            }
            html += `<div class="flex justify-between bg-gray-800 border border-gray-600 px-2 py-1 my-1"><span class="up-red font-bold text-xs">${basePrice.toLocaleString()}</span><span class="text-gray-200">${(Math.random()*5).toFixed(3)}</span></div>`;
            p = basePrice - 1000;
            for(let i=0; i<5; i++) {
                html += `<div class="flex justify-between bg-up-red px-2 py-0.5 mt-[1px]"><span class="up-red">${p.toLocaleString()}</span><span class="text-gray-400">${(Math.random()*2).toFixed(3)}</span></div>`;
                p -= 1000;
            }
            document.getElementById('orderbook').innerHTML = html;
        }

        // AI 로그 자동 생성
        const msgs = ["[추세추종 잼] BTC 골든크로스 접근", "[스캘핑 잼] 알트코인 타점 대기", "[방패 잼] 리스크 정상", "[스나이퍼 잼] 호가창 매수벽 붕괴 감지"];
        setInterval(() => {
            const box = document.getElementById('ai-analysis');
            const el = document.createElement('div');
            el.innerText = msgs[Math.floor(Math.random() * msgs.length)];
            box.appendChild(el);
            if(box.childNodes.length > 20) box.removeChild(box.firstChild);
            box.scrollTop = box.scrollHeight;
        }, 4000);

        // WebSocket 메인 로직
        const ws = new WebSocket("ws://" + window.location.host + "/ws");
        ws.onmessage = function(event) {
            const response = JSON.parse(event.data);
            document.getElementById('usdt-rate').innerText = Math.round(response.usdt_rate).toLocaleString();

            let listHtml = "";
            let portHtml = "";
            let totalProfit = 0;
            let totalValuation = 0;
            let btcPrice = 0;

            response.data.forEach(coin => {
                totalProfit += coin.profit;
                totalValuation += coin.valuation;
                
                const isProfit = coin.rate >= 0;
                const colorClass = isProfit ? 'up-red' : 'down-blue';
                const sign = isProfit ? '+' : '';
                
                if(coin.code === 'BTC') {
                    btcPrice = Math.round(coin.cur_price_krw);
                    document.getElementById('main-price').innerText = btcPrice.toLocaleString();
                    document.getElementById('main-rate').innerText = `전일대비 ${sign}${coin.rate.toFixed(2)}%`;
                    document.getElementById('main-rate').className = `text-xs font-bold num-font ${colorClass}`;
                    document.getElementById('main-price').className = `text-2xl font-bold num-font ${colorClass}`;
                }

                // 3. 우측 코인 리스트 (수량/평단가/수익률 완벽 반영)
                listHtml += `
                <div class="flex text-[11px] py-1.5 px-2 hover:bg-[#1b2029] items-center transition">
                    <div class="flex-[1.5] flex flex-col">
                        <span class="font-bold text-gray-200">${coin.name}</span>
                        <span class="text-[9px] text-gray-500">${coin.code}/KRW</span>
                    </div>
                    <div class="flex-[1.5] text-right flex flex-col">
                        <span class="text-gray-300 num-font">${coin.qty.toLocaleString(undefined, {maximumFractionDigits:4})}</span>
                        <span class="text-gray-500 text-[9px] num-font">${Math.round(coin.avg).toLocaleString()}</span>
                    </div>
                    <div class="flex-[1.5] text-right font-bold num-font ${colorClass}">
                        ${Math.round(coin.cur_price_krw).toLocaleString()}
                    </div>
                    <div class="flex-[1.5] text-right flex flex-col items-end">
                        <span class="${colorClass} font-bold num-font">${sign}${coin.rate.toFixed(2)}%</span>
                        <span class="${colorClass} text-[9px] num-font">${Math.round(coin.profit).toLocaleString()}</span>
                    </div>
                </div>`;

                // 4. 투자내역 (포트폴리오) 상세 렌더링
                portHtml += `
                <div class="flex text-sm py-4 px-4 items-center hover:bg-gray-800 transition">
                    <div class="w-1/4 flex flex-col">
                        <span class="font-bold text-gray-200 text-base">${coin.name}</span>
                        <span class="text-xs text-gray-500">${coin.code}</span>
                    </div>
                    <div class="w-1/4 text-right num-font text-gray-300">${coin.qty.toLocaleString(undefined, {maximumFractionDigits:4})}</div>
                    <div class="w-1/4 text-right num-font text-gray-400">${Math.round(coin.avg).toLocaleString()} KRW</div>
                    <div class="w-1/4 text-right flex flex-col">
                        <span class="${colorClass} font-bold num-font text-base">${Math.round(coin.profit).toLocaleString()} KRW</span>
                        <span class="${colorClass} text-xs num-font">${sign}${coin.rate.toFixed(2)}%</span>
                    </div>
                </div>`;
            });
            
            document.getElementById('coin-list').innerHTML = listHtml;
            document.getElementById('portfolio-list').innerHTML = portHtml;
            
            // 글로벌 자산 업데이트
            const tProfCls = totalProfit >= 0 ? 'up-red' : 'down-blue';
            document.getElementById('global-total-profit').innerText = Math.round(totalProfit).toLocaleString() + " KRW";
            document.getElementById('global-total-profit').className = `font-bold text-sm num-font ${tProfCls}`;
            
            document.getElementById('port-total-profit').innerText = Math.round(totalProfit).toLocaleString() + " KRW";
            document.getElementById('port-total-profit').className = `text-3xl font-bold num-font ${tProfCls}`;
            document.getElementById('port-total-val').innerText = Math.round(totalValuation).toLocaleString() + " KRW";

            if(btcPrice > 0) generateOrderbook(btcPrice);

            // 중앙 5대잼 내역 필터링 렌더링
            if(response.history) {
                globalHistory = response.history;
                renderHistory();
            }
        };
    </script>
</body>
</html>
"""

# ==========================================
# 실행 로직
# ==========================================
def install():
    if not os.path.exists(TARGET_PATH):
        os.makedirs(TARGET_PATH)

    for path, content in files.items():
        full_path = os.path.join(TARGET_PATH, path)
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ V4 적용 완료: {path}")

    print("\n🎉 [Project Phoenix V4] 최종 업데이트 완료!")
    print("--------------------------------------------------")
    print(f"1. 명령 프롬프트 이동: cd {TARGET_PATH}")
    print("2. 서버 실행: python main.py")
    print("3. 브라우저 접속: http://127.0.0.1:8000")
    print("4. 상단의 [투자내역] 탭 & 중앙의 [매수/매도] 탭을 클릭해보세요!")
    print("--------------------------------------------------")

if __name__ == "__main__":
    install()