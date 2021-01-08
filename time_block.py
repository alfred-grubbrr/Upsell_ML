import pyodbc
import pandas as pd

#connect to the SQL server using my credentials
# DB = {'servername': 'grubbrrupselldev.database.windows.net', 'database': 'DBGrubbrrUpsellDev', 'username': 'sam', 'password': '2FGHqHk4r'}
# conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])

DB = {'servername': 'grubbrrv2.database.windows.net', 'database': 'DBGrubbrrStaging', 'username': 'upsell', 'password': 'E4u28e92q4'}
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])

#this function returns the top 10 most frequent items in the given time interval (4 time intervals split up the day)
def popular_by_time(branchid, time_interval):
    sql = 'SELECT ItemID, CreatedDate FROM OrderItemMaster Where BranchID =' + str(branchid)
    items_ordered = pd.read_sql(sql, conn)
    hour_of_order = items_ordered['CreatedDate'].astype(str).str[11:13]
    hour_of_order = hour_of_order.astype(int)
    items_ordered['CreatedDate'] = hour_of_order
    items_ordered.rename(columns={'CreatedDate':'time'}, inplace=True)

    start_time = time_interval * 6
    end_time = start_time + 6
    out = items_ordered.loc[(items_ordered.time >= start_time) & (items_ordered.time < end_time)]['ItemID'].value_counts()[:10].index.tolist()
    return out



