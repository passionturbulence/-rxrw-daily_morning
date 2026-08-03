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
qweather_api_key = os.environ.get("QWEATHER_API_KEY", "")
qweather_api_host = os.environ.get("QWEATHER_API_HOST", "").strip().rstrip("/")
tianapi_key = os.environ.get("TIANAPI_KEY", "")


def check_environment():
    print("🔍 检查环境变量...")
    required = [
        ("START_DATE", start_date),
        ("CITY", city),
        ("APP_ID", app_id),
        ("APP_SECRET", app_secret),
        ("USER_ID", user_id),
        ("TEMPLATE_ID", template_id),
        ("QWEATHER_API_KEY", qweather_api_key),
        ("QWEATHER_API_HOST", qweather_api_host),
        ("TIANAPI_KEY", tianapi_key),
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


def qweather_get(path, params):
    response = requests.get(
        f"https://{qweather_api_host}{path}",
        headers={"X-QW-Api-Key": qweather_api_key},
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "200":
        raise ValueError(f"和风天气返回错误码：{payload.get('code')}")
    return payload


def get_weather(city_name):
    date_text = datetime.now().strftime("%Y年%m月%d日")

    try:
        city_payload = qweather_get(
            "/geo/v2/city/lookup",
            {"location": city_name, "range": "cn", "number": 1, "lang": "zh"},
        )
        locations = city_payload.get("location", [])
        if not locations:
            raise ValueError(f"找不到城市：{city_name}")
        location_id = locations[0]["id"]

        now = qweather_get(
            "/v7/weather/now", {"location": location_id, "lang": "zh"}
        )["now"]
        indices = qweather_get(
            "/v7/indices/1d",
            {"type": "3", "location": location_id, "lang": "zh"},
        ).get("daily", [])

        weather = now.get("text", "未知")
        temperature = now.get("temp", "20")
        feels_like = now.get("feelsLike", temperature)
        tips = indices[0].get("text", "") if indices else ""
        if not tips:
            tips = f"体感温度 {feels_like}℃，记得根据天气增减衣物"
        tips = tips.strip()
        if len(tips) > 60:
            tips = tips[:59] + "…"

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
    response = requests.get(
        "https://apis.tianapi.com/saylove/index",
        params={"key": tianapi_key},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 200:
        raise ValueError(payload.get("msg", "天行情话接口返回错误"))

    words = payload.get("result", {}).get("content", "").strip()
    if not words:
        raise ValueError("天行情话接口返回了空内容")
    return words


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
