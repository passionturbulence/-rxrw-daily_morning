from datetime import datetime, date
import os
import random
import requests
from urllib.parse import quote
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage

# ===================== 时间 =====================
today = datetime.now()

# ===================== 环境变量 =====================
start_date = os.environ.get('START_DATE', '')
second_date = "2025-08-29"  # 👈 只改这里，固定为你要的日期
city = os.environ.get('CITY', '')
app_id = os.environ.get("APP_ID", "")
app_secret = os.environ.get("APP_SECRET", "")
user_id = os.environ.get("USER_ID", "")
template_id = os.environ.get("TEMPLATE_ID", "")

# ===================== 检查环境变量 =====================
print("🔍 检查环境变量...")
required = [
    ("START_DATE", start_date),
    ("CITY", city),
    ("APP_ID", app_id),
    ("APP_SECRET", app_secret),
    ("USER_ID", user_id),
    ("TEMPLATE_ID", template_id)
]

all_ok = True
for name, val in required:
    if not val:
        print(f"❌ {name} 未配置")
        all_ok = False
    else:
        print(f"✅ {name} 已配置")

if not all_ok:
    print("\n❌ 环境变量缺失，程序退出")
    exit(1)

# ===================== 固定农历生日：腊月十六 =====================
def get_lunar_birthday_12_16():
    try:
        lunar_month = 12
        lunar_day = 16

        year = today.year
        if year == 2025:
            next_birth = datetime(2026, 1, 25)
        elif year == 2026:
            next_birth = datetime(2027, 1, 25)
        elif year == 2027:
            next_birth = datetime(2028, 1, 12)
        else:
            next_birth = datetime(year + 1, 1, 25)

        if next_birth < today:
            next_birth = datetime(next_birth.year + 1, next_birth.month, next_birth.day)

        days = (next_birth - today).days
        return max(0, days - 1)
    except:
        return 365

# ===================== 工具函数 =====================
def get_weather(city):
    try:
        encoded_city = quote(city)
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f49c5610f868069394d955&city={encoded_city}"
        response = requests.get(url, timeout=10)
        res = response.json()
        if res.get('code') != 200:
            return "未知", "20", datetime.now().strftime("%Y年%m月%d日"), "开心每一天"
        result = res.get('result', {})
        weather = result.get('weather', '晴')
        temperature = result.get('real', '20').replace('℃', '')
        date_str = result.get('date', datetime.now().strftime("%Y-%m-%d"))
        try:
            date_fmt = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
        except:
            date_fmt = datetime.now().strftime("%Y年%m月%d日")
        tips = result.get('tips', '记得开心')
        return weather, temperature, date_fmt, tips
    except:
        return "未知", "20", datetime.now().strftime("%Y年%m月%d日"), "记得开心"

def get_days(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return (today - d).days
    except:
        return 0

def get_words():
    try:
        r = requests.get("https://api.shadiao.pro/chp", timeout=3)
        if r.status_code == 200:
            return r.json()["data"]["text"]
    except:
        return "平安喜乐，万事胜意"

# ===================== 主逻辑 =====================
if __name__ == "__main__":
    print("\n🚀 开始推送微信消息...")

    weather, temp, date_str, tips = get_weather(city)
    love_days = get_days(start_date)
    second_days = get_days(second_date)
    birth_left = get_lunar_birthday_12_16()
    words = get_words()

    data = {
        "date": {"value": date_str},
        "weather": {"value": weather},
        "temperature": {"value": f"{temp}℃"},
        "tips": {"value": tips},
        "love_days": {"value": love_days},
        "second_days": {"value": second_days},
        "birthday_left": {"value": birth_left},
        "words": {"value": words, "color": "#ff69b4"}
    }

    # ==============================================
    # 输出发送内容
    # ==============================================
    print("\n" + "="*50)
    print("📱 即将发送到微信的内容如下：")
    print("="*50)
    print(f"📅 日期：{data['date']['value']}")
    print(f"☁️ 天气：{data['weather']['value']}")
    print(f"🌡 温度：{data['temperature']['value']}")
    print(f"💡 提示：{data['tips']['value']}")
    print(f"💑 相恋天数：{data['love_days']['value']} 天")
    print(f"🎯 第二个纪念日：{data['second_days']['value']} 天")
    print(f"🎂 下一个农历生日（腊月十六）还有：{data['birthday_left']['value']} 天")
    print(f"💌 每日一句：{data['words']['value']}")
    print("="*50 + "\n")

    # 发送微信
    try:
        client = WeChatClient(app_id, app_secret)
        wm = WeChatMessage(client)
        res = wm.send_template(user_id, template_id, data)
        print(f"✅ 发送成功！结果：{res}")
    except Exception as e:
        print(f"❌ 发送失败：{str(e)}")
