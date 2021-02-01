# -*- coding: utf-8 -*-
import pymongo
from numpy import *
import string
import bosonnlp
import random

'''
   1 公众号转发或官方发布数据（无用）
   2 个人用户发布实时舆情数据（有用）
   '''
class NaiveBayes:
    def __init__(self):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client['earthquake']
        self.train_db = self.db['NB_training_set']
        self.nlp = bosonnlp.BosonNLP('LRI-rwV3.33271.MDHpdgmH67eQ')

    # 加载中文标点表，返回list
    @staticmethod
    def load_chnpun():
        f = open('C:/Users/97272/graduationProject/graduationProject/Resources/chnpun.txt', 'r+', encoding='utf-8')
        k = f.read()
        chnpun = []
        for i in k:
            chnpun.append(i)
        f.close()
        return chnpun

    # 加载停用词表，返回list
    @staticmethod
    def load_stop_words():
        f = open('C:/Users/97272/graduationProject/graduationProject/Resources/stopwords.txt', 'r+', encoding='utf-8')
        lines = f.readlines()
        stopwords = []
        for word in lines:
            stopwords.append(str(word.rstrip('\n')))
        f.close()
        return stopwords

    # convert original content list to word list
    # para self doc_list(list)
    # return doc_list(list)
    def tweets2WordList(self, doc_list):
        chnpun = self.load_chnpun()
        stopwords = self.load_stop_words()
        trans_rule1 = str.maketrans({skey: None for skey in chnpun})
        trans_rule2 = str.maketrans({skey: None for skey in string.punctuation})
        transRule3 = str.maketrans({skey: None for skey in string.digits or string.ascii_letters})
        # trans_rule4 = str.maketrans({skey: None for skey in stopwords})
        tag_lists = []
        word_count = 0
        for doc in doc_list:
            doc_index = doc_list.index(doc)
            new_doc = doc
            while '\\u200b' in new_doc:
                new_doc = new_doc.replace('\\u200b', '')
            new_doc = new_doc.translate(trans_rule1).translate(trans_rule2).translate(transRule3).strip()
            result = self.nlp.tag(new_doc)
            word_list = result[0]['word']
            tag_list = result[0]['tag']
            wordNum = len(word_list)
            final_words = []
            final_tags = []
            for i in range(wordNum):
                if (len(word_list[i]) != 1) or((word_list[i] >= u'\u4e00') and (word_list[i] <= u'\u9fa5')):
                    final_words.append(word_list[i])
                    final_tags.append(tag_list[i])
            doc_list[doc_index] = final_words
            tag_lists.append(final_tags)
            word_count += 1
            print("NaiveBayes cleared index: ", word_count)
        return doc_list, tag_lists

    # 标注训练集
    def build_training_set(self, collection_name):
        col = self.db[collection_name]
        print("Start Manual tagging ")
        content_list = []
        tag_list = []
        for tweet in col.find().limit(300):
            ctx = tweet['content']
            print(ctx)
            print("input tag:")
            tag = int(input())
            content_list.append(ctx)
            tag_list.append(tag)
        doc_list = self.tweets2WordList(content_list)
        for doc, tag in zip(doc_list, tag_list):
            if self.train_db.find_one({'content': doc}):
                pass
            else:
                self.train_db.insert_one({'content': doc, 'tag': tag})

    # 输入col.find()的结果
    def add_training_set(self, doc_list):
        content_list = []
        wtag_list = []
        for tweet in doc_list:
            ctx = tweet['content']
            print(ctx)
            print("input tag")
            try:
                tag = int(input())
            except ValueError as e:
                tag = int(input("invalid error! input again:"))
            if tag != 3:
                content_list.append(ctx)
                wtag_list.append(tag)
        words_list = self.tweets2WordList(content_list)
        '''
        '''
        for doc, tag in zip(words_list, wtag_list):
            print("doc ", doc)
            print("tag ", tag)
            if self.train_db.find_one({'content': doc}):
                pass
            else:
                self.train_db.insert_one({'content': doc, 'tag': tag})

    # bayes part
    # 加载训练集
    def load_data_set(self, num):
        doc_list = []
        tag_list = []
        for data in self.train_db.find().limit(num):
            doc_list.append(data['content'])
            tag_list.append(data['tag'])
        return doc_list, tag_list

    # 生成词汇表
    def create_vocablist(self, dataSet):
        vocabSet = set([])  # create empty set
        for document in dataSet:
            vocabSet = vocabSet | set(document)  # union of the two sets
        return list(vocabSet)

    # 将doc向量化
    def set_of_words_to_vec(self, vocab_list, input_set):
        returnVec = [0] * len(vocab_list)
        for word in input_set:
            if word in vocab_list:
                returnVec[vocab_list.index(word)] = 1
            else:
                print("the word: %s is not in my Vocabulary!" % word)
        return returnVec

    # p1Num p2Num是词汇表（参数）在1类和2类中出现的次数的向量
    # p1Vect,p2Vect是出现在I类和2类中各自参数的数量和
    def trainNB0(self, trainMatrix, trainCategory):
        numTrainDocs = len(trainMatrix)  # 样本数
        numWords = len(trainMatrix[0])  # 单词书
        pAbusive = sum(trainCategory) / float(numTrainDocs)  # 无效语言的比例(pPositive = 1 - pA)
        p0Num = ones(numWords)
        p1Num = ones(numWords)  # change to ones()
        p0Denom = 2.0
        p1Denom = 2.0  # change to 2.0
        for i in range(numTrainDocs):
            if trainCategory[i] == 1:
                p1Num += trainMatrix[i]
                p1Denom += sum(trainMatrix[i])
            else:
                p0Num += trainMatrix[i]
                p0Denom += sum(trainMatrix[i])
        p1Vect = log(p1Num / p1Denom)  # change to log()
        p0Vect = log(p0Num / p0Denom)  # change to log()
        return p0Vect, p1Vect, pAbusive

    # 返回分类结果
    def classifyNB(self, vec2Classify, p0Vec, p1Vec, pClass1):
        p1 = sum(vec2Classify * p1Vec) + log(pClass1)  # element-wise mult
        p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)
        if p1 > p0:
            return 1
        else:
            return 0

    #返回词袋向量
    def bagOfWords2VecMN(self, vocabList, inputSet):
        returnVec = [0] * len(vocabList)
        for word in inputSet:
            if word in vocabList:
                returnVec[vocabList.index(word)] += 1
        return returnVec

    # get the classify result of the given content list
    # para self content_list(list)
    # return wordsList(nlp word result), Ctag_list(prop of word in list), tag_result(classify result of the content)
    def contents_classify(self, contents_list):
        wordsList, Ctag_list = self.tweets2WordList(contents_list)
        train_list, tag_list = self.load_data_set(450)
        new_tag_list = [i - 1 for i in tag_list]
        tag_list = new_tag_list
        vocabList = self.create_vocablist(train_list)
        # print('vocabList length :', len(vocabList))
        trainMat = []
        for doc in train_list:
            trainMat.append(self.bagOfWords2VecMN(vocabList, doc))
        p0v, p1v, pAb = self.trainNB0(array(trainMat), array(tag_list))
        # print('p0v= ', p0v)
        # print('p1v= ', p1v)
        # print('pAb= ', pAb)
        tag_result = []
        for words in wordsList:
            wordVector = self.bagOfWords2VecMN(vocabList, words)
            tag_result.append(self.classifyNB(array(wordVector), p0v, p1v, pAb))
        return wordsList, Ctag_list, tag_result
