def createDatasets(SQLConnection, SQLCursor, clientID):
    sql_query = f'''EXEC dbo.Create_Datasets {clientID}'''
    SQLCursor.execute(sql_query)
    SQLConnection.commit()