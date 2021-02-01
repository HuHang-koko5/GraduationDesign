import pymongo
import bosonnlp as nlp
import xlrd
'''
    SI_dict:
        {
            'key':词  #unique
            'prop':词性
            'value':数值
        }
'''

class SI:

    # load xlsx file return list[[word],[prop],[value]]
    def load_SI_dict(self):
        import xlrd
        file = "C:/Users/97272/Desktop/毕业设计/SI_dict.xlsx"
        wb = xlrd.open_workbook(filename=file)
        sheet = wb.sheets()[0]
        s = []
        for item in range(sheet.ncols):
            s.append(sheet.col_values(item))
        return s


    # return si value of word(str) in SI dict
    # para: word(str) si(list)
    # return: value(int)
    def get_value(self, word, si_dict):
        if word in si_dict[0]:
            f_value = si_dict[2][si_dict[0].index(word)]
        else:
            f_value = 1
        return f_value


    # get the closet final-tag word's direction
    # para index(str) tag(list) ftag(list)
    # return 0(forward) 1(follow)
    def get_close(self, index, tag, ftag):
        i = 1
        while i+index < len(tag) and index-i >= 0:
            if tag[i+index] in ftag:
                return 1
            elif tag[index-i] in ftag:
                return 0
            else:
                i = i+1
        if i+index < len(tag):
            return 1
        elif index-i >= 0:
            return 0
        else:
            return 0


    # get the SI value of the word list
    # para: doc(list) tag(list)
    # return: i(int)
    def SI_content_1(self, doc, tag):
        # ------------init------------------------------
        si_dict = self.load_SI_dict()
        vtag = ['ns', 'n', 'nt', 'nl', 's', 'v', 'vi', 'vyou', 'a', 'ad', 'm', 'd']
        ntag = ['ns', 'n', 'nt', 'nl', 's']
        atag = ['a', 'd']
        v1tag = ['v', 'vi', 'vyou']
        finaltag = ['ns', 'n', 'nt', 'nl', 's', 'v', 'vi', 'vyou']
        itemNum = len(doc)
        n1doc = []
        n1tag = []
        # ---------------vtag fliter----------------
        for i in range(itemNum):
            if tag[i] in vtag:
                n1doc.append(doc[i])
                n1tag.append(tag[i])
        doc = n1doc
        tag = n1tag
        i = 0
        itemNum = len(tag)
        index_group = []
        value_group = []
        follow_value = 1
        # ----------------final tag fliter ________________
        while i < itemNum:
            if tag[i] not in finaltag:
                # print(doc[i], tag[i], 'removed ')
                if tag[i] not in atag:  # follow-only type
                    # print("follow type:",doc[i],tag[i])
                    if i + 1 < itemNum:  # has follow
                        if i + 1 < itemNum:
                            follow_value *= self.get_value(doc[i], si_dict)
                        #   print("followed", follow_value)
                else:  # both-side type
                    # print("both-side type:",doc[i],tag[i])
                    if self.get_close(i, tag, finaltag) or follow_value != 1:  # follow
                        follow_value = self.get_value(doc[i], si_dict)
                    #  print("followed", follow_value)
                    else:  # forward
                        if len(index_group):
                            value_group[len(index_group) - 1] *= self.get_value(doc[i], si_dict)
                    #   print("forwarded", get_value(doc[i], si_dict))
            else:  # finaltag
                index_group.append(i)
                word_value = follow_value * self.get_value(doc[i], si_dict)
                follow_value = 1
                value_group.append(word_value)
            #   print(doc[i], tag[i], word_value,' added')
            i += 1  # next
        #   --------final gruop---------
        finalNum = len(value_group)
        #for i in range(finalNum):
           # index = index_group[i]
            # output
           # print(i, ' ', doc[index], tag[index], value_group[i])
        # print("ntag:", ntag)
        i = 0
        groupValue = []
        while i in range(finalNum):
           # print("from ", i)
            current_value = 1
            # final word
            if i == finalNum - 1:
                groupValue.append(value_group[i])
                i += 1
            # start with n
            elif tag[index_group[i]] in ntag:
                current_value = value_group[i]
                # mix n(s)
                j = i + 1
                while j < finalNum and (tag[index_group[j]] in ntag):
                  #  print(tag[index_group[j]] in ntag, ' ', tag[index_group[j]], '-> ', doc[index_group[j]])
                    current_value += value_group[j]
                    j += 1
                current_value /= j - i
              #  print("mix ns by", i, ' to ', j - 1)
                i = j
                # n  v exist
                if i < finalNum:
                    # mix vi and v/vi
                    if tag[index_group[i]] == 'vi' and i + 1 < finalNum and tag[index_group[i + 1]] in v1tag:
                        value_group[i + 1] = pow(value_group[i] + value_group[i + 1], 0.5)
                    #    print('mix vi in ', i)
                        i += 1
                    # n v
                    # if  tag[index_group[i]] in v1tag:
                    # n v n exist
                    if i + 1 < finalNum and tag[index_group[i + 1]] in ntag:
                        # n v /n v  ff1
                        if i + 2 < finalNum and tag[index_group[i + 2]] in v1tag:
                        #    print('n v /n v')
                            current_value *= value_group[i]
                            i += 1
                        # n v n / n  ff2
                        elif i + 2 < finalNum and tag[index_group[i + 2]] in ntag:
                        #    print('n v n / n')
                            current_value *= value_group[i] * value_group[i + 1]
                            i += 2
                        # n v n //
                        else:
                        #    print('n v n // ')
                            current_value *= value_group[i] * value_group[i + 1]
                            i += 2
                            # n v / v OR n v /n  OR n v//  ff3
                    else:
                     #   print('n v / v OR n v /n  OR n v//')
                        current_value *= value_group[i]
                        i += 1
                # n//
                else:
                  #  print('n//')
                    i += 1
                groupValue.append(current_value)
             #   print("to ", i - 1, "value=", current_value)
            # start with v
            elif tag[index_group[i]] in v1tag:
                # mix vi and v/vi
                if tag[index_group[i]] == 'vi' and i + 1 < finalNum and tag[index_group[i + 1]] in v1tag:
                    value_group[i + 1] = pow(value_group[i] + value_group[i + 1], 0.5)
                 #   print('mix vi in ', i)
                    i += 1
                current_value = value_group[i]
                i += 1
                # v n exist now in v->
                if i < finalNum:
                    # v n
                    if tag[index_group[i]] in ntag:
                        # v n n
                        if i + 1 < finalNum and tag[index_group[i + 1]] in ntag:
                            if i + 2 < finalNum:
                                # v n /n v  ff1
                                if tag[index_group[i + 2]] in v1tag:
                                    current_value *= value_group[i]
                                    i += 1
                                # v n n /n  ff2
                                elif tag[index_group[i + 2]] in ntag:
                                    current_value *= value_group[i] * value_group[i + 1]
                                    i += 2
                            # v n n //
                            else:
                                current_value *= value_group[i] * value_group[i + 1]
                                i += 2
                        # v n v
                        elif i + 1 < finalNum and tag[index_group[i + 1]] in v1tag:
                            if i + 2 < finalNum:
                                # v n v/v  ff3
                                if tag[index_group[i + 2]] in v1tag:
                                    current_value *= value_group[i] * value_group[i + 1]
                                    i += 2
                                # v n v n
                                elif tag[index_group[i + 2]] in ntag:
                                    if i + 3 < finalNum:
                                        # v n/v n n  ff4
                                        if tag[index_group[i + 3]] in ntag:
                                            current_value *= value_group[i]
                                            i += 1
                                        # v n v n v  ff5
                                        elif tag[index_group[i + 3]] in v1tag:
                                            current_value *= value_group[i] * value_group[i + 1]
                                            i += 2
                                    # v n /v n//
                                    else:
                                        current_value *= value_group[i]
                                        i += 1
                            # v n v//
                            else:
                                current_value *= value_group[i] * value_group[i + 1]
                                i += 1
                    # v / v
                    else:
                        pass
                groupValue.append(current_value)
             #   print("to ", i - 1, "value=", current_value)
        sortedValue = groupValue.copy()
        sortedValue.sort(reverse=True)
        if len(sortedValue) >= 2:
            final_value = sortedValue[0]+sortedValue[1]-1
        else:
            final_value = sortedValue[0]
        print('si value = ', final_value)
        return final_value


