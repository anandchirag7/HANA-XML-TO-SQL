import pandas as pd
import re
import PySimpleGUI as sg
import os
from hdbcli import dbapi


class hanaQry():
    def __init__(self, host, port, user, passwd, logintype):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.logintype = logintype

    def connectionCreate(self):
        if self.logintype == 'SSO':
            conn = dbapi.connect(
                address=self.host,
                port=self.port,
                user=os.getlogin())
            cursor = conn.cursor()
        else :
            conn = dbapi.connect(
                address=self.host,
                port=self.port,
                user=self.user,
                password = self.passwd)
            cursor = conn.cursor()

        return cursor, conn

    def capture_SchemaDrp(self,cursor,conn,inp):
        # cursor, conn = connectionCreate(environment)
        sqlSchema = []
        SchemaTableMap = {}
        schemaDropdown = []
        tableDropdown = []
        if inp == 'view':
            sqlSchemaquery = "SELECT DISTINCT PACKAGE_ID FROM \"_SYS_REPO\".\"ACTIVE_OBJECT\" WHERE (lower(PACKAGE_ID) " \
                             "NOT LIKE 'sap%' AND lower(PACKAGE_ID) NOT LIKE 'public%' AND lower(PACKAGE_ID) NOT LIKE " \
                             "'system%' AND lower(PACKAGE_ID) NOT LIKE '%.table%'AND lower(PACKAGE_ID) NOT LIKE " \
                             "'%.function%' AND lower(PACKAGE_ID) NOT LIKE '%.procedure%'AND lower(PACKAGE_ID) NOT LIKE " \
                             "'%.service%' ) ORDER BY 1; "

            cursor.execute(sqlSchemaquery)
            out = cursor.fetchall()
            df = pd.DataFrame(out)
            df['SCHEMA'] = df
            for i in df['SCHEMA'].unique():
                schemaDropdown.append(i)
        else:
            sqlSchemaquery = f"SELECT DISTINCT \"SCHEMA_NAME\" FROM TABLE_COLUMNS where SCHEMA_NAME in (\'{os.getlogin().upper()}\','SPAN_ODS') ORDER BY 1"
            cursor.execute(sqlSchemaquery)
            out = cursor.fetchall()
            df = pd.DataFrame(out)
            df['TABLE'] = df
            # print(df)
            for i in df['TABLE'].unique():
                schemaDropdown.append(i)
            # print(schemaDropdown)
        # conn.close()
        return schemaDropdown

    def capture_TableDrp(self,cursor,conn,inp, schema):
        # cursor, conn = connectionCreate(environment)
        sqlSchema = []
        SchemaTableMap = {}
        schemaDropdown = []
        tableDropdown = []
        if inp == 'view':
            sqlTablequery = f"SELECT DISTINCT OBJECT_NAME FROM \"_SYS_REPO\".\"ACTIVE_OBJECT\" WHERE (PACKAGE_ID = \'{schema}\' AND OBJECT_SUFFIX =\'calculationview\' ) ORDER BY 1 "
            cursor.execute(sqlTablequery)
            out = cursor.fetchall()
            df = pd.DataFrame(out)
            df['TABLE'] = df
            for i in df['TABLE'].unique():
                tableDropdown.append(i)

        else:
            sqlTablequery = f"SELECT DISTINCT \"TABLE_NAME\" FROM TABLE_COLUMNS  WHERE \"SCHEMA_NAME\" = \'{schema}\' order by 1"
            cursor.execute(sqlTablequery)
            out = cursor.fetchall()
            df = pd.DataFrame(out)
            df['TABLE'] = df
            for i in df['TABLE'].unique():
                tableDropdown.append(i)
            # print(tableDropdown)
        # conn.close()
        return tableDropdown