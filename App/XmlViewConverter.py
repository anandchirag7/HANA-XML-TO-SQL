import PySimpleGUI as sg
# import hanaClass as hc
from hanaClass import hanaQry
import XMLReader as xlc
import os,shutil
from pathlib import Path
import convToDoBegin as cnv
import convSrc as cns


def calculation_Convert():
    pass

def filter_Convert():
    pass
UI_font = ("Segoe UI", 11)
INPUT_SIZE = 30

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

def add_xml():
    add_layout = [[sg.Multiline(enter_submits=True,size=(60,40), key='-XML-',no_scrollbar=False)],
                  [sg.Button('Save',key ='-SAVEXML-')]]

    addXmlWindow = sg.Window(
            title='Add xml data manually',
            layout=add_layout,
            font=UI_font,
            resizable=True,
            finalize=True, return_keyboard_events=True,modal =True,
             margins=(0, 0))

    while True:             # Event Loop
        event, values = addXmlWindow.read()
        # print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == '-SAVEXML-':
            with open('toBeConverted.xml', 'wt',encoding='UTF-8') as xml:
                xml.write(values['-XML-'])
                xml.close()
            addXmlWindow.close()

def show_window(host,port,usr,passwd,lgt):
    hanaConn = hanaQry(host=host,port=port,user=usr,passwd=passwd,logintype=lgt)
    cursor, conn = hanaConn.connectionCreate()
    choices = hanaConn.capture_SchemaDrp(cursor,conn,'view')
    tableValDropdown =[]
    sg.theme('NewTheme18878')
    UI_font = ("Segoe UI", 11)
    fixed_font = ('Consolas', 11)
    menu_def = [['&Application', ['&Exit']],
                ['&Help', ['&About']]]

    layout = [ [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 15', tearoff=True)],
               [sg.T('Please choose the Object to be converted')],
                [sg.Col([[sg.Text(text='Select Package', visible=True, key='select_TableSchema')],
                     [sg.Input('', size=(30, 1),  enable_events=True, key='-IN-')],
                     [sg.pin(sg.Col([[sg.Listbox(values=[], size=(30, 4), enable_events=True, key='-SCHEMADROP-',
                                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                                                 no_scrollbar=False)]],
                                    key='-BOXCONTAINER-', pad=(0, 0), visible=False))]], key='-Frame1-',
                    vertical_alignment='top'),
             sg.Col([[sg.Text(text='Select View', visible=True, key='select_Maintable')],
                     [sg.Input('', size=(70, 1),  enable_events=True, key='-IN1-')],
                     [sg.pin(sg.Col([[sg.Listbox(values=[], size=(70, 4), enable_events=True, key='-TABLEDROP-',
                                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, )]],
                                    key='-BOXCONTAINER1-', pad=(0, 0), visible=False))]], key='-Frame2-',
                    vertical_alignment='top')],
                    [sg.Button('SQL Do Begin Block',key='-CONDB-',disabled=True,pad =(10)),sg.Button('Single SQL Query', key='-CONSQL-',disabled=True),sg.Button('Snowflake CTE View', key='-CONSNW-',disabled=True),sg.Button('Snowflake SQL View', key='-CONSNWSQL-',disabled=True),
                     sg.Button('Exit')]]

    window = sg.Window(
            title='View To Sql Creator',
            icon='logo.ico',
            layout=layout,
            font=UI_font,
            resizable=True,
            finalize=True, return_keyboard_events=True,modal =True)


    window.set_icon('logo.ico')

    list_element: sg.Listbox = window.Element('-SCHEMADROP-')
    list_element.bind('<Key>', ' Key')
    list_element1: sg.Listbox = window.Element('-TABLEDROP-')
    list_element1.bind('<Key>', ' Key')
    window['-IN-'].bind("<Return>", "_Enter")
    window['-IN1-'].bind("<Return>", "_Enter")
    prediction_list, prediction_list_table, input_text, sel_item, sel_item_table = [], [], "", 0, 0

    while True:             # Event Loop
        event, values = window.read()
        # print(event, values)
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

        elif event.startswith('Escape'):
            window['-IN-'].update('')
            window['-BOXCONTAINER-'].update(visible=False)
            window['-BOXCONTAINER1-'].update(visible=False)

        elif event.startswith('Down') and window['-BOXCONTAINER-'].visible == True:
            try:

                sel_item = (sel_item + 1) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
            except Exception as e:
                pass

        elif event.startswith('Down') and window['-BOXCONTAINER1-'].visible == True:
            try:
                sel_item_table = (sel_item_table + 1) % len(prediction_list_table)
                list_element1.update(set_to_index=sel_item_table, scroll_to_index=sel_item_table)
            except Exception as e:
                pass

        elif event.startswith('Up') and window['-BOXCONTAINER-'].visible == True:
            try:
                sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
            except Exception as e:
                pass

        elif event.startswith('Up') and window['-BOXCONTAINER1-'].visible == True:
            try:
                sel_item_table = (sel_item_table + (len(prediction_list_table) - 1)) % len(prediction_list_table)
                list_element1.update(set_to_index=sel_item_table, scroll_to_index=sel_item_table)
            except Exception as e:
                pass

        elif event == '\r':
            if len(values['-SCHEMADROP-']) > 0:
                window['-IN-'].update(value=values['-SCHEMADROP-'])
                window['-BOXCONTAINER-'].update(visible=False)

            elif len(values['-TABLEDROP-']) > 0:
                window['-IN1-'].update(value=values['-TABLEDROP-'])
                window['-BOXCONTAINER1-'].update(visible=False)
                window['-CONDB-'].update(disabled=False)


        elif event == "-IN-" + "_Enter":

            window['-IN-'].update(value=values['-SCHEMADROP-'])
            values['-SCHEMADROP-'] = values['-SCHEMADROP-']
            visible = False
            window['-BOXCONTAINER-'].update(visible=False)
            tableValDropdown = hanaConn.capture_TableDrp(cursor,conn,'view', values['-SCHEMADROP-'][0])
            window['-IN1-'].update(disabled=False)

        elif event == "-IN1-" + "_Enter":
            window['-CONDB-'].update(disabled=False)
            window['-CONSQL-'].update(disabled=False)
            window['-CONSNW-'].update(disabled=False)
            window['-CONSNWSQL-'].update(disabled=False)
            window['-IN1-'].update(value=values['-TABLEDROP-'])
            visible = False
            window['-BOXCONTAINER1-'].update(visible=False)
            window['-IN-'].update(disabled=False)

        elif event == '-IN-':
            window['-IN1-'].update(value='', disabled=True)
            SchemaTxt = values['-IN-']
            # print(SchemaTxt)
            if SchemaTxt == input_text:
                continue
            else:
                input_text = SchemaTxt
            prediction_list = []
            if SchemaTxt:
                prediction_list = [item for item in choices if item.lower().__contains__(SchemaTxt.lower())]

            list_element.update(values=prediction_list)
            sel_item = 0
            list_element.Update(set_to_index=sel_item)

            if len(prediction_list) > 0:
                window['-BOXCONTAINER-'].update(visible=True)

            else:
                window['-BOXCONTAINER-'].update(visible=False)


        elif event == '-IN1-':
            window['-CONDB-'].update(disabled=False)
            window['-CONSQL-'].update(disabled=False)
            window['-CONSNW-'].update(disabled=False)
            window['-CONSNWSQL-'].update(disabled=False)
            window['-IN-'].update(disabled=True)

            text = values['-IN1-']
            if text == input_text:
                continue
            else:
                input_text = text
            prediction_list_table = []

            if text:
                prediction_list_table = [item for item in tableValDropdown if (item.lower()).__contains__(text.lower())]

            list_element1.update(values=prediction_list_table)
            sel_item_table = 0
            list_element1.Update(set_to_index=sel_item_table)

            if len(prediction_list) > 0:
                window['-BOXCONTAINER1-'].update(visible=True)
            else:
                window['-BOXCONTAINER1-'].update(visible=False)


        elif event == '-SCHEMADROP-':
            window['-IN-'].update(value=values['-SCHEMADROP-'])
            visible = False
            window['-BOXCONTAINER-'].update(visible=False)
            # print(values['-SCHEMADROP-'])
            tableValDropdown = hanaConn.capture_TableDrp('view', values['-SCHEMADROP-'][0])
            window['-IN1-'].update(disabled=False)


        elif event == '-TABLEDROP-':
            window['-CONDB-'].update(disabled=False)
            window['-CONSQL-'].update(disabled=False)
            window['-CONSNW-'].update(disabled=False)
            window['-CONSNWSQL-'].update(disabled=False)
            window['-IN1-'].update(value=values['-TABLEDROP-'])
            visible = False
            window['-BOXCONTAINER1-'].update(visible=False)
            window['-IN-'].update(disabled=False)

        elif event == '-CONDB-':
            # print(values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0])
            try:
                data_conv,data_nr,data_src, sql_nodes,root,calculated_col,filterCol,Input_col = xlc.converViewToXml(cursor,conn, values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0])
            except Exception as e:
                sg.Popup(f'{e} : To Correct the error please place the xml text instead in next window')
                add_xml()
                try:
                    data_conv,data_nr,data_src, sql_nodes, root, calculated_col, filterCol,Input_col = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0],file='toBeConverted.xml')
                except Exception as e:
                    sg.popup('Please upload the XML in correct format')
            else:
                pass
            viewName = values['-SCHEMADROP-'][0]+'/'+values['-TABLEDROP-'][0]
            try:
                xlc.convert_to_dobegin(data_conv,viewName)
            except Exception as con:
                sg.popup('Incorrect XML data added for conversion. Please check and retry again !!')
            else:
                if len(calculated_col)+ len(filterCol)+ len(Input_col)>0:
                    windowCompleted = cnv.show_window(calculated_col,filterCol,'DOBEGIN',Input_col)
                    # for valyeild in windowCompleted:
                    if windowCompleted == 'GO':
                        # print(windowCompleted)
                        cnv.custom_meter_example()
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        source_file_path = os.path.join(script_dir, 'OUTPUT.sql')
                        filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                                   no_window=True)
                        try:
                            shutil.copy(source_file_path, filename)
                        except Exception as e:
                            sg.popup(e)
                        else:
                            sg.popup(
                                f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}",
                                title='Download Complete')

                else:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    # print(script_dir)
                    source_file_path = os.path.join(script_dir, 'OUTPUT.sql')
                    filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                               no_window=True)
                    try:
                        shutil.copy(source_file_path, filename)
                    except Exception as e:
                        sg.popup(e)
                    else:
                        sg.popup(f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}", title='Download Complete')

        elif event == '-CONSQL-':
            try:
                data_conv,data_nr,data_src, nodes_sql,root_sql,calculated_col_sql,filterCol_sql,InputCol_sql = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0])
            except Exception as e:
                sg.Popup(f'{e} : To Correct the error please place the xml text instead in next window')
                add_xml()
                try:
                    data_conv,data_nr,data_src, nodes_sql,root_sql,calculated_col_sql,filterCol_sql,InputCol_sql = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0],file='toBeConverted.xml')
                except Exception as e:
                    sg.popup('Please upload the XML in correct format')
            else:
                pass
            viewName = values['-SCHEMADROP-'][0]+'/'+values['-TABLEDROP-'][0]
            try:
                xlc.convert_to_sql(data_conv,nodes_sql,root_sql)
            except Exception as con:
                sg.popup('Incorrect XML data added for conversion. Please check and retry again !!')
            else:
                if len(calculated_col_sql)+ len(filterCol_sql)+ len(InputCol_sql)>0:
                    windowCompletedSql = cnv.show_window(calculated_col_sql,filterCol_sql,'SQL',InputCol_sql)
                    # for valyeildSql in windowCompletedSql:
                    if windowCompletedSql == 'GO':
                        # print(windowCompletedSql)
                        cnv.custom_meter_example()
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        source_file_path = os.path.join(script_dir, 'SQLOUT.sql')
                        filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                                   no_window=True)
                        try:
                            shutil.copy(source_file_path, filename)
                        except Exception as e:
                            sg.popup(e)
                        else:
                            sg.popup(
                                f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}",
                                title='Download Complete')

                            # print(valyeildSql)
                            # break
                else:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    # print(script_dir)
                    source_file_path = os.path.join(script_dir, 'SQLOUT.sql')
                    filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                               no_window=True)
                    try:
                        shutil.copy(source_file_path, filename)
                    except Exception as e:
                        sg.popup(e)
                    else:
                        sg.popup(f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}", title='Download Complete')

        elif event == '-CONSNWSQL-':
            try:
                data_conv,data_nr,data_src, nodes_sql,root_sql_snw,calculated_col_sql_snw,filterCol_sql_snw,InputCol_sql_snw = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0])
            except Exception as e:
                sg.Popup(f'{e} : To Correct the error please place the xml text instead in next window')
                add_xml()
                try:
                    data_conv,data_nr,data_src, nodes_sql,root_sql_snw,calculated_col_sql_snw,filterCol_sql_snw,InputCol_sql_snw = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0],file='toBeConverted.xml')
                except Exception as e:
                    sg.popup('Please upload the XML in correct format')
            else:
                pass
            viewName_sql_snw = values['-SCHEMADROP-'][0]+'/'+values['-TABLEDROP-'][0]
            try:
                xlc.convert_to_snowsql(data_conv,nodes_sql,root_sql_snw,f'"_SYS_BIC"."{viewName_sql_snw}"')
            except Exception as con:
                sg.popup('Incorrect XML data added for conversion. Please check and retry again !!')
            else:
                if len(calculated_col_sql_snw)+ len(filterCol_sql_snw)+ len(InputCol_sql_snw)>0:
                    windowCompletedSnwSql = cnv.show_window(calculated_col_sql_snw,filterCol_sql_snw,'SNOW_SQL',InputCol_sql_snw)
                    # for valyeildSql in windowCompletedSql:
                    if windowCompletedSnwSql == 'GO':
                        # print(windowCompletedSnwSql)
                        cnv.custom_meter_example()
                        srcConvert = cns.show_window(data_src,viewName_sql_snw)
                        if srcConvert == 'GO':
                            cnv.custom_meter_example()
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            source_file_path = os.path.join(script_dir, 'SNOWSQLOUT.sql')
                            filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                                       no_window=True)
                            try:
                                shutil.copy(source_file_path, filename)
                            except Exception as e:
                                sg.popup(e)
                            else:
                                sg.popup(
                                    f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}",
                                    title='Download Complete')

                            # print(valyeildSql)
                            # break
                else:
                    srcConvert = cns.show_window(data_src, viewName_sql_snw)
                    if srcConvert == 'GO':
                        cnv.custom_meter_example()
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        # print(script_dir)
                        source_file_path = os.path.join(script_dir, 'SNOWSQLOUT.sql')
                        filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                                   no_window=True)
                        try:
                            shutil.copy(source_file_path, filename)
                        except Exception as e:
                            sg.popup(e)
                        else:
                            sg.popup(f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}", title='Download Complete')

        elif event == '-CONSNW-':
            # print(values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0])
            view = values['-SCHEMADROP-'][0]+'/'+values['-TABLEDROP-'][0]
            # print(view)
            try:
                data_conv,data_snw,data_src, sql_nodes_snw,root_snw,calculated_col_snw,filterCol_snw,Input_col_snw = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0])
            except Exception as e:
                sg.Popup(f'{e} : To Correct the error please place the xml text instead in next window')
                add_xml()
                try:
                    data_conv,data_snw,data_src, sql_nodes_snw,root_snw,calculated_col_snw,filterCol_snw,Input_col_snw = xlc.converViewToXml(cursor,conn,values['-SCHEMADROP-'][0],values['-TABLEDROP-'][0],file='toBeConverted.xml')
                except Exception as e:
                    sg.popup('Please upload the XML in correct format')
            else:
                pass
            # viewName = values['-SCHEMADROP-'][0]+'/'+values['-TABLEDROP-'][0]
            try:
                xlc.convert_to_snowflake(data_snw,f'"_SYS_BIC"."{view}"',root_snw)
            except Exception as con:
                sg.popup('Incorrect XML data added for conversion. Please check and retry again !!')
            else:
                if len(calculated_col_snw)+ len(filterCol_snw)+ len(Input_col_snw)>0:
                    windowCompleted_snw = cnv.show_window(calculated_col_snw,filterCol_snw,'SNWSQL',Input_col_snw)
                    # for valyeild in windowCompleted:
                    if windowCompleted_snw == 'GO':
                        # print(windowCompleted_snw)
                        cnv.custom_meter_example()
                        srcConvert = cns.show_window(data_src,view)
                        if srcConvert == 'GO':
                            cnv.custom_meter_example()
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            source_file_path = os.path.join(script_dir, 'SNOWOUTPUT.sql')
                            filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                                       no_window=True)
                            try:
                                shutil.copy(source_file_path, filename)
                            except Exception as e:
                                sg.popup(e)
                            else:
                                sg.popup(
                                    f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}",
                                    title='Download Complete')

                else:
                    srcConvert = cns.show_window(data_src, view)
                    if srcConvert == 'GO':
                        cnv.custom_meter_example()
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        # print(script_dir)
                        source_file_path = os.path.join(script_dir, 'SNOWOUTPUT.sql')
                        filename = sg.PopupGetFile('Save Settings', file_types=(("All sql Files", "*.sql"),), save_as=True,
                                                   no_window=True)
                        try:
                            shutil.copy(source_file_path, filename)
                        except Exception as e:
                            sg.popup(e)
                        else:
                            sg.popup(f"View has been converted to SQL \nand the file for the view has\nbeen downloaded to: {filename}", title='Download Complete')

        elif event == '-DWNDDOC-':
            # print(Path.home())
            script_dir = os.path.dirname(os.path.abspath(__file__))
            source_file_path = os.path.join(script_dir, 'OUTPUT.sql')
            filename = sg.PopupGetFile('Save Settings',file_types=(("All sql Files", "*.sql"),), save_as=True,
                                       no_window=True)
            try:
                shutil.copy(source_file_path, filename)
            except Exception as e:
                sg.popup(e)
            else:

                sg.popup(f"DM Document file downloaded to: {filename}", title='Download Complete')


    window.close()


def main(host,port,usr,passwd,lgt):
    show_window(host,port,usr,passwd,lgt)


if __name__ == '__main__':
    main('','','','','')

