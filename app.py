import os
from flask import Flask
from linebot import LineBotApi, WebhookParser
# 這裡請確保導入了你原本用來發送股票報告的函數
# 假設你的發送邏輯在 machine 或其他地方，請根據實際情況調整
# 下面以 common_function 為範例

app = Flask(__name__)

# 從環境變數讀取 4 把鑰匙
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
user_id = os.getenv('LINE_USER_ID')
imgur_key = os.getenv('IMGUR_KEY')

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def main_process():
    """這裡放你原本觸發股票報告的程式碼"""
    print("正在執行股票報告發送...")
    # 範例：呼叫你原本產生圖表並傳送的 function
    # push_stock_report(line_bot_api, user_id) 
    print("報告發送完畢！")

if __name__ == "__main__":
    # 在 GitHub Actions 執行時，我們直接執行發送邏輯
    # 而不是跑 app.run()，這樣才不會卡住
    main_process()
