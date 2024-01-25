# import time
from hdbcli import dbapi
import PySimpleGUI as sg
from hanaClass import hanaQry
import XMLReader as xlc
import os,shutil
from pathlib import Path
import convToDoBegin as cnv
import convSrc as cns
import json
import XmlViewConverter as xmlc

UI_font = ("Segoe UI", 11)
INPUT_SIZE = 30

EnvDict = {"Development" :"DEV",
           "Quality":"QA",
           "Test":"TEST",
           "Production": "PROD"}

credDict = {"dbDrop" : ["Databases","DATABASE"],
            "hostDrop" : ["Hosts","HOST"],
            "portDrop" : ["Ports","PORT"],
            "UserDrop": ["Users","USER"],
            "PassDrop" :["Passwords","PASS"]}
sg.theme_add_new(
    'NewTheme18878',
    {
        'BACKGROUND': '#dfedf2',
        'TEXT': '#000000',
        'INPUT': '#183440',
        'SCROLL': '#dfedf2',
        'TEXT_INPUT': '#FFFFFF',
        'BUTTON': ('#dfedf2', '#183440'),
        'PROGRESS': ('#6cb6ff', '#000000'),
        'BORDER': 1,
        'SLIDER_DEPTH': 0,
        'PROGRESS_DEPTH': 0,
    }
)


EnvDrop = []

file = 'config.json'
f = open(file)
data = json.load(f)

def getEnv(InpHead):
    for dbDetails in data[InpHead]:
        for key, value in dbDetails.items():
            EnvDrop.append(value)
    return EnvDrop
getEnv('Environment')

def getLoginDetails(envInp):
    dbDrop,hostDrop,portDrop,UserDrop,PassDrop = [],[],[],[],[]

    # for col,val in credDict.items():
    #     list(col).append(data[val[0]][0][val[1]+envInp])
    #     print(data[val[0]][0][val[1]+envInp])
    dbDrop.append(data['Databases'][0][f'DATABASE{envInp}'])
    hostDrop.append(data['Hosts'][0][f'HOST{envInp}'])
    portDrop.append(data['Ports'][0][f'PORT{envInp}'])
    UserDrop.append(data['Users'][0][f'USER{envInp}'])
    PassDrop.append(data['Passwords'][0][f'PASS{envInp}'])

    return dbDrop,hostDrop,portDrop,UserDrop,PassDrop


def getVal(Env):

    outEnv = EnvDict[Env]
    db,hst,prt,usr,ps = getLoginDetails(outEnv)
    return db,hst,prt,usr,ps


def show_window():
    # choices = hc.capture_SchemaDrp('view', 'dev')
    # tableValDropdown =[]
    sg.theme('NewTheme18878')
    UI_font = ("Segoe UI", 11)
    fixed_font = ('Consolas', 11)
    menu_def = [['&Application', ['&Exit']],
                ['&Help', ['&About']]]

    layout = [ [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 15', tearoff=True)],#[sg.Text('This Application helps in converting HANA Calculation Views to SQL queries')],
               [[sg.Text('Environment : '), sg.Push(),
                 sg.InputCombo(values=EnvDrop, default_value=EnvDrop[0], size=INPUT_SIZE + 30,
                               enable_events=True, key='-ENVDRP-', visible=True)],
                [sg.Text('Select Host : '), sg.Push(),
                 sg.InputCombo(values=[], default_value=[], size=INPUT_SIZE + 30,
                               enable_events=True, key='-HSDRP-', visible=True)],
                [sg.Text('Select Port : '), sg.Push(),
                 sg.InputCombo(values=[], default_value=[], size=INPUT_SIZE + 30,
                               enable_events=True, key='-PODRP-', visible=True)],
                [sg.Text('Select Database : '), sg.Push(),
                 sg.InputCombo(values=[], default_value=[], size=INPUT_SIZE + 30,
                               enable_events=True, key='-DBDRP-', visible=True)]
                ],[sg.Text('Select User : '), sg.Push(),
                 sg.InputCombo(values=[], default_value=[], size=INPUT_SIZE + 30,
                               enable_events=True, key='-USRDRP-', visible=True)]
                ,[sg.Text('Input Password : '), sg.Push(),
                 sg.InputCombo(values=[], default_value=[], size=INPUT_SIZE + 30,
                               enable_events=True, key='-PASSDRP-', visible=True)]
                ,
                    [sg.Button('Login Using SSO',key='-CONDB-',disabled=True,pad =(10)),sg.Button('Login With Password', key='-CONSQL-',disabled=True),
                     sg.Button('Exit')]]

    window = sg.Window(
            title='View To Sql Creator',
            icon='logo.ico',
            layout=layout,
            font=UI_font,
            resizable=True,
            finalize=True, return_keyboard_events=True,modal =True)


    window.set_icon('logo.ico')

    while True:             # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            break
        elif event in (None, 'Exit'):
            # print("[LOG] Clicked Exit!")
            break
        elif event == 'About':
            # print("[LOG] Clicked About!")
            sg.popup('This is XML to view converter app created in python\nusing Pysimplegui for ui.\n\nThis application is used to convert the\ngraphical views in SAP HANA to an easily \nunderstandable SQL fomat'
                     '\n\nBelow Features are integrated in the Application',
                     '1. Conversion of View to Single SQL query',
                     '2. Conversion of View to DO BEGIN Block',
                     '3. Conversion of View to Snowflake CTE View',
                     '4. Conversion of View to Snowflake sql query View',
                     '5. Source and target name download and change',
                     '6. Calculations and filter download',
                     'Developed By : CHIRAG ANAND',keep_on_top=True)

        elif event == '-ENVDRP-':
            environemnt = values['-ENVDRP-']
            db, host, port, user, password = getVal(environemnt)
            pswd = '*'* 15
            window['-HSDRP-'].update(value= host)
            window['-PODRP-'].update(value= port)
            window['-DBDRP-'].update(value= db)
            window['-USRDRP-'].update(value=user)
            window['-PASSDRP-'].update(value=pswd)
            window['-CONDB-'].update(disabled=False)
            window['-CONSQL-'].update(disabled=False)

        elif event == '-CONDB-':
            login_type ='SSO'
            hanaConn = hanaQry(host=host[0], port=port[0], user='', passwd='', logintype=login_type)
            cursor, conn = hanaConn.connectionCreate()
            sg.Popup('connected')
            window.close()
            xmlc.main(host[0],port[0],'','',login_type)



        elif event == '-CONSQL-':
            window['-USRDRP-'].update(visible = True)
            window['-PASSDRP-'].update(visible = True)
            login_type = 'PASSWD'
            hanaConn = hanaQry(host=host[0], port=port[0], user=user[0], passwd=password[0], logintype=login_type)
            cursor, conn = hanaConn.connectionCreate()
            sg.Popup('connected')
            window.close()
            xmlc.main(host[0], port[0], user[0], password[0], login_type)



    window.close()


def main():
    show_window()


if __name__ == '__main__':
    main()

