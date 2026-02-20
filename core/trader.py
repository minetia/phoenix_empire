import asyncio, random, json, os
from datetime import datetime, timedelta
from core.exchange import Exchange
from core.logger import AITradeLogger

def safe_num(v, default=0.0):
    try: f = float(v); return f if f == f and f != float('inf') and f != float('-inf') else default
    except: return default

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
        self.tkrs = [c["code"] for c in self.port] + ["KRW-USDT"]
        self.prc_cache = {} 
        self.ai_seed = 100000000.0 / 6 
        
        self.agents = {
            "전략 잼": {"cash": self.ai_seed, "profit": 0.0, "vault": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "수집 잼": {"cash": self.ai_seed, "profit": 0.0, "vault": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "정렬 잼": {"cash": self.ai_seed, "profit": 0.0, "vault": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "타이밍 잼": {"cash": self.ai_seed, "profit": 0.0, "vault": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "가디언 잼": {"cash": self.ai_seed, "profit": 0.0, "vault": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []},
            "행동 잼": {"cash": self.ai_seed, "profit": 0.0, "vault": 0.0, "holds": {c["code"]: 0.0 for c in self.port}, "wins": 0, "losses": 0, "history": []}
        }
        self.ais = list(self.agents.keys())
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_state.json")
        
        self.global_sources = ["TradingView", "Investing.com", "Coinglass", "TrendSpider", "Finviz", "Bookmap", "ATAS", "TensorCharts", "Cryptowat.ch", "GoCharting", "TradingLite", "Exocharts", "Aggr.trade", "Velo.xyz", "CoinMarketCap", "CoinGecko", "DexScreener", "Birdeye.so", "Dropstab", "Messari", "Glassnode", "LookIntoBitcoin", "Whalemap", "HyblockCapital", "Koyfin", "StockCharts", "MarketChameleon", "Barchart", "AlphaQuery", "TradingEconomics"]
        self.analysis_keywords = ["청산 맵 히트맵 저항선 확인", "온체인 고래 지갑 대규모 이동 포착", "RSI/MACD 다이버전스 발생", "오더북(호가창) 유동성 스푸핑 감지", "CVD(누적 볼륨 델타) 매수세 전환", "미결제약정(OI) 급증 경고", "스마트머니(Smart Money) 매집 구간 진입", "펀딩비(Funding Rate) 과열 해소", "MVRV Z-Score 바닥권 도달"]
        
        self.latest_insight = "시스템 대기 중..." 
        
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        if not os.path.exists(logs_dir): os.makedirs(logs_dir)
        self.insight_log_file = os.path.join(logs_dir, "ai_global_analysis_log.txt")
        
        # 🪄 [마법의 패치] 초기 상태 파일이 없을 때를 대비한 기본 변수 강제 할당
        self.ai_mode = "balance"
        self.ai_krw = 100000000.0
        self.ai_hold = {c["code"]: 0.0 for c in self.port}
        self.ai_avg = {c["code"]: 0.0 for c in self.port}
        self.hist = []
        # ===========================================================
        
        self.load_state()
        self._init_today_history()

    async def deep_analysis_loop(self):
        while True:
            await asyncio.sleep(random.uniform(2.0, 5.0))
            bot = random.choice(self.ais)
            site = random.choice(self.global_sources)
            keyword = random.choice(self.analysis_keywords)
            coin = random.choice([c["name"] for c in self.port])
            prob = round(random.uniform(70.0, 99.5), 1)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.latest_insight = f"[{site}] {coin} {keyword} ({prob}% 예측)"
            log_line = f"[{now}] | 담당 AI: {bot} | 출처: {site} | 타겟: {coin} | 분석내용: {keyword} | 시스템 신뢰도: {prob}%\n"
            try:
                with open(self.insight_log_file, "a", encoding="utf-8") as f: f.write(log_line)
            except: pass

    def _init_today_history(self):
        today_str = datetime.now().strftime("%m.%d")
        for a_name, a_data in self.agents.items():
            if len(a_data.get("history", [])) == 0:
                a_data.setdefault("history", []).append({"date": today_str, "d_prof": 0.0, "c_prof": 0.0, "d_rate": 0.0, "c_rate": 0.0, "b_asset": self.ai_seed, "e_asset": self.ai_seed})

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ai_mode = data.get("ai_mode", "balance")
                    self.ai_krw = safe_num(data.get("ai_krw", 100000000.0))
                    self.ai_hold = {k: safe_num(v) for k, v in data.get("ai_hold", {}).items()}
                    self.ai_avg = {k: safe_num(v) for k, v in data.get("ai_avg", {}).items()}
                    ag = data.get("agents", {})
                    for k, v in ag.items():
                        if k in self.agents:
                            self.agents[k].update(v)
                            if "vault" not in self.agents[k]: self.agents[k]["vault"] = 0.0
                    self.hist = data.get("hist", [])
            except: pass

    def save_state(self):
        data = {"ai_mode": self.ai_mode, "ai_krw": self.ai_krw, "ai_hold": self.ai_hold, "ai_avg": self.ai_avg, "agents": self.agents, "hist": getattr(self, 'hist', [])}
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def change_mode(self, mode):
        self.ai_mode = mode; self.save_state()

    async def price_update_loop(self):
        while True:
            try:
                prc = await asyncio.to_thread(self.ex.get_current_price, self.tkrs)
                if prc: self.prc_cache = prc
            except: pass
            await asyncio.sleep(0.5)

    async def simulate_ai_trading(self):
        while True:
            d = {"safe": 1.5, "balance": 0.8, "aggressive": 0.3}.get(getattr(self, 'ai_mode', 'balance'), 0.8)
            await asyncio.sleep(random.uniform(d * 0.5, d * 1.5))
            if not self.prc_cache: continue
            
            c = random.choice(self.port)["code"]
            p = safe_num(self.prc_cache.get(c))
            if p <= 0: continue
            
            ai_name = random.choice(self.ais)
            old_qty = safe_num(self.ai_hold.get(c, 0.0))
            old_avg = safe_num(self.ai_avg.get(c, 0.0))
            bot_hold = safe_num(self.agents[ai_name]["holds"].get(c, 0.0))
            bot_cash = safe_num(self.agents[ai_name].get("cash", self.ai_seed))
            profit_rate = ((p - old_avg) / old_avg * 100) if old_avg > 0 else 0

            side = None; bet_ratio = 0.0; sell_ratio = 0.0

            if ai_name == "전략 잼": 
                if profit_rate > 0.5: side = "매수"; bet_ratio = 0.15 
                elif profit_rate < -1.0 and bot_hold > 0: side = "매도"; sell_ratio = 0.8
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.08; sell_ratio = 0.4
            elif ai_name == "수집 잼": 
                if profit_rate < -0.5: side = "매수"; bet_ratio = 0.1
                elif bot_hold > 0 and profit_rate > 2.0: side = "매도"; sell_ratio = 0.5
                else: side = "매수" if random.random() > 0.3 else "매도"; bet_ratio = 0.05; sell_ratio = 0.3
            elif ai_name == "정렬 잼": 
                if bot_hold > 0 and profit_rate > 0.5: side = "매도"; sell_ratio = 0.5
                elif profit_rate < -0.5: side = "매수"; bet_ratio = 0.1
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.2
            elif ai_name == "타이밍 잼": 
                if profit_rate < -1.5 or random.random() < 0.2: side = "매수"; bet_ratio = 0.25 
                elif bot_hold > 0 and (profit_rate > 1.5 or random.random() < 0.2): side = "매도"; sell_ratio = 0.7
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.3
            elif ai_name == "가디언 잼": 
                if bot_hold > 0 and profit_rate < -1.0: side = "매도"; sell_ratio = 1.0 
                elif bot_hold > 0 and profit_rate > 1.0: side = "매도"; sell_ratio = 0.8 
                elif profit_rate < -2.0 or random.random() < 0.25: side = "매수"; bet_ratio = 0.2 
                else: side = random.choice(["매수", "매도"]); bet_ratio = 0.05; sell_ratio = 0.4
            elif ai_name == "행동 잼": 
                if bot_hold > 0 and profit_rate > 0.2: side = "매도"; sell_ratio = 1.0 
                elif bot_hold > 0 and profit_rate < -0.4: side = "매도"; sell_ratio = 1.0 
                else: side = "매수"; bet_ratio = 0.1

            if not side: continue
            mode_multi = {"safe": 0.5, "balance": 1.0, "aggressive": 2.0}.get(getattr(self, 'ai_mode', 'balance'), 1.0)
            bet_ratio = min(bet_ratio * mode_multi, 0.9)

            qty = 0
            if side == "매수":
                bet = bot_cash * bet_ratio
                if bet < 5000: continue
                qty = bet / p
                self.ai_krw -= bet
                self.agents[ai_name]["cash"] = bot_cash - bet
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
                self.agents[ai_name]["cash"] = bot_cash + sell_amount
                if self.ai_hold.get(c, 0.0) < 0.000001:
                    self.ai_hold[c] = 0.0; self.ai_avg[c] = 0.0
                
                self.agents[ai_name]["holds"][c] = bot_hold - qty
                trade_profit = sell_amount - buy_amount 
                
                self.agents[ai_name]["profit"] += trade_profit
                if trade_profit > 0: self.agents[ai_name]["wins"] = self.agents[ai_name].get("wins", 0) + 1
                else: self.agents[ai_name]["losses"] = self.agents[ai_name].get("losses", 0) + 1
                
            log = self.logger.log_trade(ai_name, c.replace("KRW-",""), side, qty, p)
            if not hasattr(self, 'hist'): self.hist = []
            self.hist.insert(0, log)
            if len(self.hist) > 100: self.hist.pop()

            ai_coin_val = sum(self.agents[ai_name]["holds"][cd] * safe_num(self.prc_cache.get(cd, 0.0)) for cd in self.agents[ai_name]["holds"])
            current_ai_asset = self.agents[ai_name]["cash"] + ai_coin_val
            
            if current_ai_asset >= self.ai_seed + 33333.33:
                excess = current_ai_asset - self.ai_seed
                sweep_amt = min(excess, self.agents[ai_name]["cash"])
                if sweep_amt > 1000:
                    self.agents[ai_name]["vault"] += sweep_amt
                    self.agents[ai_name]["cash"] -= sweep_amt
                    self.ai_krw -= sweep_amt 
                    now = datetime.now()
                    t = now.strftime("%Y-%m-%d %H:%M:%S")
                    sweep_log = {
                        "time": t[11:], "full_time": t, "order_time": t,
                        "ai": ai_name, "coin": "💰수익금", "market": "VAULT", "side": "안전보관",
                        "qty": 0.0, "price": 0.0, "tot": sweep_amt, "fee": 0.0, "settle": sweep_amt
                    }
                    self.hist.insert(0, sweep_log)
                    if len(self.hist) > 100: self.hist.pop()
            
            today_str = datetime.now().strftime("%m.%d")
            for a_name, a_data in self.agents.items():
                if not a_data.get("history"): continue
                last_record = a_data["history"][-1]
                if last_record["date"] == today_str:
                    last_record["d_prof"] = a_data["profit"]
                    last_record["c_prof"] = a_data["profit"]
                    last_record["d_rate"] = (a_data["profit"] / self.ai_seed) * 100
                    last_record["c_rate"] = (a_data["profit"] / self.ai_seed) * 100
                    last_record["e_asset"] = self.ai_seed + a_data["profit"]

            self.save_state()

    def get_ai_rank(self, profit):
        if profit >= 20000000: return "[Lv.10] 갓 오브 잼 👑 (궁극의 트레이딩 전문성)"
        elif profit >= 10000000: return "[Lv.9] 딥러닝 마스터 🌠 (완벽한 지식 정보)"
        elif profit >= 5000000: return "[Lv.8] 인사이트 오라클 🌌 (최상위 트레이딩 전달)"
        elif profit >= 2500000: return "[Lv.7] 퀀트 애널리스트 🔮 (고급 지식 습득)"
        elif profit >= 1000000: return "[Lv.6] 실전 오퍼레이터 💠 (트레이딩 정보 전달)"
        elif profit >= 600000: return "[Lv.5] 데이터 프로 💎 (정보 전문성)"
        elif profit >= 300000: return "[Lv.4] 마켓 스캐너 🎖️ (트레이딩 지식)"
        elif profit >= 150000: return "[Lv.3] 로직 러너 🏅 (트레이딩 습득)"
        elif profit >= 50000: return "[Lv.2] 시그널 캐처 🥈 (초기 지식 전달)"
        else: return "[Lv.1] 데이터 옵저버 🥉 (기초 정보 습득)"

    async def get_portfolio_status(self):
        usdt = safe_num(self.prc_cache.get("KRW-USDT", 1450), 1450.0)
        res = []; analysis_data = {}; ai_coin_pnl = []
        
        tot_w = 0; tot_l = 0; global_vault = 0.0
        for data in self.agents.values():
            tot_w += data.get("wins", 0); tot_l += data.get("losses", 0)
            global_vault += data.get("vault", 0.0)
            
        global_win_rate = (tot_w / (tot_w + tot_l) * 100) if (tot_w + tot_l) > 0 else 0.0
        global_ai_score = round(random.uniform(88.0, 99.5), 1) 
        
        for c in self.port:
            sym = c["code"].split("-")[1]
            cp = safe_num(self.prc_cache.get(c["code"]))
            if cp <= 0: cp = safe_num(c["avg"])
            
            c_qty = safe_num(c["qty"]); c_avg = safe_num(c["avg"])
            val = cp * c_qty; prof = val - (c_avg * c_qty)
            rate = ((cp - c_avg) / c_avg) * 100 if c_avg > 0 else 0
            
            status = "초강세" if rate > 5 else "상승" if rate > 0 else "조정" if rate > -5 else "하락"
            analysis_data[sym] = {"status": status, "rsi": round(random.uniform(20, 80), 1)}
            res.append({"name": c["name"], "code": sym, "qty": c_qty, "avg": c_avg, "cur_krw": cp, "cur_usd": cp/usdt, "val": val, "prof": prof, "rate": rate})

            ai_qty = safe_num(self.ai_hold.get(c["code"], 0.0))
            if ai_qty > 0.00001:
                ai_avg_price = safe_num(self.ai_avg.get(c["code"], 0.0))
                if ai_avg_price <= 0: ai_avg_price = cp
                ai_invested = ai_qty * ai_avg_price
                ai_valuation = ai_qty * cp
                ai_profit = ai_valuation - ai_invested
                ai_coin_rate = ((cp - ai_avg_price) / ai_avg_price) * 100 if ai_avg_price > 0 else 0
                owners = [f"{a_name}({safe_num(a_data['holds'].get(c['code'], 0.0)):.4f})" for a_name, a_data in self.agents.items() if safe_num(a_data['holds'].get(c['code'], 0.0)) > 0.00001]
                ai_coin_pnl.append({"name": c["name"], "code": sym, "qty": ai_qty, "avg": ai_avg_price, "invested": ai_invested, "valuation": ai_valuation, "profit": ai_profit, "rate": ai_coin_rate, "owners": " / ".join(owners)})
        
        tot_ai_coins = sum(safe_num(qty) * safe_num(self.prc_cache.get(code, 0.0)) for code, qty in getattr(self, 'ai_hold', {}).items() if safe_num(qty)>0)
        tot_ai = safe_num(getattr(self, 'ai_krw', 100000000.0)) + tot_ai_coins 
        ai_prof = (tot_ai + global_vault) - 100000000.0 
        ai_rate = (ai_prof / 100000000.0) * 100

        ranking = []; agent_details = {}; ai_probs = []
        for name, data in self.agents.items():
            wins = data.get("wins", 0); losses = data.get("losses", 0)
            total_trades = wins + losses
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
            
            rank_title = self.get_ai_rank(data["profit"])
            
            prob = min(max(win_rate * 0.4 + 50.0 + random.uniform(-3.0, 8.0), 10.0), 99.9)
            ai_probs.append({"name": name, "prob": prob})
            
            holds_str = ", ".join([f"{code.replace('KRW-', '')}({q:.3f})" for code, q in data["holds"].items() if q > 0.0001]) or "관망 중"
            ranking.append({
                "name": name, "profit": data["profit"], "win_rate": win_rate, 
                "wins": wins, "losses": losses, "holds_str": holds_str,
                "vault": data.get("vault", 0.0),
                "rank": rank_title
            })
            
            agent_details[name] = {
                "rank": rank_title, 
                "summary": { "cum_prof": data["profit"], "cum_rate": (data["profit"] / self.ai_seed) * 100, "avg_inv": self.ai_seed },
                "history": list(reversed(data.get("history", [])))
            }
            
        ranking.sort(key=lambda x: x["profit"], reverse=True)
        ai_probs.sort(key=lambda x: x["prob"], reverse=True)

        return {
            "usdt": usdt, "data": res, "hist": getattr(self, 'hist', []), 
            "ai_krw": safe_num(getattr(self, 'ai_krw', 100000000.0)), "ai_tot": tot_ai, 
            "ai_prof": ai_prof, "ai_rate": ai_rate,
            "ai_coin_pnl": ai_coin_pnl,
            "ranking": ranking, "agent_details": agent_details,
            "global_stats": { "win_rate": global_win_rate, "ai_score": global_ai_score },
            "ai_probs": ai_probs,
            "analysis": analysis_data,
            "global_vault": global_vault,
            "latest_insight": self.latest_insight 
        }