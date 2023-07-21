import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

#* Mapped_IT = Alternate Titles with Alternate Industry
#* Unmatched_For_Fuzz = 

def JobTitle_SQLStoredProcedure(SQLConnection, SQLCursor, clientID, industry):
    #* --------------------------------STANDARDIZE JobTitles in SQL--------------------------------
    sql_query= '''EXEC dbo.JobTitle_Standardize ?, ?'''         #* 7Lakh Titles Took 78hrs to Standardize
    SQLCursor.execute(sql_query, (clientID,"'"+industry+"'"))
    SQLConnection.commit()


def JobTitle_FuzzyWuzzy(SQLConnection, SQLCursor, threshHoldFuzzyWuzzy, clientID, industry):
    #* -------------------Get UnMatched Titles which we have to check FuzzyWuzzy-------------------
    sql_query = '''SELECT DISTINCT TOP 100 JobTitle FROM dbo.Unmatched_For_Fuzz WHERE checked_Fuzz IS NULL ORDER BY JobTitle'''
    df_unmatchedTitlesForFuzz = pd.DataFrame(pd.read_sql_query(sql_query, SQLConnection))
    sql_query = '''SELECT * FROM dbo.Mapped_IT'''
    df_alternateJobTitles = pd.DataFrame(pd.read_sql_query(sql_query, SQLConnection))

    # #! ------------Change to IF NOT EXISTS------------
    # #! ---------take the SQL code to another FILE and call that File in Python---------
    # query='''IF EXISTS(SELECT 1 FROM sys.tables WHERE name = 'Matched_Fuzz')
    #         BEGIN
    #             DROP TABLE dbo.Matched_Fuzz;
    #         END'''
    # SQLCursor.execute(query)
    # SQLConnection.commit()
    # #! Ori_Title -> originalTitle

    # query='''CREATE TABLE Matched_Fuzz(id int primary key identity(1,1), 
    #                                     [ONET Code] nvarchar(max),
    #                                     Title nvarchar(max), 
    #                                     Ori_Title nvarchar(max),  
    #                                     Trimmed_Title nvarchar(max),
    #                                     Matched_Title nvarchar(max),
    #                                     FuzzRatio nvarchar(max),
    #                                     Industries nvarchar(max),
    #                                     Alt_Industry nvarchar(max))'''
    # SQLCursor.execute(query)
    # SQLConnection.commit()

    for index,rowTitles in df_unmatchedTitlesForFuzz.iterrows():
        query='''UPDATE dbo.Unmatched_For_Fuzz SET checked_Fuzz=1 WHERE JobTitle = ? '''
        SQLCursor.execute(query,(rowTitles['JobTitle']))
        SQLConnection.commit()

        trimmedTitle = re.sub(r'[^a-zA-Z\s.\']',' ',rowTitles['JobTitle']).strip().title()
        if(trimmedTitle != ''):
            result=process.extractOne(trimmedTitle, df_alternateJobTitles['Alternate Title'].to_list(), scorer=fuzz.token_sort_ratio)
            if(result[1]>=threshHoldFuzzyWuzzy):
                Matched_rows=df_alternateJobTitles.loc[df_alternateJobTitles['Alternate Title']==result[0]]
                for i,row in Matched_rows.iterrows():
                    query='''INSERT INTO dbo.Matched_Fuzz([ONET Code], Title, Ori_Title, Trimmed_Title, Matched_Title, FuzzRatio, Industries, Alt_Industry)
                            VALUES (?,?,?,?,?,?,?,?)'''
                    SQLCursor.execute(query,(row['ONET Code'], row['Title'], rowTitles['JobTitle'], trimmedTitle, row['Alternate Title'], str(result[1]), row['Industries'], row['Alt_Industry']))
                    SQLConnection.commit()
                    print("'"+row['ONET Code']+"'", "'"+row['Title']+"'", "'"+rowTitles['JobTitle']+"'", "'"+trimmedTitle+"'", "'"+row['Alternate Title']+"'", "'"+str(result[1])+"'", "'"+row['Industries']+"'", "'"+row['Alt_Industry']+"'")
                # print(rowTitles['JobTitle'] +'\t' + trimmedTitle + '\t' + str(Matched_rows['ONET Code']) + '\t' + str(Matched_rows['Alternate Title']) + '\t' + str(result[1]))
