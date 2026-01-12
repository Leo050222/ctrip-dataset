import os
import json

base_path = r'/Users/leolee/Desktop/work/xc_hotel/result'

name = []
for i in range(1, 15):
    result_path = os.path.join(base_path, f'result_{i}')
    if not os.path.exists(result_path):
        continue
    json_name = [f for f in os.listdir(result_path) if f.endswith('.json')]
    for json_file in json_name:
        json_path = os.path.join(result_path, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    hotel_name = item['酒店名称']
                    if hotel_name not in name:
                        name.append(hotel_name)
                        print("成功插入", hotel_name)

        except Exception as e:
            print(f'转换 {json_path} 时出错: {e}')

with open('hotel_name.json', 'w', encoding='utf-8') as f:
    json.dump(name, f, ensure_ascii=False, indent=4)