'''
# 添加训练集
NB = NaiveBayes()
cl = NB.client['earthquake']
t_col = cl['20130420--芦山地震']
i = 0
results = []
for col in t_col.find().limit(300):
    i += 1
    if i > 150:
        results.append(col)
NB.add_training_set(results)
'''

'''


# 测试准确度
NB = NaiveBayes()
doc_list, tag_list = NB.load_data_set(450)
new_tag_list = [i-1 for i in tag_list]
test_tag_list = []
test_list = []
for i in range(30):
    test_tag_list.append(new_tag_list[i*10])
    test_list.append(doc_list[i*10])
    new_tag_list.pop(i*10)
    doc_list.pop(i*10)
tag_list = new_tag_list
train_list = doc_list
print(tag_list)

vocabList = NB.create_vocablist(train_list)
print(len(vocabList))
trainMat = []
for doc in train_list:
    trainMat.append(NB.bagOfWords2VecMN(vocabList, doc))
p0v, p1v, pAb = NB.trainNB0(array(trainMat), array(tag_list))
print('p0v= ', p0v)
print('p1v= ', p1v)
print('pAb= ', pAb)
errorCount = 0
for docIndex, tag in zip(test_list, test_tag_list):
    wordVector = NB.bagOfWords2VecMN(vocabList, docIndex)
    if NB.classifyNB(array(wordVector), p0v, p1v, pAb) != tag:
        errorCount += 1
        print("classify error", docIndex)
        print("should be ", tag)
if errorCount:
    print("error rate ", float(errorCount)/len(test_list))
else:
    print('no error!')



'''

'''
# USE 
NB = NaiveBayes()
cl = NB.client['earthquake']
t_col = cl['20180528--松原地震']
col = t_col.find().limit(10)
tweets = []
for tweet in col:
    tweets.append(tweet['content'])
tags = NB.contents_classify(tweets)
for tweet, tag in zip(tweets, tags):
    print(tag)
    print(tweet)

'''
