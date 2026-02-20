import os

# ==========================================
# [설정] 설치 경로 지정 (그대로 유지)
# ==========================================
TARGET_PATH = r"C:\Users\loves\Project_Phoenix"

print("🔥 [Project Phoenix V3] 업비트 PRO UI 및 잼 5대장 실시간 트레이딩 탑재 중...")

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
    # 잼 5대장 실시간 트레이딩 시뮬레이션 백그라운드 시작
    asyncio.create_task(trader.simulate_ai_trading())

if __name__ == "__main__":
    import uvicorn
    print("🚀 PRO 버전 서버 시작: http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
"""

# 3. Core - Logger (모든 거래내역을 CSV 파일로 저장)
files["core/logger.py"] = """import csv
import os
from datetime import datetime

class AITradeLogger:
    def __init__(self, filename="ai_trade_log.csv"):
        # BASE_DIR을 Project_Phoenix 루트로 설정
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
            "time": time_str[11:], # 시:분:초 만 UI용으로 반환
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

# 5. Core - Trader (5대잼 로직 추가)
files["core/trader.py"] = """import asyncio
import random
from core.exchange import Exchange
from core.logger import AITradeLogger

class PhoenixTrader:
    def __init__(self):
        self.exchange = Exchange()
        self.logger = AITradeLogger()
        self.trade_history = [] # UI로 보낼 최근 내역
        
        self.portfolio = [
            {"code": "KRW-BTC",  "name": "비트코인",   "qty": 0.020129,   "avg": 98000000},
            {"code": "KRW-ETH",  "name": "이더리움",   "qty": 0.613473,   "avg": 4727629},
            {"code": "KRW-SOL",  "name": "솔라나",     "qty": 6.997309,   "avg": 192965},
            {"code": "KRW-XRP",  "name": "리플",       "qty": 552.0696,   "avg": 800.0},
            {"code": "KRW-ZRX",  "name": "제로엑스",   "qty": 39624.97,   "avg": 357.1},
            {"code": "KRW-SUI",  "name": "수이",       "qty": 522.1083,   "avg": 2470.3},
            {"code": "KRW-ONDO", "name": "온도",       "qty": 627.0825,   "avg": 478.0}
        ]
        self.ai_names = ["스캘핑 잼", "추세추종 잼", "방패 잼", "스나이퍼 잼", "고래 잼"]

    async def simulate_ai_trading(self):
        \"\"\"잼 5대장 실시간 트레이딩 시뮬레이션 (3~8초마다 거래 발생)\"\"\"
        while True:
            await asyncio.sleep(random.uniform(3, 8))
            coin_info = random.choice(self.portfolio)
            coin = coin_info["code"]
            ai = random.choice(self.ai_names)
            side = random.choice(["매수", "매도"])
            
            prices = self.exchange.get_current_price([coin])
            price = prices.get(coin, 0)
            if price > 0:
                qty_multiplier = 0.01 if price > 1000000 else 10
                qty = random.uniform(0.1, 5.0) * qty_multiplier
                
                # 로그 저장 및 히스토리 업데이트
                log_data = self.logger.log_trade(ai, coin.replace("KRW-", ""), side, qty, price)
                self.trade_history.insert(0, log_data)
                
                # UI에는 최근 30개만 유지
                if len(self.trade_history) > 30:
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

# 6. Templates - Index.html (업비트 PRO 레이아웃 100% 클론)
files["templates/index.html"] = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Phoenix PRO - AI Trading</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 업비트 다크 테마 완벽 구현 */
        body { background-color: #0b1016; color: #c8ccce; font-family: -apple-system, sans-serif; overflow: hidden; }
        .bg-panel { background-color: #12161f; }
        .border-line { border-color: #2b303b; }
        
        .up-red { color: #c84a31; }
        .bg-up-red { background-color: rgba(200, 74, 49, 0.1); }
        .down-blue { color: #1261c4; }
        .bg-down-blue { background-color: rgba(18, 97, 196, 0.1); }
        
        .num-font { font-family: 'Roboto', Tahoma, sans-serif; letter-spacing: -0.5px; }
        
        /* 스크롤바 커스텀 */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0b1016; }
        ::-webkit-scrollbar-thumb { background: #2b303b; }
        ::-webkit-scrollbar-thumb:hover { background: #4a5568; }

        .tab-active { border-bottom: 2px solid #c8ccce; color: #fff; font-weight: bold; }
        .tab-inactive { border-bottom: 2px solid transparent; color: #666; cursor: pointer; }
        .tab-inactive:hover { color: #999; }
    </style>
</head>
<body class="h-screen flex flex-col select-none">

    <header class="h-12 bg-panel border-b border-line flex justify-between items-center px-4 shrink-0">
        <div class="flex items-center space-x-6">
            <h1 class="text-lg font-bold text-white tracking-wider">UPBIT <span class="text-yellow-500 font-normal text-sm border border-yellow-500 px-1 rounded ml-1">AI PRO</span></h1>
            <nav class="flex space-x-4 text-sm font-bold">
                <a href="#" class="text-white border-b-2 border-white pb-[14px] pt-4">거래소</a>
                <a href="#" class="text-gray-500 hover:text-white pt-4">투자내역</a>
                <a href="#" class="text-gray-500 hover:text-white pt-4 text-yellow-400">🤖 AI 자동매매</a>
            </nav>
        </div>
        <div class="text-xs text-gray-400">환율: <span id="usdt-rate" class="text-gray-200">0</span> KRW</div>
    </header>

    <main class="flex-1 flex overflow-hidden p-1 space-x-1">
        
        <div class="flex-1 flex flex-col space-y-1 overflow-hidden min-w-[600px]">
            
            <div class="h-16 bg-panel flex items-center px-4 shrink-0">
                <div class="flex items-center gap-2">
                    <img src="https://static.upbit.com/logos/BTC.png" class="w-6 h-6 rounded-full">
                    <h2 class="text-xl font-bold text-white">비트코인 <span class="text-xs text-gray-500 font-normal">BTC/KRW</span></h2>
                </div>
                <div class="ml-6 flex flex-col">
                    <span id="main-price" class="text-2xl font-bold up-red num-font">99,000,000</span>
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
                        "autosize": true,
                        "symbol": "UPBIT:BTCKRW",
                        "interval": "15",
                        "timezone": "Asia/Seoul",
                        "theme": "dark",
                        "style": "1",
                        "locale": "kr",
                        "enable_publishing": false,
                        "backgroundColor": "#12161f",
                        "hide_top_toolbar": false,
                        "save_image": false,
                        "container_id": "tradingview_chart"
                    });
                    </script>
                </div>
            </div>

            <div class="flex-[2] bg-panel flex">
                <div class="w-1/2 border-r border-line flex flex-col">
                    <div class="text-center text-xs py-1 border-b border-line text-gray-400 font-bold">일반호가</div>
                    <div class="flex-1 flex flex-col text-[11px] num-font p-1" id="orderbook">
                        </div>
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
            <div class="flex text-sm border-b border-line">
                <div class="flex-1 text-center py-2 tab-inactive text-red-500" onclick="switchOrderTab('buy')">매수</div>
                <div class="flex-1 text-center py-2 tab-inactive text-blue-500" onclick="switchOrderTab('sell')">매도</div>
                <div class="flex-1 text-center py-2 tab-active bg-gray-800" onclick="switchOrderTab('history')" id="tab-history">거래내역 (AI)</div>
            </div>
            
            <div class="flex-1 flex flex-col overflow-hidden" id="panel-history">
                <div class="flex text-[11px] text-gray-400 border-b border-line py-1.5 px-2 text-center bg-[#0b1016]">
                    <div class="w-1/5">시간</div>
                    <div class="w-1/4">AI명</div>
                    <div class="w-1/5">종류</div>
                    <div class="w-1/3 text-right">체결가격</div>
                </div>
                <div id="trade-history-list" class="flex-1 overflow-y-auto text-[11px] num-font divide-y divide-[#2b303b]">
                    </div>
                
                <div class="p-2 border-t border-line">
                    <div class="bg-yellow-900/20 border border-yellow-700 p-2 rounded text-xs text-yellow-500 text-center">
                        모든 내역은 <b>ai_trade_log.csv</b>에 자동 저장됩니다.
                    </div>
                </div>
            </div>
        </div>

        <div class="w-[320px] flex flex-col bg-panel shrink-0">
            <div class="p-2 border-b border-line">
                <input type="text" placeholder="코인명/심볼 검색" class="w-full bg-[#0b1016] border border-line text-white text-xs px-2 py-1.5 outline-none focus:border-gray-500">
            </div>
            <div class="flex text-xs font-bold border-b border-line">
                <div class="flex-1 text-center py-1.5 border-b-2 border-white text-white">원화</div>
                <div class="flex-1 text-center py-1.5 text-gray-500">BTC</div>
                <div class="flex-1 text-center py-1.5 text-gray-500">USDT</div>
                <div class="flex-1 text-center py-1.5 text-gray-500">보유</div>
            </div>
            
            <div class="flex text-[10px] text-gray-400 py-1.5 px-2 border-b border-line">
                <div class="flex-[2]">한글명</div>
                <div class="flex-[1.5] text-right">현재가</div>
                <div class="flex-[1.5] text-right">전일대비</div>
            </div>
            
            <div id="coin-list" class="flex-1 overflow-y-auto">
                <div class="text-center text-xs text-gray-500 py-10 animate-pulse">데이터 로딩중...</div>
            </div>
        </div>
    </main>

    <script>
        // 호가창(Orderbook) 가짜 생성 로직
        function generateOrderbook(basePrice) {
            let html = "";
            let p = basePrice + 5000;
            // 매도(파랑) 5칸
            for(let i=0; i<5; i++) {
                html += `<div class="flex justify-between bg-down-blue px-2 py-0.5 mb-[1px]">
                    <span class="down-blue">${p.toLocaleString()}</span>
                    <span class="text-gray-400">${(Math.random()*2).toFixed(3)}</span>
                </div>`;
                p -= 1000;
            }
            // 현재가
            html += `<div class="flex justify-between bg-gray-800 border border-gray-600 px-2 py-1 my-1">
                <span class="up-red font-bold text-xs">${basePrice.toLocaleString()}</span>
                <span class="text-gray-200">${(Math.random()*5).toFixed(3)}</span>
            </div>`;
            // 매수(빨강) 5칸
            p = basePrice - 1000;
            for(let i=0; i<5; i++) {
                html += `<div class="flex justify-between bg-up-red px-2 py-0.5 mt-[1px]">
                    <span class="up-red">${p.toLocaleString()}</span>
                    <span class="text-gray-400">${(Math.random()*2).toFixed(3)}</span>
                </div>`;
                p -= 1000;
            }
            document.getElementById('orderbook').innerHTML = html;
        }

        // AI 로그 자동 생성
        const msgs = [
            "[추세추종 잼] BTC 15분봉 골든크로스 접근 중.",
            "[스캘핑 잼] 알트코인 변동성 확대, 타점 대기.",
            "[방패 잼] 포트폴리오 밸런스 정상. 리스크 12%.",
            "[스나이퍼 잼] 호가창 매수벽 붕괴 감지. 관망.",
            "[고래 잼] 대형 지갑 이동 포착 완료."
        ];
        setInterval(() => {
            const box = document.getElementById('ai-analysis');
            const el = document.createElement('div');
            el.innerText = msgs[Math.floor(Math.random() * msgs.length)];
            box.appendChild(el);
            if(box.childNodes.length > 20) box.removeChild(box.firstChild);
            box.scrollTop = box.scrollHeight;
        }, 4000);

        // WebSocket 연결 및 UI 업데이트
        const ws = new WebSocket("ws://" + window.location.host + "/ws");
        ws.onmessage = function(event) {
            const response = JSON.parse(event.data);
            document.getElementById('usdt-rate').innerText = Math.round(response.usdt_rate).toLocaleString();

            let listHtml = "";
            let btcPrice = 0;

            // 1. 우측 코인 리스트 렌더링
            response.data.forEach(coin => {
                const colorClass = coin.rate >= 0 ? 'up-red' : 'down-blue';
                const sign = coin.rate >= 0 ? '+' : '';
                
                if(coin.code === 'BTC') {
                    btcPrice = Math.round(coin.cur_price_krw);
                    document.getElementById('main-price').innerText = btcPrice.toLocaleString();
                    document.getElementById('main-rate').innerText = `전일대비 ${sign}${coin.rate.toFixed(2)}%`;
                    document.getElementById('main-rate').className = `text-xs font-bold num-font ${colorClass}`;
                    document.getElementById('main-price').className = `text-2xl font-bold num-font ${colorClass}`;
                }

                listHtml += `
                <div class="flex text-[11px] py-1.5 px-2 border-b border-[#1b2029] hover:bg-[#1b2029] cursor-pointer items-center">
                    <div class="flex-[2] flex flex-col">
                        <span class="font-bold text-gray-200">${coin.name}</span>
                        <span class="text-[9px] text-gray-500">${coin.code}/KRW</span>
                    </div>
                    <div class="flex-[1.5] text-right font-bold num-font ${colorClass}">${Math.round(coin.cur_price_krw).toLocaleString()}</div>
                    <div class="flex-[1.5] text-right flex flex-col items-end">
                        <span class="${colorClass} num-font">${sign}${coin.rate.toFixed(2)}%</span>
                    </div>
                </div>`;
            });
            document.getElementById('coin-list').innerHTML = listHtml;
            
            // 호가창 업데이트
            if(btcPrice > 0) generateOrderbook(btcPrice);

            // 2. 중앙 패널 거래내역 (AI 히스토리) 렌더링
            if(response.history) {
                let histHtml = "";
                response.history.forEach(h => {
                    const hColor = h.side === '매수' ? 'up-red' : 'down-blue';
                    const aiColor = {
                        "스캘핑 잼": "text-blue-400",
                        "추세추종 잼": "text-yellow-400",
                        "방패 잼": "text-green-400",
                        "스나이퍼 잼": "text-purple-400",
                        "고래 잼": "text-pink-400"
                    }[h.ai] || "text-gray-400";

                    histHtml += `
                    <div class="flex py-1.5 px-2 items-center hover:bg-gray-800 transition">
                        <div class="w-1/5 text-gray-500">${h.time}</div>
                        <div class="w-1/4 font-bold ${aiColor}">${h.ai}</div>
                        <div class="w-1/5 ${hColor} font-bold text-[10px]">${h.coin} ${h.side}</div>
                        <div class="w-1/3 text-right font-bold ${hColor}">${h.price.toLocaleString()}</div>
                    </div>`;
                });
                document.getElementById('trade-history-list').innerHTML = histHtml;
            }
        };
        
        function switchOrderTab(tab) {
            alert('현재 버전은 [AI 자동매매] 전용 모드입니다. 거래내역 탭만 활성화됩니다.');
        }
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
        print(f"✅ V3 적용 완료: {path}")

    print("\n🎉 [업비트 클론 PRO & 5대잼 트레이딩] 설치 완료!")
    print("--------------------------------------------------")
    print(f"1. 명령 프롬프트 열기 -> cd {TARGET_PATH}")
    print("2. 실행: python main.py")
    print("3. 브라우저 접속: http://127.0.0.1:8000")
    print("4. [AI 거래내역] 확인 및 PC의 ai_trade_log.csv 파일 확인")
    print("--------------------------------------------------")

if __name__ == "__main__":
    install()