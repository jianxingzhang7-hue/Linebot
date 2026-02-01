import os
import yfinance as yf
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 讀取 LINE 密鑰
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
user_id = os.getenv('LINE_USER_ID')
line_bot_api = LineBotApi(channel_access_token)

def check_market_status():
    """ 檢查大盤是否在 5 週均線之上 (M：市場走勢) """
    try:
        market = yf.download("^TWII", period="6mo", interval="1wk", progress=False)
        current_index = market['Close'].iloc[-1]
        ma5_week = market['Close'].rolling(5).mean().iloc[-1]
        return current_index > ma5_week, current_index, ma5_week
    except:
        return True, 0, 0

def ashin_strategy(ticker):
    """ Ashin 流派核心選股邏輯 """
    try:
        stock_id = f"{ticker}.TW"
        df = yf.download(stock_id, period="3mo", progress=False)
        if df.empty or len(df) < 25: return None

        # 1. 技術面：均線多頭排列 (Y欄)
        price = df['Close'].iloc[-1]
        ma5 = df['Close'].rolling(5).mean().iloc[-1]
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma24 = df['Close'].rolling(24).mean().iloc[-1]
        is_aligned = (ma5 > ma10) and (ma10 > ma24)

        # 2. 乖離率控制 (X欄)：股價距 MA24 < 15%
        bias_24 = (price - ma24) / ma24
        is_safe_bias = 0 < bias_24 < 0.15

        # 3. 流動性過濾：近 5 日平均成交金額 >= 1000 萬
        # 成交金額 = 成交量 * 收盤價
        df['Amount'] = df['Volume'] * df['Close']
        avg_amount_5d = df['Amount'].tail(5).mean()
        is_liquid = avg_amount_5d >= 10000000 

        if is_aligned and is_safe_bias and is_liquid:
            return {
                "symbol": ticker, "price": price, 
                "bias": bias_24 * 100, "amount": avg_amount_5d / 10000
            }
        return None
    except:
        return None

def main():
    # 擴大掃描範圍 (0050 + 0051 部分成分股)
    watchlist = [
        '2330', '2317', '2454', '2308', '2303', '2881', '3711', '2882', '2886', '2891',
        '3231', '2382', '2603', '2609', '2615', '3017', '1513', '1519', '1503', '1514',
        '2376', '2383', '3037', '3035', '3443', '6235', '1605', '1608', '1609'
    ]
    
    # A. 檢查大盤狀態
    market_ok, m_price, m_ma5w = check_market_status()
    market_msg = "✅ 大盤處於安全區" if market_ok else "⚠️ 大盤跌破5週線，請縮小部位"
    
    # B. 執行選股
    picked = []
    for t in watchlist:
        res = ashin_strategy(t)
        if res:
            picked.append(f"🔥 {res['symbol']}\n現價: {res['price']:.1f}\n乖離: {res['bias']:.1f}%\n均量: {res['amount']:.0f}萬")

    # C. 組合與發送訊息
    final_report = f"📊 【Ashin流派選股報告】\n{market_msg}\n{'-'*15}\n"
    if picked:
        final_report += "\n\n".join(picked)
    else:
        final_report += "今日暫無符合「多頭+低乖離+量足」之標的。"

    line_bot_api.push_message(user_id, TextSendMessage(text=final_report))

if __name__ == "__main__":
    main()
