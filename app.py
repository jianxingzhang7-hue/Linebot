import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()

#create img folder
if not os.path.exists("./img"):
    img_folder_path = "./img"
    try:
        os.mkdir(img_folder_path)
    except OSError:
        print ("Creation of the directory %s failed" % img_folder_path)

machine = TocMachine(
    states=["user", "begin","fsm","start","index","search","USA_index","index_search","index_chart","TW_index","TW_history","TW_now","stock_list","stock_now","stock_history","stock_recommend"],
    transitions=[
        {"trigger": "advance","source": ["user","start"],"dest": "begin","conditions": "is_going_to_begin"},
        {"trigger": "advance","source": "begin","dest": "fsm","conditions": "is_going_to_fsm"},
        {"trigger": "advance","source": ["begin","index","index_chart","TW_now","TW_history","search","stock_now","stock_history","stock_recommend"],"dest": "start","conditions": "is_going_to_start"},
        {"trigger": "advance","source": ["start","TW_index","index_search"],"dest": "index","conditions": "is_going_to_index"},
        {"trigger": "advance","source": "index","dest": "USA_index","conditions": "is_going_to_USA_index"},
        {"trigger": "advance","source": ["USA_index","index_chart"],"dest": "index_search","conditions": "is_going_to_index_search"},
        {"trigger": "advance","source": "index_search","dest": "index_chart","conditions": "is_going_to_index_chart"},
        {"trigger": "advance","source": ["index","TW_now","TW_history"],"dest": "TW_index","conditions": "is_going_to_TW_index"},
        {"trigger": "advance","source": "TW_index","dest": "TW_now","conditions": "is_going_to_TW_now"},
        {"trigger": "advance","source": "TW_index","dest": "TW_history","conditions": "is_going_to_TW_history"},
        {"trigger": "advance","source": ["start","stock_list"],"dest": "search","conditions": "is_going_to_search",},
        {"trigger": "advance","source": ["search","stock_now","stock_history","stock_recommend"],"dest": "stock_list","conditions": "is_going_to_stock_list",},
        {"trigger": "advance","source": "stock_list","dest": "stock_now","conditions": "is_going_to_stock_now",},
        {"trigger": "advance","source": "stock_list","dest": "stock_history","conditions": "is_going_to_stock_history",},
        {"trigger": "advance","source": "stock_list","dest": "stock_recommend","conditions": "is_going_to_stock_recommend",},
        #back
        {"trigger": "go_back", "source": ["fsm","start","index","search","USA_index","index_search","index_chart","TW_index","TW_history","TW_now","stock_list","stock_now","stock_history","stock_recommend"], "dest": "begin"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)
machine.get_graph().draw("./img/fsm.png", prog="dot", format="png")

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        
        if machine.state != "fsm":
            response = machine.advance(event)
        else:
            response = False
        print(machine.state)
        if response == False:
            if machine.state == 'search':
                send_text_message(event.reply_token, "股票名稱或代碼不存在請再次輸入\n或輸入『back』返回主選單\n或輸入『menu』返回功能選擇")
            elif machine.state == 'begin':
                send_text_message(event.reply_token, "請依照指示與按鈕來操作!\n或輸入『開始使用』以開始\n或輸入『fsm圖』查看內容")
            elif machine.state != 'user':
                if event.message.text.lower() == 'menu':
                    machine.go_back(event)
                else:
                    send_text_message(event.reply_token, "請依照指示與按鈕來操作!\n或輸入『menu』返回功能選單")
            else:
                send_text_message(event.reply_token, "請輸入『start』開始")

    return "OK"

if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
   if __name__ == "__main__":
    app.run(port=8000) # 這行就是讓 GitHub 轉圈圈的元兇！
