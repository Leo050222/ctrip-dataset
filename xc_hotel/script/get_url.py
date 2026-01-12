import requests

url = "https://hk.trip.com/hotels/harbin-hotel-detail-115580956/domei-hotel-harbin-east-railway-station-engineering-university/?locale=zh-HK&curr=HKD"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

# 保存响应的文本内容到HTML文件
with open("output.html", "w", encoding="utf-8") as f:
    f.write(response.text)