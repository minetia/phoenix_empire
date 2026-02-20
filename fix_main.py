import os

# main.py 파일만 타겟으로 지정하여 덮어씌웁니다.
TARGET_PATH = r"C:\Users\loves\Project_Phoenix\main.py"
print("🔥 노란색 경고창(DeprecationWarning) 영구 삭제 중...")

main_content = """from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from core.trader import PhoenixTrader
import asyncio, os

trader = PhoenixTrader()

# [수정 완료] 옛날 on_event 방식 대신, 파이썬이 권장하는 최신 lifespan 방식 적용
@asynccontextmanager
async def lifespan(app: FastAPI):
    t1 = asyncio.create_task(trader.price_update_loop())
    t2 = asyncio.create_task(trader.simulate_ai_trading())
    yield
    t1.cancel()
    t2.cancel()

# 최신 방식을 앱에 장착!
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
            pass
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
"""

# 강제 덮어쓰기
with open(TARGET_PATH, "w", encoding="utf-8") as f:
    f.write(main_content)

print("✅ main.py 최신 문법 패치 완료! 이제 실행해도 노란색 경고창이 뜨지 않습니다.")