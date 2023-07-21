from sklearn.preprocessing import OneHotEncoder
import pandas as pd

def fitEncoder(SQLConnection):
    oneHotEncoder = OneHotEncoder()
    sql_query = f'''SELECT DISTINCT [ONET Code] FROM dbo.Mapped_IT'''
    df_allOnetCodesForEncoding = pd.read_sql_query(sql_query, SQLConnection)
    oneHotEncoder.fit(df_allOnetCodesForEncoding['ONET Code'].values.reshape(-1,1))
    return oneHotEncoder

