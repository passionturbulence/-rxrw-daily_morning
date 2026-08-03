from datetime import datetime
import os
import sys

import requests
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage


today = datetime.now()
second_date = "2025-08-29"

start_date = os.environ.get("START_DATE", "")
city = os.environ.get("CITY", "")
app_id = os.environ.get("APP_ID", "")
app_secret = os.environ.get("APP_SECRET", "")
user_id = os.environ.get("USER_ID", "")
template_id = os.environ.get("TEMPLATE_ID", "")


def check_environment():
    print("🔍 检查环境变量...")
    required = [
        ("START_DATE", start_date),
        ("CITY", city),
        ("APP_ID", app_id),
        ("APP_SECRET", app_secret),
        ("USER_ID", user_id),
        ("TEMPLATE_ID", template_id),
    ]

    missing = []
    for name, value in required:
        if value:
            print(f"✅ {name} 已配置")
        else:
            print(f"❌ {name} 未配置")
            missing.append(name)

    if missing:
        print(f"\n❌ 缺少环境变量：{', '.join(missing)}")
        sys.exit(1)


def get_lunar_birthday_12_16():
    birthday_by_year = {
        2025: datetime(2026, 1, 25),
        2026: datetime(2027, 1, 25),
        2027: datetime(2028, 1, 12),
    }

    next_birthday = birthday_by_year.get(today.year)
    if next_birthday is None:
        print("⚠️ 当前年份没有配置腊月十六日期，暂按 365 天处理")
        return 365

    return max(0, (next_birthday - today).days)


WEATHER_NAMES = {
    0: "晴",
    1: "大部晴朗",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "毛毛雨",
    55: "较强毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "小阵雨",
    81: "阵雨",
    82: "强阵雨",
    95: "雷雨",
    96: "雷雨伴冰雹",
    99: "强雷雨伴冰雹",
}


def get_weather(city_name):
    date_text = datetime.now().strftime("%Y年%m月%d日")

    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city_name,
                "count": 1,
                "language": "zh",
                "format": "json",
            },
            timeout=15,
        )
        geo_response.raise_for_status()
        locations = geo_response.json().get("results", [])
        if not locations:
            raise ValueError(f"找不到城市：{city_name}")

        latitude = locations[0]["latitude"]
        longitude = locations[0]["longitude"]

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,apparent_temperature,weather_code",
                "timezone": "Asia/Shanghai",
            },
            timeout=15,
        )
        weather_response.raise_for_status()
        current = weather_response.json()["current"]

        weather_code = int(current["weather_code"])
        weather = WEATHER_NAMES.get(weather_code, "未知")
        temperature = str(round(float(current["temperature_2m"])))
        apparent_temperature = round(float(current["apparent_temperature"]))
        tips = f"体感温度 {apparent_temperature}℃，记得根据天气增减衣物"

        return weather, temperature, date_text, tips
    except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
        print(f"⚠️ 天气获取失败：{exc}")
        return "未知", "20", date_text, "天气暂时获取失败，记得开心"


def get_days(date_text):
    try:
        target_date = datetime.strptime(date_text, "%Y-%m-%d")
        return (today - target_date).days
    except ValueError:
        print(f"⚠️ 日期格式错误：{date_text}")
        return 0


def get_words():
    fallback = "平安喜乐，万事胜意"

    try:
        response = requests.get(
            "https://v1.hitokoto.cn/",
            params={"encode": "json", "max_length": 30},
            timeout=10,
        )
        response.raise_for_status()
        words = response.json().get("hitokoto", fallback).strip()
        if not words:
            return fallback
        return words if len(words) <= 30 else words[:29] + "…"
    except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
        print(f"⚠️ 每日一句获取失败：{exc}")
        return fallback


def main():
    check_environment()
    print("\n🚀 开始推送微信消息...")

    weather, temperature, date_text, tips = get_weather(city)
    words = get_words()

    data = {
        "date": {"value": date_text},
        "weather": {"value": weather},
        "temperature": {"value": f"{temperature}℃"},
        "tips": {"value": tips},
        "love_days": {"value": get_days(start_date)},
        "second_days": {"value": get_days(second_date)},
        "birthday_left": {"value": get_lunar_birthday_12_16()},
        "words": {"value": words, "color": "#ff69b4"},
    }

    print("\n" + "=" * 50)
    print("📱 即将发送到微信的内容如下：")
    print("=" * 50)
    print(f"📅 日期：{data['date']['value']}")
    print(f"☁️ 天气：{data['weather']['value']}")
    print(f"🌡 温度：{data['temperature']['value']}")
    print(f"💡 提示：{data['tips']['value']}")
    print(f"💑 相恋天数：{data['love_days']['value']} 天")
    print(f"🎯 第二个纪念日：{data['second_days']['value']} 天")
    print(f"🎂 下一个农历生日还有：{data['birthday_left']['value']} 天")
    print(f"💌 每日一句（{len(words)} 字）：{words}")
    print("=" * 50 + "\n")

    client = WeChatClient(app_id, app_secret)
    message = WeChatMessage(client)
    result = message.send_template(user_id, template_id, data)
    print(f"✅ 发送成功！结果：{result}")


if __name__ == "__main__":
    main()
