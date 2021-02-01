# -*- coding: utf-8 -*-

import operator
import matplotlib
import matplotlib.pyplot as plt
import pymongo
from numpy import *
from matplotlib.pyplot import savefig
from matplotlib.font_manager import FontProperties


font = FontProperties(fname=r"c:/windows/fonts/simhei.ttf", size=14)
'''
预设点
[45.841353610943806, 125.39431165654267]
[44.16085263857831, 124.1989944536762]
[45.814647133748295, 126.06725778506494]
[46.242360758120995, 125.16046514885441]
[45.27, 124.71]
'''

#  输入分类点集
def load_data_set():
    dots = array([[45.841353610943806, 125.39431165654267], [44.16085263857831, 124.1989944536762],
                  [45.814647133748295, 126.06725778506494], [46.242360758120995, 125.16046514885441],
                  [45.27, 124.71]])
    labels = ['A', 'B', 'C', 'D', 'E']
    return dots, labels


def classify(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    diffMat = tile(inX, (dataSetSize, 1))-dataSet
    sqDiffMat = diffMat**2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances**0.5
    sortedDistances = distances.argsort()
    classCount = {}
    for i in range(k):
        voteLabel = labels[sortedDistances[i]]
        classCount[voteLabel] = classCount.get(voteLabel, 0) + 1
    sortedClassCount = sorted(classCount.items(),
                            key=operator.itemgetter(1), reverse=True)
    for i in sortedClassCount:
        print(i)
    return sortedClassCount[0][0]


client = pymongo.MongoClient('localhost', 27017)
db = client['earthquake']
col = db['20180528--松原地震']
testResults = []
dotRecords = []
testDots, testLabels = load_data_set()
for item in col.find().limit(2000):
    x = item['epi_lat']
    y = item['epi_lon']
    result = classify([x, y], testDots, testLabels, 3)
    dotRecords.append([x, y])
    testResults.append(result)
    print(x, ' ', y)
    print('classified as ', result)
dotDict = {'A': 1,
           'B': 1,
           'C': 1,
           'D': 1,
           'E': 1}
for i in testResults:
    dotDict[i] += 1
print(dotDict)
testResults = [ord(i)-ord('A')+1 for i in testResults]
resultMat = zeros((len(testResults), 2))
for i in range(len(testResults)):
    resultMat[i, :] = [dotRecords[i][0], dotRecords[i][1]]
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(resultMat[:, 0], resultMat[:, 1], 1.0*array(testResults), 15.0*array(testResults))
savefig("C:/Users/97272/Desktop/output/"+str('20180528--松原地震')+"clusterResult.png")
plt.show()

