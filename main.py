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
start_date = os.environ['START_DATE']          
city = os.environ['CITY']                      
birthday = os.environ['BIRTHDAY']              

app_id = os.environ["APP_ID"]                  
app_secret = os.environ["APP_SECRET"]          
user_id = os.environ["USER_ID"]                
template_id = os.environ["TEMPLATE_ID"]        

# 核心功能函数 ==============================================================
def get_weather(city):
    """ 获取天气数据 """
    try:
        encoded_city = quote(city)
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city={encoded_city}&type=1"
        
        response = requests.get(url, timeout=10)
        res = response.json()

        if res.get('code') != 200:
            print(f"API错误：{res.get('msg')}")
            return None, None, None, None
            
        result = res.get('result', {})
        if not result:
            print("错误: 天气数据为空")
            return None, None, None, None

        # 修改点1：日期格式转换 --------------------------------------------
        raw_date = result.get('date', datetime.now().strftime("%Y-%m-%d"))
        try:
            report_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
        except:
            report_date = datetime.now().strftime("%Y年%m月%d日")
        # --------------------------------------------------------------

        weather = result.get('weather', '未知')
        temp_str = result.get('real', '0℃').replace('℃', '').strip()
        tips = result.get('tips', '今日无特别提示')
        
        try:
            temperature = round(float(temp_str), 1)
        except ValueError:
            temperature = 0.0
            
        return weather, temperature, report_date, tips
        
    except Exception as e:
        print(f"天气接口异常: {str(e)}")
        return None, None, None, None

# ... 中间保持不变 ...

# 主程序 ====================================================================
if __name__ == "__main__":
    weather, temp, date, tips = get_weather(city)
    days_count = get_days_count()
    birthday_left = get_birthday_left()
    inspiration = get_inspiration()
    
    # 修改点2：默认日期格式调整 --------------------------------------------
    data = {
        "date": {"value": date or datetime.now().strftime("%Y年%m月%d日")},  # 格式修改
        "weather": {"value": weather or "未知"},
        "temperature": {"value": f"{temp}℃" if temp else "N/A"},
        "tips": {"value": tips or "今日无特别提示"},
        "love_days": {"value": days_count},
        "birthday_left": {"value": birthday_left},
        "words": {"value": inspiration, "color": get_random_color()}
    }
    # --------------------------------------------------------------

    # ... 后续保持不变 ...
