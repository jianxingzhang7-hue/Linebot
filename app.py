import os
import yfinance as yf
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 讀取你的 4 把鑰匙
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
user_id = os.getenv('LINE_USER_ID')
line_bot_api = LineBotApi(channel_access_token)

def commuter_strategy(ticker):
    try:
        # 1. 下載資料：我們需要至少 40 天的資料來計算 MA24
        # 加上 .TW 是為了台股格式
        stock_id = f"{ticker}.TW" 
        df = yf.download(stock_id, period="2mo", progress=False)
        
        if df.empty or len(df) < 25:
            return None

        # 2. 計算 Excel 裡的均線 (MA5, MA10, MA24)
        # 你的 Excel 截圖 用的是 24日線作為月線
        price = df['Close'].iloc[-1]
        ma5 = df['Close'].rolling(5).mean().iloc[-1]
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma24 = df['Close'].rolling(24).mean().iloc[-1]

        # 3. 執行 Excel 裡的篩選邏輯
        
        # 條件 A (Y欄): 均線多頭排列 (MA5 > MA10 > MA24)
        condition_alignment = (ma5 > ma10) and (ma10 > ma24)
        
        # 條件 B (X欄): 股價距離 MA24 < 15% (避免追高)
        # 計算乖離率: (股價 - MA24) / MA24
        bias_percentage = (price - ma24) / ma24
        condition_bias = bias_percentage < 0.15 and bias_percentage > 0 # 確保是在均線之上

        # 4. 判斷是否符合
        if condition_alignment and condition_bias:
            return {
                "symbol": ticker,
                "price": price,
                "ma5": ma5,
                "ma10": ma10,
                "ma24": ma24,
                "bias": bias_percentage * 100
            }
        else:
            return None

    except Exception as e:
        print(f"Error checking {ticker}: {e}")
        return None

def main():
    # 這裡放入你想觀察的股票清單 (你可以之後把 Excel 的代號整排貼過來)
    # 先幫你放幾支熱門股測試邏輯
    watchlist = ['2330', '2317', '2454', '2303', '2603', '2881', '3231', '2382', '2376', '2383']
    
    results = []
    print("🚀 啟動通勤族 Excel 篩選邏輯...")

    for ticker in watchlist:
        res = commuter_strategy(ticker)
        if res:
            # 格式化輸出，模仿你的 Excel 欄位
            msg = (f"🔥 {res['symbol']} 符合條件！\n"
                   f"股價: {res['price']:.2f}\n"
                   f"✅ MA5({res['ma5']:.1f}) > MA10 > MA24\n"
                   f"✅ 距MA24乖離: {res['bias']:.2f}% (<15%)")
            results.append(msg)
            print(f"抓到股票: {res['symbol']}")

    # 發送結果
    if results:
        final_msg = "📊 【通勤族策略】今日精選：\n\n" + "\n----------------\n".join(results)
    else:
        final_msg = "📉 今日掃描清單中，無股票同時符合「多頭排列」且「乖離<15%」。"

    line_bot_api.push_message(user_id, TextSendMessage(text=final_msg))
    print("✅ 報告已發送")

if __name__ == "__main__":
    main()
