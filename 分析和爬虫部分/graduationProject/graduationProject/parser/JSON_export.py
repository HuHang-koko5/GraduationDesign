# coding:utf-8
import pymongo
from datetime import datetime, timedelta
from graduationProject.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME
from graduationProject.parser.doc_tag import NaiveBayes
import json
import re
client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
db = client[DB_NAME]
ocol = db['earthquake_SI']
for item in ocol.find():
    col = db[item['name']]
    output = []
    count = 0
    for i in col.find():
        i['_id'] = re.findall("'(.*)'", i.get('_id').__repr__())[0]
        output.append(i)
        count += 1
        print(i['content'])
        if count == 500:
            dir = 'C:/Users/97272/Desktop/mongo/' + item['name'] + '.json'
            with open(dir , 'w', encoding='utf-8') as jf:
                jf.write(json.dumps(output, ensure_ascii=False))
                output = []
                count = 0
    print(item['name'],' finish')