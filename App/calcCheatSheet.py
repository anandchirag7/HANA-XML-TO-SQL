import PySimpleGUI as sg
import fileinput
import pandas as pd
import xlsxwriter
import shutil,os
import calculationConvert as cc


font1 = ('Courier New', 10)
font2 = ('Courier New', 10, 'bold')


listGraph = ['component(date,1)'
,'component(date,2)'
,'component(date,3)'
,'component(time,4)'
,'component(time,5)'
,'component(time,6)'
,'strlen(string)'
,'midstr(string, int, int)'
,'leftstr(string, int)'
,'rightstr(string, int)'
,'ltrim(string) or ltrim(string, string)'
,'rtrim(string) or rtrim(string, string)'
,'trim(string) or trim(string, string)'
,'lpad(string, int) or lpad(string, int, string)'
,'rpad(string, int) or rpad(string, int, string)'
,'replace(originalString, searchString, replaceString))'
,'upper(string)'
,'lower(string)'
,'int(arg)'
,'float(arg)'
,'double (arg)'
,'string (arg)'
,'date(stringarg)'
,'longdate(stringarg)'
,'time(stringarg)'
,'seconddate(string)'
,'secondtime(string)'
,'weekday(date)'
,'now()'
,'daysbetween(date1, date2)'
,'secondsbetween(seconddate1, seconddate2)'
,'addseconds(date, int)'
,'adddays(date, int)'
,'quarter(date)'
,'format(longdate, string)'
,'if(intarg, arg2, arg3)'
,'in(arg1, ...)'
,'case(arg1, cmp1, value1, cmp2, value2, ..., default)'
,'isnull(arg1)'
,'max(arg1, arg2, arg3, ...)'
,'min(arg1, arg2, arg3, ...)',
'match(arg1,\'*string\')']

listConvert =['extract_month'
,'extract_day'
,'extract_year'
,'extract_hour'
,'extract_minute'
,'extract_second'
,'length(string)'
,'substr(string, start,chars)'
,'left(string, int)'
,'right(string, int)'
,'ltrim(string) or ltrim(string, string)'
,'rtrim(string) or rtrim(string, string)'
,'trim(string) or trim(string, string)'
,'lpad(string, int) or lpad(string, int, string)'
,'rpad(string, int) or rpad(string, int, string)'
,'replace(originalString, searchString, replaceString))'
,'upper(string)'
,'lower(string)'
,'to_int(arg)'
,'to_float(arg)'
,'to_double (arg)'
,'to_string (arg)'
,'to_date(stringarg)'
,'to_longdate(stringarg)'
,'to_time(stringarg)'
,'to_seconddate(string)'
,'to_secondtime(string)'
,'to_weekday(date)'
,'current_timestamp or now()'
,'days_between(date1, date2)'
,'seconds_between(seconddate1, seconddate2)'
,'add_seconds(date, int)'
,'add_days(date, int)'
,'quarter(date)'
,'to_varchar(date, string)'
,'case when intarg then arg2 else arg3 end'
,'arg1 in(values...)'
,'case when arg1 then value1 when arg2 then value2 else default end'
,'arg1 is null'
,'max(arg1)'
,'min(arg1)'
,'arg1 like \'%string\')']


DictConvert ={}
def show_window():
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

    windoSize =900
    windowheight =500

    calc_columns = [[sg.Push(),sg.T('Graphical View Functions'),sg.Push(),sg.T('SQL Functions'),sg.Push()],[sg.Column([[sg.Multiline(f'{listGraph[i]}', size=(50, 2), expand_x=True, no_scrollbar=True,enable_events=True, key=f'-MLINEC{i}-', disabled=True, font=font2),
                    sg.VSeparator(),sg.Multiline(listConvert[i],size=(50, 2), expand_x=True, enable_events=True, no_scrollbar=True,key=f'-CRINEC{i}-',font=font2)] for i in range(0, len(listGraph))],
                    expand_x=True,expand_y=True, scrollable=True, vertical_scroll_only=True)]]

    window = sg.Window('Graphical Calculations to SQl Format Cheatsheet', calc_columns,return_keyboard_events=True,modal=True,size=(windoSize,windowheight))  #size=(1000,800)
    window.set_icon(r'logo.ico')

    while True:  # Event Loop
        event, values = window.read() #type:[],{}
        # print('============ Event = ', event, ' ==============')
        # print('-------- Values Dictionary (key=value) --------')
        # for key in values:
        #     print(key, ' = ', values[key])
        # print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def main():
    show_window()


if __name__ == '__main__':
    main()




