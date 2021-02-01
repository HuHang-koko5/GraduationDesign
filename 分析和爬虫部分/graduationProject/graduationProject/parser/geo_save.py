# coding:utf-8
from graduationProject.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME
import pymongo
from pyecharts import Geo, Style
from datetime import datetime, timedelta
import pandas as pd
from matplotlib.font_manager import FontProperties
from graduationProject.parser.seismic_intensity import *
from graduationProject.parser.doc_tag import NaiveBayes


font = FontProperties(fname=r"c:/windows/fonts/simhei.ttf", size=14)


# save Echarts data for website

class GeoDistribution(object):
    def __init__(self, tableName):
        self.tableName = tableName
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]
        self.col = self.db[self.tableName]
        self.outputDB = self.db["geo_" + tableName[0:8]]
        print(self.col.full_name, "  loaded count = ", self.col.count())
        # self.NB = NaiveBayes()

    def load_doc(self, time):
        NB = NaiveBayes()
        ucontent = []
        ulon = []
        ulat = []
        uttime = []
        ucities = []
        content = []
        lon = []
        lat = []
        doc = []
        tag = []
        ttime = []
        cities = []
        for raw in self.col.find():
            if ('今天' not in raw['t_time']) and ('前' not in raw['t_time']):
                ucontent.append(raw['content'])
                ulat.append(raw['epi_lat'])
                ulon.append(raw['epi_lon'])
                try:
                    dt = datetime.strptime(raw['t_time'], "%Y年%m月%d日 %H:%M")
                except ValueError:
                    dt = datetime.strptime(time[0:4] + "年"+raw['t_time'], "%Y年%m月%d日 %H:%M\\n   ")

                uttime.append(dt)
                ucities.append(int(raw['dotIndex']) + 1)
        wordList, tags, NBtag = NB.contents_classify(ucontent)
        for i in range(len(ucontent)):
            if NBtag[i]:
                content.append(ucontent[i])
                lat.append(ulat[i])
                lon.append(ulon[i])
                ttime.append(uttime[i])
                cities.append(i)
                print(ucontent[i], ' in ', NBtag[i])
                doc.append(wordList[i])
                tag.append(tags[i])
                print(tags[i])
                print("--------------------------")
            else:
                pass
                print(ucontent[i], ' out ', NBtag[i])
                print("--------------------------")

        return lat, lon, doc, tag, content, ttime, cities

    def geographical_distribution(self, time):
        dir_name = time[0:4] + time[5:7] + time[8:10]
        lon, lat, doc, tag, content, ttime, cities = self.load_doc(time)
        SI_value = []
        for item, tag in zip(doc, tag):
            SI_value.append(SI_content_2(item, tag))
        vs = SI_value.copy()
        vs.sort()
        minSI = vs[0]
        vs.sort(reverse=True)
        maxSI = vs[0]
        print(SI_value)
        print('max-', maxSI, 'min- ', minSI)
        for i in range(len(SI_value)):
            if SI_value[i] > 12:
                SI_value[i] = 12
            else:
                SI_value[i] = 10*(SI_value[i]-minSI)/(12-minSI)
        if len(lon) > 7000:
            wlon = []
            wlat = []
            wttime = []
            wcities = []
            wSI_value = []
            for ilon, ilat, ittime, icities, ivalue in zip(lon, lat, ttime, cities, SI_value):
                if ivalue > 1.5:
                    wlon.append(ilon)
                    wlat.append(ilat)
                    wttime.append(ittime)
                    wcities.append(icities)
                    wSI_value.append(ivalue)
            lon = wlon
            lat = wlat
            ttime = wttime
            cities = wcities
            SI_value = wSI_value

        df_dic = {'lon': lon, 'lat': lat,  'time': ttime, 'city': cities, 'value': SI_value}
        df = pd.DataFrame(df_dic)
        print(df)
        geo_coords = {df.iloc[i]['city']: [df.iloc[i]['lat'], df.iloc[i]['lon']] for i in range(len(df))}
        attr = list(df['city'])
        value = list(df['value'])

        start_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        current_time = start_time
        timeIndex = []
        timeDoc = []
        for i in range(7):
            current_time = current_time + timedelta(hours=1)
            timeIndex.append(current_time)
            timeDoc.append([])

        for ilon, ilat, ittime, icities, ivalue in zip(lon, lat, ttime, cities, SI_value):
            flag = 1
            for i in range(7):
                if (i == 6 or ittime < timeIndex[i+1]) and flag:
                    flag = 0
                    timeDoc[i].append([ilon, ilat, ittime, icities, ivalue])
                    if self.outputDB.find_one({'lon': ilon, 'lat': ilat, 'time': ittime}):
                        self.outputDB.update_one({'name': self.tableName}, {'$set': {'lon': ilon,
                                                                                     'lat': ilat,
                                                                                     'city': icities,
                                                                                     'time': ittime,
                                                                                     'value': ivalue,
                                                                                     'index': i
                                                                                     }})
                    else:
                        self.outputDB.insert_one({'lon': ilon,
                                                  'lat': ilat,
                                                  'city': icities,
                                                  'time': ittime,
                                                  'value': ivalue,
                                                  'index': i
                                                  })


        for i in range(6):
            print("in hour ", i, 'has', len(timeDoc[i]))
            tlon = []
            tlat = []
            tttime = []
            tcities = []
            tvalue = []
            for sdoc in timeDoc[i]:
                tlon.append(sdoc[0])
                tlat.append(sdoc[1])
                tttime.append(sdoc[2])
                tcities.append(sdoc[3])
                tvalue.append(sdoc[4])


'''
for item in col.find():
    GD = GeoDistribution(item['name'])
    GD.geographical_distribution(item['time'])
'''
client = pymongo.MongoClient("localhost", 27017)
mdb = client["earthquake"]
col = mdb['earthquake_SI']
for item in col.find():
    GD = GeoDistribution(item['name'])
    GD.geographical_distribution(item['time'])

# GD.load_doc()