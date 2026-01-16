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

print("\n" + "="*60)
print("GitHub Actions 环境变量诊断")
print("="*60)

# 列出所有环境变量（过滤掉不相关的）
relevant_env_vars = {}
for key, value in os.environ.items():
    if any(secret in key for secret in ['START', 'SECOND', 'CITY', 'BIRTHDAY', 'APP', 'USER', 'TEMPLATE']):
        relevant_env_vars[key] = value

print("相关的环境变量:")
for key, value in relevant_env_vars.items():
    print(f"  {key}: {value}")

# 检查 SECOND_DATE
if 'SECOND_DATE' not in os.environ:
    print("\n❌ 诊断结果: SECOND_DATE 环境变量不存在")
    print("\n可能的原因和解决方案:")
    print("1. GitHub Secrets 中没有设置 SECOND_DATE")
    print("   - 进入仓库 Settings > Secrets and variables > Actions")
    print("   - 点击 New repository secret")
    print("   - 名称: SECOND_DATE, 值: 你的纪念日(YYYY-MM-DD)")
    print("")
    print("2. 工作流文件中没有传递 SECOND_DATE")
    print("   - 检查 .github/workflows/*.yml 文件")
    print("   - 确保有: SECOND_DATE: ${{ secrets.SECOND_DATE }}")
    print("")
    print("3. Secret 名称拼写错误")
    print("   - 确保是 SECOND_DATE 不是 Second_Date 或 second_date")
    exit(1)
else:
    second_date = os.environ['SECOND_DATE']
    print(f"\n✅ SECOND_DATE 环境变量存在: {second_date}")

# 获取其他环境变量
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

print("="*60 + "\n")

# 环境变量配置 ==============================================================
today = datetime.now()

# 安全获取环境变量，提供默认值
start_date = os.environ.get('START_DATE', '2020-01-01')          # 第一个纪念日
second_date = os.environ.get('SECOND_DATE', '2022-01-01')        # 第二个纪念日，如果未设置则使用默认值
city = os.environ.get('CITY', '北京')                            # 查询城市
birthday = os.environ.get('BIRTHDAY', '01-01')                   # 生日

app_id = os.environ.get("APP_ID", "")                            # 微信APP_ID
app_secret = os.environ.get("APP_SECRET", "")                    # 微信APP_SECRET
user_id = os.environ.get("USER_ID", "")                          # 微信用户ID
template_id = os.environ.get("TEMPLATE_ID", "")                  # 消息模板ID

# 详细的调试信息输出
print("\n=== 环境变量详细检查 ===")
print(f"所有环境变量: {dict(os.environ)}")  # 打印所有环境变量
print("\n关键环境变量:")
print(f"START_DATE: {start_date} (类型: {type(start_date)})")
print(f"SECOND_DATE: {second_date} (类型: {type(second_date)})")
print(f"CITY: {city}")
print(f"BIRTHDAY: {birthday}")
print(f"APP_ID: {app_id}")
print(f"APP_SECRET: {app_secret}")
print(f"USER_ID: {user_id}")
print(f"TEMPLATE_ID: {template_id}")
print("===================\n")

# 检查SECOND_DATE是否使用了默认值
if second_date == '2022-01-01':
    print("!!! 警告: SECOND_DATE 使用的是默认值，不是您设置的实际值")
    print("!!! 可能的原因:")
    print("    1. 环境变量名称不正确")
    print("    2. 环境变量没有正确设置")
    print("    3. 环境变量设置后没有重启应用")
else:
    print(f"✓ SECOND_DATE 使用的是您设置的值: {second_date}")
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

        # 解析数据并转换日期格式
        weather = result.get('weather', '未知')
        temp_str = result.get('real', '0℃').replace('℃', '').strip()
        raw_date = result.get('date', '')
        
        # 转换日期格式
        try:
            report_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
        except:
            report_date = datetime.now().strftime("%Y年%m月%d日")
            
        tips = result.get('tips', '今日无特别提示')
        
        try:
            temperature = round(float(temp_str), 1)
        except ValueError:
            temperature = 0.0
            
        return weather, temperature, report_date, tips
        
    except Exception as e:
        print(f"天气接口异常: {str(e)}")
        return None, None, None, None

def get_days_count(date_str, date_name="纪念日"):
    """ 计算纪念日天数 """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        delta = today - date_obj
        return delta.days
    except Exception as e:
        print(f"{date_name}计算错误: {str(e)}")
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
    weather, temp, report_date, tips = get_weather(city)
    days_count = get_days_count-1(start_date, "第一个纪念日")
    second_days_count = get_days_count-1(second_date, "第二个纪念日")
    birthday_left = get_birthday_left()
    inspiration = get_inspiration()
    
    # 构建消息数据（带容错处理）
    data = {
        "date": {"value": report_date or datetime.now().strftime("%Y年%m月%d日")},
        "weather": {"value": weather or "未知"},
        "temperature": {"value": f"{temp}℃" if temp else "N/A"},
        "tips": {"value": tips or "今日无特别提示"},
        "love_days": {"value": days_count},
        "second_days": {"value": second_days_count},  # 第二个纪念日
        "birthday_left": {"value": birthday_left},
        "words": {"value": inspiration, "color": get_random_color()}
    }
    
    # 检查必要的微信配置
    if not app_id or not app_secret or not user_id or not template_id:
        print("!!! 错误: 微信配置不完整，请检查以下环境变量:")
        print(f"    APP_ID: {'已设置' if app_id else '未设置'}")
        print(f"    APP_SECRET: {'已设置' if app_secret else '未设置'}")
        print(f"    USER_ID: {'已设置' if user_id else '未设置'}")
        print(f"    TEMPLATE_ID: {'已设置' if template_id else '未设置'}")
        print("!!! 跳过微信消息发送")
    else:
        # 发送微信消息
        try:
            print("\n=== 尝试连接微信API ===")
            client = WeChatClient(app_id, app_secret)
            
            # 测试获取access token
            print("获取access_token...")
            token = client.access_token
            print(f"access_token获取成功: {token[:20]}...")
            
            wm = WeChatMessage(client)
            print("开始发送模板消息...")
            res = wm.send_template(user_id, template_id, data)
            print("\n=== 微信发送结果 ===")
            print(res)
            print("===================")
        except Exception as e:
            print(f"\n!!! 微信消息发送失败: {str(e)}")
            # 提供更详细的错误信息
            if "40013" in str(e):
                print("!!! 错误详情: APP_ID 无效，请检查:")
                print("    1. APP_ID 是否正确")
                print("    2. APP_ID 和 APP_SECRET 是否匹配")
                print("    3. IP白名单是否配置正确")
                print("    4. 微信公众号平台账号是否正常")

    # 本地调试输出
    print("\n=== 最终发送数据 ===")
    for k, v in data.items():
        print(f"{k}: {v['value']}")
