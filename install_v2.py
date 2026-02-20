import os

# ==========================================
# [설정] 설치 경로 지정
# ==========================================
TARGET_PATH = r"C:\Users\loves\Project_Phoenix"

print(f"🔥 [Project Phoenix V2] 잼 5대장 AI 엔진 탑재를 시작합니다.")
print(f"📂 설치 경로: {TARGET_PATH}")

files = {}

# 1. 의존성 (라이브러리)
files["requirements.txt"] = """fastapi
uvicorn
jinja2
python-dotenv
pyupbit
pandas
websockets
"""

# 2. 환경변수
files[".env"] = """UPBIT_ACCESS_KEY=your_access_key
UPBIT_SECRET_KEY=your_secret_key
"""

# 3. 메인 서버 (main.py) - 127.0.0.1 유지 (OKX 지갑 경고 방지)
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 서버 시작: http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
"""

# 4. Core - Trader (Phantom Data 포함)
files["core/__init__.py"] = ""
files["core/exchange.py"] = """import pyupbit
class Exchange:
    def get_current_price(self, tickers):
        try: return pyupbit.get_current_price(tickers)
        except: return {}
"""

files["core/trader.py"] = """import asyncio
from core.exchange import Exchange

class PhoenixTrader:
    def __init__(self):
        self.exchange = Exchange()
        self.portfolio = [
            {"code": "KRW-ZRX",  "name": "제로엑스",   "qty": 39624.9782, "avg": 357.1},
            {"code": "KRW-BTC",  "name": "비트코인",   "qty": 0.020129,   "avg": 139647010},
            {"code": "KRW-ETH",  "name": "이더리움",   "qty": 0.613473,   "avg": 4727629},
            {"code": "KRW-XRP",  "name": "리플",       "qty": 552.0696,   "avg": 2913.0},
            {"code": "KRW-SOL",  "name": "솔라나",     "qty": 6.997309,   "avg": 192965},
            {"code": "KRW-SUI",  "name": "수이",       "qty": 522.1083,   "avg": 2470.3},
            {"code": "KRW-ONDO", "name": "온도",       "qty": 627.0825,   "avg": 478.0}
        ]

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

        return {"type": "update", "usdt_rate": usdt_rate, "data": response_data}
