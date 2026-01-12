import json
import math

# 你要分成的文件数
N = 7  # 你可以改成你想要的数字

with open('hotel_name_url_map_clear.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 假设是字典，转为列表方便分割
items = list(data.items())
total = len(items)
size = math.ceil(total / N)

for i in range(N):
    part = dict(items[i*size : (i+1)*size])
    with open(f'hotel_name_url_map_clear_part{i+1}.json', 'w', encoding='utf-8') as f:
        json.dump(part, f, ensure_ascii=False, indent=2)
    print(f'已保存: hotel_name_url_map_clear_part{i+1}.json, 共{len(part)}条')

print('全部完成')