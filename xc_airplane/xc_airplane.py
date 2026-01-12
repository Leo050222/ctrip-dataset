import csv
import os
import re
import time
import logging
from bs4 import BeautifulSoup
from DrissionPage import ChromiumOptions, ChromiumPage, WebPage
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# 创建必要的文件夹
if not os.path.exists('result'):
    os.makedirs('result')
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'crawler.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def read_file_to_list(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content_list = [line.strip() for line in file]
        return content_list
    except FileNotFoundError:
        logging.error(f"文件 {filename} 不存在")
        return []
    except Exception as e:
        logging.error(f"读取文件时发生错误: {str(e)}")
        return []

def FlightsPage(departurePlace, arrivePlace, departureDate):
    # 使用相对路径
    user_data_path = os.path.join(os.getcwd(), 'browser_data')
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)
        
    do1 = ChromiumOptions().set_paths(local_port=9113, user_data_path=user_data_path)
    do2 = ChromiumOptions().set_paths(local_port=9114, user_data_path=user_data_path)

    page = ChromiumPage(addr_or_opts=do1)
    page_flag = 1
    url = f'https://flights.ctrip.com/online/list/oneway-{departurePlace}-{arrivePlace}?depdate={departureDate}&cabin=y_s_c_f&adult=1&child=0&infant=0'
    page.get(url)    
    
    if page.ele('@text()=阅读并同意携程的服务协议和个人信息保护政策') != None:
        logging.info('遇到协议弹窗，关闭后重试')
        page.close()
        time.sleep(100)
        if page_flag == 1:
            page = ChromiumPage(addr_or_opts=do2)
            page_flag = 2
        else:
            page = ChromiumPage(addr_or_opts=do1)
        page.get(url)

    if page.ele('xpath:/html/body/div[1]/div[2]/div[2]/div/div[6]/div/div/div[2]/div/div[2]/div/div/div[1]') != None:
        logging.info('遇到验证码，关闭后重试')
        page.close()
        time.sleep(100)
        if page_flag == 1:
            page = ChromiumPage(addr_or_opts=do2)
        else:
            page = ChromiumPage(addr_or_opts=do1)
        page.get(url)
    
    old_lst_length = 0
    flag = 0
    count = 0
    p = 0
    while True:
        lst = page.s_eles('xpath://*[@id="hp_container"]/div[2]/div/div[3]/div[3]/div[2]/span/div')
        if count > 1:
            break        
        if flag == 0:
            if len(lst) == 0:
                time.sleep(0.5)
                p += 1
                logging.info(f"等待页面加载: {p}")
                if p >= 2:
                    break

                if page.ele('xpath://*[@id="hp_container"]/div[2]/div/div[2]/div[2]/div/div/div'):
                    count+=1
                    logging.info(f"重试次数: {count}")
                    if count <= 1:
                        page.get(url)
                continue
            else:
                default_size = len(lst)
                cont = 0
                while True:
                    cont += 1
                    page.scroll.down(400)
                    lst = page.s_eles('xpath://*[@id="hp_container"]/div[2]/div/div[3]/div[3]/div[2]/span/div')
                    if len(lst) != default_size:
                        logging.info("完成首次滚动")
                        break
                    if cont >= 2:
                        break
                flag = 1
        if len(lst) == old_lst_length:
            break
        old_lst_length = len(lst)
        page.scroll.down(600)
        time.sleep(0.75)
        logging.info("继续滚动加载")
        
    soup = BeautifulSoup(page.html, "html.parser")
    return soup, p

def AirlineNameDiv(FlightsDiv):
    return FlightsDiv.find_all("div",{"class":"airline-name"})

def AirlineNameDivFirst(FlightsDiv):
    return FlightsDiv.find_all("div",{"class":"airline-name"})

def GetDpDiv(FlightsDiv):
    return FlightsDiv.find("div",{"class":"depart-box"})

def GetArrDiv(FlightsDiv):
    return FlightsDiv.find("div",{"class":"arrive-box"})

def GetDpAirport(FlightsDiv):
    return GetDpDiv(FlightsDiv).find("div",{"class":"airport"}).text

def GetDpTime(FlightsDiv):
    return GetDpDiv(FlightsDiv).find("div",{"class":"time"}).text

def GetArrAirport(FlightsDiv):
    return GetArrDiv(FlightsDiv).find("div",{"class":"airport"}).text

def GetArrTime(FlightsDiv):
    return GetArrDiv(FlightsDiv).find("div",{"class":"time"}).text

def GetFlightInformation(FlightsDiv):
    return FlightsDiv.find("div",{"class":"transfer-info-group"}).text

def GetFlightPrice(FlightsDiv):
    return FlightsDiv.find("span",{"class":"price"}).text

def GetFlightLowPrice(FlightsDiv):
    print("\n\n\n\n:",FlightsDiv.find("id",{"class":"travelPackage_price_undefined"}).text)
    return FlightsDiv.find("id",{"class":"travelPackage_price_undefined"}).text

