import streamlit as st
import pandas as pd
from statementParser import BankStatement
from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder
import re
from streamlit_extras.switch_page_button import switch_page
import os
import sqlite3
from fuzzywuzzy import process, fuzz


uploaded_file = st.file_uploader("Upload Bank Statement", accept_multiple_files=False)


def connect_and_fetch_db_data(db='expense_tracker.db'):
    conn  = sqlite3.connect('expense_tracker.db')
    cats = pd.read_sql('select * from categories', conn)
    return cats

def find_match(desc, choices):
    try:
        desc = clean_text(desc)
        out = process.extractOne(desc, choices, scorer=fuzz.token_set_ratio, score_cutoff=45)[0]
    except:
        out = ''
    return out

def drop_reversal_transactions(df):
    '''
    Function that identifies any transactions that have been reversed and drops those records from the df
    '''
    
    df.fillna('', inplace=True)

    # tmp dataframe containing potential transactions that have been refunded
    tmp = df[(df['Description'].str.contains(r'REV(\:|\-)|Cradj|refund', regex=True, flags=re.IGNORECASE)) & (df['Description'].str.contains('incorrect', flags=re.IGNORECASE)==False)] 

    # trying to fetch the transaction id from the description column
    transactions_to_drop = ['|'.join(re.findall(r'\d{10,}', desc)) for desc in tmp['Description'].unique().tolist()]

    # basis the transaction ids found above, find the original debited transactions
    indices_found = [df.index[df['RefNo'].str.contains(t, regex=True)].values.tolist() for t in transactions_to_drop]

    # keeping a track of how many of the potential refund transactions identified actually have a debited transaction
    indices_to_drop = []
    for ind, trans in zip(indices_found, tmp.index.tolist()):
        if len(ind) == 1:
            indices_to_drop.append(ind[0])
            indices_to_drop.append(trans)
    
    # dropping the records which have both debit and credit transaction indicating refund
    df = df[~df.index.isin(indices_to_drop)]

    return df
    

def fetch_category(choice, cats_dict):
    if choice != '':
        try:
            return cats_dict[choice]
        except:
            return ''
    return ''

def apply_categories(df, descs):

    df['descs'] = list(map(clean_text, df['Description'].values.tolist()))

    if os.path.isfile('expense_tracker.db'):
        print("path found")
        # use the db to apply categories
        cats_df = connect_and_fetch_db_data()
        all_cats = cats_df['Name'].unique().tolist()
        matches = {desc: find_match(desc, all_cats) for desc in descs}
        categorized_matches = {match: fetch_category(match, dict(cats_df.values)) for match in matches}
        df['Category'] = df['descs'].map(categorized_matches)

    df.drop(columns=['descs'], inplace=True)

    df = drop_reversal_transactions(df)

    return df

def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'upi|\/|\d{6,}', " ", text)
    return text.strip()

@st.cache(allow_output_mutation=True)
def parse_df():
    bs = BankStatement(uploaded_file)
    df = bs.parse_statement_as_df()

    # filter dataframe with dates mentioned
    start_date = st.session_state['start_date']
    end_date = st.session_state['end_date']

    # formatting the date column
    df['Date'] = pd.to_datetime(df['Date'], format=("%d-%m-%Y")).dt.strftime("%Y/%m/%d")

    df =  df[(df['Date'] >= start_date.strftime("%Y/%m/%d")) & (df['Date'] <= end_date.strftime("%Y/%m/%d"))]

    df = df[df['Transaction'].str.startswith('-')]
    # converting the transaction column to numeric
    df['Transaction'] = pd.to_numeric(df['Transaction'].str.replace(',', ''), errors='coerce')
    # dropping any na rows
    df = df[df['Transaction'].isna()==False]
    # making sure that all the transactions have +ve sign
    df['Transaction'] = df['Transaction'].apply(lambda x: x*-1 if x<0 else x)
    return df

if uploaded_file:
    
    df = parse_df()

    

    descs = df['Description'].unique().tolist()

    descs = sorted(list(set(map(clean_text, descs))))

    full_df = apply_categories(df, descs)

    cats_df = full_df[full_df['Category']== '']


    if len(cats_df) > 0:
        st.text("Couldn't assign a category for the following. \nPlease apply the categories to the following transactions")
        gb = GridOptionsBuilder()
        gb.configure_column(field="Date", editable=False)
        gb.configure_column(field="Description", editable=False)
        gb.configure_column(field="Transaction", editable=False)
        gb.configure_column(field="Category", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": sorted(st.session_state['categories'] )})
        grid_return = AgGrid(cats_df, gridOptions=gb.build())

        # capture the output from grid_return
        full_df = pd.concat([full_df, grid_return.data])

        # clean full_df
        full_df = full_df[full_df['Category'] != '']

        if "categorized_df" not in st.session_state:
            st.session_state['categorized_df'] = full_df

if st.button("Next"):
    switch_page("Visualize")
