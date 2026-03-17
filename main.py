# 安装依赖 pip3 install requests html5lib bs4 schedule

import time
import os
import requests
import json
import schedule


# 从测试号信息获取
appID = ""
appSecret = ""
# 天气预报模板ID
weather_template_id = ""
# 时间表模板ID
timetable_template_id = ""
open_ids_raw = ""

appID = os.getenv("WECHAT_APP_ID", appID)
appSecret = os.getenv("WECHAT_APP_SECRET", appSecret)
weather_template_id = os.getenv("WECHAT_TEMPLATE_ID", weather_template_id)
open_ids_raw = os.getenv("WECHAT_OPEN_IDS", open_ids_raw)
openIds = [item.strip() for item in open_ids_raw.split(",") if item.strip()]
WEATHER_CITY = os.getenv("WEATHER_CITY", "青岛")


def get_weather(my_city):
    try:
        url = f"http://wttr.in/{my_city}?format=j1&lang=zh"
        resp = requests.get(url)
        data = resp.json()

        current_condition = data['current_condition'][0]
        weather_forecast = data['weather'][0]

        weather_desc = current_condition['lang_zh'][0]['value']

        min_temp = int(weather_forecast['mintempC'])
        max_temp = int(weather_forecast['maxtempC'])

        wind_dir = current_condition['winddir16Point']
        wind_speed = current_condition['windspeedKmph']

        temp_tip = build_temperature_tip(min_temp, max_temp)
        wind_text = f"刮{translate_wind_direction(wind_dir)}，风速{wind_speed}km/h"

        return my_city, temp_tip, weather_desc, wind_text

    except Exception as e:
        print(f"Weather error: {e}")
        return my_city, "未知", "未知", "未知"


def translate_wind_direction(wind_dir):
    direction_map = {
        "N": "北风", "NNE": "东北偏北风", "NE": "东北风", "ENE": "东北偏东风",
        "E": "东风", "ESE": "东南偏东风", "SE": "东南风", "SSE": "东南偏南风",
        "S": "南风", "SSW": "西南偏南风", "SW": "西南风", "WSW": "西南偏西风",
        "W": "西风", "WNW": "西北偏西风", "NW": "西北风", "NNW": "西北偏北风"
    }
    return direction_map.get(wind_dir, wind_dir)


def get_dress_advice(temp):
    if temp >= 30:
        return "短袖短裤，注意防晒"
    if temp >= 25:
        return "短袖为主，早晚可加薄外套"
    if temp >= 20:
        return "长袖或薄外套"
    if temp >= 15:
        return "卫衣或薄针织衫"
    if temp >= 10:
        return "外套+长裤"
    if temp >= 5:
        return "厚外套或轻薄羽绒"
    return "羽绒服+保暖内搭"


def build_temperature_tip(min_temp, max_temp):
    high_advice = get_dress_advice(max_temp)
    low_advice = get_dress_advice(min_temp)
    return f"最高温{max_temp}℃：{high_advice}；最低温{min_temp}℃：{low_advice}"


def get_access_token():
    if not appID.strip() or not appSecret.strip():
        raise ValueError("WECHAT_APP_ID 或 WECHAT_APP_SECRET 未配置")
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


def get_daily_love():
    # 每日一句情话
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love

def send_weather(access_token, weather):
    if not weather_template_id.strip():
        raise ValueError("WECHAT_TEMPLATE_ID 未配置")
    if not openIds:
        raise ValueError("WECHAT_OPEN_IDS 未配置")
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，value就是你要替换DATA的值

    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")

    daily_note_content = get_daily_love()

    for openId in openIds:
        body = {
            "touser": openId.strip(),
            "template_id": weather_template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "date": {
                    "value": today_str
                },
                "region": {
                    "value": weather[0]
                },
                "weather": {
                    "value": weather[2]
                },
                "temp": {
                    "value": weather[1]
                },
                "wind_dir": {
                    "value": weather[3]
                },
                "today_note": {
                    "value": daily_note_content
                }
            }
        }
        print(f"Sending to {openId}: {json.dumps(body, ensure_ascii=False)}")
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(requests.post(url, json.dumps(body)).text)


def send_timetable(access_token, message):
    for openId in openIds:
        body = {
            "touser": openId.strip(),
            "template_id": timetable_template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "message": {
                    "value": message
                },
            }
        }
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(requests.post(url, json.dumps(body)).text)


def weather_report(city):
    # 1.获取access_token
    access_token = get_access_token()
    # 2. 获取天气
    weather = get_weather(city)
    print(f"天气信息： {weather}")
    # 3. 发送消息
    send_weather(access_token, weather)


def timetable(message):
    # 1.获取access_token
    access_token = get_access_token()
    # 3. 发送消息
    send_timetable(access_token, message)


if __name__ == '__main__':
    weather_report(WEATHER_CITY)
    # timetable("第二教学楼十分钟后开始英语课")

    # schedule.every().day.at("18:30").do(weather_report, "南京")
    # schedule.every().monday.at("13:50").do(timetable, "第二教学楼十分钟后开始英语课")
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
