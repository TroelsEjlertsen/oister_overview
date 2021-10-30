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
from functions import read_pdfs,make_table, make_tables, sort_column
import glob, os


#%% IF df is not saved to csv file

if not os.path.isfile("data.csv"): 
    
    # %% READ PDF
    tables = make_tables()    
    
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
        
    #%%     
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

    # Save df to CSV
    df.to_csv("data.csv")

#%% IF df is saved to csv file
else:
    
    df = pd.read_csv("data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["call_time"] = pd.to_timedelta(df["call_time"])
    df = df.set_index("date")

#%% Analyse data
# group by monthly sum

# Data sum
df1 = df["Data[MB]"].groupby(pd.Grouper(freq="M")).sum()
# call time sum
df2 = df["call_time"].groupby(pd.Grouper(freq="M")).sum()
df2 = df2.rename("Call time[min.]")
df3 = df2.rename("Call time[hr]")
df4 = df1.rename("Data[GB]")
df4 = df4/1000

#convert to minutes
df2 = df2.astype('timedelta64[m]')
df3 = df3.astype('timedelta64[h]')

#avg. values
d = {"Avg. monthly Call time[h]":df3.mean(), "Avg. monthly data[GB]": df1.mean()/1000,
     "Max. call time[h]":df3.max(),
     "Max. Data use[GB]":df1.max()/1000}
df_avg = pd.DataFrame(data = d, index=[0])

if df3.mean() < 1:
    df_avg.iloc[0,0] = df2.mean()
    df_avg.iloc[0,2] = df2.max()
    df_avg = df_avg.rename(columns = {"Avg. monthly Call time[h]":"Avg. monthly Call time[min.]",
                                       "Max. call time[h]": "Max. call time[min.]"})

#%% Display using Streamlit

# G number of years
yr_range = [int(df.index.year.min()), int(df.index.year.max())]

st.title("Mobile data Usage for {}-{}".format(yr_range[0], yr_range[1]))


@st.cache#(persistent=True)
def load_df(df):
    return df

df_mean = load_df(df_avg)
df_data = load_df(df["Data[MB]"])
df_call = load_df(df["call_time"])
df11 = load_df(df1)
df22 = load_df(df2)
df33 = load_df(df3)
df44 = load_df(df4)

#%% Show stats in a table

st.header("Average and max. monthly usage")
st.table(df_mean)

#%% 
st.header("Overall data usage")
st.line_chart(df_data)

#%% Initialize session state
if "unit" not in st.session_state:
    st.session_state.unit = "MB"
if "data_df" not in st.session_state:
    st.session_state.data_df = df11    
if "item" not in st.session_state:
    st.session_state.item = "hr."
if "df" not in st.session_state:
    st.session_state.df = df33    
    

#%% Monthly data usage
st.header("Monthly Data usage")   
def handle_unit():
    if st.session_state.new_unit:
        st.session_state.unit = st.session_state.new_unit
        
        if st.session_state.unit == "[GB]":
            st.session_state.data_df = df44
        else:
            st.session_state.data_df = df11
            
            
unit_items = ["[MB]", "[GB]"]    
radio2 = st.radio("[MB]/[GB]", unit_items, on_change=handle_unit, key="new_unit")

st.bar_chart(st.session_state.data_df)


# st.header("Overall call time usage")
# st.line_chart(df_call)

#%% Monthly call time
st.header("Monthly Call time")


def handle_change():
    if st.session_state.new_item:
        st.session_state["item"] = st.session_state.new_item
        
        if st.session_state.item == "min.":
            st.session_state.df = df22
        else:
            st.session_state.df = df33
            
        
        

radio_items = ["hr.", "min."]
radio2 = st.radio("hr./min.", radio_items,
                 on_change=handle_change,
                 key = "new_item")


st.bar_chart(st.session_state.df)


                   



        

    
    
    



