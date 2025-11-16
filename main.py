from datetime import datetime, date
import math
import os
import random
import requests
from urllib.parse import quote
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

# 环境变量配置 ==============================================================
today = datetime.now()
start_date = os.environ['START_DATE']          # 纪念日，格式：2020-01-01
city = os.environ['CITY']                      # 查询城市，如：北京
birthday = os.environ['BIRTHDAY']              # 生日，格式：01-01

app_id = os.environ["APP_ID"]                  # 微信APP_ID
app_secret = os.environ["APP_SECRET"]          # 微信APP_SECRET
user_id = os.environ["USER_ID"]                # 微信用户ID
template_id = os.environ["TEMPLATE_ID"]        # 消息模板ID

# 核心功能函数 ==============================================================
def get_weather(city):
    """ 获取天气数据 """
    encoded_city = quote(city)
    url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city={encoded_city}&type=1"
    
    response = requests.get(url, timeout=10)
    res = response.json()
    
    result = res['result']
    weather = result['weather']
    temp_str = result['real'].replace('℃', '').strip()
    raw_date = result['date']
    
    # 转换日期格式
    report_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
    tips = result['tips']
    temperature = round(float(temp_str), 1)
    
    return weather, temperature, report_date, tips

def get_days_count():
    """ 计算纪念日天数 """
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    delta = today - start_date_obj
    return delta.days

def get_birthday_left():
    """ 计算生日倒计时 """
    next_birthday = datetime.strptime(f"{datetime.now().year}-{birthday}", "%Y-%m-%d")
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=next_birthday.year + 1)
    return (next_birthday - today).days

def get_inspiration():
    """ 获取每日鸡汤 """
    resp = requests.get("https://api.shadiao.pro/chp", timeout=5)
    return resp.json()['data']['text']

def get_random_color():
    """ 生成随机颜色 """
    return "#%06x" % random.randint(0, 0xFFFFFF)

# 主程序 ====================================================================
if __name__ == "__main__":
    # 获取所有数据
    weather, temp, report_date, tips = get_weather(city)
    days_count = get_days_count()
    birthday_left = get_birthday_left()
    inspiration = get_inspiration()
    
    # 构建消息数据
    data = {
        "date": {"value": report_date},
        "weather": {"value": weather},
        "temperature": {"value": f"{temp}℃"},
        "tips": {"value": tips},
        "love_days": {"value": days_count},
        "birthday_left": {"value": birthday_left},
        "words": {"value": inspiration, "color": get_random_color()}
    }
    
    # 发送微信消息
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)
    res = wm.send_template(user_id, template_id, data)
    print("消息发送成功:", res)
