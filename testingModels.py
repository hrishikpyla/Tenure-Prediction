import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

def testModel(SQLConnection, SQLCursor, model, encoder, testingDataColumns, datasetNumber):
    #* resetting the index because of randomisation due to test-Train-split
    testingDataColumns.reset_index(drop=True, inplace=True)

    #* Perform one-hot encoding
    encoded_data = pd.DataFrame()
    jobNumber = 1
    while jobNumber <= datasetNumber:
        encoded_features = encoder.transform(testingDataColumns[f'ONET_Code{jobNumber}'].values.reshape(-1,1))
        encoded_ONETCodes = pd.DataFrame(encoded_features.toarray())

        #*reconverting the columns names to string type because model training has to be done with same columnName types
        encoded_ONETCodes.columns = encoded_ONETCodes.columns.astype(str)

        #* Concatenate the encoded features with the original numerical features (Tenures)
        encoded_data = pd.concat([encoded_data, encoded_ONETCodes, testingDataColumns[f'Tier{jobNumber}'], testingDataColumns[f'Tenure{jobNumber}']], axis=1)
        jobNumber = jobNumber + 1
    print('Number of Rows for testing = ',len(encoded_data))

    predictions = model.predict(encoded_data.drop(f'Tenure{datasetNumber}', axis=1))
    return predictions
