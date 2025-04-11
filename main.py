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
    try:
        encoded_city = quote(city)
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city={encoded_city}&type=1"
        
        response = requests.get(url, timeout=10)
        res = response.json()
        
        # 调试输出
        print("\n=== 天气API响应 ===")
        print("请求URL:", url)
        print("响应数据:", res)
        print("==================\n")

        if res.get('code') != 200:
            print(f"API错误：{res.get('msg')}")
            return None, None, None, None
            
        result = res.get('result', {})
        if not result:
            print("错误: 天气数据为空")
            return None, None, None, None

        # 解析数据
        weather = result.get('weather', '未知')
        temp_str = result.get('real', '0℃').replace('℃', '').strip()
        report_date = result.get('date', datetime.now().strftime("%Y-%m-%d"))
        tips = result.get('tips', '今日无特别提示')
        
        try:
            temperature = round(float(temp_str), 1)
        except ValueError:
            temperature = 0.0
            
        return weather, temperature, report_date, tips
        
    except Exception as e:
        print(f"天气接口异常: {str(e)}")
        return None, None, None, None

def get_days_count():
    """ 计算纪念日天数 """
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        delta = today - start_date_obj
        return delta.days
    except Exception as e:
        print(f"纪念日计算错误: {str(e)}")
        return "N/A"

def get_birthday_left():
    """ 计算生日倒计时 """
    try:
        next_birthday = datetime.strptime(f"{datetime.now().year}-{birthday}", "%Y-%m-%d")
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=next_birthday.year + 1)
        return (next_birthday - today).days
    except Exception as e:
        print(f"生日计算错误: {str(e)}")
        return "N/A"

def get_inspiration():
    """ 获取每日鸡汤 """
    try:
        resp = requests.get("https://api.shadiao.pro/chp", timeout=5)
        if resp.status_code == 200:
            return resp.json()['data']['text']
        return "每一天都是新的开始～"
    except Exception:
        return "心灵鸡汤正在熬制中..."

def get_random_color():
    """ 生成随机颜色 """
    return "#%06x" % random.randint(0, 0xFFFFFF)

# 主程序 ====================================================================
if __name__ == "__main__":
    # 获取所有数据
    weather, temp, date, tips = get_weather(city)
    days_count = get_days_count()
    birthday_left = get_birthday_left()
    inspiration = get_inspiration()
    
    # 构建消息数据（带容错处理）
    data = {
        "date": {"value": date or datetime.now().strftime("%Y-%m-%d")},
        "weather": {"value": weather or "未知"},
        "temperature": {"value": f"{temp}℃" if temp else "N/A"},
        "tips": {"value": tips or "今日无特别提示"},
        "love_days": {"value": days_count},
        "birthday_left": {"value": birthday_left},
        "words": {"value": inspiration, "color": get_random_color()}
    }
    
    # 发送微信消息
    try:
        client = WeChatClient(app_id, app_secret)
        wm = WeChatMessage(client)
        res = wm.send_template(user_id, template_id, data)
        print("\n=== 微信发送结果 ===")
        print(res)
        print("===================")
    except Exception as e:
        print(f"\n!!! 微信消息发送失败: {str(e)}")

    # 本地调试输出
    print("\n=== 最终发送数据 ===")
    for k, v in data.items():
        print(f"{k}: {v['value']}")
