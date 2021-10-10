# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 13:18:43 2021

@author: T470 bruger
"""

import pandas as pd
import tabula
import camelot
import numpy as np
import os
import streamlit as st
from functions import load_data
from functions import sort_column


# %% READ PDF

new_name = ["2021_jan","2021_feb", "2021_mar","2021_apr","2021_may","2021_jun","2021_jul","2021_aug","2021_sep"]

pdf_name = ["data/2021-0{}.pdf".format(m+1) for m in range(0,10)]
pdf_name[-1] = "data/2021-10.pdf"

tables = {"{}".format(new_name[i]): load_data(pdf_name[i]) for i in range(0,len(new_name))}


#%% extract tables

data = []

for tab in tables:
    #print(tables[tab][0].df)
    for i in range(0,len(tables[tab])):
        #print(tab[i])
        data.append(tables[tab][i].df) 

#%% Sort dataframes
df = pd.DataFrame()

for dat in data:
    #print(dat)
    df = df.append(sort_column(dat))
    
# Reset index
df = df.reset_index(drop=True) 

#Make datetime
df["date"] = pd.to_datetime(df[0]+ " " + df[1], errors = 'coerce', dayfirst = True)

#replace NAT with zeros
df["call_time"] = df["call_time"].fillna(pd.Timedelta("0 days 00:00:00"))

#drop  columns
# df = df.drop(columns = [0,1,3,6,5,7,8])
df = df[["date","Data[MB]","call_time"]]
# set date as index
df = df.set_index("date")



#%% Analyse data
# group by monthly sum

# Data sum
df1 = df["Data[MB]"].groupby(pd.Grouper(freq="M")).sum()
# call time sum
df2 = df["call_time"].groupby(pd.Grouper(freq="M")).sum()
df2 = df2.rename("Call time[min.]")
#convert to minutes
df2 = df2.astype('timedelta64[m]')

#%% Display using Streamlit

yr_range = [int(df.index.year.min()), int(df.index.year.max())]
st.title("Mobile data Usage for {}-{}".format(yr_range[0], yr_range[1]))

st.header("Monthly Data usage")
st.bar_chart(df1)

st.header("Monthly Call time")
st.bar_chart(df2)

st.header("Overall Data Usage")
st.line_chart(df[["Data[MB]"]])

# st.header("Overall Call Usage")
# st.line_chart(df[["call_time"]])


@st.cache
def disp_data(df):
    return df

# show raw data
if st.checkbox("See raw data"):   
    
    'data', disp_data(df)   
    
    
    



                   



        

    
    
    



