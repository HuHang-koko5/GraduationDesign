import numpy as np
import matplotlib.pyplot as plt
import math
import random
import pymongo

def makeDot(lat, lon, num, radius):
    dots = []
    for i in range(num):
        theta = random.random() * 2 * np.pi
        r = random.uniform(0, radius)
        x = math.sin(theta) * (r ** 0.5) + lat
        y = math.cos(theta) * (r ** 0.5) + lon
        dots.append([x, y])
    return dots

dots = []
center_lat = 32.81
center_lon = 94.93
cnum = random.randint(4, 7)
dots = makeDot(center_lat, center_lon, cnum, 2.5)
print(dots)
dots.append([center_lat, center_lon])
dots.append([center_lat, center_lon])
client = pymongo.MongoClient('localhost', 27017)
db = client['earthquake']
col = db["20161017--杂多县地震"]
counter = 0
for doc in col.find():
    print('-----', counter)
    counter += 1
    index = random.randint(0, len(dots)-1)
    nlat, nlon = dots[index][0], dots[index][1]
    npos = makeDot(nlat, nlon, 1, 0.2)
    x, y = npos[0][0], npos[0][1]
    print(doc['_id'])
    print(doc['epi_lat'], doc['epi_lon'])
    # print(x, ',', y, ' ', index)
    col.update_one({'_id': doc['_id']}, {"$set": {'epi_lat': x, 'epi_lon': y}})
    new_doc =col.find_one({'_id': doc['_id']})
    print(new_doc['epi_lat'], ' ', new_doc['epi_lon'])

'''
纬度： 28.24
经度： 104.95
'''