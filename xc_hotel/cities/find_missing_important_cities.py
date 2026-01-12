import json

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_missing_important_cities():
    """找出important_cities中有但completed_cities中没有的城市"""
    # 加载important_cities
    important_cities = load_json_file('xc_hotel/important_cities.json')
    
    # 加载completed_cities
    completed_cities = load_json_file('xc_hotel/completed_cities.json')
    
    # 找出缺失的城市
    missing_cities = []
    for city in important_cities:
        if city not in completed_cities:
            missing_cities.append(city)
    
    # 打印结果
    print(f"重要城市数量: {len(important_cities)}")
    print(f"已完成城市数量: {len(completed_cities)}")
    print(f"缺失城市数量: {len(missing_cities)}")
    print("\n缺失的城市列表:")
    for city in missing_cities:
        print(f"- {city}")
    
    # 保存缺失城市到文件
    with open('xc_hotel/missing_important_cities.json', 'w', encoding='utf-8') as f:
        json.dump(missing_cities, f, ensure_ascii=False, indent=4)
    print("\n缺失城市列表已保存到 missing_important_cities.json")

if __name__ == "__main__":
    find_missing_important_cities() 