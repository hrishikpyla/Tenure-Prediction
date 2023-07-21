import numpy as np
import pandas as pd
import pyodbc
import json
from sklearn.linear_model import LinearRegression


with open('BR_Python/custom_settings.json','r') as file:
    settings = json.load(file)

SQLConnectionString = f"Driver={settings['SQLDriverString']};Server={settings['SQLServerName']};Database={settings['SQLDatabaseName']};Trusted_Connection=yes;"
SQLConnection = pyodbc.connect(SQLConnectionString)
SQLCursor = SQLConnection.cursor()

#? -------------------------------------------STANDARDIZATION OF THE JOBTITLES-------------------------------------------
from standardizeJobTitles import JobTitle_SQLStoredProcedure, JobTitle_FuzzyWuzzy
JobTitle_SQLStoredProcedure(SQLConnection, SQLCursor, 
                            clientID=settings['clientID'], 
                            industry=settings['industryJobTitleStandarization'])

JobTitle_FuzzyWuzzy(SQLConnection, SQLCursor, 
                    threshHoldFuzzyWuzzy=settings['fuzzRatio'], 
                    clientID=settings['clientID'], 
                    industry=settings['industryJobTitleStandarization'])

#? ------------------------------------------STANDARDIZATION OF THE ORGANISATION NAMES------------------------------------------
#* By Assigning them Tiers Based on the Money that particular Organisation's Financial Data
from standardizeOrgNames import getDistinctOrgNames, cleanOrgName, tieringOrganisations

df_orgNames = getDistinctOrgNames(SQLConnection, SQLCursor)
df_cleanedOrgName = cleanOrgName(SQLConnection, SQLCursor, 
                                df_orgNames=df_orgNames)     #* cleaning 200 OrgNames Approx took 10sec
tieringOrganisations(SQLConnection, SQLCursor, 
                    df_cleanedOrgName=df_cleanedOrgName, 
                    apiKey=settings['clearBitAPIKey_Tiering'])

#? --------------------SPLITTING THE Experience TABLE INTO DIFFERENT DATASETS SO AS TO FEED THEM TO DIFFERENT DATASETS--------------------
from createDataSets import createDatasets
# createDatasets(SQLConnection, SQLCursor, 
#                 clientID=settings['clientID'])

#? ---------------------------------fitting all the ONET_Code values to the OneHotEncoder--------------------------------- 
#* so that this encoder can be used to transform any ONET_Code in the future (trianing, testing, predictions)
from oneHotEncoder import fitEncoder
fittedEncoder = fitEncoder(SQLConnection)

#? -------------------------------------Splitting the Data into Training and Testing Data-------------------------------------
#* use testFraction = 0 while deploying; for testing use the fraction of data you want for testing
from splitData import split
trainingData, testingData = split(SQLConnection, SQLCursor, 
                                    datasetNumber=1, 
                                    clientID=516, 
                                    testFraction=0)

#? ----------------------------Training the Model with the Trianing Data That we generated before----------------------------

from trainingModels import trainModel
unTrainedmodel = LinearRegression()
trainedModel1 = trainModel(SQLConnection, SQLCursor, 
                            model=unTrainedmodel, 
                            encoder=fittedEncoder, 
                            trainingDataColumns=trainingData, 
                            datasetNumber=1)

#? ------------------If Code is used for Testing Purposes: The Model is tested Against the Testing Data that we generated before------------------
from testingModels import testModel
from modelEvaluate import evaluateModel
from createPkl import createPkl
from deployModel import deploy
if len(testingData) > 0:
    # while testing make sure that all ONET_Codes are previously supplied for training, else getting INVALID predictions
    #* we get predictions for all the testing Data 
    predictions = testModel(SQLConnection, SQLCursor, 
                            model=trainedModel, 
                            encoder=fittedEncoder, 
                            testingDataColumns=testingData, 
                            datasetNumber=1)

    #* and we can evaluate the accuracy of the model by looking at all the METRIC Scores like R2 Score, Mean Square Error, Mean Absolute Error
    evaluateModel(testingDataColumns=testingData, 
                    trainingDataColumns=trainingData, 
                    datasetNumber=1, 
                    predictions=predictions)

#? -----------If Code is Used for Deployment Purposes: The Model is saved as a .pkl file so that it can be deployed on a local Flask Server-----------
else:
    #* creates the .pkl file based on the model that we trained
    createPkl(model=trainedModel1, datasetNumber=1)
    createPkl(model=trainedModel1, datasetNumber=2)
    createPkl(model=trainedModel1, datasetNumber=3)
    createPkl(model=trainedModel1, datasetNumber=4)
    createPkl(model=trainedModel1, datasetNumber=5)
    
    #* deploys the encoder
    deploy(endPoint= settings['endPoint'], 
            flaskPortNumber=settings['flaskRunSetPort'], 
            encoder=fittedEncoder)

