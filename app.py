import os
from flask import Flask
from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage

# 初始化 Flask (雖然 GitHub 不需要它，但保留你的結構)
app = Flask(__name__)

# 從環境變數讀取 4 把鑰匙
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
user_id = os.getenv('LINE_USER_ID')

line_bot_api = LineBotApi(channel_access_token)

def send_test_message():
    """ 這就是你的油門：按下它，訊息就會發出 """
    try:
        print(f"🚀 正在發送訊息給用戶: {user_id}")
        line_bot_api.push_message(
            user_id, 
            TextSendMessage(text='恭喜！GitHub 自動化測試成功！你的股票機器人已經連線了！')
        )
        print("✅ LINE 訊息發送成功！")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    # 這裡就是 GitHub Actions 執行時會跑的地方
    send_test_message()
