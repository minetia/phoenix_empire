import pyupbit
import asyncio
class Exchange:
    def get_current_price(self, tickers):
        try:
            res = pyupbit.get_current_price(tickers)
            if isinstance(res, dict): return {k: (float(v) if v else 0.0) for k, v in res.items()}
            if isinstance(res, (float, int)): return {tickers[0]: float(res)}
            return {}
        except: return {}
