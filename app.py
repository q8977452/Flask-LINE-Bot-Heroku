import os
from datetime import datetime

from flask import Flask, abort, request
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, LocationMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


def sendText():
    try:
        message = [
            TextSendMessage(
                text="還沒撰寫說明唷!\n 開發者LineId:perplexed"
            ),
            StickerSendMessage(
                package_id='1',
                sticker_id='2'
            )
        ]
        return message
    except:
        return TextSendMessage(text='發生錯誤！\n聯絡我感恩!')


def sendMovie():
    def get_date(date_str):
        # e.g. "上映日期：2017-03-23" -> match.group(0): "2017-03-23"
        pattern = '\d+-\d+-\d+'
        match = re.search(pattern, date_str)
        if match is None:
            return date_str
        else:
            return match.group(0)

    Yahoo_MOVIE_URL = 'https://tw.movies.yahoo.com/movie_thisweek.html'

    # 以下網址後面加上 "/id=MOVIE_ID" 即為該影片各項資訊
    Yahoo_INTRO_URL = 'https://tw.movies.yahoo.com/movieinfo_main.html'  # 詳細資訊
    Yahoo_PHOTO_URL = 'https://tw.movies.yahoo.com/movieinfo_photos.html'  # 劇照
    Yahoo_TIME_URL = 'https://tw.movies.yahoo.com/movietime_result.html'  # 時刻表

    resp = requests.get(Yahoo_MOVIE_URL)

    try:
        if resp.status_code != 200:
            message = TextSendMessage(
                text="網站改版拉告知我!!!"
            )
        else:
            dom = resp.text
            soup = BeautifulSoup(dom, 'html5lib')
            movies = list()
            rows = soup.find_all('div', 'release_info_text')
            for row in rows[0:5]:
                movie = list()
                # 評價
                movie.append(row.find('div', 'leveltext').span.text.strip())
                # 片名
                movie.append(row.find('div', 'release_movie_name').a.text.strip())
                # 電影照片
                movie.append(row.parent.find_previous_sibling('div', 'release_foto').a.img['src'])
                # 上映日期
                movie.append(get_date(row.find('div', 'release_movie_time').text))

                trailer_a = row.find_next_sibling('div', 'release_btn color_btnbox').find_all('a')[1]
                # 電影網址
                movie.append(trailer_a['href'] if 'href' in trailer_a.attrs.keys() else '')

                movies.append(movie)
            message = TemplateSendMessage(
                alt_text="電影多頁訊息",
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url=movies[0][2],
                            title="片名:" + movies[0][1],
                            text="網友期待度:" + movies[0][0] + "\n\n上映日期:" + movies[0][3],
                            actions=[

                                URITemplateAction(
                                    label='電影預告',
                                    uri=movies[0][4]
                                ),

                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url=movies[1][2],
                            title="片名:" + movies[1][1],
                            text="網友期待度:" + movies[1][0] + "\n\n上映日期:" + movies[1][3],
                            actions=[
                                URITemplateAction(
                                    label='電影預告',
                                    uri=movies[1][4]
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url=movies[2][2],
                            title="片名:" + movies[2][1],
                            text="網友期待度:" + movies[2][0] + "\n\n上映日期:" + movies[2][3],
                            actions=[
                                URITemplateAction(
                                    label='電影預告',
                                    uri=movies[2][4]
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url=movies[3][2],
                            title="片名:" + movies[3][1],
                            text="網友期待度:" + movies[3][0] + "\n\n上映日期:" + movies[3][3],
                            actions=[
                                URITemplateAction(
                                    label='電影預告',
                                    uri=movies[3][4]
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url=movies[4][2],
                            title="片名:" + movies[4][1],
                            text="網友期待度:" + movies[4][0] + "\n\n上映日期:" + movies[4][3],
                            actions=[
                                URITemplateAction(
                                    label='電影預告',
                                    uri=movies[4][4]
                                )
                            ]
                        ),

                    ]
                )
            )
        return message
    except:
        return TextSendMessage(text='發生錯誤！\n聯絡我感恩!')


def sendBeautyImg():  # 傳送表特版美女或恐龍圖

    def get_web_page(url):  # 取得網頁
        resp = requests.get(
            url=url,
            cookies={'over18': '1'}
        )
        if resp.status_code != 200:
            return None
        else:
            return resp.text

    def get_articles(dom):  # 取得當頁有超連結文章
        soup = BeautifulSoup(dom, 'html5lib')

        articles = list()  # 儲存取得的文章資料
        divs = soup.find_all('div', 'r-ent')
        for d in divs:
            # 取得文章連結及標題
            if d.find('a'):  # 有超連結，表示文章存在，未被刪除
                href = d.find('a')['href']
                articles.append(href)
        return articles

    PTT_URL = 'https://www.ptt.cc'

    current_page = get_web_page(PTT_URL + '/bbs/Beauty/index.html')

    articles = get_articles(current_page)

    imgs = list()

    for article in articles:
        page = get_web_page(PTT_URL + article)
        soup = BeautifulSoup(page, 'html.parser')
        links = soup.find(id='main-content').find_all('a')
        img_urls = list()
        for link in links:  # 正規搜尋法尋找圖片網址
            if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
                img_urls.append(link['href'])
                imgs.append(img_urls)

    # 一維陣列亂數
    imgs_One_dimensionalSum = int(len(imgs))
    One_dimensionalRandom = random.randint(0, imgs_One_dimensionalSum - 1)
    # 二維陣列亂數
    imgs_Two_dimensionalSum = int(len(imgs[One_dimensionalRandom]))
    Two_dimensionalRandom = random.randint(0, imgs_Two_dimensionalSum - 1)
    try:
        message = ImageSendMessage(  # 傳送圖片
            original_content_url=imgs[One_dimensionalRandom][Two_dimensionalRandom],
            preview_image_url=imgs[One_dimensionalRandom][Two_dimensionalRandom]
        )
        return message
    except:
        return TextSendMessage(text='發生錯誤！\n聯絡我感恩!')


def sendRestaurant(event):  # 傳送附近餐廳
    # 地址
    # userAddress = event.message.address
    # 緯度
    latitude = event.message.latitude
    # 經度
    longitude = event.message.longitude

    # googlePlace_url = "https://www.google.com.tw/maps/place/"

    google_apikey = "&key=" + "你的api"

    Nearby_search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(
        latitude) + ',' + str(longitude) + " &radius=1500&type=restaurant" + google_apikey

    pictureApi = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=500&photoreference='

    restaurantData = requests.get(Nearby_search_url).json()

    allRestaurantList = list()
    for item in restaurantData['results'][0:5]:
        RestaurantList = list()
        # 名子0
        RestaurantList.append(item['name'])
        # 地址1
        RestaurantList.append(item['vicinity'])
        # 緯度2
        RestaurantList.append(str(item['geometry']['location']['lat']))
        # 經度3
        RestaurantList.append(str(item['geometry']['location']['lng']))
        # 評價4
        RestaurantList.append(str(item['rating']))
        # 是否營業5
        RestaurantList.append(str(item['opening_hours']['open_now']))
        # 總留言數6
        RestaurantList.append(str(item['user_ratings_total']))
        # 相片網址7
        RestaurantList.append(pictureApi + item['photos'][0]['photo_reference'] + google_apikey)
        allRestaurantList.append(RestaurantList)
    try:
        message = TemplateSendMessage(
            alt_text="餐廳多頁訊息",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=allRestaurantList[0][7],
                        title="餐廳:" + allRestaurantList[0][0],
                        text="Google評價:" + allRestaurantList[0][4] + "\n營業中:" + allRestaurantList[0][5] + "\n總評論數" +
                             allRestaurantList[0][6],
                        actions=[

                            URITemplateAction(
                                label='出發',
                                uri="https://www.google.com/maps/search/?api=1&query=" + allRestaurantList[0][2] + "," +
                                    allRestaurantList[0][3]
                            ),

                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=allRestaurantList[1][7],
                        title="餐廳:" + allRestaurantList[1][0],
                        text="Google評價:" + allRestaurantList[1][4] + "\n營業中:" + allRestaurantList[1][5] + "\n總評論數" +
                             allRestaurantList[1][6],
                        actions=[

                            URITemplateAction(
                                label='出發',
                                uri="https://www.google.com/maps/search/?api=1&query=" + allRestaurantList[1][2] + "," +
                                    allRestaurantList[1][3]
                            ),

                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=allRestaurantList[2][7],
                        title="餐廳:" + allRestaurantList[2][0],
                        text="Google評價:" + allRestaurantList[2][4] + "\n營業中:" + allRestaurantList[2][5] + "\n總評論數" +
                             allRestaurantList[2][6],
                        actions=[
                            URITemplateAction(
                                label='出發',
                                uri="https://www.google.com/maps/search/?api=1&query=" + allRestaurantList[2][2] + "," +
                                    allRestaurantList[2][3]
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=allRestaurantList[3][7],
                        title="餐廳:" + allRestaurantList[3][0],
                        text="Google評價:" + allRestaurantList[3][4] + "\n營業中:" + allRestaurantList[3][5] + "\n總評論數" +
                             allRestaurantList[3][6],
                        actions=[
                            URITemplateAction(
                                label='出發',
                                uri="https://www.google.com/maps/search/?api=1&query=" + allRestaurantList[3][2] + "," +
                                    allRestaurantList[3][3]
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=allRestaurantList[4][7],
                        title="餐廳:" + allRestaurantList[4][0],
                        text="Google評價:" + allRestaurantList[4][4] + "\n營業中:" + allRestaurantList[4][5] + "\n總評論數" +
                             allRestaurantList[4][6],
                        actions=[
                            URITemplateAction(
                                label='出發',
                                uri="https://www.google.com/maps/search/?api=1&query=" + allRestaurantList[4][2] + "," +
                                    allRestaurantList[4][3]
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='挖勒發生錯誤！\n聯絡我感恩!'))


@app.route("/", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message_text(event):
    get_message = event.message.text
    if get_message == "使用說明":
        reply = sendText()
    elif get_message == "最新電影":
        reply = sendMovie()
    elif get_message == "抽":
        reply = sendBeautyImg()
    else:
        reply = TextSendMessage(text=f"{get_message}")

    line_bot_api.reply_message(event.reply_token, reply)


## 沒有google api><"
@handler.add(MessageEvent, message=LocationMessage)
def handle_message_location(event):
    sendRestaurant(event)
