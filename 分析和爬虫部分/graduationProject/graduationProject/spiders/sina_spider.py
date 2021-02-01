import scrapy
import random
from graduationProject.items import SinaItem
import urllib
import re
import pymongo
from graduationProject.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME


class Sinaspider(scrapy.Spider):
    name = "Sina"
    account = [
        {"id":'sw7xnyys82co@game.weibo.com', 'psw':'aic3jmrcm'},
        {"id": 'eq05kmkmmtb2@game.weibo.com', 'psw': 'unl70p3jk'},
        {"id": 'huzyuz1cm3fy@game.weibo.com', 'psw': 'wsbpsdmw0'},
        {"id": 'ojqupmkokk6d@game.weibo.com', 'psw': 'pa378r8of'}
    ]

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        db = client[DB_NAME]
        self.col = db["ceic_data"]
        self.province = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林',
                         '黑龙江', '江苏', '浙江', '安徽', '福建',
                         '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
                         '四川', '贵州', '云南', '陕西', '甘肃', '青海', '内蒙古',
                         '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
        self.KEY_WORD = "九寨沟地震"
        self.KEY_TIME = "20170809"
        self.latitude = 33.20  # 纬度
        self.longitude = 103.82  # 经度
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

    def makeLocation(self, dots):
        dotIndex = random.randint(0, len(dots) - 1)
        lat = dots[dotIndex][0] + (random.random() - 0.5) * 8
        lon = dots[dotIndex][1] + (random.random() - 0.5) * 8
        return lat, lon, dotIndex

    def start_requests(self):


        '''
                for raw in self.col.find():
            mag = raw["mag"]
            if float(str(mag)) > 4:
                if (raw['location'][0:2] in self.province) or (raw['location'][0:3] in self.province):
                    self.KEY_WORD = list(filter(None, re.split(r'[地区盟州市]', raw['location'])))[-1] + '地震'
                    tpiece = raw['time'].split(" ")[0].split("-")
                    self.KEY_TIME = '20170808'
                    for i in tpiece:
                        self.KEY_TIME += i
                    # print(self.KEY_WORD, '  ', self.KEY_TIME)
                    key_w = urllib.parse.quote(self.KEY_WORD)
                    time.sleep(1)

        :return:
        '''

        key_w = urllib.parse.quote(self.KEY_WORD)
        new_url = "https://weibo.cn/search/mblog?hideSearchFrame=&keyword={keyword}&advancedfilter=1&starttime={time}&endtime={time}&sort=time&page=1".format(keyword=key_w, time=self.KEY_TIME)
        yield scrapy.Request(url=new_url, callback=self.parse_Page)


    def parse_Page(self, response):
        print("now in ", response.url.split("page")[1])
        tweets = response.xpath('//div[@class="c"]')
        for tweet in tweets:
            try:
                user_name = tweet.xpath("div/a[@class='nk']/text()").extract()

                if user_name == []:
                    pass
                else:
                    user_blog = tweet.xpath("div/a[@class='nk']/@href").extract()
                    content = tweet.xpath("div/span[@class='ctt']/text()").extract()
                    ct = tweet.xpath("div/span[@class='ct']/text()").extract()
                    if ct:
                        time_piece = ct[0].split("来自")
                        ttime = time_piece[0].strip()
                    else:
                        ttime = None
                    like_a = tweet.xpath('.//a[contains(text(),"赞[")]/text()')
                    if like_a:
                        like_num = int(re.search('\d+', like_a[-1].extract()).group())
                    else:
                        like_num = None
                    repost_a = tweet.xpath('.//a[contains(text(),"转发[")]/text()')
                    if repost_a:
                        repost_num = int(re.search('\d+', repost_a[-1].extract()).group())
                    else:
                        repost_num = None
                    comment_a = tweet.xpath('.//a[contains(text(),"评论[")]/text()')
                    if comment_a:
                        comment_num = int(re.search('\d+', comment_a[-1].extract()).group())
                    else:
                        comment_num = None

                    # print("ttime  ", ttime)
                    tweet_lat, tweet_lon, dotIndex = self.makeLocation(self.dots)
                    if ttime:
                        tuser_name = str(user_name).lstrip("['").rstrip("']")
                        tuser_blog = str(user_blog).lstrip("'[").rstrip("]'")
                        tcontent = str(content).strip('[').strip(']').lstrip("', '").lstrip(':')
                        #print("item--------------------")
                        url_keyword = re.search(r'keyword=(.+)&advance', response.url).group(1)
                        url_keyword = urllib.parse.unquote(url_keyword)
                        url_time =str(int(re.search(r'starttime=(.+)&endtime', response.url).group(1))-1)
                        # print("key word is ", url_keyword)
                        # print("key time is ", url_time)
                        # print(tuser_name)
                        # print(tuser_blog)
                        # print(tcontent)
                        # print(ttime)
                        # print(like_num)
                        # print(repost_num)
                        # print(comment_num)
                        sina_item = SinaItem()
                        sina_item['user_name'] = tuser_name
                        # print("!!", sina_item['user_name'])
                        sina_item['user_blog'] = tuser_blog
                        # print("!!", sina_item['user_blog'])
                        sina_item['content'] = tcontent
                        # print("!!", sina_item['content'])
                        sina_item['t_time'] = ttime
                        # print("!!", sina_item['t_time'])
                        sina_item['like_num'] = like_num
                        # print("!!", sina_item['like_num'])
                        sina_item['repost_num'] = repost_num
                        # print("!!", sina_item['repost_num'])
                        sina_item['comment_num'] = comment_num
                        sina_item['key_word'] = url_keyword
                        sina_item['key_time'] = url_time
                        sina_item['epi_lat'] = tweet_lat
                        sina_item['epi_lon'] = tweet_lon
                        sina_item['dotIndex'] = dotIndex
                        print("!!", sina_item['user_name'])
                        # print("!!", sina_item['comment_num'])
                        yield sina_item
                    else:
                        pass
            except Exception as e:
                pass
        if response.url.endswith('page=1'):
            all_page = re.search(r'&nbsp;1/(\d+)页', response.text)
            print("all_page", all_page)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page+20):     # test
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield scrapy.Request(page_url, self.parse_Page, dont_filter=True, meta=response.meta)


'''
 like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['like_num'] = int(re.search('\d+', like_num).group())

                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())

'''


'''
https://weibo.cn/search/mblog?hideSearchFrame=&keyword=%E7%8F%99%E5%8E%BF%E5%9C%B0%E9%9C%87&advancedfilter=1&starttime=20190102&endtime=20190104&sort=time&page=2
https://weibo.cn/search/mblog?hideSearchFrame=&keyword={keyword}&page={page}
'''




