import pandas as pd
import re

elemList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#A','#B','#C','#D','#E','#F','#G','#H','#I','#J','#K','#L','#M','#N','#O','#P','#Q','#R','#S','#T','#U','#V','#W','#X','#Y','#Z']

def changeColor(inpStr, texter):
    # for pattern in texter:
    patter_len = len(texter)
    res = [i for i in range(len(inpStr)) if inpStr.lower().startswith(texter, i)]
    # print(res)
    if None in res:
        pass
    else:
        indexes = []
        for num in res:
            # startIndex = f'1.{num}'
            startIndex = num
            indexes.append(startIndex)
    # print(indexes)
    return indexes


def keyToVal(Dict,InpStr):
    for key,value in Dict.items():
        # print(key,value)
        InpStr = InpStr.replace(key,value)
    return InpStr

def ReplText(inpDict,InpStr):
    for key,Val in inpDict.items():
        InpStr = InpStr.replace(Val,key)
    # print(InpStr)
    return InpStr
# file = "textCalc.xlsx"
# df = pd.read_excel(file)

def calculationConvert(inpDict):
    blankDict = {"EMPTYA": "' '", "EMPTYB": "'  '", "EMPTYC": "'   '", "EMPTYD": "'    '", "EMPTYE": "'      '"}
    operDict = {"ORCLAUSE": ' OR ', "AND": ' AND '}
    inDinct = {}
    calcConvertDict = {}
    inReplDict = {}
    colDict = {}
    quote_colDict = {}
    listObj = [' in (', 'isnull (', 'isnull( ', 'isnull ( ', '( not', '( if(', '( if (', '( if ( ', '(if( ','( match(', '( match (', '( match ( ', '(match( ']
    for filtKey,filtval in inpDict.items():
        colDict ={}
        quote_colDict = {}
        inReplDict = {}
        # _var2 = str(inpDf[inpCol][indi])
        _var2 = str(filtval)
        # print('calc without change',_var2)
        _var2 = _var2.replace('\n', '').replace('\r', '').replace('\t', '')
        # print(_var2)
        GraphicalCalc = _var2
        d = changeColor(_var2, '"')
        e = changeColor(_var2, '\'')
        # print(d)
        composite_list = [d[x:x + 2] for x in range(0, len(d), 2)]
        composite_list_quotes = [e[x:x + 2] for x in range(0, len(e), 2)]
        # print(composite_list)
        # col1umnList = []
        colCnt = 0
        for i in composite_list:
            start = i[0]
            end = i[1]
            if _var2[start:end + 1] in colDict.values():
                pass
            else:
                colDict[f'COLUMN{elemList[colCnt]}'] = _var2[start:end + 1]
                colCnt += 1
        # print(colDict)
        for colKey,colVal in colDict.items():
            pattern = f"[A-B][0-99]\.{colVal}"
            a = list(set(re.findall(pattern,_var2)))
            if len(a)>0:
                colDict[colKey] = a[0]
            # print(a)

        quoteCnt = 0
        for i in composite_list_quotes:
            start = i[0]
            end = i[1]
            if _var2[start:end + 1] in quote_colDict.values():
                pass
            else:
                quote_colDict[f'QUOTE{elemList[quoteCnt]}'] = _var2[start:end + 1]
                quoteCnt += 1

        # print(quote_colDict)

        _var2 = ReplText(colDict, _var2)
        # _var2 = _var2.lower()
        _var2 = _var2.replace('  ', ' ').replace('   ',' ').replace('    ', ' ').replace('     ',' ')#.replace(' )',')').replace('( ','(')
        for vil in listObj:
            _var2 = _var2.replace(vil, vil.replace(' ', ''))
        # print(_var2)
        # print(_var2)
        # _var2 = ReplText(blankDict,_var2)
        # print(_var2)
        outlist = []
        startEle = changeColor(_var2, 'in(')
        # print(startEle)
        for i in startEle:
            for i in range(i, len(_var2)):
                if _var2.lower().startswith(')', i):
                    outlist.append(i)
                    break
        # print(outlist)
        InClauseDict = {}
        for key in startEle:
            for value in outlist:
                InClauseDict[key] = value
                outlist.remove(value)
                break

        # print(InClauseDict)

        inCnt = 0
        for k, v in InClauseDict.items():
            # print(_var2[k:v+1])
            inClauseVal = _var2[k:v + 1]
            if 'IN(' in inClauseVal:
                inClauseVal = inClauseVal.replace('IN(', 'in(')
            else:
                pass
            # print(inClauseVal)
            inReplDict[f'INCLAUSE{elemList[inCnt]}'] = inClauseVal
            inCnt += 1
        for value in inReplDict.values():
            for col_name in colDict.keys():
                # print(col_name)
                if f'in({col_name},' in _var2:
                    # print('true')
                    _var2 = _var2.replace(f'in({col_name},', f'{col_name} IN(')
                if f'IN({col_name},' in _var2:
                    # print('true')
                    _var2 = _var2.replace(f'IN({col_name},', f'{col_name} IN(')
                if f'in({col_name} ,' in _var2:
                    # print('true')
                    _var2 = _var2.replace(f'in({col_name} ,', f'{col_name} IN(')
                if f'IN({col_name} ,' in _var2:
                    # print('true')
                    _var2 = _var2.replace(f'IN({col_name} ,', f'{col_name} IN(')
                # elif

        # print(_var2)

        _var2 = ReplText(inReplDict, _var2)
        _var2 = ReplText(quote_colDict, _var2)
        _var2 = _var2.lower()

        # print(colDict)
        # print(_var2)
        # print(_var2)
        for val in colDict.keys():
            # print(val)
            if f'not isnull({val.lower()})' in _var2:
                _var2 = _var2.replace(f'not isnull({val.lower()})', f'{val.lower()} IS NOT NULL')
            if f'isnull({val.lower()})' in _var2:
                _var2 = _var2.replace(f'isnull({val.lower()})', f'{val.lower()} IS NULL')
            if f'not isnull({val.lower()} )' in _var2:
                _var2 = _var2.replace(f'not isnull({val.lower()} )', f'{val.lower()} IS NOT NULL')
            if f'isnull({val.lower()} )' in _var2:
                _var2 = _var2.replace(f'isnull({val.lower()} )', f'{val.lower()} IS NULL')
            if f'match({val.lower()},' in _var2:
                # print(_var2)
                for quoKey,quoVal in quote_colDict.items():
                    if quoVal == '*':
                        pass
                    elif '*' in quoVal:
                        quoVal = quoVal.replace('*', '%')
                        quote_colDict[quoKey] = quoVal
                _var2 = _var2.replace(f'match({val.lower()},', f'{val.lower()} LIKE ')

        if 'leftstr(' in _var2:
            _var2 = _var2.replace('leftstr(', 'left(')
        if 'rightstr(' in _var2:
            _var2 = _var2.replace('rightstr(', 'right(')
        if 'date(' in _var2 and 'to_date(' not in _var2:
            _var2 = _var2.replace('date(', 'to_date(')
        if 'date(' in _var2 and 'to_date(' in _var2:
            _var2 = _var2.replace('to_date(', 'date(').replace('date(', 'to_date(')
        if 'format(' in _var2:
            _var2 = _var2.replace('format(', 'to_varchar(')
        if 'adddays(' in _var2:
            _var2 = _var2.replace('adddays(', 'add_days(')
        if 'strlen(' in _var2:
            _var2 = _var2.replace('strlen(', 'length(')
        if 'int(' in _var2 and 'to_int(' not in _var2:
            _var2 = _var2.replace('int(', 'to_int(')
        if 'int(' in _var2 and 'to_int(' in _var2:
            _var2 = _var2.replace('to_int(', 'int(').replace('int(', 'to_int(')
        # if 'int(' in _var2:
        #     _var2 = _var2.replace(' int(', 'to_int(')
        if 'timestamp(' in _var2 and 'to_timestamp(' not in _var2:
            _var2 = _var2.replace('timestamp(', 'to_timestamp(')
        if 'timestamp(' in _var2 and 'to_timestamp(' in _var2:
            _var2 = _var2.replace('to_timestamp(', 'timestamp(').replace('timestamp(', 'to_timestamp(')
        # if 'timestamp(' in _var2:
        #     _var2 = _var2.replace('timestamp(', 'to_timestamp(')
        if 'secondsbetween(' in _var2:
            _var2 = _var2.replace('secondsbetween(', 'seconds_between(')
        if 'daysbetween(' in _var2:
            _var2 = _var2.replace('daysbetween(', 'days_between(')
        if 'seconddate(' in _var2:
            _var2 = _var2.replace('seconddate(', 'to_seconddate(')
        if 'double(' in _var2:
            _var2 = _var2.replace('double(', 'to_double(')
        if 'float(' in _var2:
            _var2 = _var2.replace('float(', 'to_decimal(')

        _var2 = _var2.upper()
        # print(_var2)
        _var2 = keyToVal(inReplDict, _var2)
        _var2 = keyToVal(colDict, _var2)
        _var2 = keyToVal(quote_colDict, _var2)
        sqlCalc = _var2
        # print(_var2, '\n', '\n')
        calcConvertDict[filtKey] = sqlCalc
    # print(calcConvertDict)

    return calcConvertDict