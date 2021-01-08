import numpy as np
import pandas as pd
import math
import pyodbc
from itertools import combinations, product
import csv 

# DB = {'servername': 'grubbrrupselldev.database.windows.net', 'database': 'DBGrubbrrUpsellDev', 'username': 'sam', 'password': '2FGHqHk4r'}
# conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])

DB = {'servername': 'grubbrrv2.database.windows.net', 'database': 'DBGrubbrrStaging', 'username': 'upsell', 'password': 'E4u28e92q4'}
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])


        # self.STORAGEACCOUNTNAME= 'scangostgacct'
        # self.BLOBNAME= 'grubbrr'
        # self.CONNECTIONSTR = "DefaultEndpointsProtocol=https;AccountName=scangostgacct;AccountKey=gwjKUJE6d4C9rZS5g1A4xpWsJow5q4Msmazbr0PJSDkRtHydbbrLbw3cT25uzS13H8qQeWrT2mIRRx7sbj+VYA==;EndpointSuffix=core.windows.net"
        

def create_sql_table(company_id, branch_id):

    # sql = "SELECT ItemID FROM Item WHERE companyID =" + str(company_id) + "and BranchID = " + str(branch_id)
    # lp = pd.read_sql(sql, conn)
    # uni_items = lp.ItemID.unique()
    # cols = "] float, [".join([str(x) for x in uni_items])
    # cursor = conn.cursor()
    # cursor.execute ("CREATE TABLE q_table_company_" + str(company_id) + "_branch_" + str(branch_id) + "(order_index int, [" + cols + "] float)")
    # conn.commit()
    fname = "graph_company_{}_branch_{}_edges.csv".format(company_id,branch_id)
    with open(fname,"w") as file_writer:
      fields=["Item1","Item2","Weights"]
      writer=csv.DictWriter(file_writer,fieldnames=fields)
      writer.writeheader()

def create_sql_table1(company_id, branch_id):

    sql = "SELECT ItemID FROM Item WHERE companyID =" + str(company_id) + "and BranchID = " + str(branch_id)
    lp = pd.read_sql(sql, conn)
    uni_items = lp.ItemID.unique()
    cols = "] float, [".join([str(x) for x in uni_items])
    cursor = conn.cursor()
    new_table = "graph_table_company_" + str(company_id) + "_branch_" + str(branch_id)
    # cursor.execute ("CREATE TABLE q_table_company_" + str(company_id) + "_branch_" + str(branch_id) + "(order_index int, [" + cols + "] float)")
    cursor.execute ("CREATE TABLE " + new_table + "_nodes" + " AS (" + sql +");")	# Creates table for Nodes
    cursor.execute ("CREATE TABLE " + new_table + "_edges" + " ( a INTEGER NOT NULL REFERENCES " + new_table + "_nodes(ItemID) ON UPDATE CASCADE ON DELETE CASCADE," + " b INTEGER NOT NULL REFERENCES " + new_table + "_nodes(ItemID) ON UPDATE CASCADE ON DELETE CASCADE," + " PRIMARY KEY (a, b) );")	# Creates table for Edges
    conn.commit()

def create_csv_file(company_id, branch_id):

    sql = "SELECT OrderID, ItemID, ItemPrice, ItemQuantity FROM OrderItemMaster WHERE companyID =" + str(company_id) + "and BranchID = " + str(branch_id)
    sql_data_df = pd.read_sql(sql, conn)
    uni_items = sql_data_df.ItemID.unique()
    uni_orders = sql_data_df.OrderID.unique()
    edges = []
    edges_dict = {}
    print(sql_data_df.info())

    for order in uni_orders:
        ItemsInOrder = sql_data_df[sql_data_df['OrderID']==order].ItemID.unique()
        # print("ITEMSSSSSSSSSS")
        # print(ItemsInOrder)
        print(order)
        

        # Update Edges
        # Edge_ID is: str(item1) + "_" + str(item2)
        for item1, item2 in list(product(ItemsInOrder, ItemsInOrder)):
            if item1 == item2:
                continue

            item1_price = sql_data_df.loc[(sql_data_df["OrderID"]==order)&(sql_data_df["ItemID"]==item1), "ItemPrice"].values[0]
            item1_qty = sql_data_df.loc[(sql_data_df["OrderID"]==order)&(sql_data_df["ItemID"]==item1), "ItemQuantity"].values[0]
            item2_price = sql_data_df.loc[(sql_data_df["OrderID"]==order)&(sql_data_df["ItemID"]==item2), "ItemPrice"].values[0]
            item2_qty = sql_data_df.loc[(sql_data_df["OrderID"]==order)&(sql_data_df["ItemID"]==item2), "ItemQuantity"].values[0]
            # print("Price")
            # print(item1_price)

            # Edge: item1 ---> item2
            edge_id = str(item1) + "_" + str(item2)
            # print("Edge_id",edge_id)
            if edge_id not in edges_dict:
                edges_dict[edge_id] = len(edges)    # dictionary storing indices of edges list
                edges.append([edge_id, item1, item2, item2_price*item2_qty, item1_price, item2_price])
            else:
                # edges_dict[edge_id][3] += item2_price*item2_qty
                edges[edges_dict[edge_id]][3] += item2_price*item2_qty

            # Edge: item2 ---> item1
            edge_id = str(item2) + "_" + str(item1)
            if edge_id not in edges_dict:
                edges_dict[edge_id] = len(edges)
                edges.append([edge_id, item2, item1, item1_price*item1_qty, item1_price, item2_price])
            else:
                # edges_dict[edge_id][3] += item1_price*item1_qty
                edges[edges_dict[edge_id]][3] += item1_price*item1_qty


    edges_df = pd.DataFrame(edges,columns=['Edge_ID', 'Item1', 'Item2', 'Weights', 'Item1Price', 'Item2Price'], dtype=float)
    edges_csv_name = "graph_company_{}_branch_{}_edges.csv".format(company_id,branch_id)
    edges_df.to_csv("./" + edges_csv_name,index=False)

#example function calls:
#create_sql_table(219, 366)
