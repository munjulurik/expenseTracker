from statementParser import BankStatement
import pandas as pd
import sqlite3, os, re
from fuzzywuzzy import process, fuzz

class CategorizeTransactions():
    '''
    Each transaction in the statement is classified as what category the spends accounts to and whether 
    its a fixed or variable cost.

    * The classification information is stored as a sqlite table, to make sure the new/updated classes are also stored
    '''
    def __init__(self, transactions_df, cat_file_path):
        self.db = 'expense-tracker.db'
        self.cat_table = 'categories'
        self.file_to_push = cat_file_path
        self.transactions_df = transactions_df

    def create_db_if_not_present(self):
        '''
        sqlite db creation if it doesn't exist
        '''
        if not os.path.isfile(self.db):
            sqlite3.connect(self.db)
            return True
        return False

    def update_db(self, df_to_push):
        '''
        the sqlite db is updated with the data originating from cat_file_path
        containing category and transaction type information.
        '''
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS categories (name text, category text type text)')
        conn.commit()
        df_to_push.to_sql(self.cat_table, conn, if_exists='replace', index = False)
        c.close()
        conn.close()

    def fetch_categories(self):
        '''
        Function to execute sql query to fetch all the categories from the db
        '''
        creation_flag = self.create_db_if_not_present()
        if creation_flag:
            # need to update the database
            try:
                df_to_push = pd.read_csv(self.file_to_push)
            except:
                raise ('The categories file needs to be in a specific format. Please check the documentation')
            self.update_db(df_to_push)

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        self.cats = pd.read_sql("select * from {}".format(self.cat_table), conn)
        c.close()
        conn.close()

    def drop_reversal_transactions(self):
        '''
        Function that identifies any transactions that have been reversed and drops those records from the df
        '''
        
        self.transactions_df.fillna('', inplace=True)

        # tmp dataframe containing potential transactions that have been refunded
        tmp = self.transactions_df[(self.transactions_df['Description'].str.contains(r'REV(\:|\-)|Cradj|refund', regex=True, flags=re.IGNORECASE)) & (self.transactions_df['Description'].str.contains('incorrect', flags=re.IGNORECASE)==False)] 

        # trying to fetch the transaction id from the description column
        transactions_to_drop = ['|'.join(re.findall(r'\d{10,}', desc)) for desc in tmp['Description'].unique().tolist()]

        # basis the transaction ids found above, find the original debited transactions
        indices_found = [self.transactions_df.index[self.transactions_df['RefNo'].str.contains(t, regex=True)].values.tolist() for t in transactions_to_drop]

        # keeping a track of how many of the potential refund transactions identified actually have a debited transaction
        indices_to_drop = []
        for ind, trans in zip(indices_found, tmp.index.tolist()):
            if len(ind) == 1:
                indices_to_drop.append(ind[0])
                indices_to_drop.append(trans)
        
        # dropping the records which have both debit and credit transaction indicating refund
        self.transactions_df = self.transactions_df[~self.transactions_df.index.isin(indices_to_drop)]

    def assign_categories(self):
        '''
        Function to assign category and expense type to each transaction.
        Uses fuzzywuzzy string matching to assign categories
        '''
        choices = self.cats['Name'][self.cats['Type']!='Reversal'].unique().tolist()
        
        matches = dict() 
        
        for desc in self.transactions_df['Description'].values.tolist():
            try:
                if desc.lower().startswith('upi'):
                    cleaned_desc = desc.split('/')[1]
                else:
                    cleaned_desc = desc
                out = process.extractOne(cleaned_desc, choices, scorer=fuzz.token_set_ratio, score_cutoff=40)[0]
                matches[desc] = [out, self.cats['Category'][self.cats['Name']==out].values[0], self.cats['Type'][self.cats['Name']==out].values[0]]
            except:
                matches[desc] = ['', '']

        self.transactions_df = pd.concat([self.transactions_df, self.transactions_df['Description'].map(matches).apply(pd.Series).rename(columns={0: 'Entity/Person', 1: 'Category', 2: 'Type'})], axis=1)