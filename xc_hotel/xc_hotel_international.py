import csv
import os
from bs4 import BeautifulSoup
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.common import Settings
from time import sleep
import traceback
import random
import logging
from datetime import datetime
import sys

# 配置DrissionPage设置
Settings.set_singleton_tab_obj(False)

# 配置路径
INDEX = 1
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_STORAGE_PATH = os.path.join(SCRIPT_DIR, f'result_{INDEX}')
BROWSER_DATA_PATH = r'chrome_data'
BROWSER_PORT = 9115
URLS_FILE = f'urls_part{INDEX}.txt'
CRAWLED_URLS_FILE = f'crawled_urls_{INDEX}.txt'
LOGS_PATH = os.path.join(SCRIPT_DIR, f'logs_{INDEX}')

# 确保目录存在
for path in [DATA_STORAGE_PATH, BROWSER_DATA_PATH, LOGS_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

# 配置日志
def setup_logger():
    log_filename = os.path.join(LOGS_PATH, f'hotel_crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logger = logging.getLogger('hotel_crawler')
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.WARNING)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

def read_file_to_list(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def get_crawled_urls(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r', encoding='utf-8') as file:
        return set(line.strip() for line in file)

def save_crawled_url(url, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(url + '\n')

def is_login_page(page):
    """检查是否跳转到登录页面"""
    try:
        # 检查是否存在登录页面的特征元素
        login_elements = [
            'xpath://div[contains(@class, "login-container")]',
            'xpath://div[contains(@class, "login-box")]',
            'xpath://input[@type="password"]',
            'xpath://button[contains(text(), "登录")]'
        ]
        
        for element in login_elements:
            if page.ele(element, timeout=2):
                return True
        return False
    except Exception:
        return False

def get_page(url, max_retries=5, use_incognito=True):
    """
    获取页面，支持切换浏览器模式
    :param url: 要访问的URL
    :param max_retries: 最大重试次数
    :param use_incognito: 是否使用无痕模式
    :return: 页面对象
    """
    logger.info(f"正在尝试打开URL: {url}，使用{'无痕' if use_incognito else '正常'}模式")
    sleep(random.uniform(3, 7))
    
    for attempt in range(max_retries):
        try:
            do1 = ChromiumOptions().set_paths(local_port=BROWSER_PORT, user_data_path=BROWSER_DATA_PATH)
            if use_incognito:
                do1.incognito()  # 无痕模式
            logger.info(f"第{attempt + 1}次尝试启动浏览器...")
            page = ChromiumPage(addr_or_opts=do1)
            logger.info("浏览器启动成功，正在加载页面...")
            
            page.get(url)
            logger.info("页面加载完成")
            
            # 检查是否跳转到登录页面
            if is_login_page(page):
                logger.warning(f"检测到登录页面，尝试切换到{'正常' if use_incognito else '无痕'}模式...")
                page.quit()
                sleep(random.uniform(5, 10))
                # 递归调用，切换模式
                return get_page(url, max_retries, not use_incognito)
            
            sleep(random.uniform(2, 4))
            return page
            
        except Exception as e:
            logger.error(f"第{attempt + 1}次尝试失败: {str(e)}")
            logger.debug(f"详细错误信息: {traceback.format_exc()}")
            try:
                page.quit()
            except:
                pass
            if attempt < max_retries - 1:
                logger.info(f"等待5秒后进行第{attempt + 2}次尝试...")
                sleep(5)
            else:
                logger.error("已达到最大重试次数，尝试切换浏览器模式...")
                # 如果当前模式失败，尝试切换模式
                if attempt == max_retries - 1:
                    return get_page(url, max_retries, not use_incognito)
                raise

def get_hotel_info(soup):
    """获取酒店基本信息"""
    try:
        # 获取酒店名称
        hotel_name = soup.select_one('div.headInit_headInit-title__m3aAX > h1')
        if not hotel_name:
            logger.error("未找到酒店名称元素")
            return None, None
        hotel_name = hotel_name.text.strip()
        
        # 获取评分
        score = soup.select_one('em.reviewTop_reviewTop-score__FpKsA')
        if not score:
            logger.error("未找到评分元素")
            return None, None
        score = score.text.strip()
        
        logger.info(f"成功获取酒店基本信息: {hotel_name} - {score}")
        return hotel_name, score
    except Exception as e:
        logger.error(f"获取酒店基本信息时出错: {e}")
        logger.debug(f"详细错误信息: {traceback.format_exc()}")
        return None, None

def get_room_info(soup):
    """获取房型信息"""
    try:
        room_info = []
        # 打印页面内容，用于调试
        logger.debug("开始解析房型信息...")
        
        # 获取所有房型卡片
        room_cards = soup.select('div.mainRoomList__UlISo > div.commonRoomCard__BpNjl')
        logger.debug(f"找到 {len(room_cards)} 个房型卡片")
        
        if not room_cards:
            # 尝试其他可能的选择器
            room_cards = soup.select('div.mainRoomList__UlISo > div')
            logger.debug(f"使用备用选择器找到 {len(room_cards)} 个房型卡片")
            
            if not room_cards:
                # 打印页面结构，帮助调试
                logger.debug("页面结构:")
                logger.debug(soup.select('div.mainRoomList__UlISo'))
                return []
        
        for card in room_cards:
            try:
                # 获取房型名称
                room_name = card.select_one('span.commonRoomCard-title__iYBn2')
                if not room_name:
                    # 尝试其他可能的选择器
                    room_name = card.select_one('span[class*="title"]')
                    if not room_name:
                        logger.debug(f"未找到房型名称，卡片内容: {card.text[:100]}")
                        continue
                room_name = room_name.text.strip()
                
                # 获取价格信息
                price_element = card.select_one('div.saleRoomItemBox-priceBox-displayPrice__gWiOr > span')
                if not price_element:
                    # 尝试其他可能的选择器
                    price_element = card.select_one('div[class*="price"] > span')
                    if not price_element:
                        logger.debug(f"未找到价格信息，卡片内容: {card.text[:100]}")
                        continue
                price = price_element.text.strip()
                
                room_info.append(f"{room_name}:{price}")
                logger.info(f"成功获取房型信息: {room_name} - {price}")
            except Exception as e:
                logger.error(f"处理单个房型信息时出错: {e}")
                logger.debug(f"卡片内容: {card.text[:100]}")
                continue
        
        if not room_info:
            logger.warning("未找到任何房型信息")
            # 打印页面内容，帮助调试
            logger.debug("页面内容:")
            logger.debug(soup.prettify()[:1000])  # 只打印前1000个字符
        else:
            logger.info(f"共获取到 {len(room_info)} 个房型信息")
        
        return room_info
    except Exception as e:
        logger.error(f"获取房型信息时出错: {e}")
        logger.debug(f"详细错误信息: {traceback.format_exc()}")
        return []

def is_hotel_in_csv(hotel_name, city, date):
    """检查酒店是否已经在CSV文件中"""
    try:
        csv_file = os.path.join(DATA_STORAGE_PATH, f'{city}-{date}.csv')
        if not os.path.exists(csv_file):
            logger.info(f"CSV文件不存在: {csv_file}")
            return False
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过表头
            for row in reader:
                if len(row) >= 1 and row[0].strip() == hotel_name.strip():
                    logger.info(f"找到重复酒店: {hotel_name} 在文件 {csv_file}")
                    return True
        logger.info(f"酒店 {hotel_name} 未在文件 {csv_file} 中找到")
        return False
    except Exception as e:
        logger.error(f"检查酒店是否重复时出错: {e}")
        logger.debug(f"详细错误信息: {traceback.format_exc()}")
        return False

def save_to_csv(hotel_name, score, room_info, city, date):
    """保存数据到CSV文件"""
    try:
        # 检查酒店是否已存在
        if is_hotel_in_csv(hotel_name, city, date):
            logger.info(f"酒店 {hotel_name} 已存在于CSV文件中，跳过保存")
            return True
            
        csv_file = os.path.join(DATA_STORAGE_PATH, f'{city}-{date}.csv')
        first_write = not os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if first_write:
                writer.writerow(['酒店名称', '评分', '房型价格列表'])
            writer.writerow([hotel_name, score, room_info])
        
        logger.info(f"成功保存酒店信息到 {csv_file}")
        return True
    except Exception as e:
        logger.error(f"保存CSV文件时出错: {e}")
        logger.debug(f"详细错误信息: {traceback.format_exc()}")
        return False

def crawl_hotel_details(page, hotel_url, city):
    """
    爬取酒店详情页的函数
    """
    try:
        # 打开新标签页访问酒店详情
        new_tab = page.new_tab(hotel_url)
        sleep(random.uniform(2, 4))
        
        # 等待页面加载
        new_tab.wait.doc_loaded()
        
        # 滚动页面以加载所有内容
        new_tab.run_js('window.scrollTo(0, 500)')
        sleep(random.uniform(2, 4))
        
        # 再次滚动以确保所有内容都加载
        new_tab.run_js('window.scrollTo(0, 1000)')
        sleep(random.uniform(2, 4))
        
        # 获取页面内容
        soup = BeautifulSoup(new_tab.html, "html.parser")
        
        # 获取酒店基本信息
        hotel_name, score = get_hotel_info(soup)
        if not hotel_name or not score:
            logger.error("获取酒店基本信息失败")
            new_tab.close()
            return False
            
        # 从URL中获取日期
        try:
            date = hotel_url.split('checkIn=')[1].split('&')[0]
            logger.info(f"从URL提取日期信息: date={date}")
        except Exception as e:
            logger.error(f"从URL提取日期信息失败: {e}")
            new_tab.close()
            return False
            
        # 检查酒店是否已存在
        if is_hotel_in_csv(hotel_name, city, date):
            logger.info(f"酒店 {hotel_name} 已存在于CSV文件中，跳过爬取")
            new_tab.close()
            return True
        
        # 获取房型信息
        room_info = get_room_info(soup)
        if not room_info:
            logger.warning("未获取到房型信息")
            # 保存页面内容用于调试
            debug_file = os.path.join(LOGS_PATH, f'debug_{hotel_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(new_tab.html)
            logger.info(f"已保存页面内容到: {debug_file}")
        
        # 保存到CSV
        if save_to_csv(hotel_name, score, room_info, city, date):
            logger.info(f"成功爬取酒店: {hotel_name}")
        else:
            logger.error(f"保存酒店信息失败: {hotel_name}")
        
        # 关闭详情页标签
        new_tab.close()
        return True
        
    except Exception as e:
        logger.error(f"爬取酒店详情时出错: {e}")
        logger.debug(f"详细错误信息: {traceback.format_exc()}")
        # 确保关闭详情页标签
        try:
            if page.tabs_count > 1:
                page.close_tabs([page.latest_tab])
        except Exception as e:
            logger.error(f"关闭标签页时出错: {e}")
        return False

def restart_program():
    """重启程序"""
    logger.info("正在重启程序...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def get_hotel_list_length(page):
    """获取当前酒店列表的长度"""
    try:
        hotel_list = page.ele('xpath://*[@id="ibu_hotel_container"]/section/article/div/section/ul', timeout=10)
        if hotel_list:
            hotel_items = hotel_list.eles('tag:li')
            return len(hotel_items)
    except Exception as e:
        logger.error(f"获取酒店列表长度时出错: {e}")
    return 0

def process_hotel_list(page, max_hotels=50):
    """
    处理酒店列表页面的函数
    """
    try:
        # 等待页面完全加载
        page.wait.doc_loaded()
        sleep(random.uniform(3, 5))
        
        # 检查是否跳转到登录页面
        if is_login_page(page):
            logger.error("检测到登录页面，退出处理")
            return
        
        # 首先获取城市名称
        max_retries = 3
        for retry in range(max_retries):
            try:
                city_element = page.ele('xpath://*[@id="hotels-destinationV8"]', timeout=10)
                if city_element:
                    city = city_element.attr('value')
                    if city:
                        logger.info(f"获取到城市名称: {city}")
                        break
            except Exception as e:
                logger.warning(f"第{retry + 1}次尝试获取城市名称失败: {e}")
                if retry < max_retries - 1:
                    sleep(random.uniform(2, 3))
                    continue
                else:
                    logger.error("无法获取城市名称，退出处理")
                    return
        
        if not city:
            logger.error("未获取到城市名称")
            return
            
        # 添加随机延时
        sleep(random.uniform(2, 4))
        
        # 初始滚动
        try:
            page.scroll.down(845)
            sleep(random.uniform(2, 3))
        except Exception as e:
            logger.warning(f"初始滚动失败: {e}")
            # 继续执行，不返回

    except Exception as e:
        logger.error(f"[init-scroll] 初始化失败: {e}")
        return

    count = 0
    i = 5  # 初始索引
    consecutive_failures = 0  # 连续失败计数
    max_consecutive_failures = 3  # 最大连续失败次数
    last_hotel_count = get_hotel_list_length(page)  # 记录上次的酒店数量
    reached_bottom = False  # 标记是否到达底部
    visible_hotels_processed = set()  # 用于记录已处理的可见酒店
    
    while count < max_hotels:
        try:
            # 如果连续失败次数过多，重启程序
            if consecutive_failures >= max_consecutive_failures:
                logger.error(f"连续{consecutive_failures}次失败，准备重启程序...")
                try:
                    page.quit()
                except:
                    pass
                sleep(2)  # 等待2秒确保浏览器完全关闭
                restart_program()  # 重启程序
            
            # 获取酒店列表
            hotel_list = page.ele('xpath://*[@id="ibu_hotel_container"]/section/article/div/section/ul', timeout=10)
            if not hotel_list:
                logger.error("未找到酒店列表元素")
                consecutive_failures += 1
                continue
            
            # 获取所有酒店项
            hotel_items = hotel_list.eles('tag:li')
            if not hotel_items:
                logger.error("未找到酒店列表项")
                consecutive_failures += 1
                continue
            
            # 处理每个酒店项
            try:
                # 查找酒店详情链接
                hotel_xpath = (f'xpath://*[@id="ibu_hotel_container"]/section/article/div/section/ul'
                              f'/li[{i}]//a[contains(@href, "/hotels/detail")]')
                detail_link = page.ele(hotel_xpath, timeout=10)
                
                if detail_link:
                    hotel_url = detail_link.attr('href')
                    if hotel_url:
                        # 将城市名称传递给crawl_hotel_details函数
                        if crawl_hotel_details(page, hotel_url, city):
                            count += 1
                            logger.info(f"成功爬取第 {count} 个酒店")
                            consecutive_failures = 0  # 重置失败计数
                            visible_hotels_processed.add(i)  # 记录已处理的酒店索引
                            # 滚动265像素
                            page.scroll.down(265)
                            sleep(random.uniform(2, 3))
                            
                            # 检查是否出现"更多已售罄的酒店"元素
                            sold_out_element = page.ele('xpath://div[contains(@class, "toggle-sold-out-hotels")]/span', timeout=2)
                            if sold_out_element and not reached_bottom:
                                logger.info("检测到'更多已售罄的酒店'元素，已到达列表底部")
                                reached_bottom = True
                                # 获取当前可见的所有酒店数量
                                current_visible_hotels = get_hotel_list_length(page)
                                logger.info(f"当前可见酒店数量: {current_visible_hotels}")
                else:
                    logger.warning(f"未找到第 {i} 个酒店的详情链接")
                    consecutive_failures += 1
                    
                    # 检查是否出现"更多已售罄的酒店"元素
                    sold_out_element = page.ele('xpath://div[contains(@class, "toggle-sold-out-hotels")]/span', timeout=2)
                    if sold_out_element and not reached_bottom:
                        logger.info("检测到'更多已售罄的酒店'元素，已到达列表底部")
                        reached_bottom = True
                        # 获取当前可见的所有酒店数量
                        current_visible_hotels = get_hotel_list_length(page)
                        logger.info(f"当前可见酒店数量: {current_visible_hotels}")
                
                i += 1  # 增加索引
                
                # 如果已经到达底部，检查是否处理完所有可见酒店
                if reached_bottom:
                    current_visible_hotels = get_hotel_list_length(page)
                    if i > current_visible_hotels:
                        logger.info(f"已处理完所有可见酒店，共 {count} 个，结束当前城市爬取")
                        return
                
            except Exception as e:
                logger.error(f"处理酒店项时出错: {e}")
                consecutive_failures += 1
                i += 1
                
                # 检查是否出现"更多已售罄的酒店"元素
                sold_out_element = page.ele('xpath://div[contains(@class, "toggle-sold-out-hotels")]/span', timeout=2)
                if sold_out_element and not reached_bottom:
                    logger.info("检测到'更多已售罄的酒店'元素，已到达列表底部")
                    reached_bottom = True
                    # 获取当前可见的所有酒店数量
                    current_visible_hotels = get_hotel_list_length(page)
                    logger.info(f"当前可见酒店数量: {current_visible_hotels}")
                
                # 如果已经到达底部，检查是否处理完所有可见酒店
                if reached_bottom:
                    current_visible_hotels = get_hotel_list_length(page)
                    if i > current_visible_hotels:
                        logger.info(f"已处理完所有可见酒店，共 {count} 个，结束当前城市爬取")
                        return
                continue
            
        except Exception as e:
            logger.error(f"处理酒店列表时出错: {e}")
            consecutive_failures += 1
            
            # 检查是否出现"更多已售罄的酒店"元素
            sold_out_element = page.ele('xpath://div[contains(@class, "toggle-sold-out-hotels")]/span', timeout=2)
            if sold_out_element and not reached_bottom:
                logger.info("检测到'更多已售罄的酒店'元素，已到达列表底部")
                reached_bottom = True
                # 获取当前可见的所有酒店数量
                current_visible_hotels = get_hotel_list_length(page)
                logger.info(f"当前可见酒店数量: {current_visible_hotels}")
            
            # 如果已经到达底部，检查是否处理完所有可见酒店
            if reached_bottom:
                current_visible_hotels = get_hotel_list_length(page)
                if i > current_visible_hotels:
                    logger.info(f"已处理完所有可见酒店，共 {count} 个，结束当前城市爬取")
                    return
            continue

    logger.info(f"已完成爬取 {count} 个酒店")

def main():
    url_list = read_file_to_list(URLS_FILE)
    crawled_urls = get_crawled_urls(CRAWLED_URLS_FILE)
    
    for idx, url in enumerate(url_list):
        # 检查URL是否已经爬取过
        if url in crawled_urls:
            logger.info(f"跳过已爬取的URL: {url}")
            continue
            
        logger.info(f"正在爬取第{idx+1}个URL: {url}")
        try:
            page = get_page(url)
            process_hotel_list(page, max_hotels=50)  # 设置每个URL爬取50个酒店
            save_crawled_url(url, CRAWLED_URLS_FILE)
            sleep(random.uniform(5, 10))
        except Exception as e:
            logger.error(f"爬取URL时出错: {url}, 错误类型: {type(e).__name__} — {e}")
            logger.debug(f"详细错误信息: {traceback.format_exc()}")
            continue

if __name__ == '__main__':
    main() 