from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import traceback

def deploy(endPoint, flaskPortNumber, encoder):

    app = Flask(__name__)
    @app.route(f'/{endPoint}', methods=['POST'])
    def predict():
        inputValues = pd.DataFrame(request.json)
        tenureToPredict = request.query_string
        tenureToPredict = int(tenureToPredict[6:])
        model = joblib.load(f'model_{tenureToPredict}.pkl')
        print(tenureToPredict)
        if model:
            try:
                encoded_data = pd.DataFrame()
                jobNumber = 1
                while jobNumber <= tenureToPredict:
                    encoded_features =  encoder.transform(inputValues[f'ONET_Code{jobNumber}'].values.reshape(-1,1))
                    encoded_ONETCodes = pd.DataFrame(encoded_features.toarray())
                    encoded_ONETCodes.columns = encoded_ONETCodes.columns.astype(str)

                    #* Concatenate the encoded features with the original numerical features (Tiers, Tenures)
                    if(jobNumber == tenureToPredict):
                        encoded_data = pd.concat([encoded_data, encoded_ONETCodes, inputValues[f'Tier{jobNumber}']], axis=1)
                        break
                    encoded_data = pd.concat([encoded_data, encoded_ONETCodes, inputValues[f'Tier{jobNumber}'], inputValues[f'Tenure{jobNumber}']], axis=1)
                    jobNumber = jobNumber + 1

                predictions = list(model.predict(encoded_data))
                return jsonify({'prediction': str(predictions)})
            except:
                return jsonify({'trace': traceback.format_exc()})
        else:
            print('Model not good')
            return 'Model is not good'

    try:
        port = int(sys.argv[1])
    except:
        port = flaskPortNumber
    app.run(port=port, debug=True)