"""

# 5. Templates - Index.html (AI 매매 탭 & 트레이딩뷰 차트 & 잼 5대장 추가)
files["templates/index.html"] = """<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Phoenix AI Trading</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #091020; color: white; font-family: -apple-system, sans-serif; }
        .up-red { color: #c84a31; }
        .down-blue { color: #4aa8d8; }
        .txt-gray { color: #94a3b8; }
        .num-font { font-family: 'Roboto', sans-serif; letter-spacing: -0.5px; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #091020; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
    </style>
</head>
<body class="bg-[#091020] min-h-screen text-white select-none overflow-hidden">
    <div class="fixed top-0 w-full bg-[#091020] z-50 border-b border-gray-800 shadow-lg">
        <div class="flex justify-between items-center p-3">
            <div>
                <h1 class="text-xl font-bold tracking-tight text-yellow-500">🔥 Phoenix</h1>
                <p class="text-[10px] text-gray-400 flex items-center gap-1 mt-0.5">
                    <span>환율:</span><span id="usdt-rate" class="text-yellow-500 num-font">0</span><span>KRW</span>
                </p>
            </div>
            <div class="text-right">
                <p class="text-xs text-gray-400 mb-0.5">총 평가손익</p>
                <p id="total-profit" class="text-lg font-bold num-font">0</p>
            </div>
        </div>
        
        <div class="flex text-sm font-bold border-t border-gray-800 bg-[#091020]">
            <div id="tab-portfolio" onclick="switchTab('portfolio')" class="flex-1 text-center py-2.5 border-b-2 border-white cursor-pointer text-white transition-all">보유자산</div>
            <div id="tab-history" class="flex-1 text-center py-2.5 border-b-2 border-transparent text-gray-500 cursor-not-allowed">거래내역</div>
            <div id="tab-ai" onclick="switchTab('ai')" class="flex-1 text-center py-2.5 border-b-2 border-transparent text-gray-500 cursor-pointer hover:text-yellow-400 transition-all flex items-center justify-center gap-1">
                <span>🤖 AI 자동매매</span>
                <span class="relative flex h-2 w-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span></span>
            </div>
        </div>
    </div>

    <div id="view-portfolio" class="pt-28 pb-10 divide-y divide-gray-800/50 h-screen overflow-y-auto">
        <div id="coin-list">
            <div class="flex flex-col items-center justify-center h-64 text-gray-500 animate-pulse">
                <span class="text-2xl mb-2">📡</span><p>실시간 시세 연결 중...</p>
            </div>
        </div>
    </div>

    <div id="view-ai" class="pt-24 pb-4 px-2 h-screen hidden flex-col">
        <div class="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-2 h-full">
            
            <div class="lg:col-span-2 bg-[#0d1421] border border-gray-800 rounded flex flex-col">
                <div class="p-2 border-b border-gray-800 text-xs font-bold text-gray-300 flex justify-between">
                    <span>📊 비트코인 (BTC/KRW) - 실시간 차트</span>
                    <span class="text-green-400 animate-pulse">● Live</span>
                </div>
                <div class="flex-1 w-full h-full min-h-[300px]" id="tradingview_chart">
                    <div class="tradingview-widget-container" style="height:100%;width:100%">
                      <div id="tradingview_1" style="height:100%;width:100%"></div>
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
                        "backgroundColor": "#0d1421",
                        "hide_top_toolbar": false,
                        "save_image": false,
                        "container_id": "tradingview_1"
                      });
                      </script>
                    </div>
                </div>
            </div>

            <div class="bg-[#0d1421] border border-gray-800 rounded flex flex-col overflow-hidden">
                <div class="p-2 border-b border-gray-800 text-xs font-bold text-gray-300">📈 호가 (주문대기)</div>
                <div class="flex-1 p-1 text-[11px] num-font flex flex-col">
                    <div class="flex-1 flex flex-col justify-end space-y-0.5">
                        <div class="flex justify-between bg-blue-900/20 p-1"><span class="down-blue">99,345,000</span><span class="text-gray-400">0.012</span></div>
                        <div class="flex justify-between bg-blue-900/20 p-1"><span class="down-blue">99,344,000</span><span class="text-gray-400">0.023</span></div>
                        <div class="flex justify-between bg-blue-900/30 p-1"><span class="down-blue">99,342,000</span><span class="text-gray-400">0.255</span></div>
                        <div class="flex justify-between bg-blue-900/50 p-1 border border-blue-800"><span class="down-blue">99,340,000</span><span class="text-gray-200 font-bold">2.239</span></div>
                        <div class="flex justify-between bg-blue-900/20 p-1"><span class="down-blue">99,335,000</span><span class="text-gray-400">0.103</span></div>
                    </div>
                    <div class="py-2 text-center font-bold text-sm bg-gray-800 border-y border-gray-700 my-1">
                        <span id="ai-current-price" class="up-red">99,305,000</span> KRW
                    </div>
                    <div class="flex-1 flex flex-col space-y-0.5">
                        <div class="flex justify-between bg-red-900/20 p-1"><span class="up-red">99,303,000</span><span class="text-gray-400">0.025</span></div>
                        <div class="flex justify-between bg-red-900/30 p-1"><span class="up-red">99,302,000</span><span class="text-gray-400">0.122</span></div>
                        <div class="flex justify-between bg-red-900/20 p-1"><span class="up-red">99,299,000</span><span class="text-gray-400">0.193</span></div>
                        <div class="flex justify-between bg-red-900/50 p-1 border border-red-800"><span class="up-red">99,298,000</span><span class="text-gray-200 font-bold">1.502</span></div>
                        <div class="flex justify-between bg-red-900/20 p-1"><span class="up-red">99,297,000</span><span class="text-gray-400">0.008</span></div>
                    </div>
                </div>
            </div>

            <div class="bg-[#0d1421] border border-yellow-600/50 rounded flex flex-col shadow-[0_0_15px_rgba(234,179,8,0.1)]">
                <div class="p-3 border-b border-yellow-600/30 bg-yellow-900/20 flex justify-between items-center">
                    <span class="text-sm font-bold text-yellow-500">🤖 잼 5대장 AI 엔진</span>
                    <span class="text-[10px] bg-green-600 px-2 py-0.5 rounded-full">가동 중</span>
                </div>
                
                <div class="p-3 text-xs space-y-3">
                    <div class="grid grid-cols-2 gap-2 text-center">
                        <div class="bg-gray-800 p-2 rounded border border-gray-700 hover:border-yellow-500 cursor-pointer">
                            <div class="text-[10px] text-gray-400">제1대장</div>
                            <div class="font-bold text-blue-400">스캘핑 잼</div>
                        </div>
                        <div class="bg-yellow-900/40 p-2 rounded border border-yellow-500 cursor-pointer">
                            <div class="text-[10px] text-yellow-200">제2대장 (Active)</div>
                            <div class="font-bold text-yellow-500">추세추종 잼</div>
                        </div>
                        <div class="bg-gray-800 p-2 rounded border border-gray-700 hover:border-yellow-500 cursor-pointer">
                            <div class="text-[10px] text-gray-400">제3대장</div>
                            <div class="font-bold text-green-400">방패 잼(방어)</div>
                        </div>
                        <div class="bg-gray-800 p-2 rounded border border-gray-700 hover:border-yellow-500 cursor-pointer">
                            <div class="text-[10px] text-gray-400">제4대장</div>
                            <div class="font-bold text-purple-400">스나이퍼 잼</div>
                        </div>
                    </div>

                    <div class="mt-4">
                        <p class="text-[10px] text-gray-400 mb-1">AI 실시간 분석 로그</p>
                        <div class="bg-black p-2 rounded h-32 overflow-y-auto text-[10px] font-mono space-y-1 border border-gray-800" id="ai-logs">
                            <p class="text-yellow-500">[System] 잼 5대장 AI 엔진 초기화 완료.</p>
                            <p class="text-gray-400">[추세추종 잼] BTC 15분봉 이동평균선 정배열 감지.</p>
                            <p class="text-gray-400">[스캘핑 잼] ZRX 매수 타점 분석 중...</p>
                            <p class="text-green-400">[방패 잼] 포트폴리오 리스크 15% 이하 유지 중.</p>
                        </div>
                    </div>

                    <button class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 rounded text-sm mt-2 transition">
                        긴급 정지 (Panic Sell)
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 탭 전환 로직
        function switchTab(tab) {
            const vPort = document.getElementById('view-portfolio');
            const vAi = document.getElementById('view-ai');
            const tPort = document.getElementById('tab-portfolio');
            const tAi = document.getElementById('tab-ai');

            if(tab === 'portfolio') {
                vPort.classList.remove('hidden');
                vAi.classList.add('hidden');
                vAi.classList.remove('flex');
                
                tPort.classList.replace('border-transparent', 'border-white');
                tPort.classList.replace('text-gray-500', 'text-white');
                tAi.classList.replace('border-white', 'border-transparent');
                tAi.classList.replace('text-yellow-400', 'text-gray-500');
            } else if (tab === 'ai') {
                vPort.classList.add('hidden');
                vAi.classList.remove('hidden');
                vAi.classList.add('flex');
                
                tAi.classList.replace('border-transparent', 'border-white');
                tAi.classList.replace('text-gray-500', 'text-yellow-400');
                tPort.classList.replace('border-white', 'border-transparent');
                tPort.classList.replace('text-white', 'text-gray-500');
            }
        }

        // AI 로그 시뮬레이션
        const aiLogs = [
            "[스나이퍼 잼] 호가창 매도벽 2.239 BTC 감지.",
            "[추세추종 잼] RSI 65 도달. 매수 보류.",
            "[방패 잼] XRP 손절 라인 재설정 완료.",
            "[고래 잼] 대규모 자금 이동 포착. 관망 권장.",
            "[스캘핑 잼] SUI 단기 반등 패턴 확인. 1차 진입 준비."
        ];
        
        setInterval(() => {
            const logBox = document.getElementById('ai-logs');
            if(logBox && document.getElementById('view-ai').classList.contains('flex')) {
                const p = document.createElement('p');
                p.className = "text-gray-300";
                p.innerText = aiLogs[Math.floor(Math.random() * aiLogs.length)];
                logBox.appendChild(p);
                logBox.scrollTop = logBox.scrollHeight; // 자동 스크롤
            }
        }, 3500);

        // 데이터 통신 로직
        const ws = new WebSocket("ws://" + window.location.host + "/ws");
        ws.onmessage = function(event) {
            const response = JSON.parse(event.data);
            document.getElementById('usdt-rate').innerText = Math.round(response.usdt_rate).toLocaleString();

            let totalProfit = 0;
            let htmlContent = "";

            response.data.forEach(coin => {
                totalProfit += coin.profit;
                const isProfit = coin.rate >= 0;
                const colorClass = isProfit ? 'up-red' : 'down-blue';
                const sign = isProfit ? '+' : '';
                
                // BTC 가격을 AI 화면에 업데이트
                if(coin.code === 'BTC') {
                    const aiPrice = document.getElementById('ai-current-price');
                    if(aiPrice) {
                        aiPrice.innerText = Math.round(coin.cur_price_krw).toLocaleString();
                        aiPrice.className = colorClass;
                    }
                }
                
                htmlContent += `
                <div class="px-4 py-3 border-b border-gray-800/50 hover:bg-[#111827]">
                    <div class="flex justify-between mb-1">
                        <div><span class="font-bold">${coin.name}</span> <span class="text-[11px] txt-gray">${coin.code}/KRW</span></div>
                        <div class="text-right">
                            <div class="${colorClass} font-bold text-sm num-font">${Math.round(coin.profit).toLocaleString()}</div>
                            <div class="${colorClass} text-xs num-font">${sign}${coin.rate.toFixed(2)}%</div>
                        </div>
                    </div>
                    <div class="flex justify-between text-xs mt-2">
                        <div class="w-1/3"><div class="txt-gray">보유수량</div><div class="num-font">${coin.qty.toLocaleString(undefined, {maximumFractionDigits: 4})}</div></div>
                        <div class="w-1/3 text-center"><div class="txt-gray">매수평균</div><div class="num-font">${Math.round(coin.avg).toLocaleString()}</div></div>
                        <div class="w-1/3 text-right">
                            <div class="txt-gray">현재가</div>
                            <div class="${colorClass} font-bold num-font">${Math.round(coin.cur_price_krw).toLocaleString()}</div>
                            <div class="text-[10px] text-yellow-500">$${coin.cur_price_usd.toFixed(2)}</div>
                        </div>
                    </div>
                </div>`;
            });

            document.getElementById('coin-list').innerHTML = htmlContent;
            
            const totalEl = document.getElementById('total-profit');
            totalEl.innerText = Math.round(totalProfit).toLocaleString() + " KRW";
            totalEl.className = "text-lg font-bold num-font " + (totalProfit >= 0 ? "up-red" : "down-blue");
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
        print(f"✅ V2 적용 완료: {path}")

    print("\n🎉 [잼 5대장 AI 엔진] 설치가 완료되었습니다!")
    print("---------------------------------------")
    print(f"1. 명령 프롬프트 열기 -> cd {TARGET_PATH}")
    print("2. 실행: python main.py")
    print("3. 브라우저 접속: http://127.0.0.1:8000")
    print("4. 상단의 [🤖 AI 자동매매] 탭을 클릭해보세요!")
    print("---------------------------------------")

if __name__ == "__main__":
    install()