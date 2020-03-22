# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")
print(os.getcwd())

import pandas as pd
import re

master_sec_df= pd.DataFrame(columns=['ticker', 'filing_type', 'path', 'datettime'])
import os
for root, dirs, files in os.walk("downloaded\\SEC", topdown=False):
    for name in files:
        print(name)
        print(os.path.join(root, name))
        temp_path=os.path.join(root, name)
        temp_ticker=temp_path.split('\\')[3]
        temp_type=temp_path.split('\\')[4]
        
        temp_text=open(os.path.join(root, name), "r").read(500)
        temp_text_obj=re.search(r'(<ACCEPTANCE-DATETIME>)(.*$)', temp_text, re.M|re.I)
        try:
            temp_text_dt=temp_text_obj.group(2)
        except:
            temp_text_dt=""
            print("No Datetime Found")
            
        master_sec_df =  master_sec_df.append({'ticker': temp_ticker, 'filing_type': temp_type, 'path': temp_path, 'datettime': temp_text_dt}, ignore_index=True)

master_sec_df.to_csv("constructed\\sec_data_tabulated.csv", sep=',')
