import xml.etree.ElementTree as ET
import pandas as pd
import fileinput
import jinja2
from hanaClass import hanaQry

elemList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#A','#B','#C','#D','#E','#F','#G','#H','#I','#J','#K','#L','#M','#N','#O','#P','#Q','#R','#S',
            '#T','#U','#V','#W','#X','#Y','#Z','#a','#b','#c','#d','#e','#f','#g','#h','#i','#j','#k','#l','#m','#n','#o','#p','#q','#r','#s','#t','#u','#v','#w','#x','#y','#z','1','2','3','4','5','6','7','8','9','0',
            '$a','$b','$c','$d','$e','$f','$g','$h','$i','$j','$k','$l','$m','$n','$o','$p','$q','$r','$s','$t','$u','$v','$w','$x','$y','$z','$A','$B','$C','$D','$E','$F','$G','$H','$I','$J','$K','$L','$M','$N','$O',
            '$P','$Q','$R','$S','$T','$U','$V','$W','$X','$Y','$Z']
def converViewToXml(cursor,conn,package, view,file = None):
    pd.set_option('display.max_rows', 5000)
    pd.set_option('display.max_columns', 5000)
    pd.set_option('display.width', 10000)
    xsi = '{http://www.w3.org/2001/XMLSchema-instance}type'
    if file is None:
        inputView = view
        inputPkg = package
        sql = f'select CDATA from "_SYS_REPO"."ACTIVE_OBJECT" where PACKAGE_ID = \'{inputPkg}\' and OBJECT_NAME = \'{inputView}\' '
        # print(sql)
        cursor.execute(sql)
        out = cursor.fetchall()
        xmlFile = out[0][0]
        # conn.close()
        # print(xmlFile)
        with open('toBeConverted.xml', 'w') as xml:
            xml.write(xmlFile)

            xml.close()

        tree = ET.parse('toBeConverted.xml')

    else:
    # tree = ET.parse(filename)

        tree = ET.parse('toBeConverted.xml')

    root = tree.getroot()
    keyList = [f'{xsi}type', 'id', 'cardinality', 'joinOrder', 'joinType']
    typeList = {'Calculation:JoinView': ['id', 'cardinality', 'joinOrder', 'joinType'],
                'Calculation:ProjectionView': ['id', 'filterExpressionLanguage'],
                'Calculation:UnionView': ['id'],
                'Calculation:AggregationView': ['id'],
                'Calculation:RankView': ['id']}

    tableDict = {}
    nameList = []
    dataSourceDict = {}
    idList = []
    objTypeList = []
    objnameList = []
    FuncParam =[]
    dataSrc =[]

    objUsed = {'id': '',
               'Type': '',
               'name': ''}
    nodeObjMapping = {'NodeName': '',
                      'NodeType': '',
                      'cardinality': '',
                      'JoinOrder': '',
                      'joinType': '',
                      'FilterLang': '',
                      'Filter': ''}
    nodeColumn = {'NodeName': '',
                  'Sql': ''}
    nodeFilterDict = {'AccessControl:SingleValueFilter' : ['operator','including','value'],
                      'AccessControl:RangeValueFilter' :['operator','including','lowValue','highValue'],
                      'AccessControl:ListValueFilter' :['operator','including']}

    joins = {"leftOuter": 'LEFT OUTER JOIN', "rightOuter": 'RIGHT OUTER JOIN', "fullOuter": 'FULL OUTER JOIN',
             "inner": 'INNER JOIN', "text": 'TEXT JOIN', "referential": 'REFERENTIAL JOIN'}
    Aggregates = {"sum": 'SUM', "max": 'MAX', "avg": 'AVG', "count": 'COUNT', "min": 'MIN'}

    nodeQueryDict = {}
    df2 = pd.DataFrame(objUsed, index=[0])
    dfnodeobj = pd.DataFrame(objUsed, index=[0])
    dfnodeCol = pd.DataFrame(nodeColumn, index=[0])

    def getInputNode(InpElement):
        InpNodes = []
        for i in range(0, len(child1)):
            if child1[i].tag == 'input':
                if '$' in child1[i].attrib['node']:
                    nodeName = child1[i].attrib['node'].split('$$$$')[1][:-2]
                    # print(nodeName)
                    InpNodes.append(nodeName)
                else:
                    InpNodes.append(child1[i].attrib['node'][1:])
        # print(InpNodes)
        return InpNodes

    def get_key(diction, val):
        for key, value in diction.items():
            if val == value:
                return key

        return "key doesn't exist"

    def checkPresence(inpVal, SearchList):
        for i in SearchList:
            if inpVal in i:
                return 1
            else:
                pass
    def checkPresenceStr(inpVal, SearchList):
        for i in SearchList:
            if i in inpVal:
                # print(i,': ',inpVal)
                return 1
            else:
                # print(i,': ',inpVal)
                return 0



    def convIfToCase(Inp):
        return Inp

    ##For Data source Capture
    for parent in root.findall('dataSources'):
        pd.set_option('display.max_rows', 5000)
        pd.set_option('display.max_columns', 5000)
        pd.set_option('display.width', 10000)
        for child1 in parent:
            if '$$$$' in child1.attrib['id']:
                id = (child1.attrib['id']).split('$$$$')
                id = id[0]
                dataSourceDict['id'] = id
            else:
                id = (child1.attrib['id'])
                dataSourceDict['id'] = id
            objType = child1.attrib['type']
            dataSourceDict['Type'] = objType
            if objType == 'CALCULATION_VIEW':
                name = (child1[1].text[1:]).replace('/calculationviews/', '/')
                dataSourceDict['name'] = name
            elif objType == 'DATA_BASE_TABLE' or objType == 'TABLE_FUNCTION':
                if objType == 'DATA_BASE_TABLE':
                    name = f"\"{child1[1].attrib['schemaName']}\".\"{child1[1].attrib['columnObjectName']}\""
                    dataSourceDict['name'] = name
                elif objType == 'TABLE_FUNCTION':
                    # cursor,conn = connectionCreate('dev')
                    sqlfunc = f'SELECT SCHEMA_NAME FROM SYS.FUNCTIONS WHERE FUNCTION_NAME =\'{child1[0].text}\''
                    inpParamFunc = f'''select "PARAMETER_NAME"
                                        FROM "SYS"."FUNCTION_PARAMETERS" 
                                        WHERE ( UPPER("FUNCTION_NAME") LIKE  UPPER(\'%{child1[0].text}%\'))
                                        AND "PARAMETER_TYPE" = \'IN\' and "HAS_DEFAULT_VALUE" = \'FALSE\''''
                    cursor.execute(sqlfunc)
                    out = cursor.fetchall()
                    cursor.execute(inpParamFunc)
                    outParam = cursor.fetchall ()
                    FuncSchema = f'\"{out[0][0]}\"'
                    outParaFunc = [i[0] for i in outParam]
                    FuncParam
                    funcInp =''
                    for inpVal in outParaFunc:
                        funcInp += f"'{inpVal}',"
                        FuncParam.append(inpVal)
                    # print(funcInp[:-1])
                    # print(FuncParam)
                    funcInp = funcInp[:-1]
                    # print(child1[0].text)
                    if funcInp == '':
                        name = f"{FuncSchema}.\"{child1[0].text}\"()"
                    else:
                        name = f"{FuncSchema}.\"{child1[0].text}\"({funcInp})"
                    dataSourceDict['name'] = name

            df = pd.DataFrame(dataSourceDict, index=[0])
            df2 = pd.concat([df2, df])

    # df2.style.set_properties(**{'text-align': 'left'})
    srcviews = set(df2['name'])
    srcvlist = []
    for vw in srcviews:

        try:
            srcvlist.append(vw)
        except:
            pass
    viewShrt = []

    def getBaseViews(NodeType, NodeList, datafr):
        outDict = {}
        node_viewMap = {}
        views = set(datafr['name'])
        vlist =[]
        for vw in views:
            if '/' in vw:
                vnameold = vw.split('/')
                vname = vnameold[1]
            elif '::' in vw:
                # vname = vw
                viewSplit = vw.split('"."')
                vname = viewSplit[1].replace('"', '').replace(' ', '')
            try:
                vlist.append(vname)
            except:
                pass

        if 'join' in NodeType.lower() or 'union' in NodeType.lower():
            for num in range(0, len(NodeList)):
                viewname = NodeList[num]
                viewType = 'variable'
                node_viewMap[NodeList[num]] = viewname
                outDict[viewname] = viewType
        else:
            if NodeList[0] in set(datafr['id']):
                # print(NodeList[0])
                if NodeList[0] in set(vlist):
                    # print('true')

                    viewname = datafr.query(f'id ==\'{NodeList[0]}\'')['name'][0]
                    node_viewMap[NodeList[0]] = viewname
                    viewType = datafr.query(f'id ==\'{NodeList[0]}\'')['Type'][0]
                else:
                    viewname = NodeList[0]
                    node_viewMap[NodeList[0]] = viewname
                    viewType = 'variable'
            else:
                viewname = NodeList[0]
                node_viewMap[NodeList[0]] = viewname
                viewType = 'variable'
            outDict[viewname] = viewType

        return outDict, node_viewMap
    # getBaseViews('Calculation:AggregationView',['P_Meta2'],df2)

    ##For Node level data capture
    for parent in root.findall('calculationViews'):

        joinList = []
        leftTable = ''
        righttable = ''
        InputNodes = []
        node_qryDict = {}
        node_snwqryDict = {}
        node_InputView = {}
        calccol_list = []
        calcol_dict ={}
        filterList = []
        InlistDict = {}
        nodLineageDict = {}
        tableCnt = 0

        for child1 in parent:
            baseViewDict = {}
            col_str = ''
            joincol_str = ''
            NodeType = child1.attrib[xsi]
            NodeName = child1.attrib['id']
            var = f'{NodeName} = Select '
            currentNodeCalcDict = {}
            currentNodeCalcList = []
            # print(NodeType, ' : ', NodeName) #-- for column lineage
            # get input nodes for node name
            InputNodes = getInputNode(child1)
            # print(NodeType, ' : ', NodeName,' : ',InputNodes)
            # print(InputNodes) #-- for column lineage
            node_InputView[NodeName] = InputNodes

            # get Column names
            if NodeType == 'Calculation:AggregationView':
                columns = []
                aggregated_col = []
                groupCol = []
                for i in range(0, len(child1[1])):

                    if '$' not in child1[1][i].attrib['id']:
                        # print(child1[1][i].attrib)
                        if 'aggregationType' in child1[1][i].attrib:

                            if child1[1][i].attrib['aggregationType'] in Aggregates:
                                columns.append(
                                    f"{Aggregates[child1[1][i].attrib['aggregationType']]}(\"{child1[1][i].attrib['id']}\") as \"{child1[1][i].attrib['id']}\"")
                                aggregated_col.append(child1[1][i].attrib['id'])
                                groupCol.append(f"\"{child1[1][i].attrib['id']}\"")
                        else:
                            columns.append(f"\"{child1[1][i].attrib['id']}\"")
                            groupCol.append(f"\"{child1[1][i].attrib['id']}\"")
                    else:
                        pass

            else:
                columns = [('\"' + child1[1][i].attrib['id'] + '\"') for i in range(0, len(child1[1])) if
                           '$' not in (child1[1][i].attrib['id'])]

            if NodeType == 'Calculation:RankView':
                rankCol = ''
                for func_val in child1.findall('windowFunction'):
                    partitionCol = ''
                    orderCol = ''
                    ordrBy = ''
                    aliasCol = ''
                    for subFunc in range(0, len(func_val)):
                        if func_val[subFunc].tag == 'partitionViewAttributeName':
                            partitionCol = partitionCol + f'\"{func_val[subFunc].text}\", '
                        elif func_val[subFunc].tag == 'order':
                            orderCol = f"\"{func_val[subFunc].attrib['byViewAttributeName']}\""
                            ordrBy = func_val[subFunc].attrib['direction']
                            # print(func_val[subFunc].tag, ' : ', func_val[subFunc].attrib)
                        elif func_val[subFunc].tag == 'rankViewAttributeName':
                            aliasCol = func_val[subFunc].text
                            # print(func_val[subFunc].tag, ' : ', func_val[subFunc].attrib, ' : ', func_val[subFunc].text)
                rankCol = f'RANK() OVER (PARTITION BY {partitionCol[:-2]} ORDER BY {orderCol} {ordrBy}) as \"{aliasCol}\"'
                columns.append(rankCol)
            # print(columns) #-- for column lineage

            # get Base View
            view, nodeView = getBaseViews(NodeType, InputNodes, df2)

            nodLineageDict[NodeName] = InputNodes
            # if NodeName =='Proj_itemGrpItemAssoc':
            #     print(NodeType, ' : ', NodeName)
            #     print(InputNodes)  #-- for column lineage
            #
            #     print(view, ':', nodeView)  #-- for column lineage

            # get join attributes
            joinList = []
            toBeRemKey = []
            for i in range(0, len(child1)):
                # print(i)
                if 'join' in NodeType.lower():
                    # print('in this loop')
                    col_list = []
                    if child1[i].tag == 'joinAttribute':
                        toBeRemKey.append(child1[i].attrib['name'])
                        if '$' in child1[i].attrib['name']:
                            joincolSrc = child1[i].attrib['name'].split('$')[1]
                            joincolTrg = child1[i].attrib['name'].split('$')[2]
                            joinList.append(f"A{tableCnt}.\"{joincolSrc}\" = B{tableCnt}.\"{joincolTrg}\"")
                        else:
                            joinList.append(f"A{tableCnt}.\"{child1[i].attrib['name']}\" = B{tableCnt}.\"{child1[i].attrib['name']}\"")

                        # print(f"{child1[i].attrib['name']} = {child1[i].attrib['name']}")

            for i_calc in range(0, len(child1)):
                if child1[i_calc].tag == 'calculatedViewAttributes':
                    for num_calc in range(0, len(child1[i_calc])):
                        col_name = child1[i_calc][num_calc].attrib['id']
                        col_logic = convIfToCase(child1[i_calc][num_calc][0].text)
                        col_logic = col_logic.replace('\n', ' ').replace('\t', '')
                        calccol_list.append(col_logic)
                        currentNodeCalcList.append(col_logic)
                        currentNodeCalcDict[col_name] = col_logic
                        # print(col_logic)
                        # print(calccol_list)

                        # print(currentNodeCalcList)
                        # print(currentNodeCalcDict)

            tableACols = []
            tableBCols = []
            if NodeType == 'Calculation:JoinView' or NodeType == 'Calculation:UnionView':
                # print(view.items())
                if NodeType == 'Calculation:JoinView':
                    for key, value in nodeView.items():
                        cnt = 0
                        for h in child1.findall('input'):
                            cnt += 1
                            if h.attrib['node'] == '#' + key:
                                # print(h.attrib['node'],'\n\n')
                                col_list = []
                                for num in range(0, len(h)):
                                    if h[num].attrib['source'] == h[num].attrib['target']:
                                        col_list.append(f"\"{h[num].attrib['target']}\"")
                                        if cnt == 1:
                                            tableACols.append(f"\"{h[num].attrib['target']}\"")
                                        elif cnt == 2:
                                            tableBCols.append(f"\"{h[num].attrib['target']}\"")
                                    else:
                                        if "'" in h[num].attrib['source']:
                                            col_list.append(
                                                f"{h[num].attrib['source']} as \"{h[num].attrib['target']}\"")
                                            if cnt == 1:
                                                tableACols.append(f"\"{h[num].attrib['target']}\"")
                                            elif cnt == 2:
                                                tableBCols.append(f"\"{h[num].attrib['target']}\"")
                                        elif "$" in h[num].attrib['target']:
                                            setCol = list(set(h[num].attrib['target'].split('$')))
                                            # print (len(setCol), ' : ',f"\"{h[num].attrib['source']}\"")
                                            # print(setCol)
                                            if len(setCol) == 2 and f"\"{h[num].attrib['source']}\"" in col_list:
                                                pass
                                            else:
                                                col_list.append(
                                                    f"\"{h[num].attrib['source']}\"")  # as \"{h[num].attrib['source']}\"")
                                            # print(col_list)

                                            if cnt == 1:
                                                tableACols.append(f"\"{h[num].attrib['target']}\"")
                                            elif cnt == 2:
                                                tableBCols.append(f"\"{h[num].attrib['target']}\"")
                                        else:
                                            col_list.append(
                                                f"\"{h[num].attrib['source']}\" as \"{h[num].attrib['target']}\"")
                                            if cnt == 1:
                                                tableACols.append(f"\"{h[num].attrib['target']}\"")
                                            elif cnt == 2:
                                                tableBCols.append(f"\"{h[num].attrib['target']}\"")
                            baseViewDict[key] = col_list
                    for keyCol, valueCol in currentNodeCalcDict.items():
                        # print(currentNodeCalcDict.items())
                        present = checkPresence(f'\"{keyCol}\"', currentNodeCalcList)
                        if present == 1:
                            baseViewDict[key].append(f'{valueCol} as \"{keyCol}\"')
                            # print(valueCol)
                            # print('calculated column being used inside calculated column')
                        else:
                            columns.append(f'{valueCol} as \"{keyCol}\"')
                        # print(baseViewDict)

                elif NodeType == 'Calculation:UnionView':
                    for key, value in nodeView.items():
                        # print(nodeView.items())
                        for h in child1.findall('input'):
                            # print(h.attrib['node'])
                            # print(key)
                            if h.attrib['node'] == '#' + key:
                                col_list = []
                                for num in range(0, len(h)):
                                    if h[num].attrib[xsi] == 'Calculation:ConstantAttributeMapping':
                                        col_list.append(
                                            f" '' as \"{h[num].attrib['target']}\"")
                                    else:
                                        if h[num].attrib['source'] == h[num].attrib['target']:
                                            col_list.append(f"\"{h[num].attrib['target']}\"")
                                        else:
                                            if "'" in h[num].attrib['source']:
                                                col_list.append(
                                                    f"{h[num].attrib['source']} as \"{h[num].attrib['target']}\"")

                                            elif "$" in h[num].attrib['target']:
                                                col_list.append(
                                                    f"\"{h[num].attrib['source']}\" as \"{h[num].attrib['source']}\"")

                                            else:
                                                col_list.append(
                                                    f"\"{h[num].attrib['source']}\" as \"{h[num].attrib['target']}\"")

                            # print(key,' columns for this are ',col_list)
                            baseViewDict[key] = col_list
                            # print(baseViewDict)
                # print(tableACols, '\n', tableBCols,'\n\n\n')
            else:
                for view_key, val in view.items():
                    # print(view.items())
                    key = view_key
                    alias = NodeName[1] + NodeName[3]
                for h in child1.findall('input'):
                    node_name = h.attrib['node']
                    if '$' in node_name:
                        nodeName = f"#{h.attrib['node'].split('$$$$')[1][:-2]}"
                    else:
                        nodeName = h.attrib['node']
                    if nodeName == '#' + InputNodes[0]:
                        col_list = []
                        for num in range(0, len(h)):
                            if h[num].attrib['source'] == h[num].attrib['target']:
                                col_list.append(f"\"{h[num].attrib['target']}\"")
                            else:
                                if "'" in h[num].attrib['source']:
                                    col_list.append(f"{h[num].attrib['source']} as \"{h[num].attrib['target']}\"")
                                else:
                                    col_list.append(f"\"{h[num].attrib['source']}\" as \"{h[num].attrib['target']}\"")

                        # print(col_list)
                        # print(key)
                        if NodeType == 'Calculation:RankView':
                            col_list.append(rankCol)

                        baseViewDict[key] = col_list
                        for keyCol_jn, valueCol_jn in currentNodeCalcDict.items():
                            # print(keyCol_jn,' : ',valueCol_jn)
                            # print(currentNodeCalcList)
                            present = checkPresence(f'\"{keyCol_jn}\"', currentNodeCalcList)
                            if present == 1:
                                baseViewDict[key].append(f'{valueCol_jn} as \"{keyCol_jn}\"')
                                # print(valueCol)
                                # print('calculated column being used inside calculated column')
                            else:
                                columns.append(f'{valueCol_jn} as \"{keyCol_jn}\"')
                    # print(baseViewDict)
            # print(baseViewDict) #for column lineage
            # get filter columns  #-- for column lineage
            for i in range(0, len(child1)):
                col_list = []
                filter = ''
                if child1[i].tag == 'filter':
                    filter = (child1[i].text).replace('\n', ' ').replace('\t', '').replace('\r', '')
                    filter = f'({filter})'

                    # print(filter)
                    filterList.append(filter)
                    # print(filter)

            for i in range(0, len(child1)):
                if child1[i].tag == 'viewAttributes':
                    # print(NodeType, ' : ', NodeName)
                    filter_text =''
                    nodeFilter =''
                    for j in range(0, len(child1[i])):
                        column_name = child1[i][j].attrib['id']
                        for k in child1[i][j].findall('filter'):
                            filt = k.attrib
                            # for filterType,filterAttrib in nodeFilterDict.items():
                            if filt[xsi] == 'AccessControl:SingleValueFilter':
                                if 'operator' not in filt:
                                    if filt['including'] == 'true':
                                        filter_text = f"(\"{column_name}\" = \'{filt['value']}\')"
                                        # print(filter_text)
                                    else:
                                        filter_text = f"(\"{column_name}\" != \'{filt['value']}\')"
                                        # print(filter_text)
                                else:
                                    if filt['operator'] == 'NL':
                                        if filt['including'] == 'true':
                                            filter_text = f"(\"{column_name}\" IS NULL)"
                                            # print(filter_text)
                                        elif filt['including'] == 'false':
                                            filter_text = f"(\"{column_name}\" IS NOT NULL)"
                                            # print(filter_text)
                                    elif filt['operator'] == 'LT':
                                        filter_text = f"(\"{column_name}\" < \'{filt['value']}\')"
                                        # print(filter_text)
                                    elif filt['operator'] == 'LE':
                                        filter_text = f"(\"{column_name}\" <= \'{filt['value']}\')"
                                        # print(filter_text)
                                    elif filt['operator'] == 'GT':
                                        filter_text = f"(\"{column_name}\" > \'{filt['value']}\')"
                                        # print(filter_text)
                                    elif filt['operator'] == 'GE':
                                        filter_text = f"(\"{column_name}\" >= \'{filt['value']}\')"
                                        # print(filter_text)
                                    elif filt['operator'] == 'CP':
                                        filter_text = f"MATCH(\"{column_name}\", \'{filt['value']}\')"
                                        # print(filter_text)

                            elif filt[xsi] == 'AccessControl:RangeValueFilter':
                                if filt['operator'] == 'BT':
                                    filter_text = f"(\"{column_name}\" >= \'{filt['lowValue']}\' AND \"{column_name}\" <= \'{filt['highValue']}\')"
                                    # print(filter_text)
                            elif filt[xsi] == 'AccessControl:ListValueFilter':
                                subValList = ''
                                for subVal in k.findall('operands'):
                                    # print(subVal.attrib)
                                    subValList = subValList + f"\'{subVal.attrib['value']}\'" + ","
                                subValList = subValList[:-1]
                                if filt['operator'] == 'IN':
                                    if filt['including'] == 'true':
                                        filter_text = f"(\"{column_name}\" IN({subValList}))"
                                        # print(filter_text)
                                    elif filt['including'] == 'false':
                                        filter_text = f"(\"{column_name}\" NOT IN({subValList}))"
                                        # print(filter_text)

                            nodeFilter = nodeFilter +  filter_text + ' AND '

                    filter_text = nodeFilter[:-4].replace('\n', '').replace('\r', '').replace('\t', '')
                    # print(filter_text)
                    if nodeFilter == '':
                        pass

                    else:
                        # print(nodeFilter[:-4])
                        filterList.append(nodeFilter[:-4])
            # print(filter_text)
            if len(filter) <= 1 and len(filter_text)>=1:
                filter = f'({filter_text})'
                # print(filter)
            else:
                pass
                # print(filter)

            column_str = ''
            whr = ' WHERE '
            snowview = ''
            if NodeType == 'Calculation:ProjectionView' or NodeType == 'Calculation:AggregationView' or NodeType == 'Calculation:RankView':


                for viewname, val in view.items():
                    if val == 'CALCULATION_VIEW':
                        snowview = '"_SYS_BIC"."' + viewname + '"'
                        viewname = '"_SYS_BIC"."' + viewname + '"'
                    elif val == 'DATA_BASE_TABLE' or val == 'TABLE_FUNCTION':
                        viewname = viewname
                        snowview = viewname

                    else:
                        snowview = viewname
                        viewname = ':' + viewname

                    # print(viewname)
                    innerCol = ''
                for key, value in baseViewDict.items():
                    for colval in value:
                        innerCol += colval + ',\n\t'
                    # print(innerCol)
                for clmNm in columns:
                    column_str += clmNm + ',\n\t'
                # print(column_str)
                if columns == value and filter == '':
                    if NodeType == 'Calculation:AggregationView':
                        for agg_name in aggregated_col:
                            groupCol.remove(f'\"{agg_name}\"')
                            # columns.remove(agg_name)
                        columnAgg_str = ''
                        for clmNmAgg in groupCol:
                            columnAgg_str += clmNmAgg + ',\n\t'
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM {viewname} GROUP BY {columnAgg_str[:-3]}'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM {snowview} GROUP BY {columnAgg_str[:-3]} )'
                    else:
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM {viewname} '
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM {snowview} )'
                elif columns != value and filter == '':
                    if NodeType == 'Calculation:AggregationView':
                        for agg_name in aggregated_col:
                            groupCol.remove(f'\"{agg_name}\"')
                            # value.remove(f'\"{agg_name}\"')
                        columnAgg_str = ''
                        for clmNmAgg in groupCol:
                            columnAgg_str += clmNmAgg + ',\n\t'
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {viewname} ) GROUP BY {columnAgg_str[:-3]}'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {snowview} ) GROUP BY {columnAgg_str[:-3]} )'
                    else:
                        # print(innerCol)
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {viewname} )'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {snowview} ) )'
                elif columns == value and filter != '':
                    if NodeType == 'Calculation:AggregationView':
                        for agg_name in aggregated_col:
                            groupCol.remove(f'\"{agg_name}\"')
                            # value.remove(f'\"{agg_name}\"')
                        columnAgg_str = ''
                        for clmNmAgg in groupCol:
                            columnAgg_str += clmNmAgg + ',\n\t'
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {viewname} ) WHERE {filter} GROUP BY {columnAgg_str[:-3]}'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {snowview} ) WHERE {filter} GROUP BY {columnAgg_str[:-3]} )'
                    else:
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM {viewname} WHERE {filter}'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM {snowview} WHERE {filter} )'
                else:
                    if NodeType == 'Calculation:AggregationView':
                        for agg_name in aggregated_col:
                            groupCol.remove(f'\"{agg_name}\"')
                            # value.remove(f'\"{agg_name}\"')
                        columnAgg_str = ''
                        for clmNmAgg in groupCol:
                            columnAgg_str += clmNmAgg + ',\n\t'
                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {viewname} ) WHERE {filter} GROUP BY {columnAgg_str[:-3]}'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {snowview} ) WHERE {filter} GROUP BY {columnAgg_str[:-3]} )'
                    else:

                        query = f'{NodeName} = SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {viewname} ) WHERE {filter}'
                        querySnow = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM ( SELECT {innerCol[:-3]} FROM {snowview} ) WHERE {filter} )'

            elif NodeType == 'Calculation:JoinView' or NodeType == 'Calculation:UnionView':
                outerQry = ''
                snowouterqry =''
                # print(nodeName)
                for clmSrc in range(0, len(columns)):
                    # print(columns[clmSrc])
                    if columns[clmSrc] in tableACols and columns[clmSrc] in tableBCols:
                        columns[clmSrc] = f'A{tableCnt}.{columns[clmSrc]}'
                        # print(f'{columns[clmSrc]} is present in both')
                    elif columns[clmSrc] in tableACols:
                        columns[clmSrc] = f'A{tableCnt}.{columns[clmSrc]}'
                        # print(f'{columns[clmSrc]} is present in A')
                    elif columns[clmSrc] in tableBCols:
                        columns[clmSrc] = f'B{tableCnt}.{columns[clmSrc]}'
                        # print(f'{columns[clmSrc]} is present in B')
                    elif 'as' in columns[clmSrc]:
                        # print('im in')
                        presentCountA =0
                        presentColA =''
                        presentCountB = 0
                        presentColB = ''
                        # print(columns[clmSrc])
                        # print(tableACols)
                        # print(tableBCols)
                        for inColA in tableACols:
                            if inColA in columns[clmSrc]:
                                presentColA = inColA
                                presentCountA = 1
                        for inColB in tableBCols:
                            # print(f'im double inn : {inColB}')
                            if inColB in columns[clmSrc]:
                                # print(inColB)
                                presentCountB = 1
                                presentColB = inColB
                                # print(presentColB)
                        if presentCountA == presentCountB == 1:
                            # toReplace = columns[clmSrc]
                            toReplace = columns[clmSrc].split(' as')[0]
                            columns[clmSrc] = columns[clmSrc].replace(presentColA,f'A{tableCnt}.{presentColA}')
                            for calcValNum in range(0, len(calccol_list)):

                                if toReplace == calccol_list[calcValNum]:
                                    # print(toReplace)
                                    # print(calccol_list[calcValNum])
                                    # print(True)
                                    calccol_list[calcValNum] = columns[clmSrc].split(' as')[0]
                            # print(calccol_list)
                            # print('\n')
                        elif presentCountA == 1 and presentCountB ==0 :
                            toReplace = columns[clmSrc].split(' as')[0]
                            columns[clmSrc] = columns[clmSrc].replace(presentColA, f'A{tableCnt}.{presentColA}')
                            for calcValNum in range(0, len(calccol_list)):

                                if toReplace == calccol_list[calcValNum]:
                                    # print(toReplace)
                                    # print(calccol_list[calcValNum])
                                    # print(True)
                                    calccol_list[calcValNum] = columns[clmSrc].split(' as')[0]
                            # print(calccol_list)
                            # print('\n')
                        elif presentCountA == 0 and presentCountB ==1 :
                            # print(f'im triple in  : {columns[clmSrc]}'  )
                            toReplace = columns[clmSrc].split(' as')[0]
                            # print(f"{presentColB} is to be replace with {f'B{tableCnt}.{presentColB}'}")
                            columns[clmSrc] = columns[clmSrc].replace(presentColB, f'B{tableCnt}.{presentColB}')
                            # print(columns[clmSrc])
                            for calcValNum in range(0,len(calccol_list)):

                                if toReplace == calccol_list[calcValNum]:
                                    # print("this is true")
                                    # print(toReplace)
                                    # print(calccol_list[calcValNum])
                                    # print(True)
                                    calccol_list[calcValNum] = columns[clmSrc].split(' as')[0]
                            # print(calccol_list)
                            # print('\n')
                        else:
                            pass
                    else:
                        pass

                        # pass
                # print(columns)
                # print(tableACols)
                # print(tableBCols)
                for clmNm in columns:
                    column_str += clmNm + ',\n\t'
                # print('this is outer columns : ',column_str)
                outerQry = f'{NodeName} = SELECT {column_str[:-3]} FROM ('
                snowouterqry = f'{NodeName} AS ( SELECT {column_str[:-3]} FROM ('
                inlist = []
                snowinList =[]
                inlistDict ={}
                snowinListDict ={}
                srcCnt = 0

                for viewname, val in view.items():
                    srcCnt += 1
                    # print(viewname, ' is  ', val)
                    if val == 'CALCULATION_VIEW':
                        col_val = baseViewDict[get_key(nodeView, viewname)]
                        snow_view = '"_SYS_BIC"."' + viewname + '"'
                        view_name = '"_SYS_BIC"."' + viewname + '"'

                    elif val == 'DATA_BASE_TABLE' or val == 'TABLE_FUNCTION':
                        viewname = viewname
                        snow_view = viewname
                    else:
                        snow_view = viewname
                        view_name = ':' + viewname

                        col_val = baseViewDict[viewname]
                        col_val = list(dict.fromkeys(col_val))

                    innerCol = ''
                    for culv in col_val:
                        innerCol += culv + ',\n\t'


                    # print('this is inner columns : ', innerCol)
                    if NodeType == 'Calculation:JoinView':
                        if srcCnt == 1:
                            qry = f'SELECT {innerCol[:-3]} FROM {view_name} '
                            snwqry = f'SELECT {innerCol[:-3]} FROM {snow_view} '
                        elif srcCnt == 2:
                            qry = f'SELECT {innerCol[:-3]} FROM {view_name} '
                            snwqry = f'SELECT {innerCol[:-3]} FROM {snow_view} '
                    elif NodeType == 'Calculation:UnionView':
                        qry = f'SELECT {innerCol[:-3]} FROM {view_name} '
                        snwqry = f'SELECT {innerCol[:-3]} FROM {snow_view} '

                    inlist.append(qry)
                    inlistDict[view_name] = qry
                    snowinList.append(snwqry)
                    snowinListDict[view_name] = snwqry

                # print(inlist)
                if NodeType == 'Calculation:JoinView':
                    joinStr = ''
                    for cond in joinList:
                        if '$' in cond:
                            pass
                        else:
                            joinStr += cond + ' AND '
                    # jointype = joins[child1.attrib['joinType']]
                    try :
                        jointype = joins[child1.attrib['joinType']]
                    except Exception as e:
                        jointype = 'INNER JOIN'
                        cond = ''
                        cond = '1 = 1'
                        joinStr += cond + ' AND '
                        # print(cond)
                        # print(NodeType, ' : ', NodeName)
                        # print(InputNodes)
                        # print(view, ':', nodeView)
                        # print(joinList)
                        # print(jointype)
                        # print(e)
                    query = f'{outerQry} ({inlist[0]} ) A{tableCnt} {jointype} ({inlist[1]} ) B{tableCnt} ON {joinStr[:-4]})'
                    # print(query)
                    querySnow = f'{snowouterqry} ({snowinList[0]} ) A{tableCnt} {jointype} ({snowinList[1]} ) B{tableCnt} ON {joinStr[:-4]}) )'
                    tableCnt += 1
                else:
                    innqry = ''
                    snwinnqry = ''
                    # print(inlistDict)
                    for key_inlist,value_inlist in inlistDict.items():
                        # print(InputNodes[i])
                        innqry += value_inlist + ' UNION ALL '

                    for key_inlist,value_inlist in snowinListDict.items():
                        # print(InputNodes[i])
                        snwinnqry += value_inlist + ' UNION ALL '
                    # print(innqry[:-10])
                    query = f'{outerQry} {innqry[:-10]} )'
                    querySnow = f'{snowouterqry} {snwinnqry[:-10]} ) )'
            # calcCnt = 0
            # for calc in filterList:
            #     calcol_dict[f'FILTER{elemList[calcCnt]}'] = calc
            #     calcCnt += 1
            # print(calcol_dict)
            # for filterKey,filterVal in calcol_dict.items():
            #     if filterVal in query:
            #         query = query.replace(filterVal,filterKey)
            # print(querySnow)

            node_qryDict[NodeName] = query
            node_snwqryDict[NodeName] = querySnow
            # print("\n\n")

    # print(nodLineageDict)
    df_final = pd.DataFrame(node_qryDict.items(), columns=['NODENAME', 'SQL'])
    df_final_snw = pd.DataFrame(node_snwqryDict.items(), columns=['NODENAME', 'SQL'])
    # df_src = df2
    return df_final,df_final_snw,srcvlist,node_InputView,root,calccol_list,filterList,FuncParam


