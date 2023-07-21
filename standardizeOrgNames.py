import pandas as pd
import re
import requests
import pyodbc

from tiering import getTier

def getDistinctOrgNames(SQLConnection, SQLCursor):
    # sql_query = '''SELECT DISTINCT OrgName INTO dbo.OrgNames FROM dbo.Combined_ONET_Codes WHERE [ONET Code] IS NOT NULL AND Tenure IS NOT NULL AND OrgName IS NOT NULL;'''
    # SQLCursor.execute(sql_query)
    # SQLConnection.commit()

    # sql_query = '''ALTER TABLE dbo.OrgNames ADD cleanedOrgName nvarchar(max);'''
    # SQLCursor.execute(sql_query)
    # SQLConnection.commit()

    # sql_query = '''ALTER TABLE dbo.OrgNames ADD Tier int'''
    # SQLCursor.execute(sql_query)
    # SQLConnection.commit()

    # sql_query = '''ALTER TABLE dbo.OrgNames ADD noDomain int'''
    # SQLCursor.execute(sql_query)
    # SQLConnection.commit()

    # sql_query = '''ALTER TABLE dbo.OrgNames ADD isCalledByAPI int'''
    # SQLCursor.execute(sql_query)
    # SQLConnection.commit()

    sql_query = '''SELECT TOP 10 * FROM dbo.OrgNames WHERE cleanedOrgName = 'GOOGLE' '''
    return pd.read_sql_query(sql_query, SQLConnection)

def cleanOrgName(SQLConnection, SQLCursor, df_orgNames):
    def clean_text(text):
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.upper()
        text = text.strip()
        if(text == ''):
            text=None
        return text

    df_orgNames['cleanedOrgName'] = df_orgNames['OrgName'].apply(clean_text)

    for index, orgDetails in df_orgNames.iterrows():
        sql_query = '''UPDATE dbo.OrgNames SET cleanedOrgName = ? WHERE OrgName = ?'''
        SQLCursor.execute(sql_query, (orgDetails['cleanedOrgName'], orgDetails['OrgName']))
        SQLConnection.commit()

    sql_query = '''SELECT TOP 10 * FROM dbo.OrgNames WHERE cleanedOrgName IS NOT NULL ORDER BY cleanedOrgName'''
    return pd.read_sql_query(sql_query,SQLConnection)

def tieringOrganisations(SQLConnection, SQLCursor, df_cleanedOrgName, apiKey):
    headers = {'Authorization': f'Bearer {apiKey}'}
    for index, org in df_cleanedOrgName['cleanedOrgName'].items():        
        #* Auto-Complete API gives us the Domain for the company name that we provide
        #* if there are multiple findings (of Organisations) in the autoComplete it returns a list of Data 
        #* where the 1st one is the best Match to our OrgName
        url_auto_complete = f'https://autocomplete.clearbit.com/v1/companies/suggest?query={org}'
        response = requests.get(url_auto_complete, headers=headers)

        sql_query = 'UPDATE dbo.OrgNames SET isCalledByAPI = 1 WHERE cleanedOrgName = ?'
        SQLCursor.execute(sql_query, org)
        SQLConnection.commit()
        
        if response.status_code == 200:         #* means that autoComplete understood our OrgName
            data = response.json()
            if len(data)>0:                     #* means that we got atleast one domain for our Orgname and we select the domain from 1st resultData
                bestMatchedCompany = data[0]
                companyDomain = bestMatchedCompany['domain']

                #* ClearBit Enrichment API gives us the financials of the Company that registerd the given Domain
                #* as the domain cant be registered to more than 1 company, we only get the datails of the company that we want

                url_enrichment = f'https://company.clearbit.com/v2/companies/find?domain={companyDomain}'
                response = requests.get(url_enrichment, headers=headers)
                if response.status_code == 200:                     #* means that enrichment understood our domain AND 
                                                                    #* that there are free trials left still
                    detailsOfCompany = response.json()
                    
                    tier = getTier(detailsOfCompany)

                    sql_query = "UPDATE dbo.OrgNames SET Tier = ? WHERE cleanedOrgName = ?;"
                    SQLCursor.execute(sql_query, str(tier), str(org))
                    SQLConnection.commit()

                elif str(response.status_code) == '402':
                    sql_query = '''UPDATE dbo.OrgNames SET isCalledByAPI = NULL where cleanedOrgName = ?'''
                    SQLCursor.execute(sql_query, org)
                    SQLConnection.commit()

                    print(f'Error: {response.status_code} - {response.text}')
                    break
            else:
                sql_query = "UPDATE dbo.OrgNames SET noDomain = ? WHERE cleanedOrgName = ?;"
                SQLCursor.execute(sql_query, 1, str(org))
                SQLConnection.commit()
        else:
            print(f'Error: {response.status_code} - {response.text}')