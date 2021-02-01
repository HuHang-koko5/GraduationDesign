# coding:utf-8


from graduationProject.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME
import pymongo
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import matplotlib
from matplotlib.font_manager import FontProperties
# from graduationProject.parser.doc_tag import NaiveBayes

font = FontProperties(fname=r"c:/windows/fonts/simhei.ttf", size=14)


class TimeDistribute(object):
    def __init__(self, tableName):
        self.tableName = tableName
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]
        self.col = self.db[self.tableName]
        print(self.col.full_name, "  loaded ", self.col.count())
        # self.NB = NaiveBayes()
        self.loc = []

    # 加载数据
    def load_doc(self):
        for raw in self.col.find():
            epi_lat = raw['epi_lat']
            epi_lon = raw['epi_lon']
            ttime = raw['t_time']
            self.loc.append([ttime, epi_lat, epi_lon])

    # 生成时间分布图
    def time_distribution(self, doc):
        doc = self.loc
        # startTime = pd.Timestamp(self.tableName[0:8] + "0:00")
        startTime = datetime.strptime(self.tableName[0:8] + " 8:00", "%Y%m%d %H:%M")
        dates = pd.date_range(start=startTime, periods=24, freq="1H")
        time_dis = pd.DataFrame(0, index=dates, columns=["tweets"])
        timeList = []
        for tweet in doc:
            t_time = datetime.strptime(tweet[0], "%Y年%m月%d日 %H:%M")
            timeList.append(t_time)
        for time in timeList:
            for j in time_dis.index:
                if time.hour < j.hour+1 and time.day == j.day:
                # if time.minute < j.minute+10 and time.day == j.day and time.hour == j.hour:
                    time_dis.loc[j, ['tweets']] += 1
                    break
        matplotlib.matplotlib_fname()
        dfplt = time_dis.plot(kind="bar")
        plt.title(self.tableName, fontproperties=font)
        plt.xlabel("Time")
        plt.ylabel("tweers")
        plt.subplots_adjust(bottom=0.4)
        savefig("C:/Users/97272/Desktop/output/"+str(self.tableName)+".png")
        plt.show()


'''
# use
TD = TimeDistribute("20130420--芦山地震")
TD.load_doc()
TD.time_distribution()
'''