def convert_to_dobegin(dataframe,viewname):
    with open('OUTPUT.sql', 'w') as f:
        # pass
        f.truncate()
        f.write(f'DO \n BEGIN \n\n\n--VIEWNAME : "_SYS_BIC"."{viewname}"\n\n')
        for indi in dataframe.index:
            # print(f'{indi}\n\n')
            f.write(
                f"{str(dataframe['SQL'][indi])} ;\n\n--SELECT * FROM :{str(dataframe['NODENAME'][indi])};\n--END\n\n")
        f.write('END')
    f.close()

def convert_to_snowflake(dataframe,viewname,sqlRoot):
    # for indi in dataframe.index:
    #     out =  str(dataframe['SQL'][max(dataframe.count()-1)])
    #     print(out,'\n')
    col_def = ''
    for parent in sqlRoot.findall('logicalModel'):
        for child1 in parent.findall('attributes'):
            # print(child1.tag)
            for subchild in child1:
                final_col_name = subchild.attrib['id']
                outColName = f'\"{final_col_name}\"'
                # print(subchild.attrib['id'])
                col_def += f"{outColName},\n"
    col_def = col_def[:-2]

    with open('SNOWOUTPUT.sql', 'w') as f:
        # pass

        f.truncate()
        f.write(f'CREATE OR REPLACE VIEW {viewname}(\n{col_def} \n)AS \nWITH\n')
        for indi in dataframe.index:
            # print(f'{indi}\n\n')
            if indi == max(dataframe.count()) - 1:
                outerQry = f"{str(dataframe['SQL'][indi])} \n\nSELECT "
                # print(dataframe)

                for parent in sqlRoot.findall('logicalModel'):
                    for child1 in parent.findall('attributes'):
                        # print(child1.tag)
                        for subchild in child1:
                            final_col_name = subchild.attrib['id']
                            for innerChild in subchild.findall('keyMapping'):
                                sub_col_name = innerChild.attrib['columnName']
                            if final_col_name != sub_col_name:
                                outColName = f'\"{sub_col_name}\" as \"{final_col_name}\"'
                            else:
                                outColName = f'\"{final_col_name}\"'
                            # print(subchild.attrib['id'])
                            outerQry += f"{outColName},\n"
                outerQry = outerQry[:-2] + f" FROM {dataframe['NODENAME'][indi]}"
                f.write(f"{outerQry}\n")

            else:
                f.write(f"{str(dataframe['SQL'][indi])} ,\n")
        # f.write('END')
    f.close()

