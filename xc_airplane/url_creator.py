# departurePlace = {'bjs','sha','tsn','ckg','sjw','shp','shf','tyn','dat','cih','het','bav','xil','hlh','hld','wua','cif','tgo','nzh','hrb','ndg','mdg','jmu','hek','cgq','jil','ynj','she','dlc','ddg','iob','jng','chg','nkg','lyg','ntg','czx','xuz','ynz','wux','foc','xmn','wus','jjn','kow','hgh','wnz','ngb','yiw','hsn','juz','hyn','khn','jdz','jiu','jgs','tna','weh','tao','ynt','jng','wef','doy','lyi','hfe','txn','fug','aqg','cgo','nny','lya','ayn','csx','dyg','cgd','hny','hjj','llf','dax','wuh','yih','xfn','shs','enh','can','zuh','szx','swa','mxz','zha','shg','xin','nng','kwl','lzh','wuz','bhy','hak','syx','ctu','lzo','ybp','mig','jzh','pzi','dax','wxn','xic','nao','gys','kwe','zyi','ava','ten','kmg','ljg','jhg','dlu','sym','bsd','lnj','zat','yua','lum','dig','lxa','bpx','acx','urc','khg','yin','krl','aku','htn','aat','hmi','kry','fyn','tcg','kca','iqm','sia','eny','aka','uyn','hzg','dnh','jgn','chw','iqn','lhw','xnn','goq','inc','hkg','mfm'}
# arrivePlace = {'bjs','sha','tsn','ckg','sjw','shp','shf','tyn','dat','cih','het','bav','xil','hlh','hld','wua','cif','tgo','nzh','hrb','ndg','mdg','jmu','hek','cgq','jil','ynj','she','dlc','ddg','iob','jng','chg','nkg','lyg','ntg','czx','xuz','ynz','wux','foc','xmn','wus','jjn','kow','hgh','wnz','ngb','yiw','hsn','juz','hyn','khn','jdz','jiu','jgs','tna','weh','tao','ynt','jng','wef','doy','lyi','hfe','txn','fug','aqg','cgo','nny','lya','ayn','csx','dyg','cgd','hny','hjj','llf','dax','wuh','yih','xfn','shs','enh','can','zuh','szx','swa','mxz','zha','shg','xin','nng','kwl','lzh','wuz','bhy','hak','syx','ctu','lzo','ybp','mig','jzh','pzi','dax','wxn','xic','nao','gys','kwe','zyi','ava','ten','kmg','ljg','jhg','dlu','sym','bsd','lnj','zat','yua','lum','dig','lxa','bpx','acx','urc','khg','yin','krl','aku','htn','aat','hmi','kry','fyn','tcg','kca','iqm','sia','eny','aka','uyn','hzg','dnh','jgn','chw','iqn','lhw','xnn','goq','inc','hkg','mfm'}
# departureDate = {}

# 'https://flights.ctrip.com/online/list/oneway-' + departurePlace + '-' + arrivePlace + '?depdate='+ departureDate + '&cabin=y_s_c_f&adult=1&child=0&infant=0'

# 导入所需模块
import itertools

departurePlace = {'bjs','sha','tsn','ckg','sjw','shp','shf','tyn','dat','cih','het','bav','xil','hlh','hld','wua','cif','tgo','nzh','hrb','ndg','mdg','jmu','hek','cgq','jil','ynj','she','dlc','ddg','iob','jng','chg','nkg','lyg','ntg','czx','xuz','ynz','wux','foc','xmn','wus','jjn','kow','hgh','wnz','ngb','yiw','hsn','juz','hyn','khn','jdz','jiu','jgs','tna','weh','tao','ynt','jng','wef','doy','lyi','hfe','txn','fug','aqg','cgo','nny','lya','ayn','csx','dyg','cgd','hny','hjj','llf','dax','wuh','yih','xfn','shs','enh','can','zuh','szx','swa','mxz','zha','shg','xin','nng','kwl','lzh','wuz','bhy','hak','syx','ctu','lzo','ybp','mig','jzh','pzi','dax','wxn','xic','nao','gys','kwe','zyi','ava','ten','kmg','ljg','jhg','dlu','sym','bsd','lnj','zat','yua','lum','dig','lxa','bpx','acx','urc','khg','yin','krl','aku','htn','aat','hmi','kry','fyn','tcg','kca','iqm','sia','eny','aka','uyn','hzg','dnh','jgn','chw','iqn','lhw','xnn','goq','inc','hkg','mfm'}
arrivePlace = {'bjs','sha','tsn','ckg','sjw','shp','shf','tyn','dat','cih','het','bav','xil','hlh','hld','wua','cif','tgo','nzh','hrb','ndg','mdg','jmu','hek','cgq','jil','ynj','she','dlc','ddg','iob','jng','chg','nkg','lyg','ntg','czx','xuz','ynz','wux','foc','xmn','wus','jjn','kow','hgh','wnz','ngb','yiw','hsn','juz','hyn','khn','jdz','jiu','jgs','tna','weh','tao','ynt','jng','wef','doy','lyi','hfe','txn','fug','aqg','cgo','nny','lya','ayn','csx','dyg','cgd','hny','hjj','llf','dax','wuh','yih','xfn','shs','enh','can','zuh','szx','swa','mxz','zha','shg','xin','nng','kwl','lzh','wuz','bhy','hak','syx','ctu','lzo','ybp','mig','jzh','pzi','dax','wxn','xic','nao','gys','kwe','zyi','ava','ten','kmg','ljg','jhg','dlu','sym','bsd','lnj','zat','yua','lum','dig','lxa','bpx','acx','urc','khg','yin','krl','aku','htn','aat','hmi','kry','fyn','tcg','kca','iqm','sia','eny','aka','uyn','hzg','dnh','jgn','chw','iqn','lhw','xnn','goq','inc','hkg','mfm'}
departureDates = {'2025-06-01','2025-06-02','2025-06-03','2025-06-04','2025-06-05','2025-06-06','2025-06-07','2025-06-08','2025-06-09','2025-06-010','2025-06-11','2025-06-12','2025-06-13','2025-06-14','2025-06-15','2025-06-16','2025-06-17','2025-06-18','2025-06-19','2025-06-20','2025-06-21','2025-06-22','2025-06-23','2025-06-24','2025-06-25','2025-06-26','2025-06-27','2025-06-28','2025-06-29','2025-06-30'}

# 基础URL
base_url = 'https://flights.ctrip.com/online/list/oneway-'

# 生成所有可能的城市对
city_pairs = list(itertools.product(departurePlace, arrivePlace))
# 过滤掉出发地和目的地相同的情况
filtered_pairs = [pair for pair in city_pairs if pair[0] != pair[1]]

# 为每个日期和每个城市对生成URL
urls = []
for date in sorted(departureDates):  # 对日期进行排序
    for dep, arr in filtered_pairs:
        url = f"{base_url}{dep}-{arr}?depdate={date}&cabin=y_s_c_f&adult=1&child=0&infant=0"
        urls.append(url)

# 将所有URL写入单个文件
with open('all_urls.txt', 'w', encoding='utf-8') as file:
    for url in urls:
        file.write(url + '\n')
print(f"所有URL已写入 'all_urls.txt' 文件，共 {len(urls)} 个URL。")