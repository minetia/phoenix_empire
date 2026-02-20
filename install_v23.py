import os
import socket

TARGET_PATH = r"C:\Users\loves\Project_Phoenix"
print("🔥 [Project Phoenix V23] 터미널 렉 제거 및 IP 자동출력 엔진 장착 중...")

files = {}

# 1. Main Server (V23: 터미널 렉 제거 및 IP 자동 안내 기능)
files["main.py"] = """from fastapi import FastAPI, Request, WebSocket
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
        except:
            break
        # 모바일 Wi-Fi 과부하 방지를 위해 화면 업데이트 주기를 1초로 최적화
        await asyncio.sleep(1.0)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    
    print("\\n" + "="*60)
    print("🦅 [Project Phoenix AI Trading] 엔진이 성공적으로 가동되었습니다!")
    print("="*60)
    print(f"💻 [PC 모니터용 주소] 👉 http://127.0.0.1:8000")
    print(f"📱 [스마트폰용 주소] 👉 http://{local_ip}:8000")
    print("="*60)
    print("💡 종료하려면 키보드에서 [Ctrl + C] 를 누르세요.\\n")
    
    # [핵심] access_log=False 를 통해 터미널 수다를 막아 렉(Lag)을 완벽히 제거합니다!
    uvicorn.run("main:app", host="0.0.0.0", port=8000, access_log=False)
"""

# HTML (V23: 모바일 상단 메뉴 글씨 찌그러짐 방지 적용)
html_part1 = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
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
    </style>
</head>
<body class="md:h-screen flex flex-col select-none overflow-y-auto md:overflow-hidden">
    <header class="py-3 md:h-14 md:py-0 bg-panel border-b border-line flex flex-col md:flex-row justify-between items-center px-4 shrink-0 gap-3">
        <div class="flex flex-col md:flex-row items-center w-full md:w-auto gap-3 overflow-hidden">
            <div class="flex items-center cursor-pointer shrink-0" onclick="setTab('trd')">
                <span class="text-2xl md:text-xl mr-1">🦅</span>
                <h1 class="text-2xl md:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-300 tracking-widest italic drop-shadow-md">PHOENIX</h1>
                <span class="text-[10px] text-yellow-500 border border-yellow-500/50 bg-yellow-900/30 px-1.5 py-0.5 rounded ml-2 font-bold tracking-wide">AI CORE</span>
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
                <span class="text-yellow-500 font-bold hidden md:inline">🤖 AI 누적 손익:</span> 
                <span class="text-yellow-500 font-bold md:hidden">AI 손익:</span> 
                <span id="ai-global-prof" class="font-bold text-sm md:text-base num-font text-white">0 KRW (0.00%)</span>
            </div>
        </div>
    </header>
"""

# HTML Part 2, 3은 기존 내용 유지 (글자수 제한 생략, 파일 읽기로 교체 처리)
def read_and_replace():
    html_path = os.path.join(TARGET_PATH, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        full_html = f.read()
    
    # 헤더 부분만 V23 코드로 정밀 교체
    start_idx = full_html.find("<!DOCTYPE html>")
    end_idx = full_html.find("</header>") + 9
    
    new_html = html_part1 + full_html[end_idx:]
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_html)

for path, content in files.items():
    fp = os.path.join(TARGET_PATH, path)
    with open(fp, "w", encoding="utf-8") as f: f.write(content)

read_and_replace()

print("✅ V23 터미널 렉 제거 및 IP 자동화 패치 완료!")