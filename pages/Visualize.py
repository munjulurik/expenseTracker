import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import plotly.express as px  
import pandas as pd

st.session_state['categorized_df']['Type'] = st.session_state['categorized_df']['Category'].apply(lambda x: 'Fixed' if x in st.session_state['fixed_exp'] else 'Variable')

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

avg_daily_exp, num_trans, max_trans, day_with_most_trans, total_exp = compute_metrics(st.session_state['categorized_df'])

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
        fig = px.pie(data_frame=st.session_state['categorized_df'], values="Transaction", names="Category", title="Category Wise Expenses", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        st.plotly_chart(fig)

    with fig_col2:
        fig2= px.pie(data_frame=st.session_state['categorized_df'], values="Transaction", names="Type", title="Fixed vs Variable Expense", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig2.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        st.plotly_chart(fig2)

    with st.container():
        fig= px.bar(data_frame=st.session_state['categorized_df'], y="Transaction", x="Date", color="Category", title="Daily Expenses with Transaction Category", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = False)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        fig= px.bar(data_frame=st.session_state['categorized_df'], y="Transaction", x="Date", color="Type", title="Daily Expenses with Transaction Type", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = False)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.session_state['categorized_df']['Day'] = pd.to_datetime(st.session_state['categorized_df']['Date'], format="%Y/%m/%d").dt.day_name()
        fig= px.box(data_frame=st.session_state['categorized_df'], y="Transaction", x="Day", color="Type", title="Expenses on each day of the week", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = True)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        tmp = st.session_state['categorized_df']
        tmp['Month'] = pd.to_datetime(tmp['Date'], format="%Y/%m/%d").dt.month_name()
        fig= px.bar(tmp.groupby(['Month', 'Category'])['Transaction'].sum().reset_index(), y="Transaction", x="Month", color="Category", title="Total expenses each month", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.update_traces(showlegend = True)
        st.plotly_chart(fig, use_container_width=True)


if st.button("Start Over"):
    st.session_state.clear()
    switch_page("Home")
