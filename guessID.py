import time
import re
import psutil
import os
import threading
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

thread_count = 12
disable_memory = False

def is_valid_id_number(id_number):
    """校验身份证号码"""
    if len(id_number) != 18:
        return False
    if not re.match(r'^\d{17}[\dXx]$', id_number):
        return False
    
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    id_remainders = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    total = sum(int(id_number[i]) * factors[i] for i in range(17))
    check_code = id_remainders[total % 11]
    return check_code == id_number[17].upper()

def get_gender(id_number):
    """根据第17位判断性别"""
    gender_digit = id_number[16]
    if gender_digit.isdigit():
        return "男" if int(gender_digit) % 2 == 1 else "女"
    return "未知"

def get_memory_usage():
    while not disable_memory:
        memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        print(f'>>> 内存使用: {memory:.2f} MB', end='\r')
        time.sleep(0.8)

def generate_tails(tail_str):
    stars = tail_str.count('*')
    if stars == 0:
        return [tail_str]
    
    results = []
    last_is_star = tail_str[-1] == '*'
    digit_stars = stars - 1 if last_is_star else stars
    
    for i in range(10 ** digit_stars):
        s = f"{i:0{digit_stars}d}" if digit_stars > 0 else ""
        temp = tail_str
        for char in s:
            temp = temp.replace('*', char, 1)
        
        if last_is_star:
            for d in range(10):
                results.append(temp.replace('*', str(d), 1))
            results.append(temp.replace('*', 'X', 1))
        else:
            results.append(temp)
    return results

def get_valid_days(month, year):
    month = int(month)
    if month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        return 28
    return 31

# ==================== 加载最新城市代码（带本地备用） ====================
def load_city_codes():
    print(">>> 正在从网络获取最新行政区划代码...")
    city_dict = {}
    cities = []
    
    # 优先尝试网络
    try:
        url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/areas.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        areas = json.loads(response.text)
        
        cities = [item['code'] for item in areas if item.get('code') and len(item['code']) == 6]
        city_dict = {item['code']: item.get('name', '未知') for item in areas if item.get('code') and len(item['code']) == 6}
        
        print(f">>> 成功从网络加载 {len(cities)} 个最新城市代码")
        return cities, city_dict
    except Exception as e:
        print(f">>> 网络获取失败: {e}")
        print(">>> 尝试使用本地 areas.json 文件...")
    
    # 网络失败时使用本地文件
    try:
        if os.path.exists('areas.json'):
            with open('areas.json', 'r', encoding='utf-8') as f:
                areas = json.load(f)
            
            cities = [item['code'] for item in areas if item.get('code') and len(item['code']) == 6]
            city_dict = {item['code']: item.get('name', '未知') for item in areas if item.get('code') and len(item['code']) == 6}
            
            print(f">>> 成功从本地 areas.json 加载 {len(cities)} 个城市代码")
            return cities, city_dict
        else:
            print(">>> 错误：本地 areas.json 文件不存在")
            print(">>> 请下载 https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/areas.json 并保存到当前目录")
            exit()
    except Exception as e:
        print(f">>> 本地加载也失败: {e}")
        exit()

# ==================== 主程序 ====================
id_input = input("请输入身份证号码，用星号 (*) 替代未知数字：").strip().upper()

if len(id_input) != 18 or id_input.count('*') == 0:
    print(">>> 请输入18位身份证，并至少包含1个星号")
    exit()

# 性别筛选
print("\n>>> 性别筛选选项：")
print("1. 全部（男+女）")
print("2. 仅男性")
print("3. 仅女性")
gender_choice = input("请输入选项 (1/2/3)：").strip()

if gender_choice == '2':
    target_gender = "男"
elif gender_choice == '3':
    target_gender = "女"
else:
    target_gender = None

# 加载城市代码
cities, city_name_dict = load_city_codes()

city_code = id_input[0:6]
birth_year = id_input[6:10]
birth_month = id_input[10:12]
birth_day = id_input[12:14]
tail = id_input[14:18]

print(f'>>> 城市代码: {city_code}')

# 输出城市名称
city_name = city_name_dict.get(city_code, "未知地区")
print(f'>>> 城市名称: {city_name}')

print(f'>>> 出生年份: {birth_year}')
print(f'>>> 出生月份: {birth_month}')
print(f'>>> 出生日期: {birth_day}')
print(f'>>> 顺序号: {tail}')

# 有效城市代码
city_pattern = city_code.replace('*', r'\d')
valid_cities = [c for c in cities if re.match(f"^{city_pattern}$", c)]
if not valid_cities:
    print(">>> 错误：没有匹配的城市代码")
    exit()

# 出生年份、月份处理
current_year = datetime.now().year
if birth_year == '****':
    birth_year_options = list(range(1949, current_year - 8))
else:
    pattern = birth_year.replace('*', r'\d')
    birth_year_options = [y for y in range(1949, current_year) if re.match(f"^{pattern}$", str(y))]

if birth_month == '**':
    birth_month_options = [f"{m:02d}" for m in range(1, 13)]
elif '*' in birth_month:
    birth_month_options = [f"{m:02d}" for m in range(1, 13) if re.match(f"^{birth_month.replace('*', '.')}$", f"{m:02d}")]
else:
    birth_month_options = [birth_month]

tail_options = generate_tails(tail)

# 精确估算
days_estimate = 1 if birth_day != '**' and '*' not in birth_day else 15
estimated = len(valid_cities) * len(birth_year_options) * len(birth_month_options) * days_estimate * len(tail_options)
print(f'>>> 将生成约 {estimated:,} 条候选')

# ==================== 多线程校验 ====================
valid_ids = []
lock = threading.Lock()

def verify_worker(city, year, month):
    local = []
    max_day = get_valid_days(month, year)
    day_pattern = birth_day.replace('*', '.')
    
    for day in range(1, max_day + 1):
        day_str = f"{day:02d}"
        if birth_day != '**' and not re.match(f"^{day_pattern}$", day_str):
            continue
        for tail_opt in tail_options:
            id_num = city + str(year) + month + day_str + tail_opt
            if is_valid_id_number(id_num):
                if target_gender is None or get_gender(id_num) == target_gender:
                    local.append(id_num)
    return local

# 启动内存监控
disable_memory = False
threading.Thread(target=get_memory_usage, daemon=True).start()

start_time = time.time()
print(">>> 开始验证，请耐心等待...")

with ThreadPoolExecutor(max_workers=thread_count) as executor:
    futures = []
    for city in valid_cities:
        for year in birth_year_options:
            for month in birth_month_options:
                futures.append(executor.submit(verify_worker, city, year, month))
    
    for future in as_completed(futures):
        result = future.result()
        if result:
            with lock:
                valid_ids.extend(result)

disable_memory = True
print(f"\n>>> 完成！耗时: {time.time() - start_time:.2f} 秒")
print(f">>> 找到有效身份证数量: {len(valid_ids)}")

if valid_ids:
    with open('resultID.txt', 'a', encoding='utf-8') as f:
        f.write('\n'.join(valid_ids) + '\n')
    
    print(">>> 结果已保存到 resultID.txt")
    print("\n=== 最终结果（含性别）===")
    for vid in valid_ids:
        gender = get_gender(vid)
        print(f"{vid}  →  {gender}")
else:
    print(">>> 未找到符合条件的有效身份证")
