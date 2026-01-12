import json

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_city_id_map():
    """过滤city_id_map，只保留completed_cities中存在的城市"""
    # 加载文件
    city_id_map = load_json_file('xc_hotel/city_id_map.json')
    completed_cities = load_json_file('xc_hotel/complete_cities.json')
    
    # 创建新的映射字典
    filtered_map = {}
    for city in completed_cities:
        if city in city_id_map:
            filtered_map[city] = city_id_map[city]
    
    # 打印统计信息
    print(f"原始城市ID映射数量: {len(city_id_map)}")
    print(f"已完成城市数量: {len(completed_cities)}")
    print(f"过滤后城市ID映射数量: {len(filtered_map)}")
    
    # 保存过滤后的映射
    output_file = 'xc_hotel/filtered_city_id_map.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_map, f, ensure_ascii=False, indent=4)
    print(f"\n过滤后的城市ID映射已保存到: {output_file}")
    
    # 打印未找到ID的城市
    missing_cities = [city for city in completed_cities if city not in city_id_map]
    if missing_cities:
        print("\n以下城市在city_id_map中未找到ID:")
        for city in missing_cities:
            print(f"- {city}")

if __name__ == "__main__":
    filter_city_id_map() 