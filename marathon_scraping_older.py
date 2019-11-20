# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:02:02 2019

@author: night
"""

import requests
import dill
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
import re
import pandas as pd
import numpy as np

def save_pkl(df, filename):
    with open(filename,'wb') as fobj:
        dill.dump(df,fobj)
    
def remove_prefix(raw, pref):
    re_str = pref+'(.+)'
    compiled_regex = re.compile(re_str)
    return re.findall(compiled_regex, raw)[0]
    
    
def split_name(namefield):
    compiled_regex = re.compile(r'(.+) \(([A-Z]+)\)')
    try:
        name_country = re.findall(compiled_regex, namefield)[0]
    except IndexError:
        name_country = (namefield, None)
    return name_country

def parse_time(time_string):
    dt = parse(time_string)-parse('00:00:00')
    return dt.seconds/3600

def get_fields(row):
    
    name_country = split_name(row.find_all('h4', class_=' list-field type-fullname')[0].text)
    try:
        data_row = [int(row.find_all('div', class_=' list-field type-place place-secondary hidden-xs numeric')[0].text), #overall place
                    int(row.find_all('div', class_=' list-field type-place place-primary numeric')[0].text), #gender place
                    name_country[0], #name
                    name_country[1], #country
                    remove_prefix(row.find_all('div', class_=' list-field type-field')[0].text, 'BIB'), #bib number
                    remove_prefix(row.find_all('div', class_=' list-field type-age_class')[0].text, 'Division')] # division
        try:
            half_time = parse_time(remove_prefix(row.find_all('div', class_='split list-field type-time')[0].text, 'HALF')) # half time
        except ValueError:
            half_time = None
            
        try:
            fin_time = parse_time(remove_prefix(row.find_all('div', class_=' list-field type-time')[0].text, 'Finish')) # finish time
        except ValueError:
            fin_time = None
            
        data_row.extend([half_time, fin_time])
                
        return data_row
    except IndexError:
        return None
    
data = []

num_dnf = 0
sexes = ['M','W']
yrs = [str(yr) for yr in np.arange(2018,1995,-1)]
event_codes = ['MAR_999999107FA30900000000B5'#2018,
               'MAR_999999107FA30900000000A1', #2017
               'MAR_999999107FA309000000008D', #2016
               'MAR_999999107FA3090000000079', #2015
               'MAR_999999107FA3090000000065', #2014
               'MAR_9999990E9A92360000000079', #2013
               'MAR_9999990E9A9236000000003D', #2012
               'MAR_9999990E9A92360000000029', #2011
               'MAR_9999990E9A92360000000015', #2010
               'MAR_9999990E9A92360000000002', #2009
               'MAR_9999990E9A92360000000051', #2008
               'MAR_9999990E9A92360000000052', #2007
               'MAR_9999990E9A92360000000065', #2006
               'MAR_9999990E9A92360000000066', #2005
               'MAR_9999990E9A92360000000067', #2004
               'MAR_9999990E9A92360000000068', #2003
               'MAR_9999990E9A92360000000069', #2002
               'MAR_9999990E9A9236000000006A', #2001
               'MAR_9999990E9A9236000000006B', #2000
               'MAR_9999990E9A9236000000006C', #1999
               'MAR_9999990E9A9236000000006D', #1998
               'MAR_9999990E9A9236000000006E', #1997
               'MAR_9999990E9A9236000000006F' #1996
               ] 

for count, event_code in enumerate(event_codes):
    yr_df = pd.DataFrame()
    for sex in sexes:
        data = []
        i = 1
        pg_found = True
        while pg_found:
            
            print(f'Page: {i}')
            result_pg = f'https://chicago-history.r.mikatiming.com/2018/?page={i}&event={event_code}&lang=EN_CAP&num_results=1000&pid=list&search%5Bsex%5D={sex}&search%5Bage_class%5D=%25'
            page = requests.get(result_pg)
            soup = BeautifulSoup(page.text, 'html.parser')
        
            rows = soup.find_all('li', class_=' list-active list-group-item row')
            rows.extend(soup.find_all('li', class_=' list-group-item row'))
            if len(rows) > 0:
                for row in rows:
                    data_row = get_fields(row)
                    if data_row:
                        data.append(data_row)
                    else:
                        num_dnf += 1
            else:
                pg_found = False
            i += 1
        sex_df = pd.DataFrame(data, columns=['Place', 'GenderPlace', 'Name', 'Country', 'BibNumber', 'Division', 'HalfTime', 'Time'])
        sex_df['Gender'] = [sex for i in range(len(sex_df))]
        if yr_df.empty:
            yr_df = sex_df            
        else:
            yr_df = pd.concat([yr_df, sex_df])
    filename = f'{yrs[count]}_results'
    save_pkl(yr_df, filename)

        
            