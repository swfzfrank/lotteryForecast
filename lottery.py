import requests
import pandas as pd
import random  # 新增：导入random模块
import time  # 新增：导入time模块

# 新增：定义agent_list
agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def fetch_ssq_data(page_no=1, page_size=30):
    url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
    params = {
        "name": "ssq",
        "pageNo": page_no,
        "pageSize": page_size,
        "systemType": "PC"
    }
    
    # 随机User-Agent和Headers（参考网页1防爬策略）
    headers = {
        "User-Agent": random.choice(agent_list),
        "Referer": "https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None

def fetch_ssq_all_data(max=64):
    all_data = []
    for page in range(2, max):
        data = fetch_ssq_data(page_no=page)
        if data is None:
            break
        all_data.extend(data)
        time.sleep(random.uniform(0.5, 2))  # 随机延迟防封禁:cite[1]
    
    df_all = pd.DataFrame(all_data)
    df_all.to_excel("双色球历史数据.xlsx", index=False)
    return df_all

def get_history_ssq_data():
    df_existing = pd.DataFrame()
    # 读取已存在的Excel文件
    try:
        df_existing = pd.read_excel("双色球历史数据.xlsx")
    except FileNotFoundError:
        print(f"读取历史数据失败")
        return pd.DataFrame()
    return df_existing

def update_ssq_data():
    data = fetch_ssq_data(page_no=1)
    df_new = pd.DataFrame(data)
    df_old = get_history_ssq_data()

    # 合并数据并去重
    df_combined = pd.concat([df_new, df_old], ignore_index=True).drop_duplicates(subset='code')

    # 保存合并后的数据到Excel文件
    df_combined.to_excel("双色球历史数据.xlsx", index=False)