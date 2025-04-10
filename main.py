from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
from urllib.parse import quote

# 时间相关初始化
today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']  # 从环境变量获取城市
birthday = os.environ['BIRTHDAY']

# 微信凭证
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

def get_weather(city):
    try:
        encoded_city = quote(city)
        # 修正URL使用动态城市参数
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city={encoded_city}&type=1"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        res = response.json()
        print("编码后的城市名:", encoded_city)
        print("API响应数据:", res)

        # 增强数据校验
        if res.get('code') != 200:
            print(f"API错误码：{res.get('code')}, 错误信息：{res.get('msg')}")
            return None, None
            
        weather_data = res.get('data', {}).get('list', [])
        if not weather_data:
            print("错误: 天气数据为空")
            return None, None
            
        current_weather = weather_data[0]
        return current_weather.get('weather'), math.floor(current_weather.get('temp'))
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None, None
    except Exception as e:
        print(f"解析异常: {str(e)}")
        return None, None

def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

def get_birthday():  # 保留唯一正确定义
    next_date = datetime.strptime(f"{date.today().year}-{birthday}", "%Y-%m-%d")
    if next_date < today:
        next_date = next_date.replace(year=next_date.year + 1)
    return (next_date - today).days

def get_words():
    try:
        resp = requests.get("https://api.shadiao.pro/chp", timeout=3)
        return resp.json()['data']['text'] if resp.status_code == 200 else "今日无鸡汤"
    except Exception:
        return "每日一句获取失败"

def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

# 微信客户端初始化
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

# 获取数据（关键修正：传递city参数）
wea, temperature = get_weather(city)  # 使用环境变量中的城市

# 构建消息数据（增加空值保护）
data = {
    "weather": {"value": wea or "未知"},
    "temperature": {"value": temperature or "N/A"},
    "love_days": {"value": get_count()},
    "birthday_left": {"value": get_birthday()},
    "words": {"value": get_words(), "color": get_random_color()}
}

# 发送模板消息
try:
    res = wm.send_template(user_id, template_id, data)
    print("发送结果:", res)
except Exception as e:
    print(f"微信消息发送失败: {str(e)}")
