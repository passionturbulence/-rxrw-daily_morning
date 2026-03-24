from datetime import datetime
import os
import random
import requests
from urllib.parse import quote
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
from zhdate import ZhDate

# ===================== 时间 =====================
today = datetime.now()

# ===================== 环境变量 =====================
start_date = os.environ.get('START_DATE', '')
second_date = os.environ.get('SECOND_DATE', '')
city = os.environ.get('CITY', '')
birthday_solar = os.environ.get('BIRTHDAY_SOLAR', '2007-02-03')

app_id = os.environ.get("APP_ID", "")
app_secret = os.environ.get("APP_SECRET", "")
user_id = os.environ.get("USER_ID", "")
template_id = os.environ.get("TEMPLATE_ID", "")

# ===================== 检查环境变量 =====================
print("🔍 检查环境变量...")
required = [
    ("START_DATE", start_date),
    ("SECOND_DATE", second_date),
    ("CITY", city),
    ("BIRTHDAY_SOLAR", birthday_solar),
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

# ===================== 工具函数 =====================
def get_weather(city):
    try:
        encoded_city = quote(city)
        url = f"https://apis.tianapi.com/tianqi/index?key=1267e3290f4f9c5610f868069394d955&city={encoded_city}"
        response = requests.get(url, timeout=10)
        res = response.json()
        if res.get('code') != 200:
            return "未知", "20", datetime.now().strftime("%Y年%m月%d日"), "加油"
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

# ===================== 🔥 农历生日倒计时 =====================
def get_lunar_birthday_remaining(solar_birth_str):
    try:
        solar_birth = datetime.strptime(solar_birth_str, "%Y-%m-%d")
        lunar_birth = ZhDate.from_datetime(solar_birth)
        lunar_month = lunar_birth.month
        lunar_day = lunar_birth.day

        this_year = today.year
        lunar_this = ZhDate(this_year, lunar_month, lunar_day)
        solar_this = lunar_this.to_datetime()

        if solar_this < today:
            lunar_next = ZhDate(this_year + 1, lunar_month, lunar_day)
            solar_next = lunar_next.to_datetime()
        else:
            solar_next = solar_this

        days_left = (solar_next - today).days
        return max(0, days_left - 1)
    except Exception as e:
        print(f"生日计算错误：{e}")
        return 0

# ===================== 主逻辑 =====================
if __name__ == "__main__":
    print("\n🚀 开始推送微信消息...")

    weather, temp, date_str, tips = get_weather(city)
    love_days = get_days(start_date)
    second_days = get_days(second_date)
    birth_left = get_lunar_birthday_remaining(birthday_solar)

    def get_words():
        try:
            r = requests.get("https://api.shadiao.pro/chp", timeout=3)
            if r.status_code == 200:
                return r.json()["data"]["text"]
        except:
            pass
        return "平安喜乐，万事胜意"

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

    try:
        client = WeChatClient(app_id, app_secret)
        wm = WeChatMessage(client)
        res = wm.send_template(user_id, template_id, data)
        print(f"✅ 发送成功！结果：{res}")
    except Exception as e:
        print(f"❌ 发送失败：{str(e)}")