def ReviseResult(FlightsDiv,airlineName):
    result={
    'airline': 'null',
    'departure_airport': 'null',
    'arrival_airport': 'null',
    'departure_time': 'null',
    'arrival_time': 'null',
    'FlightInformation':'null',
    'price': 'null'
    }
    result['airline'] = airlineName
    if 'span' in str(result['airline'][0]):
        result['airline'] = airlineName[0].text
    result['departure_airport']=GetDpAirport(FlightsDiv)
    result['arrival_airport']=GetArrAirport(FlightsDiv)
    result['departure_time']=GetDpTime(FlightsDiv)
    result['arrival_time']=GetArrTime(FlightsDiv)     
    result['FlightInformation']=GetFlightInformation(FlightsDiv)
    result['price']=GetFlightPrice(FlightsDiv)
    if result['price'] == None:
        result['price']=GetFlightLowPrice(FlightsDiv)
    return result

def DataProcessing(FlightsDiv):
    if len(AirlineNameDiv(FlightsDiv)) == 2:
      return  ReviseResult(FlightsDiv,[AirlineNameDiv(FlightsDiv)[0].contents[0],AirlineNameDiv(FlightsDiv)[1].contents[0]])
    elif len(AirlineNameDiv(FlightsDiv)) == 1:
      return  ReviseResult(FlightsDiv,[AirlineNameDiv(FlightsDiv)[0].contents[0]])

def write_to_csv(data, filename, write_header=True):
    # 写入CSV文件的逻辑保持不变，确保写入模式为追加
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header and os.path.getsize(filename) == 0:  # 检查文件是否为空，且需要写入标题
            writer.writerow(['Airline', 'Departure Airport', 'Arrival Airport', 'Departure Time', 'Arrival Time', 'Flight Information', 'Price'])
        writer.writerow([data['airline'], data['departure_airport'], data['arrival_airport'], data['departure_time'], data['arrival_time'], data['FlightInformation'], data['price']])


def AllFlights(allFlightsDiv):
    for FlightsDiv in allFlightsDiv[1:]:
        print(DataProcessing(FlightsDiv))

def query_flights_route(departure_city, arrival_city, departure_date, filename):
    if os.path.isfile(filename):
        logging.info(f"文件 '{filename}' 已存在，跳过查询 {departure_city} 到 {arrival_city} 的航班")
        return
    
    logging.info(f"正在查询 {departure_city} 到 {arrival_city} 在 {departure_date} 的航班...")
    soup, p = FlightsPage(departure_city, arrival_city, departure_date)
    
    if p < 2:
        allFlightsDiv = soup.find_all("div", {"class": "flight-box"})
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if os.path.getsize(filename) == 0:
                writer.writerow(['Airline', 'Departure Airport', 'Arrival Airport', 'Departure Time', 'Arrival Time', 'Flight Information', 'Price'])
            for FlightsDiv in allFlightsDiv[1:]:
                flight_data = DataProcessing(FlightsDiv)
                if flight_data != None:
                    writer.writerow([
                        flight_data['airline'],
                        flight_data['departure_airport'],
                        flight_data['arrival_airport'],
                        flight_data['departure_time'],
                        flight_data['arrival_time'],
                        flight_data['FlightInformation'],
                        flight_data['price']
                    ])
    else:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if os.path.getsize(filename) == 0:
                writer.writerow(['Airline', 'Departure Airport', 'Arrival Airport', 'Departure Time', 'Arrival Time', 'Flight Information', 'Price'])
        logging.warning("没有找到航班数据")
        return

def main(departure_city, arrival_city, departure_date):
    try:
        # 修改文件保存路径到result文件夹
        filename = os.path.join('result', f"flights_{departure_city}_{arrival_city}_{departure_date}.csv")
        if not os.path.isfile(filename):
            logging.info(f"开始查询 {departure_city} 到 {arrival_city} 在 {departure_date} 的航班...")
            query_flights_route(departure_city, arrival_city, departure_date, filename)
        else:
            logging.info(f"文件 '{filename}' 已存在，跳过查询")
    except Exception as e:
        logging.error(f"处理 {departure_city} 到 {arrival_city} 的航班信息时发生错误: {str(e)}")

# 主程序部分
url_list = read_file_to_list('all_urls.txt')
route_pattern = re.compile(r'/oneway-(\w{3})-(\w{3})')
date_pattern = re.compile(r'depdate=(\d{4}-\d{2}-\d{2})')      

for url in url_list:
    try:
        parsed_url = urlparse(url)
        route_match = route_pattern.search(parsed_url.path)
        if route_match:
            logging.info(f"匹配到路线: {route_match.group(0)}")
        else:
            logging.warning("未找到路线匹配")
            continue

        date_match = date_pattern.search(parsed_url.query)
        if date_match:
            departureDate = date_match.group(1)
            logging.info(f"匹配到日期: {departureDate}")
        else:
            logging.warning(f"未找到日期匹配，URL: {url}")
            continue

        departurePlace = route_match.group(1)
        arrivePlace = route_match.group(2)
        main(departurePlace, arrivePlace, departureDate)
    except Exception as e:
        logging.error(f"处理URL时发生错误: {str(e)}")
 

# departure_cities = ['bjs', 'can']  # 示例出发城市列表
# arrival_cities = ['bjs', 'can']    # 示例到达城市列表
# departure_dates = ['2024-8-20']    # 示例出发日期列表
# main(departure_cities, arrival_cities, departure_dates)