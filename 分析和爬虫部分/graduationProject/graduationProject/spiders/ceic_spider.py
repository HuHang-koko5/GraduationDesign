import scrapy
import re
import json
import pymongo
import time
from graduationProject.items import CeicItem

class Ceicspider(scrapy.Spider):
    name = "ceic"
    start_urls = ["http://www.ceic.ac.cn/ajax/search?page=2&&start=&&end=&&jingdu1=&&jingdu2=&&weidu1=&&weidu2=&&height1=&&height2=&&zhenji1=&&zhenji2=&&callback=jQuery180007840009800485714_1546756935805&_=1546758053736"]
    ajax_pre_url = "http://www.ceic.ac.cn/ajax/search?page="
    ajax_suf_url = "&&start=&&end=&&jingdu1=&&jingdu2=&&weidu1=&&weidu2=&&height1=&&height2=&&zhenji1=&&zhenji2=&&callback=jQuery180007840009800485714_1546756935805&_=1546758053736"

    def __init__(self):
        self.page = 1
        self.client = pymongo.MongoClient('localhost')
        self.collection = self.client['earthquake']['ceic_data']

    def closed(self, reason):
        self.client.close()

    def parse(self, response):
        print("in page :", self.page)
        if len(response.body) != 0:
            print("=========now parse page:", self.page)
            p1 = re.compile(r'[[][{](.*)[}][]]', re.S)
            re_data = re.search(p1, response.text)
            json_data = re_data.group()
            raw_data = json.loads(json_data)
            count = 0
            for i in raw_data:
                item = CeicItem()
                item['time'] = i['O_TIME']
                item['epi_lat'] = i['EPI_LAT']
                item['epi_lon'] = i['EPI_LON']
                item['epi_depth'] = i['EPI_DEPTH']
                item['mag'] = i['M']
                item['location'] = i['LOCATION_C']
                count += 1
                self.collection.update({'time':item['time']}, item, upsert=True)
            self.page += 1
            time.sleep(2)
            if self.page<4:
                print(count, "====>NEXT")
                new_url = self.ajax_pre_url + str(self.page) + self.ajax_suf_url
                yield scrapy.Request(new_url, callback=self.parse)

'''

    time = scrapy.Field()
    epi_lat = scrapy.Field()
    epi_lon = scrapy.Field()
    epi_depth = scrapy.Field()
    mag = scrapy.Field()
    location = scrapy.Field()
    http://www.ceic.ac.cn/ajax/search?page=1&&start=&&end=&&jingdu1=&&jingdu2=&&weidu1=&&weidu2=&&height1=&&height2=&&zhenji1=&&zhenji2=&&callback=jQuery180007840009800485714_1546756935805&_=1546758053736
    http://www.ceic.ac.cn/ajax/search?page=2&&start=&&end=&&jingdu1=&&jingdu2=&&weidu1=&&weidu2=&&height1=&&height2=&&zhenji1=&&zhenji2=&&callback=jQuery180008025349545091687_1546761703600&_=1546764869040
'''