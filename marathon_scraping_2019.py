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
    return parse(time_string)-parse('00:00:00')

def get_fields(row):
    
    name_country = split_name(row.find_all('h4', class_='list-field type-fullname')[0].text)
    try:
        data_row = [int(row.find_all('div', class_='list-field type-place place-secondary hidden-xs numeric')[0].text), #overall place
                    int(row.find_all('div', class_='list-field type-place place-primary numeric')[0].text), #gender place
                    name_country[0], #name
                    name_country[1], #country
                    remove_prefix(row.find_all('div', class_='list-field type-field')[0].text, 'BIB'), #bib number
                    remove_prefix(row.find_all('div', class_='list-field type-age_class')[0].text, 'Division')] # division
        try:
            half_time = parse_time(remove_prefix(row.find_all('div', class_='split list-field type-time')[0].text, 'HALF')), # half time
        except ValueError:
            half_time = None
            
        try:
            fin_time = parse_time(remove_prefix(row.find_all('div', class_='list-field type-time')[0].text, 'Finish')) # finish time
        except ValueError:
            fin_time = None
            
        data_row.extend([half_time, fin_time])
                
        return data_row
    except IndexError:
        return None
    
data = []
tot_pgs = 2221
start_pg = 301

num_dnf = 0
genders = ['M','F']
for gender in genders:
    i = 1
    pg_found = True
    while pg_found:
        
        print(f'Page: {i}')
        result_pg = f'https://results.chicagomarathon.com/2019/?page={i}&event=MAR&lang=EN_CAP&num_results=1000&pid=list&search%5Bsex%5D={gender}&search%5Bage_class%5D=%25'
        page = requests.get(result_pg)
        soup = BeautifulSoup(page.text, 'html.parser')
    
        rows = soup.find_all('li', class_='list-active list-group-item row')
        rows.extend(soup.find_all('li', class_='list-group-item row'))
        if len(rows) > 0:
            for row in rows:
                data_row = get_fields(row)
                if data_row:
                    data.append(data_row)
                else:
                    num_dnf += 1
        else:
            pg_found = False
            
            
    gender_df = pd.DataFrame(data, columns=['Place', 'GenderPlace', 'Name', 'Country', 'BibNumber', 'Division', 'HalfTime', 'Time'])
    df.concat()            
            

        
            