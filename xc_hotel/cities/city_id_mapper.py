import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import re
import pandas as pd

def get_chrome_profiles():
    """获取Chrome用户配置文件列表"""
    user_data_dir = "C:\\Users\\Leo\\AppData\\Local\\Google\\Chrome\\User Data"
    profiles = []
    if os.path.exists(user_data_dir):
        for item in os.listdir(user_data_dir):
            if os.path.isdir(os.path.join(user_data_dir, item)) and item.startswith('Profile'):
                profiles.append(item)
        if os.path.exists(os.path.join(user_data_dir, 'Default')):
            profiles.append('Default')
    return profiles

def setup_driver():
    """设置并返回WebDriver实例"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    # 使用新的配置文件目录
    user_data_dir = "C:\\Users\\Leo\\AppData\\Local\\Google\\Chrome\\User Data"
    profile_name = "Profile_CTrip"  # 新的配置文件名称
    
    # 添加必要的Chrome选项
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    # 设置用户数据目录
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument(f'--profile-directory={profile_name}')
    
    # 禁用日志输出
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_city_id(driver, city_name):
    """获取指定城市的ID"""
    base_url = "https://hotels.ctrip.com/hotels/list?countryId=1&city=1&checkin=2025/06/01&checkout=2025/06/02&display=1&domestic=1"
    
    # 添加重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"尝试加载页面 (第{attempt + 1}次)")
            driver.get(base_url)
            
            # 等待页面加载完成
            WebDriverWait(driver, 20).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            # 等待输入框加载
            input_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "hotels-destination"))
            )
            
            # 确保页面完全加载
            time.sleep(3)
            
            # 清空输入框
            input_box.clear()
            time.sleep(1)
            
            # 输入城市名
            input_box.send_keys(city_name)
            time.sleep(2)
            
            # 点击搜索按钮
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ibu_hotel_container"]/div/div[1]/ul/li[5]/button/i'))
            )
            search_button.click()
            
            # 等待URL更新
            time.sleep(3)
            
            # 获取当前URL
            current_url = driver.current_url
            print(f"当前URL: {current_url}")
            
            # 从URL中提取city参数
            city_id = re.search(r'city=(\d+)', current_url)
            if city_id:
                return city_id.group(1)
            return None
            
        except Exception as e:
            print(f"处理城市 {city_name} 时出错 (第{attempt + 1}次尝试): {str(e)}")
            if attempt < max_retries - 1:
                print("等待5秒后重试...")
                time.sleep(5)
            else:
                print("达到最大重试次数，跳过该城市")
                return None

def main():
    # 显示现有的Chrome配置文件
    print("现有的Chrome配置文件:")
    profiles = get_chrome_profiles()
    for profile in profiles:
        print(f"- {profile}")
    print("\n将使用新的配置文件: Profile_CTrip")
    
    # 示例城市列表
    cities = ["北京", "上海", "广州", "深圳", "杭州"]
    
    # 创建结果字典
    city_id_map = {}
    
    # 设置WebDriver
    driver = setup_driver()
    
    try:
        for city in cities:
            print(f"正在处理城市: {city}")
            city_id = get_city_id(driver, city)
            if city_id:
                city_id_map[city] = city_id
                print(f"{city}: {city_id}")
            time.sleep(2)  # 添加延迟以避免请求过快
        
        # 将结果保存到CSV文件
        df = pd.DataFrame(list(city_id_map.items()), columns=['城市', 'ID'])
        df.to_csv('city_id_mapping.csv', index=False, encoding='utf-8-sig')
        print("\n结果已保存到 city_id_mapping.csv")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 