def textChange(file, toBeRep, repWith):
    with open(file, 'r+') as new:
        for l in fileinput.input(files=file):
            l = l.replace(toBeRep, repWith)
            # sys.stdout.write(l)
            new.write(l)
    new.close()


def convert_to_sql(dataframe, nodes,sqlRoot):
    nodelist = []
    nodeDict = {}
    for indi in dataframe.index:
        dataframe['SQL'][indi] = str(dataframe['SQL'][indi]).replace(f"{dataframe['NODENAME'][indi]} = ",'')

    outerQry ='SELECT '
    # print(dataframe)

    for parent in sqlRoot.findall('logicalModel'):
        for child1 in parent.findall('attributes'):
            # print(child1.tag)
            for subchild in child1:
                final_col_name = subchild.attrib['id']
                for innerChild in subchild.findall('keyMapping'):
                    sub_col_name = innerChild.attrib['columnName']
                if final_col_name != sub_col_name :
                    outColName = f'\"{sub_col_name}\" as \"{final_col_name}\"'
                else:
                    outColName = f'\"{final_col_name}\"'
                # print(subchild.attrib['id'])
                outerQry += f"{outColName},\n"
    outerQry = outerQry[:-2] + ' FROM '

    for num_nodeList in dataframe.index:
        nodelist.append(dataframe['NODENAME'][num_nodeList])
    # print(nodelist)

    for node_sql_num in range(0,len(nodelist)):
        nodeDict[nodelist[node_sql_num]] = f'NODE{elemList[node_sql_num]}'
    # print(nodeDict)

    for indi in dataframe.index:
        for nodename, nodeassign in nodeDict.items():
            if dataframe['NODENAME'][indi] == nodename:
                dataframe['NODENAME'][indi] = nodeassign
            dataframe['SQL'][indi] = str(dataframe['SQL'][indi]).replace(f":{nodename} ",f":{nodeassign} ")
        # print(dataframe['NODENAME'][indi])
        # print(dataframe['SQL'][indi], '\n\n')

    # for indi in dataframe.index:


    for node_num in dataframe.index:
        # for nodename, nodeassign in nodeDict.items():

        for node in nodeDict.values():
            # print(node)
            # print(dataframe['SQL'][node_num].replace('\r', ''))
            _var = dataframe['SQL'][node_num].replace('\r','')
            nodeSqlDf = dataframe.query('NODENAME == @node')
            # print(nodeSqlDf)
            nodeSql= str(nodeSqlDf['SQL'].values[0])
            # print(nodeSql)
            dataframe['SQL'][node_num] = _var.replace(f':{node}',f'({nodeSql})')
        # print(dataframe['SQL'][node_num])


    mainQuery = outerQry + '(' +str(dataframe['SQL'][max(dataframe.count()) - 1])+' )'

    with open('SQLOUT.sql', 'w') as f:
        # pass
        f.truncate()
        f.write(mainQuery)
    f.close()



