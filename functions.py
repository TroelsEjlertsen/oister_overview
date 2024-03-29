# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 15:14:31 2021

@author: T470 bruger
"""

import pandas as pd
import tabula
import camelot
import numpy as np
import glob, os
from pikepdf import Pdf
#%% functions

def read_pdfs():
   # Change directory to data folder
   os.chdir("data/")
   
   # read PDF names
   pdfs = [file for file in glob.glob("*.pdf")]
   
   # repair corrupted PDF
   for name in pdfs:
       with Pdf.open(name, allow_overwriting_input=True) as pdf:
           pdf.save(name)
  
   return pdfs 
      


def make_table(pdf):
    
    table = camelot.read_pdf(pdf, flavor='stream',
                          pages='all',
                          strip_text='Data',
                          row_tol=10,
                          #columns=['100'],
                           split_text = True)
    return table
    
def make_tables():
    pdfs = read_pdfs()
    
    tables = {"{}".format(pdf): make_table(pdf) for pdf in pdfs}
    
    #return to main directory
    os.chdir("../")
    
    return tables
    
    
def sort_column(df):
    
    df1 = df[df.iloc[:,2].str.contains("KB")]
    df2 = df[df.iloc[:,2].str.contains("MB")]

    df4 = df1.append(df2)
      
    
    if df[4].str.contains("Vrighed\nE").any() or df[4].str.contains("Vrighed").any():
        df3 = df[[0,1,4]]
        df3 = df3.rename(columns = {4:"call_time"})
        
        if df[4].str.contains("Vrighed\nE").any():
            df3["call_time"] = df3["call_time"].str.strip("Vrighed\nE")
        else:
            df3["call_time"] = df3["call_time"].str.strip("Vrighed")
            
        df3["call_time"] = pd.to_timedelta(df3["call_time"], errors = 'ignore')
        df3["call_time"] = df3["call_time"].fillna(pd.Timedelta("0 days 00:00:00"))
        
        df4 = pd.concat([df4,df3],axis=0)
        
    else:
        df3 = 0
      
    #keep index in ascending order
    df4 = df4.sort_index()
    
    df4.iloc[:,2] = df4.iloc[:,2].str.replace(",",".")
    
    data = df4.iloc[:,2].str.split()
    data = data.fillna(0)
    
    out = []
    #Convert to MB
    for dat in data:
        if dat != 0:
           
            if dat[1] == "KB":
                out.append(float(dat[0])/1000)
            
            else :
                out.append(float(dat[0]))
        else:
            out.append(0)
        
    df4["Data[MB]"] = out         
    
    return df4