import json

with open('hotel_name_url_map.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_data = {}
hotel_name_list = []
for key, value in data.items():
    if value is not None:
        new_data[key] = value
    else:
        hotel_name_list.append(key)


with open('hotel_name_url_map_clear.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

with open('hotel_left.json', 'w', encoding='utf-8') as f:
    json.dump(hotel_name_list, f, ensure_ascii=False, indent=4)

print('done')