# vectorlize
    def SI_content_2(self, doc, tag):
        # ------------init------------------------------
        si_dict = self.load_SI_dict()
        vtag = ['ns', 'n', 'nt', 'nl', 's', 'v', 'vi', 'vyou', 'a', 'ad', 'm', 'd']
        ntag = ['ns', 'n', 'nt', 'nl', 's']
        atag = ['a', 'd']
        v1tag = ['v', 'vi', 'vyou']
        finaltag = ['ns', 'n', 'nt', 'nl', 's', 'v', 'vi', 'vyou']
        itemNum = len(doc)
        n1doc = []
        n1tag = []
        # ---------------vtag fliter----------------
        for i in range(itemNum):
            if tag[i] in vtag:
                n1doc.append(doc[i])
                n1tag.append(tag[i])
        doc = n1doc
        tag = n1tag
        i = 0
        itemNum = len(tag)
        index_group = []
        value_group = []
        follow_value = 1
        # ----------------final tag fliter ________________
        while i < itemNum:
            if tag[i] not in finaltag:
                # print(doc[i], tag[i], 'removed ')
                if tag[i] not in atag:  # follow-only type
                    # print("follow type:",doc[i],tag[i])
                    if i + 1 < itemNum:  # has follow
                        if i + 1 < itemNum:
                            follow_value *= self.get_value(doc[i], si_dict)
                        #   print("followed", follow_value)
                else:  # both-side type
                    # print("both-side type:",doc[i],tag[i])
                    if self.get_close(i, tag, finaltag) or follow_value != 1:  # follow
                        follow_value = self.get_value(doc[i], si_dict)
                    #  print("followed", follow_value)
                    else:  # forward
                        if len(index_group):
                            value_group[len(index_group) - 1] *= self.get_value(doc[i], si_dict)
                    #   print("forwarded", get_value(doc[i], si_dict))
            else:  # finaltag
                index_group.append(i)
                word_value = follow_value * self.get_value(doc[i], si_dict)
                follow_value = 1
                value_group.append(word_value)
            #   print(doc[i], tag[i], word_value,' added')
            i += 1  # next
        #   --------final gruop---------
        finalNum = len(value_group)
        #for i in range(finalNum):
           # index = index_group[i]
            # output
           # print(i, ' ', doc[index], tag[index], value_group[i])
        # print("ntag:", ntag)
        i = 0
        groupValue = []
        while i in range(finalNum):
           # print("from ", i)
            current_value = 1
            # final word
            if i == finalNum - 1:
                groupValue.append(value_group[i])
                i += 1
            # start with n
            elif tag[index_group[i]] in ntag:
                current_value = value_group[i]
                # mix n(s)
                j = i + 1
                while j < finalNum and (tag[index_group[j]] in ntag):
                  # print(tag[index_group[j]] in ntag, ' ', tag[index_group[j]], '-> ', doc[index_group[j]])
                    current_value += value_group[j]
                    j += 1
                current_value /= j - i
              #  print("mix ns by", i, ' to ', j - 1)
                i = j
                # n  v exist
                if i < finalNum:
                    # mix vi and v/vi
                    if tag[index_group[i]] == 'vi' and i + 1 < finalNum and tag[index_group[i + 1]] in v1tag:
                        value_group[i + 1] = pow(value_group[i] + value_group[i + 1], 0.5)
                    #    print('mix vi in ', i)
                        i += 1
                    # n v
                    # if  tag[index_group[i]] in v1tag:
                    # n v n exist
                    if i + 1 < finalNum and tag[index_group[i + 1]] in ntag:
                        # n v /n v  ff1
                        if i + 2 < finalNum and tag[index_group[i + 2]] in v1tag:
                        #    print('n v /n v')
                            current_value = pow(pow(value_group[i], 2)+pow(current_value, 2), 0.5)
                            i += 1
                        # n v n / n  ff2
                        elif i + 2 < finalNum and tag[index_group[i + 2]] in ntag:
                        #    print('n v n / n')
                            current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                            i += 2
                        # n v n //
                        else:
                        #    print('n v n // ')
                            current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                            i += 2
                            # n v / v OR n v /n  OR n v//  ff3
                    else:
                     #   print('n v / v OR n v /n  OR n v//')
                        current_value = pow(pow(value_group[i], 2)+pow(current_value, 2), 0.5)
                        i += 1
                # n//
                else:
                  #  print('n//')
                    i += 1
                groupValue.append(current_value)
             #   print("to ", i - 1, "value=", current_value)
            # start with v
            elif tag[index_group[i]] in v1tag:
                # mix vi and v/vi
                if tag[index_group[i]] == 'vi' and i + 1 < finalNum and tag[index_group[i + 1]] in v1tag:
                    value_group[i + 1] = pow(value_group[i] + value_group[i + 1], 0.5)
                 #   print('mix vi in ', i)
                    i += 1
                current_value = value_group[i]
                i += 1
                # v n exist now in v->
                if i < finalNum:
                    # v n
                    if tag[index_group[i]] in ntag:
                        # v n n
                        if i + 1 < finalNum and tag[index_group[i + 1]] in ntag:
                            if i + 2 < finalNum:
                                # v n /n v  ff1
                                if tag[index_group[i + 2]] in v1tag:
                                    current_value = pow(pow(value_group[i], 2)+pow(current_value, 2), 0.5)
                                    i += 1
                                # v n n /n  ff2
                                elif tag[index_group[i + 2]] in ntag:
                                    current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                                    i += 2
                            # v n n //
                            else:
                                current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                                i += 2
                        # v n v
                        elif i + 1 < finalNum and tag[index_group[i + 1]] in v1tag:
                            if i + 2 < finalNum:
                                # v n v/v  ff3
                                if tag[index_group[i + 2]] in v1tag:
                                    current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                                    i += 2
                                # v n v n
                                elif tag[index_group[i + 2]] in ntag:
                                    if i + 3 < finalNum:
                                        # v n/v n n  ff4
                                        if tag[index_group[i + 3]] in ntag:
                                            current_value = pow(pow(value_group[i], 2)+pow(current_value, 2), 0.5)
                                            i += 1
                                        # v n v n v  ff5
                                        elif tag[index_group[i + 3]] in v1tag:
                                            current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                                            i += 2
                                    # v n /v n//
                                    else:
                                        current_value = pow(pow(value_group[i], 2) + pow(current_value, 2), 0.5)

                                        i += 1
                            # v n v//
                            else:
                                current_value = pow(pow(value_group[i+1], 2) + pow(value_group[i], 2) + pow(current_value, 2), 0.5)
                                i += 1
                    # v / v
                    else:
                        pass
                groupValue.append(current_value)
             #   print("to ", i - 1, "value=", current_value)
        sortedValue = groupValue.copy()
        sortedValue.sort(reverse=True)
        if len(sortedValue) >= 2:
            final_value = sortedValue[0] + sortedValue[1] - 1
        else:
            final_value = sortedValue[0]
        return final_value

'''
    # judge the intensity value of the comment
    # input is 2 list of [word] and [tag]
    def get_value(self, words):
        print(words)
        itemList = []
        wordIndex = len(words)
        for i in range(wordIndex):
            result = self.refer2dict(words[i])
            # in SI dict
            if result:
                itemList.append(result)
            else:
                # add2dict model off
                pass
                # add2dict model on
                print("want to add ", words[i], ' to SI dict ?:')
                sinput = input()
                if sinput:
                    nlpR = self.nlp.tag(words[i])
                    tag = nlpR[0]['tag']
                    print("nlp tag is ", tag)
                    try:
                        word_value = int(input("set value: "))
                    except ValueError:
                        word_value = int(input("invalid error! input again:"))
                    self.add2dict([words[i], tag, word_value])
                    itemList.append({'key': words[i], 'prop': tag, 'value': word_value})
        for item in itemList:
            print(item)
'''






