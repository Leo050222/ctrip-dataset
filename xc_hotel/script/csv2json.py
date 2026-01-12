import csv
import json
import ast
import os
import re

base_path = r'/Users/leolee/Desktop/work/xc_hotel/result'

def convert(csv_path, json_path):
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 将房型价格列表从字符串转为列表
            row['房型价格列表'] = ast.literal_eval(row['房型价格列表'])
            data.append(row)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'已将 {csv_path} 转换为 {json_path}')

for i in range(1, 15):
    result_path = os.path.join(base_path, f'result_{i}')
    if not os.path.exists(result_path):
        continue
    csv_name = [f for f in os.listdir(result_path) if f.endswith('.csv')]
    for csv_file in csv_name:
        csv_path = os.path.join(result_path, csv_file)
        json_file = os.path.splitext(csv_file)[0] + '.json'
        json_path = os.path.join(result_path, json_file)
        try:
            convert(csv_path, json_path)
        except Exception as e:
            print(f'转换 {csv_path} 时出错: {e}')

print('done')