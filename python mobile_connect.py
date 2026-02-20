import os
import socket

TARGET_PATH = r"C:\Users\loves\Project_Phoenix"
MAIN_FILE = os.path.join(TARGET_PATH, "main.py")

def get_local_ip():
    try:
        # 내 PC의 와이파이 내부 IP 주소를 자동으로 찾아내는 마법
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "IP를 찾을 수 없습니다. (명령 프롬프트에서 ipconfig로 확인 요망)"

print("📱 [Project Phoenix] 모바일 연동 시스템을 구축합니다...")

if os.path.exists(MAIN_FILE):
    with open(MAIN_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 서버를 PC 내부(127.0.0.1) 전용에서 -> 모든 기기 허용(0.0.0.0)으로 변경
    if 'host="127.0.0.1"' in content:
        content = content.replace('host="127.0.0.1"', 'host="0.0.0.0"')
        with open(MAIN_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 핸드폰 외부 접속 허용 완료!")
    elif 'host="0.0.0.0"' in content:
        print("✅ 이미 외부 접속이 허용되어 있습니다.")
else:
    print("❌ main.py 파일을 찾을 수 없습니다. 경로를 확인해주세요.")

local_ip = get_local_ip()

print("\n🎉 모든 설정이 완료되었습니다! 아래 단계에 따라 접속하세요.")
print("==================================================================")
print("1️⃣ (중요) 핸드폰이 PC와 **같은 와이파이(공유기)**에 연결되어 있어야 합니다.")
print("2️⃣ 터미널에서 서버를 다시 실행하세요: python main.py")
print("3️⃣ 핸드폰에서 인터넷(크롬, 사파리, 삼성인터넷 등)을 켜고 주소창에 아래를 입력하세요:")
print(f"\n   👉  http://{local_ip}:8000  👈\n")
print("==================================================================")
print("💡 PC에서 대시보드를 볼 때는 기존처럼 http://127.0.0.1:8000 을 사용하시면")
print("   지갑(OKX)의 피싱 경고창이 뜨지 않습니다.")
print("==================================================================")
