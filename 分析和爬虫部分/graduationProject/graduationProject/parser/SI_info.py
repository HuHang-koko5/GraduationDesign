import pymongo
from datetime import datetime, timedelta
from graduationProject.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME
from graduationProject.parser.doc_tag import NaiveBayes


class si_info():

    def __init__(self):
        self.NB = NaiveBayes()
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]
        self.ceic_col = self.db['ceic_data']
        self.output_db = self.db['earthquake_SI']
        self.province = {'北京': 1,
                         '天津': 1,
                         '上海': 1,
                         '重庆': 2,
                         '河北': 2,
                         '山西': 1,
                         '辽宁': 2,
                         '吉林': 3,
                         '黑龙': 1,
                         '江苏': 1,
                         '浙江': 1,
                         '安徽': 1,
                         '福建': 2,
                         '江西': 1,
                         '山东': 2,
                         '河南': 2,
                         '湖北': 1,
                         '湖南': 1,
                         '广东': 2,
                         '海南': 1,
                         '四川': 4,
                         '贵州': 2,
                         '云南': 4,
                         '陕西': 2,
                         '甘肃': 2,
                         '青海': 3,
                         '内蒙': 2,
                         '广西': 1,
                         '西藏': 4,
                         '宁夏': 2,
                         '新疆': 4,
                         '香港': 1,
                         '澳门': 1}

    def get_ceic_data(self, table_name, time):
        for item in self.ceic_col.find():
            if time == item['time']:
                print('match! doc= ', item['location'], item['time'])
                return item['location'][0:2].strip(), item['mag']
        print("item not find!")
        return None, None

    def update_basic_info(self):
        for item in self.output_db.find({'name': '20190225--荣县地震'}):
            print("------------")
            name = item['name']
            time = item['time']
            print('Deal with :', name, time)
            pro, mag = self.get_ceic_data(name, time)
            #province value
            proPara = self.province[pro]
            print("province =", pro, ' value= ', proPara, ' mag= ', mag)
            col = self.db[name]
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            if 22 > time.hour > 18:
                timePara = 1.5
            elif 18 >= time.hour >= 7:
                timePara = 1
            else:
                timePara = 2
            print("timePara = ", timePara)
            timeIndex = []
            docList = []
            onehour = timedelta(hours=1)
            for i in range(6):
                time += onehour
                timeIndex.append(time)
                docList.append([])
            for doc in col.find():
                # this year xx月xx日
                if doc['t_time'][2] == '月':
                    time = "2019年"+doc['t_time']
                else:
                    time = doc['t_time']
                flag = 1
                try:
                    time = datetime.strptime(time, '%Y年%m月%d日 %H:%M\\n   ')
                except ValueError:
                    flag = 0
                if flag:
                    ob = 1
                    for i in range(6):
                        if time < timeIndex[i] and ob:
                            # print(time, '___', timeIndex[i])
                            docList[i].append(doc['content'])
                            ob = 0
            totalNum = [0, 0, 0, 0, 0, 0]
            personalNum = [0, 0, 0, 0, 0, 0]
            for i in range(6):
                print("doc list =", len(docList[i]))
                wordList, tags, NBtag = self.NB.contents_classify(docList[i])
                for j in range(len(NBtag)):
                    totalNum[i] += 1
                    if NBtag[j]:
                        personalNum[i] += 1
            print(personalNum)
            print(totalNum)
            self.output_db.update_one({'name': name}, {'$set': {
                'proPara': proPara,
                'timePara': timePara,
                'personalNum': personalNum,
                'totalNum': totalNum,
            }})


si = si_info()
si.update_basic_info()