def convert_to_snowsql(dataframe,nodes,sqlRoot,viewname):
    nodelist = []
    nodeDict = {}
    col_def = ''
    for parent in sqlRoot.findall('logicalModel'):
        for child1 in parent.findall('attributes'):
            # print(child1.tag)
            for subchild in child1:
                final_col_name = subchild.attrib['id']
                outColName = f'\"{final_col_name}\"'
                # print(subchild.attrib['id'])
                col_def += f"{outColName},\n"
    col_def = col_def[:-2]

    for indi in dataframe.index:
        dataframe['SQL'][indi] = str(dataframe['SQL'][indi]).replace(f"{dataframe['NODENAME'][indi]} = ",'')
        # print(dataframe['NODENAME'][indi])
        # print(dataframe['SQL'][indi],'\n\n')
    outerQry =f'CREATE OR REPLACE VIEW {viewname}(\n{col_def} \n)AS \nSELECT '
    # print(dataframe)

    for parent in sqlRoot.findall('logicalModel'):
        for child1 in parent.findall('attributes'):
            # print(child1.tag)
            for subchild in child1:
                final_col_name = subchild.attrib['id']
                for innerChild in subchild.findall('keyMapping'):
                    sub_col_name = innerChild.attrib['columnName']
                if final_col_name != sub_col_name :
                    outColName = f'\"{sub_col_name}\" as \"{final_col_name}\"'
                else:
                    outColName = f'\"{final_col_name}\"'
                # print(subchild.attrib['id'])
                outerQry += f"{outColName},\n"
    outerQry = outerQry[:-2] + ' FROM '

    for num_nodeList in dataframe.index:
        nodelist.append(dataframe['NODENAME'][num_nodeList])
    # print(nodelist)

    for node_sql_num in range(0,len(nodelist)):
        nodeDict[nodelist[node_sql_num]] = f'NODE{elemList[node_sql_num]}'
    # print(nodeDict)

    for indi in dataframe.index:
        for nodename, nodeassign in nodeDict.items():
            if dataframe['NODENAME'][indi] == nodename:
                dataframe['NODENAME'][indi] = nodeassign
            dataframe['SQL'][indi] = str(dataframe['SQL'][indi]).replace(f":{nodename} ",f":{nodeassign} ")
        # print(dataframe['NODENAME'][indi])
        # print(dataframe['SQL'][indi], '\n\n')

    # for indi in dataframe.index:


    for node_num in dataframe.index:
        # for nodename, nodeassign in nodeDict.items():

        for node in nodeDict.values():
            # print(node)
            # print(dataframe['SQL'][node_num].replace('\r', ''))
            _var = dataframe['SQL'][node_num].replace('\r','')
            nodeSqlDf = dataframe.query('NODENAME == @node')
            # print(nodeSqlDf)
            nodeSql= str(nodeSqlDf['SQL'].values[0])
            # print(nodeSql)
            dataframe['SQL'][node_num] = _var.replace(f':{node}',f'({nodeSql})')
        # print(dataframe['SQL'][node_num])


    mainQuery = outerQry + '(' +str(dataframe['SQL'][max(dataframe.count()) - 1])+' )'

    with open('SNOWSQLOUT.sql', 'w') as f:
        # pass
        f.truncate()
        f.write(mainQuery)
    f.close()