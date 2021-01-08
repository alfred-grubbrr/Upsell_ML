import random
import pandas as pd
import math
#import os
import pyodbc
import operator as op
from functools import reduce
from graph_poc_csv import UpsellGraph 
from generate_data_azure import main as get_data

#connect to the SQL server using my credentials
# DB = {'servername': 'grubbrrupselldev.database.windows.net', 'database': 'DBGrubbrrUpsellDev', 'username': 'sam', 'password': '2FGHqHk4r'}
# conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])

DB = {'servername': 'grubbrrv2.database.windows.net', 'database': 'DBGrubbrrStaging', 'username': 'upsell', 'password': 'E4u28e92q4'}
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])
        
"""
def rec(state, company_id, branch_id):
    # create the menu, which we will use to detemine the order_index
    sql = 'select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'' + 'q_table_company_' + str(company_id) + '_branch_' + str(branch_id) + '\''
    menu = pd.read_sql(sql, conn)[1:].values.flatten().tolist()

    # will we explore? (between 1-100):
    explore_rate = 1
    explore = random.randint(0,100)

    ### SQL code for updating edge weights needs to be written

    return menu[rand(menu)]
"""

def rec(order, company_id, branch_id):
    edges_csv_name = "graph_company_{}_branch_{}_edges.csv".format(company_id,branch_id)
    edges_df = pd.read_csv(edges_csv_name)
    edges_df['Item1'] = edges_df['Item1'].astype('int64')
    edges_df['Item2'] = edges_df['Item2'].astype('int64')
    menu = pd.unique(edges_df[["Item1", "Item2"]].values.ravel())

    # orders_list, prices = get_data()
    # will we explore? (between 1-100):
    explore_rate = 1
    explore = random.randint(0,100)
    print("I'm here, bro!", menu)
    # rec_ind = UG.order_recommend(state,prices)
    # print("exploiting, ",rec_ind)

    if explore >= explore_rate:
        # rec_ind = UG.order_recommend(order=state, prices=prices)
        best_reco = ""
        weights = {}    # Dictionary holding all 'to' connections and their weights to all items in the order
        for itemA in order:
            print(type(itemA),itemA)
            itemA_connections = edges_df.loc[edges_df['Item1']==int(itemA)].Item2.unique()
            for itemB in itemA_connections:
                if itemB not in order:
                    # w = item2_price*item2_quantity
                    w = edges_df.loc[(edges_df['Item1']==int(itemA))&(edges_df['Item2']==int(itemB)),'Weights'].values[0]
                    if itemB not in weights:
                        weights[itemB] = w
                    else:
                        weights[itemB] += w
        # print(weights.items())
        best_reco = max(weights.items(), key=op.itemgetter(1))[0]   # returns key with max value in weights dictionary

        print("exploiting")
        print(str(best_reco))
        return str(best_reco)
    else:
        print("exploring")
        print(menu[rand(menu)])
        return menu[rand(menu)]

# this function returns a random index that will be used to for recommendation
def rand(menu):
    return random.randint(0, (len(menu) - 1))

def update(company_id, branch_id, order, rec_item_ID, bool):
    sql_nodes = "SELECT ItemID, Price FROM Item WHERE companyID =" + str(company_id) + "and BranchID = " + str(branch_id)
    sql_nodes_df = pd.read_sql(sql_nodes, conn)
    edges_csv_name = "graph_company_{}_branch_{}_edges.csv".format(company_id,branch_id)
    edges_df = pd.read_csv(edges_csv_name)
    menu = pd.unique(edges_df[["Item1", "Item2"]].values.ravel())
    edges_df['Item1'] = edges_df['Item1'].astype('int64')
    edges_df['Item2'] = edges_df['Item2'].astype('int64')
    print(sql_nodes_df['ItemID'].unique())
    print(edges_df.Item1.unique())
    print(sql_nodes_df.info())
    print(edges_df.info())
    rec_item_ID_price = sql_nodes_df.loc[sql_nodes_df["ItemID"]==rec_item_ID, "Price"]

    for itemA in order:
        # print(type(itemA))
        edge_id = str(itemA) + "_" + str(rec_item_ID)
        itemA_prices = edges_df.loc[edges_df['Item1']==int(itemA),'Item1Price'].unique()
        print(itemA_prices)
        itemA_price = itemA_prices[0]

        # Recommendation accepted: record it
        if (bool == 1):
            if edge_id not in edges_df.Edge_ID.unique():
                edges_df.loc[edges_df.index.max() + 1] = [edge_id, itemA, rec_item_ID, rec_item_ID_price, itemA_price, rec_item_ID_price]
            else:
                edges_df[edges_df['Edge_ID']==edge_id, 'Weights'] += rec_item_ID_price

        # Recommendation rejected: give penalty
        else:
            if edge_id not in edges_df.Edge_ID.unique():
                edges_df.loc[edges_df.index.max() + 1] = [edge_id, itemA, rec_item_ID, rec_item_ID_price, itemA_price, -rec_item_ID_price]
            else:
                edges_df[edges_df['Edge_ID']==edge_id, 'Weights'] += -rec_item_ID_price

    edges_df.to_csv("./" + edges_csv_name,index=False)

# example function calls:
# update(10, 0, ['1107', '1108'], 1107, 1)
# update(16, 23, ['1142', '1122'], 1132, 1)
# to reset: update(10, 0, ['1107', '1108'], 1107, 73738)
# rec(['1213', '1232'], 16, 23)
# rec(['1156', '1243'], 16, 23)
# update(16,23,['1228',  '1229',  '1230'], 47287,1)