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

# 修改点1：添加环境变量默认值防止KeyError
start_date = os.getenv('START_DATE', '2020-01-01')          # 纪念日
city = os.getenv('CITY', '北京')                            # 默认北京
birthday = os.getenv('BIRTHDAY', '01-01')                  # 默认1月1日

app_id = os.getenv("APP_ID")                               # 修改点：这些保持强制要求
app_secret = os.getenv("APP_SECRET")
user_id = os.getenv("USER_ID")
template_id = os.getenv("TEMPLATE_ID")

# 核心功能函数 ==============================================================
def get_weather(city):
    """ 获取天气数据（增加重试机制） """
    try:
        encoded_city = quote(city)
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city={encoded_city}&type=1"
        
        # 修改点4：添加重试机制（最多3次）
        for _ in range(3):
            try:
                response = requests.get(url, timeout=15)
                res = response.json()
                break
            except requests.exceptions.Timeout:
                if _ == 2: raise
                print("请求超时，重试中...")
        
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

        # 修改点3：增强温度解析逻辑
        temp_str = str(result.get('real', '0')).replace('℃', '').strip()
        try:
            temperature = round(float(temp_str.split('/')[0]), 1)  # 处理"25/30℃"格式
        except (ValueError, IndexError):
            temperature = 0.0
            
        return (
            result.get('weather', '未知'),
            temperature,
            result.get('date', datetime.now().strftime("%Y-%m-%d")),
            result.get('tips', '今日无特别提示')
        )
        
    except Exception as e:
        print(f"天气接口异常: {str(e)}")
        return None, None, None, None

def get_days_count():
    """ 计算纪念日天数（无需修改） """
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        delta = today - start_date_obj
        return delta.days
    except Exception as e:
        print(f"纪念日计算错误: {str(e)}")
        return "N/A"

def get_birthday_left():
    """ 修改点2：修复闰年生日问题 """
    try:
        now_year = datetime.now().year
        try:
            next_birthday = datetime.strptime(f"{now_year}-{birthday}", "%Y-%m-%d")
        except ValueError:
            # 处理2月29日情况
            if birthday == "02-29":
                next_birthday = datetime(now_year, 3, 1)
            else:
                raise

        if next_birthday < today:
            try:
                next_birthday = datetime.strptime(f"{now_year+1}-{birthday}", "%Y-%m-%d")
            except ValueError:
                if birthday == "02-29":
                    next_birthday = datetime(now_year+1, 3, 1)
                else:
                    raise

        return (next_birthday - today).days + 1  # 包含当天
    except Exception as e:
        print(f"生日计算错误: {str(e)}")
        return "N/A"

def get_inspiration():
    """ 获取每日鸡汤（增加备用API） """
    try:
        # 修改点：添加备用API
        try:
            resp = requests.get("https://api.shadiao.pro/chp", timeout=5)
            if resp.status_code == 200:
                return resp.json()['data']['text']
        except:
            resp = requests.get("https://v1.hitokoto.cn/")
            if resp.status_code == 200:
                return resp.json()['hitokoto']
        return "每一天都是新的开始～"
    except Exception:
        return "心灵鸡汤正在熬制中..."

# 主程序 ====================================================================
if __name__ == "__main__":
    # 修改点5：关键数据缺失时阻止发送
    essential_data_ok = True
    
    weather, temp, date, tips = get_weather(city)
    if weather is None:
        print("警告：天气数据获取失败，可能影响消息发送")
        essential_data_ok = False
    
    # 强制要求的数据检查
    if not all([app_id, app_secret, user_id, template_id]):
        print("错误：缺少微信配置参数")
        essential_data_ok = False
    
    if essential_data_ok:
        # 构建消息数据
        data = {
            "date": {"value": date or datetime.now().strftime("%Y-%m-%d")},
            "weather": {"value": weather or "未知"},
            "temperature": {"value": f"{temp}℃" if temp is not None else "N/A"},
            "tips": {"value": tips or "今日无特别提示"},
            "love_days": {"value": get_days_count()},
            "birthday_left": {"value": get_birthday_left()},
            "words": {"value": get_inspiration(), "color": get_random_color()}
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
    else:
        print("程序终止：缺少关键数据")
