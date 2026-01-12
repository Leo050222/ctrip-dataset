from datetime import datetime, timedelta
from urllib.parse import quote

def generate_taiwan_urls(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # 生成所有checkin日期（从后往前）
    dates = []
    current_date = end_date
    while current_date >= start_date:
        dates.append(current_date)
        current_date -= timedelta(days=1)

    # 生成URL列表
    urls = []
    for checkin_date in dates:  # 从后往前遍历日期
        checkout_date = checkin_date + timedelta(days=1)
        checkin_str = checkin_date.strftime("%Y-%m-%d")
        checkout_str = checkout_date.strftime("%Y-%m-%d")
        
        # 台湾省酒店URL格式
        url = f"https://hk.trip.com/hotels/list?city=-1&provinceId=53&countryId=1&districtId=0&checkin={checkin_str}&checkout={checkout_str}"
        urls.append(url)

    # 保存到文件
    with open('generated_taiwan_urls.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(urls))

    print(f"已生成 {len(urls)} 条台湾省酒店URL，保存至文件：generated_taiwan_urls.txt")
    print(f"日期范围：{start_date_str} 到 {end_date_str}")
    print(f"URL生成顺序：从 {end_date_str} 到 {start_date_str}")

# 输入日期范围
start_date_str = input("请输入开始日期（格式：YYYY-MM-DD）：")
end_date_str = input("请输入结束日期（格式：YYYY-MM-DD）：")

# 生成普通城市URL
start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

# 生成所有checkin日期（从后往前）
dates = []
current_date = end_date
while current_date >= start_date:
    dates.append(current_date)
    current_date -= timedelta(days=1)

city_ids = [
    1, 3, 428, 468, 147, 275, 947, 185, 550, 562, 216, 340, 290, 105, 136, 907, 137, 1092, 1317, 1453, 140, 513, 139,
    103, 141, 1133, 202, 458, 451, 6, 178, 252, 1155, 221, 327, 1300, 254, 351, 387, 1048, 211, 1050, 158, 159, 440,
    352, 456, 1303, 1116, 5, 149, 157, 1611, 1617, 231, 517, 317, 1599, 150, 281, 1128, 2, 12, 13, 512, 213, 14, 82,
    353, 577, 1200, 15, 16, 579, 1472, 17, 375, 491, 571, 86, 22, 308, 407, 19, 578, 346, 278, 478, 182, 287, 1024, 272,
    459, 177, 23, 214, 257, 521, 1705, 1078, 218, 1006, 258, 25, 667, 437, 406, 560, 606, 348, 378, 376, 305, 24, 603,
    534, 268, 933, 518, 411, 144, 7, 542, 614, 236, 533, 475, 318, 454, 479, 1106, 569, 1370, 1071, 1074, 559, 331, 350,
    181, 951, 507, 1093, 1232, 1094, 1088, 436, 385, 441, 510, 551, 1454, 477, 292, 452, 515, 496, 992, 1121, 1490, 328,
    937, 1117, 206, 601, 598, 297, 1111, 539, 201, 27, 1125, 612, 970, 282, 918, 32, 422, 30, 31, 447, 251, 316, 547,
    1105, 552, 299, 1436, 693, 692, 1422, 223, 553, 215, 956, 380, 354, 33, 492, 189, 1677, 1518, 1113, 1140, 42, 43,
    57, 4, 28, 544, 1097, 355, 237, 370, 267, 1371, 1597, 345, 377, 1148, 514, 1100, 1233, 1560, 38, 605, 558, 179, 34,
    985, 186, 197, 555, 37, 1236, 41, 92, 575, 108, 439, 10, 118, 112, 111, 1030, 110, 129, 527, 171, 100, 326, 1158,
    1541, 464, 664, 663, 388, 662, 404, 1021, 124, 99, 321, 556, 39, 166, 40, 285, 426, 657, 46, 44, 52, 45, 50, 47, 53,
    54, 56, 49, 55, 35, 867, 98, 365, 1341, 59, 93, 97, 58, 7631, 3976, 4255, 3887, 7518, 3886, 1840, 3884, 1820, 3222,
    3221, 3885, 1882, 4154, 3920, 3053, 3933, 1899, 4146, 3969, 1892, 1896, 78689, 3277, 3966, 22031, 22014, 3996,
    3839, 7551, 7707, 7752, 4216, 7587, 20943, 21888, 7792, 77537, 78900, 78901, 680003, 679693, 700845, 700846, 20836,
    20868, 21025, 712947, 455, 7844, 21862, 1838, 7663, 21778, 21482, 175, 533, 21468, 7576, 21114, 20931, 7589, 7802,
    21269, 21021, 21892, 533, 3921, 7537, 21358, 20893, 36, 21179, 21613, 1342, 22032, 21379, 7807, 21672, 3910, 21130
]

# 生成URL列表
urls = []
for checkin_date in dates:  # 从后往前遍历日期
    checkout_date = checkin_date + timedelta(days=1)
    checkin_str = checkin_date.strftime("%Y-%m-%d")
    checkout_str = checkout_date.strftime("%Y-%m-%d")
    
    for city_id in city_ids:  # 遍历城市ID
        url = f"https://hk.trip.com/hotels/list?city={city_id}&countryId=1&checkIn={checkin_str}&checkOut={checkout_str}"
        urls.append(url)

# 保存到文件
with open('generated_urls.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(urls))

print(f"已生成 {len(urls)} 条URL，保存至文件：generated_urls.txt")
print(f"日期范围：{start_date_str} 到 {end_date_str}")
print(f"城市数量：{len(city_ids)}")
print(f"每天生成的URL数量：{len(city_ids)}")
print(f"URL生成顺序：从 {end_date_str} 到 {start_date_str}")

# 生成台湾省酒店URL
generate_taiwan_urls(start_date_str, end_date_str)