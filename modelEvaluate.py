from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pandas as pd
import numpy as np

def evaluateModel(testingDataColumns, trainingDataColumns, datasetNumber, predictions):
    actualTenureValues = testingDataColumns[f'Tenure{datasetNumber}']
    
    inValidPredictions = 0
    index = 0
    inValidPredictionsInTrained = 0
    n = len(actualTenureValues)
    while index < n:
        if(predictions[index] > 20 or predictions[index] < 0):
            if testingDataColumns['ONET_Code1'][index] in trainingDataColumns['ONET_Code1']:
                inValidPredictionsInTrained = inValidPredictionsInTrained + 1

            predictions = np.delete(predictions, index)
            actualTenureValues = actualTenureValues.drop(index=[index])
            actualTenureValues.reset_index(drop=True, inplace=True)
            inValidPredictions = inValidPredictions + 1 
            n = n - 1
        else:
            index = index + 1

    print('number of valid predictions = ', len(actualTenureValues))
    print('number of inValid predictions = ', inValidPredictions)
    print('number of inValid predictions which are in trained = ', inValidPredictionsInTrained)

    r2 = r2_score(actualTenureValues, predictions)
    mse = mean_squared_error(actualTenureValues, predictions)
    mae = mean_absolute_error(actualTenureValues,predictions)
    print('R2 Score = ', r2, '\nMSE = ', mse, '\nMAE = ', mae)
