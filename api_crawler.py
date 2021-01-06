import requests
import json
import pymongo
from time import sleep

#参数
# query=药店    是你想查询的内容
# region=郑州   是你想查询的城市
# page_num={}   是页码, 意思是第几页
# page_size=20     是每页显示的个数
# ak=你的百度地图api授权码  
queries = ["客栈","酒店","旅馆","民宿","宾馆","旅社"]
city = "北京"
ak = ""
url = 'http://api.map.baidu.com/place/v2/search?query={}&region={}&output=json&output=json&ak={}&page_num={}&page_size=50&scope=2'
#连接mongo
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.hotels
collection = db.hotel

def getData(query,city,i):    
    response = requests.get(url.format(query,city,ak,i))               # 对网页进行请求
    jsondata = json.loads(response.text)          			# 对下载的内容进行loads
    for j in jsondata['results']:
        #print(j,'\n')
        result={
            'name':j.get('name'),
            'tag':j['detail_info'].get('tag'),
            'lat':j['location'].get('lat'),
            'lng':j['location'].get('lng'),
            'address':j.get('address'),
            'province':j.get('province'),
            'city':j.get('city'),
            'area':j.get('area'),
            'tel':j.get('telephone'),
            'score':j['detail_info'].get('overall_rating')
        }
        print(result, '\n')
        collection.update({'name': result['name']}, {'$set': result}, True) #数据库去重
    return jsondata["results"]

if __name__=="__main__":
    #页数i
    for query in queries:
        i = 0
        while i<=100:#循环请求
            res=getData(query,city,i)
            if not res:
                break
            sleep(5) #防止被阻止访问，sleep一下
            print(i)
            i+=1
    client.close()
    
