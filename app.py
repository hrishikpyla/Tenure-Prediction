from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import traceback
from standardizeOrgNames import cleanOrgName 
from standardizeOrgNames import tieringOrganisations
import pyodbc



"SQLDriverString": "{ODBC Driver 17 for SQL Server}",
"SQLServerName": "LAPTOP-PSGN8OOE",
"SQLDatabaseName": "INFINITE_ML",

SQLConnectionString = f"Driver={settings['SQLDriverString']};Server={settings['SQLServerName']};Database={settings['SQLDatabaseName']};Trusted_Connection=yes;"
SQLConnection = pyodbc.connect(SQLConnectionString)
SQLCursor = SQLConnection.cursor()





app = Flask(__name__)
@app.route('/api/data', methods=['GET'])
def get_data():
    input = pd.DataFrame(request.json)
    cleanOrgName(SQLConnection, SQLCursor, df_orgNames)
    tieringOrganisations(SQLConnection, SQLCursor, df_cleanedOrgName, apiKey)
    data = {'key': 'value'}

    return jsonify(data)

@app.route('/api/submit', methods=['POST'])
def submit_data():
    data = request.get_json()
    
    return jsonify({'message': 'Data submitted successfully'})

if __name__ == '__main__':
    app.run(debug=True)



