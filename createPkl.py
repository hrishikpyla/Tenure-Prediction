import joblib
import pandas as pd
import numpy as np

def createPkl(model, datasetNumber):
    joblib.dump(model, f'model_{datasetNumber}.pkl')
    print(f"Model_{datasetNumber} Saved")

