# coding: utf-8

# # Download articles from The Guardian UK using API
# 
# Author: Jorge de Leon 
# 
# This script allows you to download news articles that match your parameters from the Guardian newspaper, https://www.theguardian.com/us.
# 
# The files are downloaded into JSON files. 

# https://content.guardianapis.com/search?from-date=2020-04-01&to-date=2020-04-07&show-fields=all&order-by=newest&page-size=200&q=S%26P500&api-key=cc861453-f313-4412-9805-0290e2885061

# ### Import packages

import os
import json
import requests
import pandas as pd 

from os import makedirs
from os.path import join, exists
from datetime import date, timedelta

# ### Create directory for files

ARTICLES_DIR = join('theguardian', 'articles')
makedirs(ARTICLES_DIR, exist_ok=True)

# ### Select parameters and provide API key

# Sample URL
#
# http://content.guardianapis.com/search?from-date=2016-01-02&
# to-date=2016-01-02&order-by=newest&show-fields=all&page-size=200
# &api-key=your-api-key-goes-here

START_DATE_GLOBAL = date(2020, 4, 1)
END_DATE_GLOBAL = date(2020, 4, 12)

MY_API_KEY = open("..\\input files\\creds_guardian.txt").read().strip()
API_ENDPOINT = 'http://content.guardianapis.com/search'
my_params = {
    'from-date': "",
    'to-date': "",
    'show-fields': 'all',
    'order-by': "newest",
    'page-size': 200,
    'q': "%22financial%20markets%22",
    'api-key': MY_API_KEY
}

# ### Request files from the Guardian
# The requests are saved to a file per day. 

# day iteration from here:
# http://stackoverflow.com/questions/7274267/print-all-day-dates-between-two-dates
start_date = START_DATE_GLOBAL
end_date = END_DATE_GLOBAL
dayrange = range((end_date - start_date).days + 1)
for daycount in dayrange:
    dt = start_date + timedelta(days=daycount)
    datestr = dt.strftime('%Y-%m-%d')
    fname = join(ARTICLES_DIR, datestr + '.json')
    if not exists(fname):
        # then let's download it
        print("Downloading", datestr)
        all_results = []
        my_params['from-date'] = datestr
        my_params['to-date'] = datestr
        current_page = 1
        total_pages = 1
        while current_page <= total_pages:
            print("...page", current_page)
            my_params['page'] = current_page
            resp = requests.get(API_ENDPOINT, my_params)
            data = resp.json()
            all_results.extend(data['response']['results'])
            # if there is more than one page
            current_page += 1
            total_pages = data['response']['pages']

        with open(fname, 'w') as f:
            print("Writing to", fname)

            # re-serialize it for pretty indentation
            f.write(json.dumps(all_results, indent=2))

# ### Open JSON file 

with open('theguardian/articles/2020-04-01.json') as file:
  example = json.load(file)

# Output: 
print(example)

# ### Code to convert files into CSV files

test_directory = 'theguardian/articles/'

for file_name in [file for file in os.listdir(test_directory) if file.endswith('.json')]:
  with open(test_directory + file_name) as json_file:
    data = pd.read_json(json_file)
    data.to_csv(test_directory + file_name + '.csv', index =  None)
