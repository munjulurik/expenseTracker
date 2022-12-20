import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page


st.title("Add categories here")

st.text("Create categories that you would like to assign to each transaction.")

st.text("Following categories have already been created. Add more if needed")

# categories = [('Miscellaneous', 'Variable'), ('Groceries', 'Fixed'), ('Insurance', 'Fixed'), ('Health', 'Variable'), ('Phone', 'Fixed'), ('Donation', 'Variable'), ('Shopping', 'Variable'), ('Medicine', 'Variable'), ('Entertainment', 'Variable'), ('Personal', 'Variable'), ('Maid', 'Fixed'), ('Food', 'Variable'), ('Travel', 'Variable'), ('Education', 'Variable'), ('Credit Card', 'Fixed'), ('Couriers', 'Variable'), ('Utilities', 'Fixed'), ('Investment', 'Fixed'), ('Fuel', 'Fixed'), ('Internet', 'Fixed'), ('Repair', 'Variable'), ('Clothing', 'Variable'), ('Photography', 'Variable'), ('Beauty', 'Variable'), ('Helath', 'Variable'), ('Charges', 'Variable'), ('Reversal', 'Reversal'), ('Tax', 'Variable'), ('Salary', 'Variable'), ('Rent', 'Fixed'), ('Dividends', 'Variable'), ('Interest', 'Variable')]

categories = ['Miscellaneous', 'Groceries', 'Insurance', 'Health', 'Phone', 'Donation', 'Shopping', 
                'Medicine', 'Entertainment', 'Personal', 'Maid', 'Food & Drinks', 'Travel', 'Education', 'Credit Card', 
                    'Couriers', 'Utilities', 'Investment', 'Fuel', 'Internet', 'Repair', 'Clothing', 'Photography', 
                        'Beauty', 'Charges', 'Rent']

cat_table = st.table(pd.DataFrame(categories, columns=['Categories']))

col1, _ = st.columns(2)
with col1:
    text_input = st.text_input("Category")

if "categories" not in st.session_state:
    st.session_state['categories'] = categories

placeholder = st.empty()
with placeholder.container():
    col1, _ =  st.columns(2)
    with col1:
        add_button = st.button('Add')

    if add_button & (text_input != ''):
        if text_input not in st.session_state['categories']:
            st.session_state['categories'] += [text_input]
            cat_table.add_rows([text_input])
        else:
            st.error("{} already exists in the list".format(text_input))


st.header("Specify the categories as either Fixed or Variable type")

c1, c2 = st.columns(2)
with c1:
    fixed_exp = st.multiselect("Fixed Expenses", st.session_state['categories'], key='fc')
with c2:
    var_exp = st.multiselect("Variable Expenses", st.session_state['categories'], key='vc')

done_button = st.button('Done')
if done_button:
    condition_two_fields_are_not_empy = (len(fixed_exp) == 0) and (len(var_exp)==0)
    condition_no_common_elements = len(set(fixed_exp).intersection(set(var_exp))) > 0
    condition_if_all_categories_are_selected = (len(fixed_exp + var_exp)) != (len(st.session_state['categories']))

    if condition_no_common_elements or condition_no_common_elements or condition_if_all_categories_are_selected:
        st.error("Fixed and Variable expenses cannot be empty and cannot have common values between them")

    else:

        # saving fixed_exp and var_exp in session 
        if 'fixed_exp' not in st.session_state:
            st.session_state['fixed_exp'] = fixed_exp
        
        if 'var_exp' not in st.session_state:
            st.session_state['var_exp'] = var_exp

        switch_page('Apply_Categories')
