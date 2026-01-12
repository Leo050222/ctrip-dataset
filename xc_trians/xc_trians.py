import csv
import os
from bs4 import BeautifulSoup
from DrissionPage import ChromiumOptions, ChromiumPage
import re
import os
import pdb 
import json
from tqdm import tqdm

# 添加空数据记录文件路径
EMPTY_ROUTES_FILE = './result/empty_routes.json'

def read_file_to_list(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        # 使用列表推导式读取每一行
        url_list = [line.strip() for line in file]
    return url_list

# get_page 负责获取指定url的page对象 并返回一个可操作的page对象
def get_page(url):
    do1 = ChromiumOptions().set_paths(local_port=9112, user_data_path=r'D:\cookie\WechatDocument\WeChat Files\wxid_rr7urhmr4ckj22\FileStorage\File\2025-03\xc_trians')
    page = ChromiumPage(addr_or_opts=do1)
    page.get(url)  # 使用传入的URL
    return page

def extract_data(html_element, seat_open_div):
    # 核心字段提取
    card = {
        "车次号": html_element.find("div", class_="checi").get_text(strip=True),
        "出发时间": html_element.find("div", class_="from").find("div", class_="time").text.strip(),
        "到达时间": html_element.find("div", class_="to").find("div", class_="time").text.strip(),
        "出发地点": html_element.find("div", class_="from").find("div", class_="station").text.strip(),
        "到达地点": html_element.find("div", class_="to").find("div", class_="station").text.strip(),
        "运行时间": html_element.find("div", class_="haoshi").text.strip(),
    }
    # 新增：提取五种座位价格
    seat_price_map = {"无座": "", "二等座": "", "一等座": "", "商务座": "", "特等座": ""}
    seat_info_debug = []
    if seat_open_div:
        seat_ul = seat_open_div.find("ul", class_="list-seat-select")
        if seat_ul:
            seat_list = seat_ul.find_all("li")
            for seat in seat_list:
                seat_type_tag = seat.find("strong", class_="seat-type")
                price_tag = seat.find("div", class_="price")
                if seat_type_tag and price_tag:
                    seat_type = seat_type_tag.get_text(strip=True)
                    price = price_tag.get_text(strip=True)
                    if seat_type in seat_price_map:
                        seat_price_map[seat_type] = price + "元"
                        seat_info_debug.append(f"{seat_type}:{price}元")
    # 合并到card
    card.update({
        "无座": seat_price_map["无座"],
        "二等座": seat_price_map["二等座"],
        "一等座": seat_price_map["一等座"],
        "商务座": seat_price_map["商务座"],
        "特等座": seat_price_map["特等座"],
    })
    return card

def get_dep_arr_city(url):
    # 正则匹配
    match = re.search(r'dStation=([^&]+)&aStation=([^&]+)', url)
    if match:
        departure_station = match.group(1)  # 佛山
        arrival_station = match.group(2)    # 乳山
        return departure_station, arrival_station
    return None, None

def check_route_exists(departure_station, arrival_station):
    # 检查CSV文件是否存在
    csv_file_name = f'{departure_station}_{arrival_station}.csv'
    csv_file_dir = f'./result/'
    csv_file_path = f'{csv_file_dir}/{csv_file_name}'
    
    # 检查是否在空数据记录中
    if os.path.exists(EMPTY_ROUTES_FILE):
        with open(EMPTY_ROUTES_FILE, 'r', encoding='utf-8') as f:
            empty_routes = json.load(f)
            route_key = f"{departure_station}_{arrival_station}"
            if route_key in empty_routes:
                return True
    
    return os.path.isfile(csv_file_path)

def filter_urls(url_list):
    filtered_urls = []
    for url in url_list:
        departure_station, arrival_station = get_dep_arr_city(url)
        if departure_station and arrival_station:
            if not check_route_exists(departure_station, arrival_station):
                filtered_urls.append(url)
            else:
                print(f'skip {departure_station}-{arrival_station}')
    return filtered_urls

def record_empty_route(departure_station, arrival_station):
    route_key = f"{departure_station}_{arrival_station}"
    empty_routes = set()
    
    # 读取现有的空数据记录
    if os.path.exists(EMPTY_ROUTES_FILE):
        with open(EMPTY_ROUTES_FILE, 'r', encoding='utf-8') as f:
            empty_routes = set(json.load(f))
    
    # 添加新的空数据记录
    empty_routes.add(route_key)
    
    # 保存更新后的记录
    with open(EMPTY_ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(empty_routes), f, ensure_ascii=False, indent=2)

def get_data(page, url):
    soup = BeautifulSoup(page.html, "html.parser")
    trains_raw = soup.find_all('div', class_='card-white list-item')
    departure_station, arrival_station = get_dep_arr_city(url)

    if not trains_raw:
        record_empty_route(departure_station, arrival_station)
        return

    trains = []
    for div in trains_raw:
        if not div.has_attr('id'):
            continue
        if not div.find_parent('div', class_='transfer-box'):
            trains.append(div)

    if not trains:
        record_empty_route(departure_station, arrival_station)
        return

    csv_file_name = f'{departure_station}_{arrival_station}.csv'
    csv_file_dir = f'./result/'
    csv_file_path = f'{csv_file_dir}/{csv_file_name}'

    if not os.path.exists(csv_file_dir):
        os.mkdir(csv_file_dir)

    with open(csv_file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        columns = ["车次号", "出发时间", "到达时间", "出发地点", "到达地点", "运行时间", "无座", "二等座", "一等座", "商务座", "特等座"]
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for div in trains:
            next_sibling = div.find_next_sibling(lambda tag: tag.name == 'div' and 'list-open' in tag.get('class', []))
            data = extract_data(div, next_sibling)
            writer.writerow(data)

def __main__():
    url_list = read_file_to_list("urls.txt")
    filtered_urls = filter_urls(url_list)
    total = len(filtered_urls)

    for url in tqdm(filtered_urls, desc="整体进度", ncols=80):
        page = get_page(url)
        get_data(page, url)
    print("全部抓取任务已完成！")

__main__()