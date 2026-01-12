import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 读取酒店名列表
with open('hotel_left.json', 'r', encoding='utf-8') as f:
    hotel_names = json.load(f)

with open('hotel_name_url_map.json', 'r', encoding='utf-8') as f:
    hotel_name_url_map = json.load(f)

base_url = "https://hk.trip.com"
search_url = "https://hk.trip.com/global-search/searchlist/search/?keyword={}&from=home"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# 加载已爬取结果
result = hotel_name_url_map
lock = threading.Lock()
if os.path.exists('hotel_name_url_map.json'):
    with open('hotel_name_url_map.json', 'r', encoding='utf-8') as f:
        try:
            result = json.load(f)
        except Exception:
            result = {}

def fetch_url(hotel_name):
    if hotel_name in result and result[hotel_name]:
        return hotel_name, result[hotel_name], 'skip'
    url = search_url.format(requests.utils.quote(hotel_name))
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find('div', class_='default-img')
        if div:
            a_tag = div.find('a')
            if a_tag and a_tag.has_attr('href'):
                href = a_tag['href']
                full_url = base_url + href + "?locale=zh-HK&curr=HKD"
                return hotel_name, full_url, 'ok'
            else:
                return hotel_name, None, 'no_a'
        else:
            return hotel_name, None, 'no_div'
    except Exception as e:
        return hotel_name, None, f'error: {e}'

max_workers = 16  # 可根据机器性能调整

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(fetch_url, name): name for name in hotel_names}
    for future in tqdm(as_completed(futures), total=len(futures), desc='处理进度'):
        hotel_name, url, status = future.result()
        with lock:
            result[hotel_name] = url
            with open('hotel_name_url_map.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        if status == 'ok':
            print(f'{hotel_name} -> {url}')
        elif status == 'skip':
            print(f'已存在，跳过: {hotel_name}')
        else:
            print(f'{hotel_name} 未找到，状态: {status}')

print('已保存为 hotel_name_url_map.json') 