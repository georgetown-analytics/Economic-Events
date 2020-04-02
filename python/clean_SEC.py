# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")


import pandas as pd
import re
import datetime as dt

#Create blank dataframe to fill in with SEC data
#Dataframe will have row for every downloaded SEC document
#"text_mention_decline'=how many times the document mentions the word "decline"
#'text mention growth'=how many times the text mentions growth
master_sec_df= pd.DataFrame(columns=['ticker', 'filing_type', 'path', \
'string_datetime', \
'text_mention_decline', \
'text_mention_growth' \
\
])

for root, dirs, files in os.walk("downloaded\\SEC", topdown=False):
    for name in files:
        print(name)
        print(os.path.join(root, name))
        temp_path=os.path.join(root, name)
        temp_ticker=temp_path.split('\\')[3]
        temp_type=temp_path.split('\\')[4]
        
        
        temp_text=open(os.path.join(root, name), "r").read(1000000)
        temp_text_obj=re.search(r'(<ACCEPTANCE-DATETIME>)(.*$)', temp_text, re.M|re.I)
        try:
            temp_text_dt=temp_text_obj.group(2)
        except:
            temp_text_dt=""
            print("No Datetime Found")

        temp_text_decline=temp_text.lower().count('decline')
        temp_text_growth=temp_text.lower().count('growth')
            
        master_sec_df =  master_sec_df.append({'ticker': temp_ticker, 'filing_type': temp_type, 'path': temp_path, \
        'string_datetime': temp_text_dt, \
        'text_mention_decline': temp_text_decline, \
        'text_mention_growth': temp_text_growth \
        \
        }, ignore_index=True)
        print("Master SEC Dataset Created")

pd.set_option('mode.chained_assignment', None)
#variables 6 and 7
master_sec_df['datetime']=0 
master_sec_df['date']=0
for i in range(len(master_sec_df)):
    try:
        year=int(master_sec_df['string_datetime'][i][0:4])
        month=int(master_sec_df['string_datetime'][i][4:6])
        day=int(master_sec_df['string_datetime'][i][6:8])
        hr=int(master_sec_df['string_datetime'][i][8:10])
        minu=int(master_sec_df['string_datetime'][i][10:12])
        sec=int(master_sec_df['string_datetime'][i][12:14])
        master_sec_df.iloc[i, 6]=dt.datetime(year, month, day, hr, minu, sec)
        master_sec_df.iloc[i, 7]=dt.date(year, month, day)
        #print("line {}".format(i))
    except:
        master_sec_df.iloc[i-1, 6]=0
        master_sec_df.iloc[i-1, 7]=0
        print("No Extractable Date Value")

master_sec_df.to_csv("constructed\\sec_data_tabulated.csv", sep=',')

