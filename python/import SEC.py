# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import pandas as pd
from sec_edgar_downloader import Downloader
#tickers_data = pd.read_csv(".."\
#"...TriggeredEvents\\input files\\equity tickers.csv")
tickers_data = pd.read_csv(".."\
"\\input files\\equity tickers.csv")
tickers_data.head()
#del tickers_data

dl = Downloader("...TriggeredEvents\\downloaded\\SEC")
for i in range(len(tickers_data)):
    print("Begin Downloading "+tickers_data['ticker'][i])
    for filing_type in dl.supported_filings:
        try:
            dl.get(filing_type, tickers_data['ticker'][i], 10)
        except:
            print("An Error Occured in Downloading Process")
    print("Finished Downloading "+tickers_data['ticker'][i])

