import streamlit as st
from statementParser import BankStatement
import pandas as pd
import plotly.express as px  
from st_aggrid import AgGrid
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="Expense Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Expense Tracker")
start_date = st.date_input('Start Date', datetime.now().date().replace(month=1, day=1))
end_date = st.date_input('End Date')

if 'start_date' not in st.session_state:
    st.session_state['start_date'] = start_date

if 'end_date' not in st.session_state:
    st.session_state['end_date'] = end_date

bank_option = st.selectbox("Select Bank", ("Kotak Bank",))

if st.button('Next'):
    switch_page("Create_Categories")