import random

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
# ===============要使用的回覆模組============== #
from linebot.v3.messaging import(
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    Emoji,
    VideoMessage,
    AudioMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    ReplyMessageRequest,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    URIAction,
    MessageAction,
    ConfirmTemplate,

)
# ================================== #
# =========各種事件的介紹============ #
from linebot.v3.webhooks import(
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessageContent
)
# from linebot.models import (
#     MessageEvent, TextMessage,TextMessageContent, FollowEvent, PostbackEvent
# )
import os

app = Flask(__name__)
PUBLIC_BASE_URL = "https://bot-project-one.vercel.app"


# 建立一個自訂的連線物件
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))    # LINE developers 後台的 secret


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 加入好友事件 > 加入好友會之後會發生的事情
# Follow event 介紹
@line_handler.add(FollowEvent)
def handle_follow(event):
    print(f'Got {event.type} event')


# 餐點清單
food_list = [
    {
        "name": "兩分肥",
        "description": "包手老闆",
        "order_url": "https://line.me/R/ti/p/@711qpheg",
        "thumbnail_file": "兩分肥.jpg"
    },
    {
        "name": "小米食光",
        "description": "還不錯",
        "order_url": "https://line.me/R/ti/p/@823cztgp",
        "thumbnail_file": "小米食光.jpg"
    },
    {
        "name": "蛋白盒子",
        "description": "菜好吃",
        "order_url": "https://order.ocard.co/theproteinbox/w2rZ2w",
        "thumbnail_file": "蛋白盒子.jpg"
    },
    {
        "name": "原初舒食",
        "description": "???",
        "order_url": "https://line.me/R/ti/p/@462bqhuz",
        "thumbnail_file": "原初舒食.jpg"
    }
]

# 記錄上一次推薦的餐點
last_food = None

# 訊息事件
# 第一個參數是呼叫要做這件事，第二個是只接受使用者的文字訊息
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    # 利用上面的連線，創造一個api_client物件
    # 用with 確保有產生物件才會有後續步驟
    with ApiClient(configuration) as api_client:
        # 創造一個物件
        line_bot_api = MessagingApi(api_client)
        # 判斷使用這傳甚麼
        if text in ('吃什麼','?','？','吃甚麼'):

            # 宣告使用外部的變數
            global last_food

            # 排除上一次推薦的餐點
            candidates = [
                food for food in food_list
                if food["name"] != last_food
            ]

            # 隨機挑選餐點
            selected_food = random.choice(candidates)

            # 更新上次推薦的餐點
            last_food = selected_food["name"]

            # 組合圖片網址
            base_url = request.url_root.rstrip("/")
            image_url = f'{base_url}/static/{selected_food["thumbnail_file"]}'

            # 將 http 改為 https
            image_url = image_url.replace("http", "https")

            app.logger.info("圖片網址：" + image_url)

            # 建立 Buttons Template > # 吃甚麼的物件
            what_to_eat = TemplateMessage(
                alt_text=f'今日推薦：{selected_food["name"]}',
                template=ButtonsTemplate(
                    title='🍱 今日午餐推薦',
                    text=(
                        f'{selected_food["name"]}\n'
                        f'{selected_food["description"]}'
                    ),
                    # thumbnail_image_url=image_url,
                    actions=[
                        URIAction(
                            label='前往點餐',
                            uri=selected_food["order_url"]
                        ),
                        MessageAction(
                            label='再推薦一次',
                            text='再一次'
                            # text='吃什麼 # 取消重選
                        )
                    ]
                )
            )


            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    # messages=[TextMessage(text='這是文字訊息')]
                    messages=[
                        what_to_eat
                    ]
                )
            )
        elif text in ('再一次'):
            confirm_template = TemplateMessage(
                alt_text='你確定?',
                template=ConfirmTemplate(
                    text='你真的確定?',
                    actions=[
                        MessageAction(lanel='是', text='yes'),
                        MessageAction(label='否', text='no')
                    ]
                )
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[confirm_template]
                )
            )
        elif text in ('yes','no'):
            image_message = ImageMessage(
                original_content_url="https://bot-project-one.vercel.app/4c56fd34-62e4-438e-a366-294da5fb6bb0.jpg",
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[image_message]
                )
            )
            
        # elif text == '表情符號':
        #     # 相關id可以去Line developers 官方查
        #     emojis = [
        #         Emoji (index=0, product_id="5ac1bfd5040ab15980c9b435", emoji_id="001"),
        #         Emoji(index=12, product_id="5ac1bfd5040ab15980c9b435", emoji_id="002")
        #     ]
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token, 
        #             messages=[TextMessage(text='$ LINE 表情符號$', emojis=emojis)]
        #         )   
        #     )
        # elif text == '貼圖':
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token,
        #             messages=[StickerMessage (package_id="446", sticker_id="1988")]
        #         )
        #     )
        # elif text == '圖片':
        #     url = request.url_root + '/static/Logo.jpg'
        #     url = url.replace("http", "https")
        #     app.logger.info("url=" + url)
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token,
        #             messages=[
        #                 ImageMessage(original_content_url=url, preview_image_url=url)
        #             ]
        #         )
        #     )       
        # elif text == '影片':
        #     url = request.url_root + '/static/video.mp4'
        #     url = url.replace("http", "https")
        #     app.logger.info("url=" + url)
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token,
        #             messages=[
        #                 VideoMessage(original_content_url=url, preview_image_url=url)
        #             ]
        #         )
        #     )
        # elif text == '音訊':
        #     url = request.url_root + 'static/music.mp3'
        #     url = url.replace("http", "https")
        #     app.logger.info("url=" + url)
        #     duration = 60000 # in milliseconds
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token,
        #             messages=[
        #                 AudioMessage(original_content_url=url, duration=duration)
        #             ]
        #         )
        #     )
        # elif text == '位置':
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token,
        #             messages=[
        #                 LocationMessage(title='Location', address="Taipei", latitude=25.0475, longitude=121.5173)
        #             ]
        #         )
        #     )

if __name__ == "__main__":
    app.run()

# https://www.youtube.com/watch?v=Mw3cODdkaFM&list=PLha0eZqN6cEewcDua2P3cYG6-9hnBloe8
# 教材在這