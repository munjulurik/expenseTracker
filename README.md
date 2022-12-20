# expenseTracker
Parse bank statements and track your expenses by visualizing the transactions through a dashboard built using streamlit.

The intention of building this app was to learn using streamlit.

Use the following command to run the script: <code>streamlit run Home.py</code>

Project Files:

1. <b>statementParser.py</b> - Methods to parse the pdf file and extract the table containing transactions
2. <b>categorizeTransactions.py</b> - Methods to categorize each transaction such as Food, Travel, Utility etc. and label them as either Fixed or Variable. This is achieved through some manual labelling to start with using the entities.csv file. <br> <br> The csv file contains the keywords that can be used to tag/assign the category and labels. For any changes/additions, feel free to modify the csv file.  Within the script, the csv file is pushed to a sqlite database, so that any changes the user makes, stay in place for the next run.

3. <b>3_Visualize.py</b> - StreamLit dashboard is created through this script. The Dashboard allows the parsed dataframe to be visualized and make any edits i.e. to override any category or labels assinged automatically. All the charts and figures are automatically updated post any edits

## Screenshot:
<img width="1431" alt="Dashoboard_shot1" src="https://user-images.githubusercontent.com/23265421/199983795-bb5bf7cf-4bed-4059-a8c3-5269ff20374c.png">

<br><br>

<img width="1427" alt="Dashoboard_shot2" src="https://user-images.githubusercontent.com/23265421/199983557-7150a0af-e2bd-4176-9623-1b29039e7b86.png">



