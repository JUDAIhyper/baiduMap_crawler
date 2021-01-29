import requests
import json
import pymongo
from time import sleep
import threading
from pathos.multiprocessing import ProcessingPool as Pool

#参数
# query=药店    想查询的内容
# region=北京   想查询的城市
# page_num={}   页码, 意思是第几页
# page_size=20     每页显示的个数
# ak=你的百度地图api授权码
queries = ["客栈", "酒店", "旅馆", "民宿", "宾馆"]
cities = ["深圳","长沙","武汉"]
ak = ""
base_url = 'http://api.map.baidu.com/place/v2/search?query={}&region={}&output=json&output=json&ak={}&page_num={}&page_size=50&scope=2'
#连接mongo
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.hotels
collection = db.hotel

def getUrl(query, city, i):
    url = base_url.format(query, city, ak, i)
    return url

def getData(url):
    response = requests.get(url)               # 对网页进行请求
    jsondata = json.loads(response.text)       # 对下载的内容进行loads
    for j in jsondata['results']:
        #print(j,'\n')
        result = {
            'name': j.get('name'),
            'tag': j['detail_info'].get('tag'),
            'lat': j['location'].get('lat'),
            'lng': j['location'].get('lng'),
            'address': j.get('address'),
            'province': j.get('province'),
            'city': j.get('city'),
            'area': j.get('area'),
            'tel': j.get('telephone') if j.get('telephone') else 0,
            'score': j['detail_info'].get('overall_rating') if j['detail_info'].get('overall_rating') else 0
        }
        print(result, '\n')
        collection.update({'name': result['name']}, {
                          '$set': result}, True)  # 数据库去重
    return jsondata["results"]

def run(city,query):
    for i in range(0, 10):  # 循环请求
        url = getUrl(query, city, i)
        t = threading.Thread(target=getData, args=(url,)) #加入了多线程
        t.setDaemon(True)
        t.start()
        if not getData(url):
            break
        #print("========================",res,"========================")
        sleep(1)  # 防止被阻止访问，sleep一下
        t.join()


if __name__ == "__main__":
    # for city in cities:
    #     for query in queries:
    #         run(city,query)
    pool=Pool()
    pool.map(run,cities,queries)
    pool.close()
    pool.join()
    client.close()
