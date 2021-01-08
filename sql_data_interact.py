
import pandas as pd
import warnings
from sqlalchemy import create_engine
import urllib
import pyodbc

warnings.filterwarnings("ignore")


def get_sqldata(server_name='grubbrrupselldev.database.windows.net', table_name='Item', columns='*'):
    """
    input:
        server_name str
        table_name str
        columns: default select all; str
    output:
        pd.DataFrame
    """
    DB = {'servername': server_name, 'database': 'DBGrubbrrUpsellDev', 'username': 'tong', 'password': 'Ht2ke68r9'}
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                          + DB['servername']
                          + ';DATABASE=' + DB['database']
                          + ';UID=' + DB['username']
                          + ';PWD=' + DB['password'])
    cursor = conn.cursor()
    try:
        sql_query = pd.read_sql_query('SELECT {} FROM dbo.{};'.format(columns, table_name), conn)
        data = pd.DataFrame(sql_query)
        print('succeed get {} table!'.format(table_name))

        return data
    except:
        print('check input')




def insert_table(server_name='grubbrrupselldev.database.windows.net', table_name=None, df=None):
    """
    input:
        server_name str
        table_name str
        df pd.DataFrame
    """
    DB = {'servername': server_name, 'database': 'DBGrubbrrUpsellDev', 'username': 'tong', 'password': 'Ht2ke68r9'}
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                          + DB['servername']
                          + ';DATABASE=' + DB['database']
                          + ';UID=' + DB['username']
                          + ';PWD=' + DB['password'])
    cursor = conn.cursor()

    if cursor.tables(table=table_name, tableType='TABLE').fetchone():
        print("Table already exists")
    else:
        print('Start to input data set')
        quoted = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                          + DB['servername']
                          + ';DATABASE=' + DB['database']
                          + ';UID=' + DB['username']
                          + ';PWD=' + DB['password'])
        engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        df.to_sql(table_name, schema='dbo', con=engine)
        print("Succeed!")


def insert_row(server_name='grubbrrupselldev.database.windows.net', table_name=None, df=None):
    DB = {'servername': server_name, 'database': 'DBGrubbrrUpsellDev', 'username': 'tong', 'password': 'Ht2ke68r9'}
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                          + DB['servername']
                          + ';DATABASE=' + DB['database']
                          + ';UID=' + DB['username']
                          + ';PWD=' + DB['password'])
    cursor = conn.cursor()
    columns = ''
    for name in df.columns:
        columns += (',' + name)
    record_list = df.values.tolist()

    insert_records = '''INSERT INTO {}({}) VALUES(?,?) '''.format(table_name, columns)
    cursor.executemany(insert_records, record_list)
    conn.commit()
    print("Succeed!")


def update_row(server_name='grubbrrupselldev.database.windows.net', table_name=None, set_str=None, conditions=None ):
    DB = {'servername': server_name, 'database': 'DBGrubbrrUpsellDev', 'username': 'tong', 'password': 'Ht2ke68r9'}
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                          + DB['servername']
                          + ';DATABASE=' + DB['database']
                          + ';UID=' + DB['username']
                          + ';PWD=' + DB['password'])
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM {}'.format(table_name))
    
    cursor.execute('''
                    UPDATE {}
                    SET {}
                    WHERE {}
                    '''.format(table_name, set_str, conditions))
    conn.commit()
    print("Succeed!")