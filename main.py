from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


import requests
import math
from urllib.parse import quote
from json import JSONDecodeError

import requests
import math
from urllib.parse import quote
from json import JSONDecodeError

def get_weather(city):
    try:
        # 编码城市名
        encoded_city = quote(city)
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city=101070201&type=1=encoded_city"
        
        # 发送请求
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        response = requests.get(api_url)
        data = response.json()
        
        res = response.json()
        print("编码后的城市名:", encoded_city)
        print("API响应数据:", res)
        
        # 检查数据结构
        if 'data' not in res or 'list' not in res['data'] or len(res['data']['list']) == 0:
            print("错误: API数据结构异常")
            return None, None
            
        weather = res['data']['list'][0]
        return weather['weather'], math.floor(weather['temp'])
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None, None
    except JSONDecodeError:
        print("错误: API返回的数据不是有效的JSON格式")
        return None, None
    except KeyError as e:
        print(f"错误: 字段缺失 - {e}")
        return None, None

# 测试调用
weather, temp = get_weather("大连")
print(f"天气: {weather}, 温度: {temp}℃")
def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {"weather":{"value":wea},"temperature":{"value":temperature},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
