import streamlit as st
from statementParser import BankStatement
from categorizeTransactions import CategorizeTransactions
import pandas as pd
import plotly.express as px  
from st_aggrid import AgGrid
from datetime import datetime


@st.cache
def generate_statement_as_df(uploaded_file):
    '''
    Function to parse, clean and categorise the transactions
    '''
    # parsing the statement
    bs = BankStatement(uploaded_file)
    df = bs.parse_statement_as_df()

    # categorizing the transactions
    ct = CategorizeTransactions(df, 'entities.csv')
    ct.drop_reversal_transactions()
    ct.fetch_categories()
    ct.assign_categories()

    # additional clean up on the dataframe
    df = ct.transactions_df
    # formatting the date column
    df['Date'] = pd.to_datetime(df['Date'], format=("%d-%m-%Y")).dt.strftime("%Y/%m/%d")
    df = df[df['Transaction'].str.startswith('-')]
    # converting the transaction column to numeric
    df['Transaction'] = pd.to_numeric(df['Transaction'].str.replace(',', ''), errors='coerce')
    # dropping any na rows
    df = df[df['Transaction'].isna()==False]
    # making sure that all the transactions have +ve sign
    df['Transaction'] = df['Transaction'].apply(lambda x: x*-1 if x<0 else x)
    # keeping only the required columns
    df = df[['Date', 'Description', 'Entity/Person', 'Transaction', 'Category', 'Type']]

    return df

def compute_metrics(df):
    '''
    Function that computes key metrics in the dashboard
    '''
    avg_daily_exp = df['Transaction'].mean()
    num_trans = len(df)
    max_trans = df['Transaction'].max()
    day_with_most_trans = df['Date'].value_counts().index[0]
    total_exp = df['Transaction'].sum()

    return avg_daily_exp, num_trans, max_trans, day_with_most_trans, total_exp

st.set_page_config(
    page_title="Expense Tracker",
    layout="wide",
)

# creating sidebar to pass in dates and upload statement
with st.sidebar:
    st.title("Expense Tracker")
    start_date = st.date_input('Start Date', datetime.now().date().replace(month=1, day=1))
    end_date = st.date_input('End Date')
    # TODO: Currently not in use, but incorporate when more banks are added
    bank_option = st.selectbox("Select Bank", ("Kotak Bank",))
    
    uploaded_file = st.file_uploader("Upload Bank Statement", accept_multiple_files=False, )

if uploaded_file:
    # once the file is upload, parser is called
    df = generate_statement_as_df(uploaded_file)
    # filtering the df with user specified dates
    df =  df[(df['Date'] >= start_date.strftime("%Y/%m/%d")) & (df['Date'] <= end_date.strftime("%Y/%m/%d"))]

    # Adding a dynamic header to the dashboard, indicating from and to dates
    st.header("Expenses between {} and {}".format(start_date.strftime("%d %b"), end_date.strftime("%d %b, %Y")))

    # expander widget to visualize the parsed data
    with st.expander("See the statement & make any edits if required: "):
        # AgGrid lets you edit the dataframe if required
        # idea is to use it overwrite auto assigned categories and expense type values
        grid_return = AgGrid(df, editable=True, key="df_values")
        
    # button to track if any changes have been made to the parsed df
    update_status = st.button("I have made corrections. Update the charts!")

    if update_status:
        # if button is updated, need to update the graphs and charts basis the new df
        # fetching the updated df here
        new_df = grid_return['data']
        # making the necessary date conversions and fetching the key metrics
        new_df['Date'] = pd.to_datetime(new_df['Date'], format=("%Y-%m-%d")).dt.strftime("%Y/%m/%d")
        df = new_df
        avg_daily_exp, num_trans, max_trans, day_with_most_trans, total_exp = compute_metrics(df)

        # TODO: In the updated df, track if any categories have been changed or updated and push them to db


    else:
        # if no changes made, we can move on..
        avg_daily_exp, num_trans, max_trans, day_with_most_trans, total_exp = compute_metrics(df)
    
    # Dashboard visualizations start here
    placeholder2 = st.empty()

    with placeholder2.container():
        # key metrics
        metric1, metric2, metric3, metric4, metric5 = st.columns(5)

        metric1.metric(label = 'Avg. Transaction Amount',
                        value = "{:.2f}".format(avg_daily_exp))

        metric2.metric(label = 'Total No. of Transactions',
                        value = num_trans)

        metric3.metric(label='Highest Expense',
                        value="{:.2f}".format(max_trans))

        metric4.metric(label="Day with most transactions",
                        value=day_with_most_trans)

        metric5.metric(label="Total Expense",
                        value="{:.2f}".format(total_exp))

    placeholder3 = st.empty()
    with placeholder3.container():
        # pie charts
        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            fig = px.pie(data_frame=df, values="Transaction", names="Category", title="Category Wise Expenses", color_discrete_sequence=px.colors.qualitative.Dark2)
            fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
            st.plotly_chart(fig)
        
        with fig_col2:
            fig2= px.pie(data_frame=df, values="Transaction", names="Type", title="Fixed vs Variable Expense", color_discrete_sequence=px.colors.qualitative.Dark2)
            fig2.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
            st.plotly_chart(fig2)

    # wide charts - bar and box plots
    with st.container():
        fig= px.bar(data_frame=df, y="Transaction", x="Date", color="Category", title="Daily Expenses with Transaction Category", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = False)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        fig= px.bar(data_frame=df, y="Transaction", x="Date", color="Type", title="Daily Expenses with Transaction Type", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = False)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        df['Day'] = pd.to_datetime(df['Date'], format="%Y/%m/%d").dt.day_name()
        fig= px.box(data_frame=df, y="Transaction", x="Day", color="Type", title="Expenses on each day of the week", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = True)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        fig= px.bar(data_frame=df, y="Transaction", x="Entity/Person", color="Type", title="Expenses with each Entity/Person", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = False)
        st.plotly_chart(fig, use_container_width=True)


