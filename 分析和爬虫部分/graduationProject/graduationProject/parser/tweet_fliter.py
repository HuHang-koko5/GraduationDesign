# coding:utf-8

from graduationProject.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME
from graduationProject.parser.filter import ClientFilter
import pymongo
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from bosonnlp import BosonNLP
import string
import re

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

class TweetFilter(object):
    def __init__(self, table_name):
        self.table_name = table_name
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        db = client[DB_NAME]
        self.col = db[self.table_name]

    def parse_tweet(self):
        normal_tweets = []
        publish_tweets = []
        normal = publish = 0
        client_filter = ClientFilter()
        print(self.table_name[0:4])
        for raw in self.col.find():
            #print(raw['user_name'])
            if client_filter.check(raw['user_name']):
                #print(raw['user_name'], " normal user")
                t_time = datetime.strptime(self.table_name[0:4]+"年"+raw['time'], "%Y年%m月%d日 %H:%M")
                normal_tweets.append([raw['content'], datetime.strftime(t_time, "%Y-%m-%d %H:%M")])
                normal = normal + 1
            else:
                #print(raw['user_name'], " publisher")
                publish = publish + 1
        for i in normal_tweets:
            print(i)

    def time_analy(self):
        cf = ClientFilter()
        dates = pd.date_range(start=self.table_name[0:11]+" 0:00", periods=48, freq="1H")
        df = pd.DataFrame(0, index=dates, columns=['tweets'])
        tweet_times=[]
        for raw in self.col.find():
            if cf.check(raw['user_name']):
                t_time = datetime.strptime(self.table_name[0:4]+"年"+raw['time'],"%Y年%m月%d日 %H:%M")
                tweet_times.append(t_time)
        for i in tweet_times:
            for j in df.index:
                if i.hour < j.hour+1 and i.day == j.day:
                    df.loc[j, ['tweets']] += 1
                    break
        matplotlib.matplotlib_fname()
        #print(df)
        dfplt = df.plot(kind='bar', title=self.table_name)

        plt.xlabel("time")
        plt.ylabel("tweets")
        plt.show()

    def remove_common_words(self,s:str):
        keys = ["珙县", "地震", "秒拍", "深度", "月日时分", "中国", "震源", "经度", "纬度",
                "震感", "受灾", "测定", "正式", "级", "台网", "市", "县", "区"]
        province = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林',
                    '黑龙江', '江苏', '浙江', '安徽', '福建',
                    '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
                    '四川', '贵州', '云南', '陕西', '甘肃', '青海', '内蒙古',
                    '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
        for key in keys + province:
            s = s.replace(key, "")
        return s




i = TweetFilter("20170808--九寨沟地震")
i.test()
print(i.table_name)



'''
useless

    def test(self):
        tweets_content = []
        cf = ClientFilter()
        for raw in self.col.find():
            if cf.check(raw['user_name']):
                tweets_content.append(raw['content'])
        nlp = BosonNLP('LRI-rwV3.33271.MDHpdgmH67eQ')
        #result = nlp.sentiment(tweets_content, model='weibo')

        trantab1 = str.maketrans({key: None for key in string.punctuation})
       #  file io
        f = open('C:/Users/97272/Desktop/chnpun.txt', 'r+', encoding='utf-8')
        k = f.read()
        chnpun = []
        for i in k:
            chnpun.append(i)
        f.close()
        #  file io
        trantab2 = str.maketrans({key: None for key in chnpun})
        word_dic = {}
        for i in range(300):
            tweet = re.compile(u"[^\u4e00-\u9fa5^]+").sub('', tweets_content[i])
            #k = tweet.translate(trantab1).translate(trantab2)
            k = self.remove_common_words(tweet)
            result = nlp.extract_keywords(k, top_k=5)
            for word in result:
                if word[1] in word_dic.keys():
                    word_dic[word[1]][0] += word[0]
                    word_dic[word[1]][1] += 1
                else:
                    word_dic[word[1]] = [word[0], 1]

        df_list = pd.DataFrame.from_dict(word_dic, orient='index', columns=['Freq', 'Times'])
        df_list.sort_values(by='Times').to_csv(path_or_buf="C:/Users/97272/Desktop/out.csv")

'''