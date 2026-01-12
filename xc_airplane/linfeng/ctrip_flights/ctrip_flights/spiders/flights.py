import scrapy
import json
import re
import subprocess
from datetime import datetime
from scrapy.http import JsonRequest
from ..items import FlightItem
from bson import ObjectId
import time
import logging

class FlightsSpider(scrapy.Spider):
    name = 'flights'
    allowed_domains = ['flights.ctrip.com']
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'COOKIES_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
    }
    
    def __init__(self, departure='北京', arrival='上海', date='2025-06-20', *args, **kwargs):
        super(FlightsSpider, self).__init__(*args, **kwargs)
        self.departure = departure
        self.arrival = arrival
        self.departure_date = date
        self.options=[]
        # self.start_time = time.time()
        # self.logger = logging.getLogger(self.name)
        
        # Load city codes
        try:
            with open(r'C:\Users\Leo\Desktop\work\wzx\xc_airplane\linfeng\place.json', 'r', encoding='utf-8') as f:
                self.city_data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading city codes: {e}")
            raise
            
    def get_city_code(self, city_name):
        """Get city code from city name"""
        # print(self.city_data)
        for city in self.city_data['cityList']:
            if city_name in city[7]:
                return city[0]
        return None

    def start_requests(self):
        # Get city codes
        departure_code = self.get_city_code(self.departure)
        arrival_code = self.get_city_code(self.arrival)
        
        if not departure_code or not arrival_code:
            self.logger.error("Invalid city codes")
            return
            
        # Initial search URL
        self.search_url = f"https://flights.ctrip.com/online/list/oneway-{str.lower(departure_code)}-{str.lower(arrival_code)}?_=1&depdate={self.departure_date}&cabin=Y_S_C_F"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://flights.ctrip.com/online/channel/domestic',
        }
        scookies = {
            "_abtest_userid": "aeeffe96-f278-4dd8-a249-d0c81a1b60e1",
            'UBT_VID': '1743490003818.8d6efKkBjXtS',
            'GUID': '09031041219931850977',
            '_ga': 'GA1.1.656553223.1743490005',
            'MKT_CKID': '1743490004638.0dxdg.xj5i',
            '_RSG': 'W9KyxwlIZwAwGl_FEBJdBA',
            '_RDG': '28c1e3ff2b4f342845329bac0496193a1d',
            '_RGUID': 'aea34afe-bbf1-4260-a2e7-4cb38ffef43a',
            '_bfaStatusPVSend': '1',
            'nfes_isSupportWebP': '1',
            '_abtest_userid': '53c39163-94da-4264-8e86-96adc4938ea6',
            'cticket': '0C0138CD7D3D5927FC03FB3AC722FBB82ECDE4EF44C9FC0D337129F0844F8C15',
            'login_type': '0',
            'login_uid': '92E1DE08926761898725761C8741A441',
            'DUID': 'u=91E6B2176663BC25248B6B02C220EEEC&v=0',
            'IsNonUser': 'F',
            'AHeadUserInfo': 'VipGrade=0&VipGradeName=%C6%D5%CD%A8%BB%E1%D4%B1&UserName=&NoReadMessageCount=0',
            '_udl': '708D70C2B179E2F91CC5ED1C2CCE362D',
            '_ubtstatus': '%7B%22vid%22%3A%221743490003818.8d6efKkBjXtS%22%2C%22sid%22%3A15%2C%22pvid%22%3A39%2C%22pid%22%3A600001375%7D',
            '_bfaStatus': 'send',
            'MKT_Pagesource': 'PC',
            'ibulanguage': 'CN',
            'ibulocale': 'zh_cn',
            'cookiePricesDisplayed': 'CNY',
            'Hm_lvt_a8d6737197d542432f4ff4abc6e06384': '1745932083,1746155500,1746892744,1747052140',
            'HMACCOUNT': 'E3356F3C7513DAD5',
            'FlightIntl': 'Search=[%22BJS|%E5%8C%97%E4%BA%AC(BJS)|1|BJS|480%22%2C%22SHA|%E4%B8%8A%E6%B5%B7(SHA)|2|SHA|480%22%2C%222025-05-13%22]',
            '_RF1': '111.23.19.124',
            'Hm_lpvt_a8d6737197d542432f4ff4abc6e06384': '1747065234',
            'Union': 'OUID=&AllianceID=4902&SID=22921635&SourceID=&createtime=1747065234133',
            'MKT_OrderClick': 'ASID=490222921635&AID=4902&CSID=22921635&OUID=&CT=1747065234135&CURL=https%3A%2F%2Fwww.ctrip.com%2F%3Fallianceid%3D4902%26sid%3D22921635%26msclkid%3Da6f49943edb01c781957f161f4200c34%26keywordid%3D82327006001772&VAL={"pc_vid":"1743490003818.8d6efKkBjXtS"}',
            '_jzqco': '%7C%7C%7C%7C1747052140532%7C1.1115404307.1743490004642.1747065014672.1747065234173.1747065014672.1747065234173.0.0.0.46.46',
            '_ga_5DVRDQD429': 'GS2.1.s1747065014$o20$g1$t1747065235$j0$l0$h0',
            '_ga_B77BES1Z8Z': 'GS2.1.s1747065014$o20$g1$t1747065235$j58$l0$h0',
            '_ga_9BZF483VNQ': 'GS2.1.s1747065014$o20$g1$t1747065235$j0$l0$h0',
            '_bfa': '1.1743490003818.8d6efKkBjXtS.1.1747065236901.1747065269201.27.7.10320673302'
        }
        yield scrapy.Request(
            url=self.search_url,
            headers=headers,
            cookies=scookies,
            callback=self.parse_search_page,
            meta={
                'departure_code': departure_code,
                'arrival_code': arrival_code,
                'dont_redirect': True,
                'handle_httpstatus_list': [301, 302]
            },
            errback=self.handle_error,
            dont_filter=True  # 禁用请求去重
        )

    def parse_search_page(self, response):
        try:
            # Extract transaction ID
            transaction_id = re.search(r'"transactionID":"([^"]+)"', response.text).group(1)
            
            # Save search parameters
            search_params = {
                'transaction_id': transaction_id,
                'departure': response.meta['departure_code'],
                'arrival': response.meta['arrival_code'],
                'departure_date': self.departure_date
            }
            
            with open(r'C:\Users\Leo\Desktop\work\wzx\xc_airplane\linfeng\data.json', 'w', encoding='utf-8') as f:
                json.dump(search_params, f, indent=4)
                
            # Generate tokens using Node.js script
            result = subprocess.run(
                ['node', r'C:\Users\Leo\Desktop\work\wzx\xc_airplane\linfeng\xiecheng.js'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Error generating tokens: {result.stderr}")
                return
                
            sign = re.findall(r'Sign=([a-f0-9]{32})', result.stdout)[0]
            token = re.findall(r'Token=([a-zA-Z0-9-]+)', result.stdout)[0]
            
            # API headers
            headers = {
                "accept": "application/json",
                "accept-encoding":"gzip, deflate, br, zstd",
                "accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "cache-control":"no-cache",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
                'transactionid': transaction_id,
                "token": token,
                "sign": sign,
                "scope": "d",
                "content-type": "application/json;charset=UTF-8",
                "rms-token":"fp=&vid=&pageId=&r=aea34afebbf14260a2e74cb38ffef43a&ip=111.23.19.123&rg=b4&kpData=0_0_0&kpControl=0_0_0-0_0_0&kpEmp=0_0_0_0_0_0_0_0_0_0-0_0_0_0_0_0_0_0_0_0-0_0_0_0_0_0_0_0_0_0&screen=1494x934&tz=+8&blang=zh-CN&oslang=zh-CN&ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F131.0.0.0%20Safari%2F537.36%20Edg%2F131.0.0.0&d=flights.ctrip.com&v=25&kpg=0_0_0_0_0_0_0_0_0_0&adblock=F&cck=F",
                "referer":self.search_url,
                "sec-ch-ua":'"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "sec-ch-ua-mobile":"?0",
                "sec-ch-ua-platform":"Windows",
                "sec-fetch-dest":"empty",
                "sec-fetch-mode":"cors",
                "sec-fetch-site":"same-origin",
                "sessionid":32,
            }

            # API request payload
            params={
                "adultCount": 1,
                "childCount": 0,
                "infantCount": 0,
                "flightWay": "S",
                "cabin": "Y_S_C_F",
                "scope": "d",
                "extensionAttributes": {
                    "LoggingSampling": False,
                    "isFlightIntlNewUser": False
                },
                "segmentNo": 1,
                "transactionID": transaction_id,
                "flightSegments": [
                    {
                        "departureCityCode": response.meta['departure_code'],
                        "arrivalCityCode": response.meta['arrival_code'],
                        "departureCityName": self.departure,
                        "arrivalCityName": self.arrival,
                        "departureDate": self.departure_date,
                        "departureCountryId": 1,
                        "departureCountryName": "中国",
                        "departureCountryCode": "CN",
                        "departureProvinceId": 1,
                        "departureCityId": 1,
                        "arrivalCountryId": 1,
                        "arrivalCountryName": "中国",
                        "arrivalCountryCode": "CN",
                        "arrivalProvinceId": 2,
                        "arrivalCityId": 1,
                        "departureCityTimeZone": 480,
                        "arrivalCityTimeZone": 480,
                        "timeZone": 480
                    }
                ],
                "directFlight": False,
                "extGlobalSwitches": {
                    "useAllRecommendSwitch": True,
                    "unfoldPriceListSwitch": True
                },
                "noRecommend": False
            }

            # Convert cookie string to dictionary
            self.cookies = {
                "cticket": "B3A338E97EFFE24E450816AAB79CC015C83539813F5E02E81D2F2817A26CC6F9"
            }
            yield JsonRequest(
                url="https://flights.ctrip.com/international/search/api/search/batchSearch?v=0.44481860357751546",
                method='post',
                headers=headers,
                cookies=self.cookies,
                data=params,
                callback=self.parse_flight_data,
                meta={
                    'departure': self.departure,
                    'arrival': self.arrival,
                    'date': self.departure_date,
                    'transaction_id': transaction_id,
                    'dont_redirect': True,
                    'handle_httpstatus_list': [301, 302]
                },
                errback=self.handle_error,
                dont_filter=True  # 禁用请求去重
            )
        except Exception as e:
            self.logger.error(f"Error in parse_search_page: {e}")
            raise

    def parse_flight_data(self, response):
        try:
            flight_data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"API返回的JSON数据无效: {e}")
            return

        if "data" not in flight_data or "flightItineraryList" not in flight_data["data"]:
            self.logger.error("未在响应中找到航班数据")
            return

        flight_item = FlightItem()
        flight_item['document'] = {
            "id": str(ObjectId()),
            "departureCity": self.departure,
            "arrivalCity": self.arrival,
            "Date": self.departure_date,
            "options": []
        }

        for fli_data in flight_data["data"]["flightItineraryList"]:
            if ',' not in fli_data['itineraryId']:
                flight_company = fli_data['flightSegments'][0]['flightList'][0]['marketAirlineName']
                flight_number = fli_data['flightSegments'][0]['flightList'][0]['flightNo']
                if 'operateAirlineName' in fli_data['flightSegments'][0]['flightList'][0]:
                    operating_company = fli_data['flightSegments'][0]['flightList'][0]['operateAirlineName']
                    operating_number = fli_data['flightSegments'][0]['flightList'][0]['operateFlightNo']
                else:
                    operating_company = ''
                    operating_number = ''
                if fli_data['flightSegments'][0]['flightList'][0]['stopList'] != []:
                    stop_city = fli_data['flightSegments'][0]['flightList'][0]['stopList'][0]['cityName']
                else:
                    stop_city = ''
                dep_city = self.departure
                dep_airport = fli_data['flightSegments'][0]['flightList'][0]['departureAirportName'].replace('国际机场','')
                if dep_city in dep_airport:
                    dep_airport = dep_airport
                else:
                    dep_airport = dep_city + dep_airport
                dep_terminal = fli_data['flightSegments'][0]['flightList'][0]['departureTerminal'] if 'departureTerminal' in fli_data['flightSegments'][0]['flightList'][0] else ''
                dep = fli_data['flightSegments'][0]['flightList'][0]['departureDateTime']
                dep_time = dep.split(' ')[1][:-3]
                dep_date = dep.split(' ')[0]
                arr_city = self.arrival
                arr_airport = fli_data['flightSegments'][0]['flightList'][0]['arrivalAirportName'].replace('国际机场','')
                if arr_city in arr_airport:
                    arr_airport = arr_airport
                else:
                    arr_airport = arr_city + arr_airport
                arr_terminal = fli_data['flightSegments'][0]['flightList'][0]['arrivalTerminal'] if 'arrivalTerminal' in fli_data['flightSegments'][0]['flightList'][0] else ''
                arr = fli_data['flightSegments'][0]['flightList'][0]['arrivalDateTime']
                arr_time = arr.split(' ')[1][:-3]
                arr_date = arr.split(' ')[0]
                trans_total_time = ''
                total_time = datetime.strptime(arr_date+" "+arr_time,'%Y-%m-%d %H:%M')-datetime.strptime(dep_date+" "+dep_time,'%Y-%m-%d %H:%M')
                total_seconds = int(total_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                total_time = f"{hours}h{minutes}m"
                Price = fli_data['priceList']
                price_type = '￥'
                price = 100000
                for pri in Price:
                    if int(str(pri['adultPrice']).replace('.0','')) < price:
                        price = int(str(pri['adultPrice']).replace('.0',''))
                options = {
                    "legs": [],                                      
                    "transfer_totalTime": trans_total_time,              
                    "totalTime": total_time,                         
                    "price_type": price_type,                        
                    "price": price                               
                }
                leg = {                                   
                    "flightCompany": flight_company,            
                    "flightNumber": flight_number,               
                    "operating": {               
                        "flightCompany": operating_company,
                        "flightNumber": operating_number
                    },
                    "departure": {                 
                        "city": dep_city,
                        "airport": dep_airport,
                        "terminal": dep_terminal,
                        "date": dep_date,
                        "time": dep_time                    
                    }, 
                    "arrival": {                   
                        "city": arr_city,
                        "airport": arr_airport,
                        "terminal": arr_terminal,
                        "date": arr_date,
                        "time": arr_time   
                    },
                    "stop":{
                        "city":stop_city
                    }
                }
                options['legs'].append(leg)
                self.options.append(options)
            else:
                flight_company = fli_data['flightSegments'][0]['flightList'][0]['marketAirlineName']
                flight_number = fli_data['flightSegments'][0]['flightList'][0]['flightNo']
                operating_company = fli_data['flightSegments'][0]['flightList'][0]['operateAirlineName'] if 'operateAirlineName' in fli_data['flightSegments'][0]['flightList'][0] else ''
                operating_number = fli_data['flightSegments'][0]['flightList'][0]['operateFlightNo'] if 'operateFlightNo' in fli_data['flightSegments'][0]['flightList'][0] else ''
                if fli_data['flightSegments'][0]['flightList'][0]['stopList'] != []:
                    stop_city = fli_data['flightSegments'][0]['flightList'][0]['stopList'][0]['cityName']
                else:
                    stop_city = ''
                dep = fli_data['flightSegments'][0]['flightList'][0]['departureDateTime']
                dep_time = dep.split(' ')[1][:-3]
                dep_date = dep.split(' ')[0]
                dep_city = self.departure
                dep_airport = fli_data['flightSegments'][0]['flightList'][0]['departureAirportName'].replace('国际机场', '')
                if dep_city in dep_airport:
                    dep_airport = dep_airport
                else:
                    dep_airport = dep_city + dep_airport
                dep_terminal = fli_data['flightSegments'][0]['flightList'][0]['departureTerminal'] if 'departureTerminal' in fli_data['flightSegments'][0]['flightList'][0] else ''
                arr_city = fli_data['flightSegments'][0]['flightList'][0]['arrivalCityName']
                arr_airport = fli_data['flightSegments'][0]['flightList'][0]['arrivalAirportName'].replace('国际机场', '')
                if arr_city in arr_airport:
                    arr_airport = arr_airport
                else:
                    arr_airport = arr_city + arr_airport
                arr_terminal = fli_data['flightSegments'][0]['flightList'][0]['arrivalTerminal'] if 'arrivalTerminal' in fli_data['flightSegments'][0]['flightList'][0] else ''
                arr = fli_data['flightSegments'][0]['flightList'][0]['arrivalDateTime']
                arr_time = arr.split(' ')[1].replace(':00', '')
                arr_date = arr.split(' ')[0]
                trans_company = fli_data['flightSegments'][0]['flightList'][1]['marketAirlineName']
                trans_number = fli_data['flightSegments'][0]['flightList'][1]['flightNo']
                trans_operating_company = fli_data['flightSegments'][0]['flightList'][1]['operateAirlineName'] if 'operateAirlineName' in fli_data['flightSegments'][0]['flightList'][1] else ''
                trans_operating_number = fli_data['flightSegments'][0]['flightList'][1]['operateFlightNo'] if 'operateFlightNo' in fli_data['flightSegments'][0]['flightList'][1] else ''
                if fli_data['flightSegments'][0]['flightList'][1]['stopList'] != []:
                    trans_stop_city = fli_data['flightSegments'][0]['flightList'][1]['stopList'][0]['cityName']
                else:
                    trans_stop_city = ''
                trans_dep_city = fli_data['flightSegments'][0]['flightList'][1]['departureCityName']
                trans_dep_airport = fli_data['flightSegments'][0]['flightList'][1]['departureAirportName'].replace('国际机场','')
                if trans_dep_city in trans_dep_airport:
                    trans_dep_airport = trans_dep_airport
                else:
                    trans_dep_airport = trans_dep_city + trans_dep_airport
                trans_dep_terminal = fli_data['flightSegments'][0]['flightList'][1]['departureTerminal'] if 'departureTerminal' in fli_data['flightSegments'][0]['flightList'][1] else ''
                trans_dep = fli_data['flightSegments'][0]['flightList'][1]['departureDateTime']
                trans_dep_time = trans_dep.split(' ')[1].replace(':00','')
                trans_dep_date = trans_dep.split(' ')[0]
                trans_arr_city = self.arrival
                trans_arr_airport = fli_data['flightSegments'][0]['flightList'][1]['arrivalAirportName'].replace('国际机场','')
                if trans_arr_city in trans_arr_airport:
                    trans_arr_airport = trans_arr_airport
                else:
                    trans_arr_airport = trans_arr_city+trans_arr_airport
                trans_arr_terminal = fli_data['flightSegments'][0]['flightList'][1]['arrivalTerminal'] if 'arrivalTerminal' in fli_data['flightSegments'][0]['flightList'][1] else ''
                trans_arr = fli_data['flightSegments'][0]['flightList'][1]['arrivalDateTime']
                trans_arr_time = trans_arr.split(' ')[1][:-3]
                trans_arr_date = trans_arr.split(' ')[0]
                trans_total_time = datetime.strptime(trans_dep_date+" "+trans_dep_time,'%Y-%m-%d %H:%M')-datetime.strptime(arr_date+" "+arr_time,'%Y-%m-%d %H:%M')
                trans_total_seconds = int(trans_total_time.total_seconds())
                trans_hours = trans_total_seconds // 3600
                trans_minutes = (trans_total_seconds % 3600) // 60
                trans_total_time = f"{trans_hours}h{trans_minutes}m"
                total_time = datetime.strptime(trans_arr_date+" "+trans_arr_time,'%Y-%m-%d %H:%M')-datetime.strptime(dep_date+" "+dep_time,'%Y-%m-%d %H:%M')
                total_seconds = int(total_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                total_time = f"{hours}h{minutes}m"
                Price = fli_data['priceList']
                price_type = '￥'
                price = 100000
                for pri in Price:
                    if int(str(pri['adultPrice']).replace('.0','')) < price:
                        price = int(str(pri['adultPrice']).replace('.0',''))
                options = {
                    "legs": [],                                      
                    "transfer_totalTime": trans_total_time,              
                    "totalTime": total_time,                         
                    "price_type": price_type,                        
                    "price": price                               
                }
                leg = {                                   
                    "flightCompany": flight_company,            
                    "flightNumber": flight_number,               
                    "operating": {               
                        "flightCompany": operating_company,
                        "flightNumber": operating_number
                    },
                    "departure": {                 
                        "city": dep_city,
                        "airport": dep_airport,
                        "terminal": dep_terminal,
                        "date": dep_date,
                        "time": dep_time                    
                    }, 
                    "arrival": {                   
                        "city": arr_city,
                        "airport": arr_airport,
                        "terminal": arr_terminal,
                        "date": arr_date,
                        "time": arr_time   
                    },
                    'stop':{
                        "city": stop_city 
                    }
                }
                options['legs'].append(leg)
                leg = {                                    
                    "flightCompany": trans_company,            
                    "flightNumber": trans_number,               
                    "operating": {                    
                        "flightCompany": trans_operating_company,
                        "flightNumber": trans_operating_number
                    },    
                    "departure": {                   
                        "city": trans_dep_city,
                        "airport": trans_dep_airport,
                        "terminal": trans_dep_terminal,
                        "date": trans_dep_date,
                        "time": trans_dep_time
                    },
                    "arrival": {                       
                        "city": trans_arr_city,
                        "airport": trans_arr_airport,
                        "terminal": trans_arr_terminal,
                        "date": trans_arr_date,
                        "time": trans_arr_time
                    },
                    'stop':{
                        'city':trans_stop_city
                    }
                } 
                options['legs'].append(leg)
                self.options.append(options)

        flight_item['document']['options'] = self.options
        yield flight_item

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.value}")

    def closed(self, reason):
        end_time = time.time()
        # self.logger.info(f"数据爬取完成，耗时{end_time - self.start_time}秒") 