# 携程数据采集器

这是一个用于采集携程（Ctrip）旅游数据的爬虫项目。

## 项目结构

```
.
├── xc_hotel/          # 酒店数据采集脚本
│   ├── cities/        # 城市数据处理
│   ├── script/        # 主要爬虫脚本
│   └── result_plus/   # 采集结果
├── xc_airplane/       # 机票数据（数据文件未上传）
├── xc_trians/         # 火车票数据（数据文件未上传）
└── script.py          # 主脚本
```

## 功能模块

### 酒店数据采集 (xc_hotel)
- `get_url.py` - 获取酒店URL
- `get_detail_*.py` - 获取酒店详细信息（多线程）
- `collect_hotel_name.py` - 收集酒店名称
- `save_trip_html.py` - 保存页面HTML
- `csv2json.py` - 数据格式转换

### 城市数据处理
- `city.py` - 城市数据处理
- `city_id_mapper.py` - 城市ID映射
- `filter_city_id_map.py` - 过滤城市ID
- `find_missing_important_cities.py` - 查找缺失的重要城市

## 说明

⚠️ **注意**: 
- 本仓库仅包含爬虫代码，不包含采集的数据文件（CSV、ZIP等）
- 数据文件体积较大，已在 `.gitignore` 中排除
- 使用前请确保遵守携程网站的使用条款和 robots.txt

## 使用方法

1. 安装依赖（请根据脚本需求自行安装）
2. 配置相关参数
3. 运行对应的爬虫脚本

## License

请合理使用爬虫，遵守相关法律法规。
