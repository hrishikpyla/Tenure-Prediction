import pandas as pd
from sklearn.model_selection import train_test_split

#*datasetNumber = 1 means we want to split the Dataset_1 and so on......

def split(SQLConnection, SQLCursor, datasetNumber, clientID, testFraction):
    #* jobNumber = 1 is the values of 1st job and so on.....
    jobNumber = 1
    while jobNumber <= datasetNumber:
        sql_query = f'''UPDATE dbo.Dataset{datasetNumber}_{clientID} SET Tenure{jobNumber} = CONVERT(int,Tenure{jobNumber}), Tier{jobNumber} = CONVERT(int,Tier{jobNumber});'''
        SQLCursor.execute(sql_query)
        SQLConnection.commit()
        jobNumber = jobNumber + 1

    sql_query = f'''SELECT * FROM dbo.Dataset{datasetNumber}_{clientID} ORDER BY ResumeKey '''
    df_data = pd.read_sql_query(sql_query,SQLConnection)

    #* ONET_Code1 Tier1 Tenure1 ONET_Code2 Tier2 Tenure2

    jobNumber = 1
    df_dataColumns = pd.DataFrame()
    while jobNumber <= datasetNumber:
        df_dataColumns = pd.concat([df_dataColumns, df_data[f'ONET_Code{jobNumber}'], df_data[f'Role{jobNumber}'], df_data[f'Tier{jobNumber}'], df_data[f'OrgName{jobNumber}'], df_data[f'Tenure{jobNumber}']],axis=1)
        jobNumber = jobNumber + 1

    #* if testFraction = 0 dont do this split
    if testFraction == 0:
        trainingDataColumns = df_dataColumns
        testingDataColumns = pd.DataFrame()
        trainingDataColumns.columns = trainingDataColumns.columns.astype(str)
    else:
        trainingDataColumns, testingDataColumns = train_test_split(df_dataColumns, test_size=testFraction)
        trainingDataColumns.columns = trainingDataColumns.columns.astype(str)
        testingDataColumns.columns = testingDataColumns.columns.astype(str)

    #*reconverting the columns names to string type because the concatanation method is changing the type of the column names

    return trainingDataColumns, testingDataColumns

