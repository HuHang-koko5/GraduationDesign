import scrapy
from datetime import datetime, timedelta
import pymongo
import urllib
import time
import random
from graduationProject.items import SinaItem
from graduationProject.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME


class Sinacomspider(scrapy.Spider):
    name = "Sinacom"

    def __init__(self):
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]
        self.KEY_WORD = "荣县地震"   # 关键字
        self.KEY_TIME = "20190225 08:40"  # 时间
        self.KEY_DATE = self.KEY_TIME[0:8]
        self.timestamp = []
        dtime = datetime.strptime(self.KEY_TIME, "%Y%m%d %H:%M")
        for i in range(24):
            self.timestamp.append(dtime)
            dtime += timedelta(hours=1)
        print("time stamps :")
        for stamp in self.timestamp:
            print(stamp)
        self.latitude = 29.48  # 纬度
        self.longitude = 104.49  # 经度
        self.dots = self.makeDot(self.latitude, self.longitude)

    def makeDot(self, epi_lat, epi_lon):
        dot = []
        dot.append([epi_lat, epi_lon])
        dotNum = random.randint(3, 5)
        for i in range(dotNum):
            lat = epi_lat + (random.random() - 0.5) * 30
            lon = epi_lon + (random.random() - 0.5) * 30
            dot.append([lat, lon])
        return dot

    @staticmethod
    def make_location( dots):
        dotIndex = random.randint(0, len(dots) - 1)
        lat = dots[dotIndex][0] + (random.random() - 0.5) * 8
        lon = dots[dotIndex][1] + (random.random() - 0.5) * 8
        return lat, lon, dotIndex

    def start_requests(self):
        r_url = "https://s.weibo.com/weibo?q={keyword}&scope=ori&suball=1&timescope=custom:{starttime}:{endtime}&Refer=g&page=1"
        url_keyword = urllib.parse.quote(self.KEY_WORD)
        for stamp in self.timestamp:
            start_time = datetime.strftime(stamp, "%Y-%m-%d-%H")
            end_time = datetime.strftime(stamp + timedelta(hours=1), "%Y-%m-%d-%H")
            new_url = r_url.format(keyword=url_keyword, starttime=start_time, endtime=end_time)
            yield scrapy.Request(url=new_url, callback=self.parse_Page)


    def parse_Page(self, response):
        print("+++++++++++++++++++++++++++++++++++")
        print("now in ", response.url.split("page")[1])
        tweets = response.xpath("//div[@class='card-wrap']")
        if tweets:
            print("get lists")
        for tweet in tweets:
            try:
                # get user name
                name = tweet.xpath("div/div/div/div[@class='info']/div/a[@class='name']/text()").extract()[0]
                blog = tweet.xpath("div/div/div/div[@class='info']/div/a[@class='name']//@href") .extract()[0]
                if name == []:
                    pass
                else:
                    # print("--------------")
                    # print("name：", name)
                    # print("blog: ", blog)
                    ntext = ''
                    content = tweet.xpath("div/div/div/p[@class='txt']//text()").extract()
                    # remove space in content[0]
                    for text in content:
                        if text == content[0]:
                            ntext += text[20:]
                        else:
                            ntext += text
                    # print("content:", ntext)
                    ttime = str(tweet.xpath("div/div/div/p[@class='from']/a[1]/text()").extract())
                    ttime = ttime[28:45]
                    # print("time: ", ttime)
                    tweet_lat, tweet_lon, dotIndex = self.make_location(self.dots)
                    sina_item = SinaItem()
                    sina_item['user_name'] = name
                    # print("!!", sina_item['user_name'])
                    sina_item['user_blog'] = blog
                    # print("!!", sina_item['user_blog'])
                    sina_item['content'] = ntext
                    # print("!!", sina_item['content'])
                    sina_item['t_time'] = ttime
                    # print("!!", sina_item['t_time'])
                    sina_item['like_num'] = None
                    # print("!!", sina_item['like_num'])
                    sina_item['repost_num'] = None
                    # print("!!", sina_item['repost_num'])
                    sina_item['comment_num'] = None
                    sina_item['key_word'] = self.KEY_WORD
                    sina_item['key_time'] = self.KEY_DATE
                    sina_item['epi_lat'] = tweet_lat
                    sina_item['epi_lon'] = tweet_lon
                    sina_item['dotIndex'] = dotIndex
                    print("!!  ", sina_item['user_name'])
                    yield sina_item
                    print("--------------")
            except Exception as e:
                pass
        if response.url.endswith('page=1'):
            page_list = response.xpath("//ul[@class='s-scroll']/li")
            for page in page_list[1:]:
                #print("page : ", page.xpath("a/text()").extract()[0])
                next_url = "https://s.weibo.com" + page.xpath("a//@href").extract()[0]
                print("url : ", next_url)
                time.sleep(1)
                yield scrapy.Request(next_url, self.parse_Page, dont_filter=True, meta=response.meta)


# //*[@id="pl_feedlist_index"]/div[2]/div[1]/div/div[1]/div[2]/div[1]/div[2]/a[1]
