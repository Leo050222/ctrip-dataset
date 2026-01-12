import json

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_unmapped_cities():
    """找出未映射的城市"""
    # 加载已映射的城市ID
    city_id_map = load_json_file('xc_hotel/city_id_map.json')
    
    # 加载已完成的城市列表
    completed_cities = load_json_file('xc_hotel/complete_cities.json')
    
    # 找出未映射的城市
    unmapped_cities = []
    for city in completed_cities:
        if city not in city_id_map:
            unmapped_cities.append(city)
    
    # 打印结果
    print(f"总城市数量: {len(completed_cities)}")
    print(f"已映射城市数量: {len(city_id_map)}")
    print(f"未映射城市数量: {len(unmapped_cities)}")
    print("\n未映射的城市列表:")
    for city in unmapped_cities:
        print(f"- {city}")
    
    # 保存未映射城市到文件
    with open('xc_hotel/unmapped_cities.json', 'w', encoding='utf-8') as f:
        json.dump(unmapped_cities, f, ensure_ascii=False, indent=4)
    print("\n未映射城市列表已保存到 unmapped_cities.json")

if __name__ == "__main__":
    find_unmapped_cities() 