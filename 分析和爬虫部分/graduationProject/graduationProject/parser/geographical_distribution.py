# coding:utf-8
from graduationProject.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME
import pymongo
from pyecharts import Geo, Style
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import matplotlib
from matplotlib.font_manager import FontProperties
from graduationProject.parser.seismic_intensity import *
from graduationProject.parser.doc_tag import NaiveBayes
import os


font = FontProperties(fname=r"c:/windows/fonts/simhei.ttf", size=14)


class GeoDistribution(object):
    def __init__(self, tableName):
        self.tableName = tableName
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]
        self.col = self.db[self.tableName]
        self.outputDB = self.db['earthquake_SI']
        print(self.col.full_name, "  loaded count = ", self.col.count())
        self.SI= SI()
        # self.NB = NaiveBayes()

    # 加载训练集，返回进行分词后的结果
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

    #
    def geographical_distribution(self, time):
        dir_name = time[0:4] + time[5:7] + time[8:10]
        lon, lat, doc, tag, content, ttime, cities = self.load_doc(time)
        SI_value = []
        for item, tag in zip(doc, tag):
            SI_value.append(self.SI.SI_content_2(item, tag))
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
        vrange = [0, 0, 0, 0, 0]
        for i in range(len(df)):
            if df.iloc[i]['value'] > 8:
                vrange[0] += 1
            elif df.iloc[i]['value'] > 6:
                vrange[1] += 1
            elif df.iloc[i]['value'] > 4:
                vrange[2] += 1
            elif df.iloc[i]['value'] > 2:
                vrange[3] += 1
            else:
                vrange[4] += 1
        print('percentage:')
        for item in vrange:
            print(item/len(df)*100, '%')
        if self.outputDB.find_one({'name': self.tableName}):
            self.outputDB.update_one({'name': self.tableName}, {'$set': {
                                                                'time': time,
                                                                'SI-V': vrange[0]/len(df),
                                                                'SI-IV': vrange[1]/len(df),
                                                                'SI-III': vrange[2]/len(df),
                                                                'SI-II': vrange[3]/len(df),
                                                                'SI-I': vrange[4]/len(df),
                                                                }})
        else:
            self.outputDB.insert_one({'name': self.tableName,
                                      'time': time,
                                      'SI-V': vrange[0]/len(df),
                                      'SI-IV': vrange[1]/len(df),
                                      'SI-III': vrange[2]/len(df),
                                      'SI-II': vrange[3]/len(df),
                                      'SI-I': vrange[4]/len(df),
                                      })

        if not os.path.exists(dir_name + '/'):
            print("make new dir")
            os.makedirs(dir_name + '/')
        style = Style(title_color="#fff", title_pos="center",
                      width=800, height=800, background_color="#404a59")
        total_geo = Geo('总体分布图', **style.init_style)
        total_geo.add("", attr, value, visual_range=[1, 10], symbol_size=5,
                      visual_text_color="#fff",
                      is_visualmap=True, maptype='china', visual_split_number=10,
                      geo_cities_coords=geo_coords)
        total_geo.render(dir_name + '/' + dir_name+'_all.html')
        # heatmap
        htotal_geo = Geo('总体热力分布图', **style.init_style)
        htotal_geo.add("", attr, value, visual_range=[1, 10], symbol_size=5,
                      visual_text_color="#fff", type="heatmap",
                      is_visualmap=True, maptype='china', visual_split_number=10,
                      geo_cities_coords=geo_coords)
        arg = htotal_geo.get_js_dependencies()

        htotal_geo.render(dir_name + '/' + dir_name + '_allH.html')
        start_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        current_time = start_time
        timeIndex = []
        timeDoc = []
        for i in range(7):
            current_time = current_time + timedelta(hours=1)
            timeIndex.append(current_time)
            timeDoc.append([])

        for ilon, ilat, ittime, icities, ivalue in zip(lon, lat, ttime, cities, SI_value):
            for i in range(7):
                if i == 6 or ittime < timeIndex[i+1]:
                    timeDoc[i].append([ilon, ilat, ittime, icities, ivalue])

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
            tdf_dic = {'lon': tlon, 'lat': tlat, 'time': tttime, 'city': tcities, 'value': tvalue}
            tdf = pd.DataFrame(tdf_dic)
            tgeo_coords = {tdf.iloc[i]['city']: [tdf.iloc[i]['lat'], tdf.iloc[i]['lon']] for i in range(len(tdf))}
            tattr = list(tdf['city'])
            tvalue = list(tdf['value'])
            tgeo = Geo(str(i+1) + '小时内分布图', **style.init_style)
            tgeo.add("", tattr, tvalue, visual_range=[5, 10], symbol_size=3,
                     visual_text_color="#fff",
                     is_visualmap=True, maptype='china', visual_split_number=10,
                     geo_cities_coords=tgeo_coords)
            tgeo.render(dir_name + '/ ' + dir_name + str(i+1) + 'h.html')
            # heatmap
            htgeo = Geo(str(i + 1) + '小时内热力分布图', **style.init_style)
            htgeo.add("", tattr, tvalue, visual_range=[5, 10], symbol_size=3,
                     visual_text_color="#fff", type='heatmap',
                     is_visualmap=True, maptype='china', visual_split_number=10,
                     geo_cities_coords=tgeo_coords)
            htgeo.render(dir_name + '/ ' + dir_name + str(i + 1) + 'H.html')

'''
        for i in ttime[50:53]:
            if i < after_1H:
                re = '<'
            else:
                re = '>'
            print(i, ' ', re, ' ', after_1H)
            if i < after_2H:
                re = '<'
            else:
                re = '>'
            print(i, ' ', re, ' ', after_2H )

'''

'''
# use
client = pymongo.MongoClient("localhost", 27017)
mdb = client["earthquake"]
col = mdb['earthquake_SI']
for item in col.find():
    GD = GeoDistribution(item['name'])
    GD.geographical_distribution(item['time'])
'''


# GD.load_doc()