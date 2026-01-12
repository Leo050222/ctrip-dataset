from DrissionPage import ChromiumPage
import time
import traceback
import json
import os

INDEX = 5

def get_detail(dict, result, INDEX):
    page = ChromiumPage()
    # 1. 提取已采集酒店名集合
    collected_hotel_names = set(item['hotel_name'] for item in result)
    data = result.copy()  # 2. 直接在已有数据基础上追加
    total = len(dict)
    for idx, (hotel_name, url) in enumerate(dict.items(), 1):
        print(f"\n[{idx}/{total}] 开始采集酒店: {hotel_name}，URL: {url}")
        if hotel_name in collected_hotel_names:
            print(f"[跳过] {hotel_name} 已在结果中，跳过采集。")
            continue
        try:
            page.get(url)
            print(f"已打开页面: {url}")
            try:
                print("等待房型列表(mainRoomList__UlISo)出现...")
                page.wait.ele_displayed('@class=mainRoomList__UlISo')
                main_list_div = page.ele('@class=mainRoomList__UlISo')
                if main_list_div:
                    print("找到房型列表div，开始采集房型...")
                    room_divs = main_list_div.eles('@class=commonRoomCard__BpNjl')
                    print(f"共找到 {len(room_divs)} 个房型div")
                    room_list = []
                    for room_idx, room_div in enumerate(room_divs, 1):
                        print(f"  [房型{room_idx}/{len(room_divs)}] 采集中...")
                        try:
                            room_name = room_div.ele('@class=commonRoomCard-title__iYBn2').text
                            print(f"    房型名: {room_name}")
                        except Exception as e:
                            print(f"    获取房型名出错: {e}")
                            room_name = None
                        try:
                            room_type = room_div.ele('@class=baseRoom-bedsInfo_title__vhMHW').text
                            print(f"    房型类型: {room_type}")
                        except Exception as e:
                            print(f"    获取房型类型出错: {e}")
                            room_type = None
                        try:
                            baseRoom_main_ele = room_div.ele('@class=baseRoom-facility__a54rp')
                            baseRoom_eles = baseRoom_main_ele.eles('tag:span') if baseRoom_main_ele else []
                            room_baseinfo = [baseRoom_ele.text for baseRoom_ele in baseRoom_eles]
                            print(f"    房型基础信息: {room_baseinfo}")
                        except Exception as e:
                            print(f"    获取房型基础信息出错: {e}")
                            room_baseinfo = []
                        try:
                            room_detail_button = room_div.ele('@class=_3fBxrt84aR59Wm31poTt baseRoom-roomAmenitiesA__E8R8X')
                            if room_detail_button:
                                print("    点击房型详情按钮...（弹窗）")
                                room_detail_button.click()
                                room_facilities_info = {}
                                try:
                                    room_facilities_ele = page.ele('@class=baseRoomLayer-facilitys__XTzrl')
                                    lis = room_facilities_ele.eles('tag:li') if room_facilities_ele else []
                                    print(f"    采集房型设施，共{len(lis)}项...")
                                    for li in lis:
                                        try:
                                            title = li.ele('@class=baseRoomLayer-facilityItem_title__OzIZr').text
                                            contents = li.eles('@class=baseRoomLayer-subItem_content__q9G_u')
                                            data_temp = [content.text for content in contents]
                                            print(f"      设施: {title}，内容: {data_temp}")
                                            room_facilities_info[title] = data_temp
                                        except Exception as e:
                                            print(f"      解析房型设施项出错: {e}")
                                except Exception as e:
                                    print(f"    获取房型设施详情出错: {e}")
                                    room_facilities_info = {}
                                try:
                                    cancel = page.ele('@class = smarticon u-icon u-icon-ic_new_close_line u-icon_ic_new_close_line o7kWSgJIe2nzJrtBhUs0')
                                    if cancel:
                                        print("    关闭详情弹窗...")
                                        cancel.click()
                                except Exception as e:
                                    print(f"    关闭详情弹窗出错: {e}")
                            else:
                                print("    未找到房型详情按钮，跳过设施采集。")
                                room_facilities_info = {}
                        except Exception as e:
                            print(f"    点击房型详情按钮或获取详情出错: {e}")
                            room_facilities_info = {}
                        room_list.append({
                            "room_name": room_name,
                            "room_type": room_type,
                            "room_baseinfo": room_baseinfo,
                            "room_facilities_info": room_facilities_info
                        })
                    data.append({
                        "hotel_name": hotel_name,
                        "room_list": room_list
                    })
                    print(f"[完成] {hotel_name} 共采集 {len(room_list)} 个房型。")
                else:
                    print("未找到class=mainRoomList__UlISo的div元素")
            except Exception as e:
                print(f"处理酒店 {hotel_name} 时出错: {e}")
                traceback.print_exc()
        except Exception as e:
            print(f"打开酒店页面 {url} 时出错: {e}")
            traceback.print_exc()
        os.makedirs('result_plus', exist_ok=True)
        # 每处理完一个酒店就保存一次，采用追加后的data
        with open(rf'result_plus/result_part{INDEX}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'[保存] 已保存到 result_plus/result_part{INDEX}.json，当前已采集酒店数：{len(data)}')
    print(f'全部采集完成，本批次共采集酒店数：{len(data)}')
    page.close()
    page.quit()


def main():
    with open(f'hotel_name_url_map_clear_part{INDEX}.json', 'r', encoding='utf-8') as f:
        dict = json.load(f)
    if os.path.exists(rf'result_plus/result_part{INDEX}.json'):
        with open(rf'result_plus/result_part{INDEX}.json', 'r', encoding='utf-8') as f:
            result = json.load(f)
    else:
        result = []
    get_detail(dict, result,INDEX)

if __name__ == "__main__":
    main()