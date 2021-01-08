import random
import pandas as pd
import math
#import os
import pyodbc
import operator as op
from functools import reduce

#connect to the SQL server using my credentials
# DB = {'servername': 'grubbrrupselldev.database.windows.net', 'database': 'DBGrubbrrUpsellDev', 'username': 'sam', 'password': '2FGHqHk4r'}
# conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])

DB = {'servername': 'grubbrrv2.database.windows.net', 'database': 'DBGrubbrrStaging', 'username': 'upsell', 'password': 'E4u28e92q4'}
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+DB['servername']+';DATABASE='+DB['database']+';UID='+DB['username']+';PWD='+DB['password'])

# this function takes in an order, company_id, and branch_id to return a recommendation in terms
# of its ItemID. It does this by using a q-table, which is stored in sql, to randomly select an
# ItemID from the top sqrt of menu items. Depending on the exploration rate, which can be manually set,
# it may simply return a completely random ItemID, which is necessary for the learning process; however,
# overtime the exploration rate should be set to something quite low once it has learned user preferences
def rec(state, company_id, branch_id):
    # create the menu, which we will use to detemine the order_index
    sql = 'select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'' + 'q_table_company_' + str(company_id) + '_branch_' + str(branch_id) + '\''
    menu = pd.read_sql(sql, conn)[1:].values.flatten().tolist()

    # will we explore? (between 1-100):
    explore_rate = 1
    explore = random.randint(0,100)

    print("I'm here. bro!")

    # calculate order index
    r = 0
    if (len(state) > 1):
        state = sorted(state)
    if (len(state) == 1):
        print("Menu is: ",menu)
        order_id = menu.index(state[0])
    if (len(state) == 2):
        order_id = len(menu)
        for x in state:
            n = menu.index(x)
            r += 1
            order_id += ((reduce(op.mul, range(n, n-r, -1), 1)) // (reduce(op.mul, range(1, r+1), 1)))
    if (len(state) == 3):
        order_id = len(menu) + ((reduce(op.mul, range(len(menu),
        len(menu)-2, -1), 1)) // (reduce(op.mul, range(1, 2+1), 1)))
        for x in state:
            n = menu.index(x)
            r += 1
            order_id += ((reduce(op.mul, range(n, n-r, -1), 1)) // (reduce(op.mul, range(1, r+1), 1)))

    # QUERY SQL FOR EXISTING ORDERS IN THE FORM OF THEIR TRANSFORMED VALUE (index as calculated above)
    sql = 'SELECT order_index FROM q_table_company_' + str(company_id) + '_branch_' + str(branch_id)
    existing_orders = pd.read_sql(sql, conn).values.flatten().tolist()

    # check if order exists in the q-table; if so, query that row to determine recommendation
    # else create the row w/ transformed value as order_index
    # This also determines the recommendation:
    # If this exploration value is less than the pre-set explore_rate, we will simply recommend
    # a random item; otherwise, we will select randomly from the top sqrt of items
    # (based on the q table) (if there are values in the q table, that is)

    if (order_id in existing_orders):
        sql = 'SELECT * FROM q_table_company_' + str(company_id) + '_branch_' + str(branch_id) + ' WHERE order_index = ' + str(order_id)
        order_info = pd.read_sql(sql,conn)
        if explore >= explore_rate:
            sq = int(math.sqrt(len(menu)))
            sq_largest = order_info.transpose()[1:].nlargest(sq, 0).index.tolist()
            rec_ind = random.randint(0, len(sq_largest) - 1)
            print("exploiting")
            print(sq_largest[rec_ind])
            return sq_largest[rec_ind]
        else:
            print("exploring")
            print(menu[rand(menu)])
            return menu[rand(menu)]

    else:
        zeros = len(menu) * '0'
        zeros = ", ".join(zeros)
        cursor = conn.cursor()
        cursor.execute (" INSERT INTO q_table_company_" + str(company_id) + "_branch_" + str(branch_id) + " VALUES (" + str(order_id) + ", " + str(zeros) + ")")
        conn.commit()
        print("created new row")
        print(menu[rand(menu)])
        return menu[rand(menu)]

# this function returns a random index that will be used to for recommendation
def rand(menu):
    return random.randint(0, (len(menu) - 1))

# this function updates the q table in sql. bool is 1 if the recommendation was
# accepted, and 0 if it was not. To clear the values in a row (useful during the development
# process), set bool to 73738, which spells 'reset' on a phone alphabet. ID is the
# item id of the recommened item. state is the customer's order.
def update(company_id, branch_id, state, ID, bool):
    # set the menu to a list
    sql = 'select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'' + 'q_table_company_' + str(company_id) + '_branch_' + str(branch_id) + '\''
    menu =  pd.read_sql(sql, conn)[1:].values.flatten().tolist()

    # calculate order index
    r = 0
    if (len(state) > 1):
        state = sorted(state)
    if (len(state) == 1):
        order_id = menu.index(state[0])
    if (len(state) == 2):
        order_id = len(menu)
        for x in state:
            n = menu.index(x)
            r += 1
            order_id += ((reduce(op.mul, range(n, n-r, -1), 1)) // (reduce(op.mul, range(1, r+1), 1)))
    if (len(state) == 3):
        order_id = len(menu) + ((reduce(op.mul, range(len(menu),
        len(menu)-2, -1), 1)) // (reduce(op.mul, range(1, 2+1), 1)))
        for x in state:
            n = menu.index(x)
            r += 1
            order_id += ((reduce(op.mul, range(n, n-r, -1), 1)) // (reduce(op.mul, range(1, r+1), 1)))
    print("order_id:", order_id)

    #set value
    if (bool == 1):
        # get item price from sql
        sql = 'SELECT price FROM Item WHERE (ItemID =' + str(ID) + ')'
        price = pd.read_sql(sql, conn).price[0]
        print("price:", price)
        cursor = conn.cursor()
        cursor.execute ("UPDATE q_table_company_" + str(company_id) + "_branch_" + str(branch_id) + " SET [" + str(ID) + "] += " + str(price) + " WHERE order_index = " + str(order_id))
        conn.commit()

    #reset row
    if (bool == 73738):
        items_for_reset = "] = 0, [".join(menu)
        cursor = conn.cursor()
        cursor.execute (" UPDATE q_table_company_" + str(company_id) + "_branch_" + str(branch_id) + " SET [" + str(items_for_reset) + "] = 0 WHERE order_index = " + str(order_id))
        conn.commit()

    #add data to UpsellData table
    else:
        cursor = conn.cursor()
        cursor.execute ("INSERT INTO UpsellData VALUES (" + str(company_id) + ", " + str(branch_id) + ", '" + ", ".join(state) + "', " + str(ID) + ', ' + str(bool) + ')')
        conn.commit()

# example function calls:
# update(10, 0, ['1107', '1108'], 1107, 1)
# update(10, 0, ['1110', '1142', '1122'], 1132, 1)
# to reset: update(10, 0, ['1107', '1108'], 1107, 73738)
# rec(['1109', '1108'], 10, 0)
# rec(['1141', '1142', '1143'], 10, 0)
