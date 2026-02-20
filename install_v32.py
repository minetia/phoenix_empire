import os

TARGET_PATH = r"C:\Users\loves\Project_Phoenix\templates\index.html"
print("🔥 [Project Phoenix V32] UI 깨짐 완벽 복구 및 AI 상세 장부 탑재 중...")

# HTML UI 전체 최적화 코드
html_content = """<!DOCTYPE html>
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
        .scrollbar-hide::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="md:h-screen flex flex-col select-none overflow-y-auto md:overflow-hidden bg-[#0b1016]">
    <header class="py-3 md:h-14 md:py-0 bg-panel border-b border-line flex flex-col md:flex-row justify-between items-center px-4 shrink-0 gap-3">
        <div class="flex flex-col md:flex-row items-center w-full md:w-auto gap-3 overflow-hidden">
            <div class="flex items-center cursor-pointer shrink-0" onclick="setTab('trd')">
                <span class="text-2xl md:text-xl mr-1">🦅</span>
                <h1 class="text-2xl md:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-300 tracking-widest italic drop-shadow-md">PHOENIX</h1>
                <span class="text-[10px] text-yellow-500 border border-yellow-500/50 bg-yellow-900/30 px-1.5 py-0.5 rounded ml-2 font-bold tracking-wide">AI CORE V32</span>
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
                <div id="t-hist" class="flex-[1.2] text-center py-3 o-hist whitespace-nowrap text-xs md:text-sm" onclick="setOrd('history')">⚡ AI 체결</div>
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
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-10">
                <div class="min-w-[600px] flex text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016]"><div class="flex-[1.5]">보유코인</div><div class="flex-[1] text-right">보유수량</div><div class="flex-[1] text-right">매수평균가</div><div class="flex-[1] text-right">현재가</div><div class="flex-[1.5] text-right">평가손익 / 수익률</div></div>
                <div id="p-list" class="min-w-[600px] divide-y divide-gray-800"></div>
            </div>

            <h2 class="text-xl md:text-2xl font-bold mt-10 mb-4 text-yellow-500 flex items-center gap-2 border-b border-gray-800 pb-2">🤖 AI 실시간 체결 상세 장부 <span class="text-xs font-normal text-gray-500 ml-2">※ 최근 100건 기록</span></h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full pb-4 mb-10">
                <div class="flex text-[11px] md:text-xs text-gray-400 py-3 px-4 border-b border-gray-800 bg-[#0b1016] min-w-[1050px] font-bold">
                    <div class="w-[12%]">주문시간</div>
                    <div class="w-[12%]">체결시간</div>
                    <div class="w-[12%]">AI / 코인명</div>
                    <div class="w-[8%] text-center">종류</div>
                    <div class="w-[10%] text-right">거래수량</div>
                    <div class="w-[12%] text-right">거래단가</div>
                    <div class="w-[12%] text-right">거래금액</div>
                    <div class="w-[10%] text-right">수수료</div>
                    <div class="w-[12%] text-right">정산금액</div>
                </div>
                <div id="ai-detail-list" class="divide-y divide-gray-800 min-w-[1050px]">
                    <div class="p-10 text-center text-gray-500 animate-pulse">실시간 체결 내역 대기 중...</div>
                </div>
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
                <div id="ai-ranking-list" class="divide-y divide-gray-800 text-xs md:text-sm min-w-[800px]"></div>
            </div>

            <h2 class="text-lg md:text-xl font-bold mt-8 md:mt-10 mb-4 text-white border-b border-gray-800 pb-2">📂 6대잼 전용 코인 장부</h2>
            <div class="bg-panel rounded-lg border border-gray-800 overflow-x-auto w-full mb-10">
                <div class="flex text-xs text-gray-400 py-3 md:py-4 px-4 md:px-6 border-b border-gray-800 bg-[#0b1016] min-w-[600px]">
                    <div class="flex-[1.5] font-bold">코인명 <span class="text-[10px] ml-1 text-gray-500">(소유 AI)</span></div>
                    <div class="flex-[1.5] text-right">AI 총 보유수량<br>평균단가</div>
                    <div class="flex-[1.5] text-right">매수금액<br>현재 평가금액</div>
                    <div class="flex-[1.5] text-right">평가손익<br>수익률</div>
                </div>
                <div id="ai-coin-pnl-list" class="divide-y divide-gray-800 text-xs md:text-sm min-w-[600px]"></div>
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
        
        function setOrd(t) { co=t; ['buy','sell','hist'].forEach(x=>document.getElementById(`t-${x}`).className="flex-1 text-center py-3 t-inact hover:text-gray-300"); document.getElementById(`t-${t==='history'?'hist':t}`).className=`flex-[1.2] text-center py-3 o-${t==='history'?'hist':t} whitespace-nowrap text-xs md:text-sm`; drawH(); }
        
        // [V32 핵심] 상세 내역 장부에 데이터를 예쁘게 그리는 함수 완벽 구현!
        function drawH() { 
            let f=gh; if(co==='buy') f=gh.filter(x=>x.side==='매수'); if(co==='sell') f=gh.filter(x=>x.side==='매도'); 
            
            // 1. 거래소 탭 - 우측 사이드바 간략 내역
            let h=""; 
            f.forEach(x=>{ 
                const c=x.side==='매수'?'up-red':'down-blue'; 
                // AI 이름이 길면 첫 단어만 자르기 (예: "전략 잼 (Strategist)" -> "전략")
                const shortAiName = x.ai.split(' ')[0];
                h+=`<div class="flex py-2 md:py-1.5 px-2 hover:bg-gray-800"><div class="w-1/5 text-gray-500">${x.time}</div><div class="w-1/4 font-bold text-gray-300 truncate text-[10px] md:text-xs">${shortAiName}</div><div class="w-1/5 ${c} font-bold text-[10px] md:text-xs">${x.coin} ${x.side}</div><div class="w-1/3 text-right font-bold ${c}">${sn(x.price).toLocaleString()}</div></div>`;
            }); 
            document.getElementById('h-list').innerHTML=h;

            // 2. 투자내역 탭 - AI 실시간 체결 상세 장부 렌더링
            let adH = "";
            gh.forEach(x => {
                const c = x.side === '매수' ? 'up-red' : 'down-blue'; 
                const bgC = x.side === '매수' ? 'bg-red-900/30 text-red-400' : 'bg-blue-900/30 text-blue-400';
                adH += `<div class="flex py-3 md:py-2 px-4 hover:bg-gray-800 transition text-[11px] md:text-xs min-w-[1050px] items-center border-b border-gray-800">
                    <div class="w-[12%] text-gray-500">${x.order_time}</div>
                    <div class="w-[12%] text-gray-300 font-bold">${x.full_time}</div>
                    <div class="w-[12%] flex flex-col"><span class="text-yellow-500 font-bold text-[10px] truncate pr-2">${x.ai}</span><span class="font-bold text-white">${x.coin}(${x.market})</span></div>
                    <div class="w-[8%] font-bold text-center ${bgC} rounded p-1">${x.side}</div>
                    <div class="w-[10%] text-right num-font">${sn(x.qty).toFixed(4)}</div>
                    <div class="w-[12%] text-right num-font">${sn(x.price).toLocaleString()}</div>
                    <div class="w-[12%] text-right num-font">${sn(x.tot).toLocaleString()}</div>
                    <div class="w-[10%] text-right num-font text-gray-500">${sn(x.fee).toLocaleString()}</div>
                    <div class="w-[12%] text-right font-bold num-font ${c}">${sn(x.settle).toLocaleString()}</div>
                </div>`;
            });
            const detailList = document.getElementById('ai-detail-list');
            if(detailList) detailList.innerHTML = adH || '<div class="p-10 text-center text-gray-500">실시간 체결 내역이 없습니다.</div>';
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
                    
                    // V32 픽스: 소켓에서 데이터(r.hist)가 올 때마다 drawH()를 실행하여 상세 장부를 업데이트!
                    if(r.hist){ gh=r.hist; drawH(); } 

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

with open(TARGET_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ V32 UI 깨짐 복구 및 AI 상세 장부 탑재 완료!")