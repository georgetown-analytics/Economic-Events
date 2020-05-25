# -*- coding: utf-8 -*-
"""
Created on Thu May 21 13:16:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")
from past.builtins import execfile
def include(filename):
    if os.path.exists(filename): 
        execfile(filename)

execfile("python\\capstone\\1. Capstone import financial_own.py")
execfile("python\\capstone\\2. Capstone SEC Import and Clean.py")
execfile("python\\capstone\\3. Capstone Scrape Google.py")
execfile("python\\capstone\\4. Capstone Merge and Analyze.py")

