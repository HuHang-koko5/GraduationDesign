import  pymongo
import numpy as np
from numpy import  *
from graduationProject.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME
from pyecharts import Line


class SI_result:
    def __init__(self):
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]

    def setLabel(self):
        col = self.db['earthquake_SI']
        for item in col.find():
            print("set label")
            print(item['name'])
            sinput = input()
            col.update_one({'name': item['name']}, {'$set': {
                    'label': sinput
                }})

    # 梯度上升法
    def gradAscent(self, dataMatIn, classLabels):
        dataMatrix = mat(dataMatIn)              # convert to NumPy matrix
        labelMat = mat(classLabels).transpose()  # convert to NumPy matrix
        m, n = shape(dataMatrix)
        alpha = 0.001
        maxCycles = 500
        weights = ones((n, 1))
        for k in range(maxCycles):              # heavy on matrix operations
            h = sigmoid(dataMatrix*weights)     # matrix mult
            error = (labelMat - h)              # vector subtraction
            weights = weights + alpha * dataMatrix.transpose() * error # matrix mult
        return weights

    # 随机梯度上升
    def stocGradAscent1(self, dataMatrix, classLabels, numIter=50):
        m, n = shape(dataMatrix)
        weights = ones(n)  # initialize to all ones
        for j in range(numIter):
            dataIndex = list(range(m))
            for i in range(m):
                alpha = 4 / (1.0 + j + i) + 0.0001  # apha decreases with iteration, does not
                randIndex = int(random.uniform(0, len(dataIndex)))  # go to 0 because of the constant
                h = sigmoid(sum(dataMatrix[randIndex] * weights))
                error = classLabels[randIndex] - h
                '''
                print("-----------------")
                print(weights)
                print(alpha)
                print(error)
                print(dataMatrix[randIndex])
                print("-----------------")
    
                '''
                weights = weights + alpha * error * dataMatrix[randIndex]
                del (dataIndex[randIndex])
        return weights


    def loadDataSet(self, level):
        col = self.db['earthquake_SI']
        dataMat = []
        labelMat = []
        for item in col.find():
            perNum = item['personalNum']
            allNum = item['totalNum']
            perPer = [0, 0, 0, 0, 0, 0]
            allPer = [0, 0, 0, 0, 0, 0]
            perCount = 0
            allCount = 0
            index = 0
            for perP, allP in zip(perNum, allNum):
                perP = float(perP)
                allP = float(perP)
                perCount += perP
                allCount += allP
                if allP == 0:
                    perPer[index] = 0
                else:
                    perPer[index] = float(perP/allP)
                if allCount == 0:
                    allPer[index] == 0
                else:
                    allPer[index] = float(perCount/allCount)
                index += 1
            label = item['label']
            para1 = item['proPara']  # 省份影响
            para2 = item['timePara']  # 时间影响
            para3 = item['SI-V'] * 100  # 5级烈度比例
            para4 = item['SI-IV']  # 4级烈度比例
            para5 = item['SI-III']   # 3级烈度比例
            # para6 = perPer[0]  # 第一小时内tag比例
            para6 = db[item['name']].count() / 1000
            para7 = allPer[5]  # 整体tag比例
            ParaList = []
            ParaList.append(1.0)
            ParaList.append(float(para1))
            ParaList.append(float(para2))
            ParaList.append(float(para3))
            ParaList.append(float(para4))
            ParaList.append(float(para5))
            ParaList.append(float(para6))
            ParaList.append(float(para7))
            dataMat.append(ParaList)
            if level+4 < float(label) <= level+5:
                label = 1
            else:
                label = 0
            labelMat.append(label)
        return dataMat, labelMat

    def getWeights(self):
        weightArr = []
        for i in range(5):
            dataArr, labelMat = self.loadDataSet(i)
            weightArr.append(self.stocGradAscent1(array(dataArr), labelMat))
        return weightArr

    def classifyVector(self, inX, Aweights):
        maxNum = 0
        plist  = []
        maxLabel = -1
        for i in range(5):
            prob = sigmoid(sum(inX*Aweights[i]))
            plist.append(prob*100)
            if prob > maxNum:
                maxLabel = i+5
                maxNum =prob
        print("possibility  = ", plist)
        return maxLabel

    def getPara(self, itemName):
        col = self.db['earthquake_SI']
        for item in col.find({'name': itemName}):
            perNum = item['personalNum']
            allNum = item['totalNum']
            perPer = [0, 0, 0, 0, 0, 0]
            allPer = [0, 0, 0, 0, 0, 0]
            perCount = 0
            allCount = 0
            index = 0
            for perP, allP in zip(perNum, allNum):
                perP = float(perP)
                allP = float(perP)
                perCount += perP
                allCount += allP
                if allP == 0:
                    perPer[index] = 0
                else:
                    perPer[index] = float(perP / allP)
                if allCount == 0:
                    allPer[index] == 0
                else:
                    allPer[index] = float(perCount / allCount)
                index += 1
            label = item['label']
            para1 = item['proPara']  # 省份影响
            para2 = item['timePara']  # 时间影响
            para3 = item['SI-V'] * 100 # 5级烈度比例
            para4 = item['SI-IV']  # 4级烈度比例
            para5 = item['SI-III']   # 3级烈度比例
            para6 = db[item['name']].count() / 1000
            # para6 = perPer[0]  # 第一小时内tag比例
            para7 = allPer[5]  # 整体tag比例
            ParaList = []
            ParaList.append(1.0)
            ParaList.append(float(para1))
            ParaList.append(float(para2))
            ParaList.append(float(para3))
            ParaList.append(float(para4))
            ParaList.append(float(para5))
            ParaList.append(float(para6))
            ParaList.append(float(para7))
        return ParaList, label


