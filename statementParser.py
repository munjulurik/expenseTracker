from pdfminer.high_level import extract_pages
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


class BankStatement():

    def __init__(self, file):
        self.file = file

    def read_statement(self):
        """
        Function to parse each line and return a dataframe containing the coords of the line and the text within.
        """
        self.raw_df = pd.DataFrame()

        try:
            pages = extract_pages(self.file)

            for page_layout in pages:
                data = []
                for ind, element in enumerate(page_layout):
                    if (element.__class__.__name__ == "LTTextBoxHorizontal") and (ind>=26):
                        for each_element in element: data.append((each_element.x0, each_element.y0, each_element.x1, each_element.y1, each_element.get_text()))

                tmp = pd.DataFrame(data, columns=['x0', 'y0', 'x1', 'y1', 'text'])
                tmp = tmp.sort_values(by=['y0', 'x0'], ascending = [False, True])[3:]
                self.raw_df = pd.concat([self.raw_df, tmp])
        
        except:
            raise('Could not work with the pdf file. Please recheck the file format and path')


    def get_indices_of_column_starts(self):
        '''
        Helper function to group multi line records into one.
        The start coord of the line is used for grouping.
        '''
        # find the start of the first column
        start = self.raw_df['x0'].min()

        # reset the index of df
        self.raw_df = self.raw_df.reset_index(drop=True)

        # get indices of column starts
        indices = self.raw_df[self.raw_df['x0']==start].index.values.tolist()

        return indices

    def partition_df(self):
        '''
        Partitions the dataframe into smaller chunks, where each chunk constitutes 
        to a single record which is present as multiple lines in the document
        '''
        self.indices = self.get_indices_of_column_starts()

        for ind in range(1, len(self.indices)):
            yield self.raw_df.iloc[self.indices[ind-1]: self.indices[ind]]

    def structure_the_data(self):
        '''
        Function to merge/join the multi lines into one.
        Checks the overlap between start and end columns to combine rows
        '''

        data = []
        self.df = pd.DataFrame()
        for part in self.partition_df():
            part = part.reset_index(drop=True)
            part.loc[0, 'text'] = ' '.join(part['text'][(part['x0']>=part['x0'].iloc[0]) & (part['x0']<=part['x1'].iloc[0])].values.tolist()).replace('\n', '')
            part.loc[1, 'text'] = ' '.join(part['text'][(part['x0']>=part['x0'].iloc[1]) & (part['x0']<=part['x1'].iloc[1])].values.tolist()).replace('\n', '')
            cols = part['text'][:4].values.tolist()
            data.append(tuple(map(lambda x: x.replace('\n', ''),cols[0].split(" ", 1) + cols[1:])))
        self.df = pd.DataFrame(data, columns=['Date', 'Description', 'RefNo', 'Transaction', 'Balance'])

    def correct_df_columns(self, clean_type):
        '''
        Helper function that tries to identify any issues in parsing by checking for 
        empty column values and rectifies them
        '''

        if clean_type == 'blanks':
            tmp = self.df[self.df['Balance'].isna()==True]
        elif clean_type == 'refno':
            tmp = self.df[~self.df['Balance'].str.contains(r'(\(Dr\)|\(Cr\))', regex=True)]

        to_be_desc = tmp['Balance']
        to_be_trans = tmp['RefNo']
        to_be_bal = tmp['Transaction']

        tmp['Balance'] = to_be_bal
        tmp['Transaction'] = to_be_trans
        tmp['RefNo'] = to_be_desc

        self.df.loc[tmp.index.to_list(), self.df.columns.to_list()] = tmp


    def clean_df(self):
        '''
        Function to clean the records/rows in the dataframe
        '''
        # cleaning rows/records which have blank/None value in Balance column
        self.correct_df_columns('blanks')

        # cleaning rows/records which have ref no. values in the Balance column
        self.correct_df_columns('refno')

        # assign + and - for debit/credit transactions
        self.df['Transaction'] = self.df['Transaction'].apply(lambda val: '-' + val.replace('(Dr)', '') if '(Dr)' in val else  val.replace('(Cr)', ''))
        self.df['Balance'] = self.df['Balance'].apply(lambda val: '-' + val.replace('(Dr)', '') if '(Dr)' in val else val.replace('(Cr)', ''))

    
    def parse_statement_as_df(self):
        self.read_statement()
        self.structure_the_data()
        self.clean_df()
        return self.df