# sigmoid函数
def sigmoid(inX):
    return 1.0/(1+exp(-inX))


# 计算评估值
def judgement (Para, label,weightList):
    resultList = []
    for i in range(5):
        print('------', i)
        TP = 0
        FP = 0
        FN = 0
        TN = 0
        for j in range(len(Para)):
            item = Para[j]
            xlabel = label[j]
            prob = sigmoid(sum(item*weightList[i]))
            print(prob,' ', xlabel, ' ', i+5,end='')
            if prob >= 0.3:
                #TP
                if int(xlabel) == i+5:
                   TP += 1
                   print(' TP')
                #FP
                else:
                    FP += 1
                    print(' FP')
            else:
                if int(xlabel) == i+5:
                    FN += 1
                    print(' FN')
                else:
                    TN += 1
                    print(' TN')
        resultList.append([TP, FP, FN, TN])
    return resultList



'''
#绘制分类结果折线图
client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
db = client[DB_NAME]
col = db['earthquake_SI']
exc = 0
hxc = 0
lxc = 0
elx = 0
count = 0
ParaList = []
tagList = []
labelList = []
nameIndex= []
index = 0
SI = SI_result()
weightList = SI.getWeights()
for item in col.find().sort('label'):
    if item['name'] != '20160102--林口县地震':
        # print(item['name'])
        index += 1
        Para, label = SI.getPara(item['name'])
        ParaList.append(Para)
        tagList.append(SI.classifyVector(Para,weightList))
        labelList.append(int(label))
        nameIndex.append(item['name'])
print (labelList)
print (tagList)
lineGra = Line('LR 分类结果','实际烈度与评估烈度比较')
lineGra.add('实际烈度', nameIndex, labelList)
lineGra.add('评估密度', nameIndex, tagList)
lineGra.render('C:/Users/97272/Desktop/output/LR.html')
'''


'''
#计算评估系数
resultOF = SI.judgement(ParaList, labelList, weightList)
inum = 4
for i in resultOF:
    inum += 1
    print('------------第', inum ,'级烈度分类器评估-------------------------------')
    print('FN------FP------FN------TN')
    for k in i:
        print(k/len(labelList)*100, '%  ',end='')
    print()
    print("误检率 fp rate = FP/TN+FP = ", round(i[1] / (i[1] + i[3]), 2))
    print("漏检率 miss rate = FN/TP+FN = ", round(i[2] / (i[0] + i[2]), 2))
    print("查准率 precision rate = TP/TP+FP = ",round(i[0]/(i[0]+i[1]),2))
    print('查全率 recall rate = TP/TP+FN = ',round(i[0]/(i[0]+i[2]),2))
    print('准确率 Correctly Classified rate = TP+TN/ALL  = ',round((i[0]+i[3])/(i[0]+i[1]+i[2]+i[3]),2))
'''





