# import package
import warnings
import itertools
import collections
import random
import heapq
import pandas as pd
from sql_data_interact import get_sqldata
from sql_data_interact import insert_table
import graph_poc as gp
warnings.filterwarnings("ignore")


# Item_price dictionary Key itemID, Value: Item
def item_price_dic_f(branchID, companyID, item_orders_raw):
    item_price = collections.defaultdict()
    selected_company = item_orders_raw[(item_orders_raw['BranchID_x'] == branchID) & (item_orders_raw['CompanyID_y'] == companyID)]
    selected_company['ItemID'] = selected_company['ItemID'].astype(str)
    item_price = dict(zip(selected_company['ItemID'], selected_company['Price']))
    # print(item_price)
    return item_price


# Item_Order dictionary: Key itemID, Value: orderID
def item_order_dic_f(train_data):
    dic = collections.defaultdict(list)
    for index in range(train_data.shape[0]):
        if train_data.loc[index, 'OrderID'] not in dic[train_data.loc[index, 'ItemID']]:
            dic[train_data.loc[index, 'ItemID']].append(train_data.loc[index, 'OrderID'])
    return dic


# Order_Item dictionary: Key OrderID, Value: Items be ordered
def order_item_dic_f(train_data_comp):
    order_item_dic = collections.defaultdict(str)
    for index in range(train_data_comp.shape[0]):
        order_item_dic[train_data_comp.loc[index, 'OrderID']] = train_data_comp.loc[index, 'ItemID']
    return order_item_dic


# Find the similar order and return non-ordered item
def similar_order(new_order_str, item_order_dic, order_item_dic):
    order_matches = []
    for item in new_order_str:
        order_matches.extend(item_order_dic[item])

    order_matches = set(order_matches)
    not_order_item = []

    for order in order_matches:
        pair1, pair2 = order_item_dic[order].split(','), new_order_str
        odd = [s for s in pair1 if s != '' and s not in pair2]
        not_order_item.extend(odd)
    not_order_item = list(set(not_order_item ))
    return not_order_item


# Return unordered item with highest price
def recommend_product(not_order_item, item_price):
    heap = []
    for item in not_order_item:
        heapq.heappush(heap, (item_price[item], item))
        if len(heap) > 1:
            heapq.heappop(heap)
    item = heapq.heappop(heap)
    return item[1]


# Generate Previous Paired Items And Get Recommend ItemID
def similar_order_dic(item_order_dic, order_item_dic, prev_orders, item_price):
    """"
    Input:

        prev_orders : list of strs
        item_order_dic: dic
        order_item_dic: dic
        item_price: dic

    Output:
        order_store_dic: dic
    """
    order_store_dic = collections.defaultdict(str)
    for prev_order in prev_orders:
        order_matches = []
        prev_order_list = prev_order.split(",")
        prev_order_list.sort()
        prev_order = ','.join(prev_order_list)
        if prev_order not in order_store_dic:
            for item in prev_order_list:
                order_matches.extend(item_order_dic[item])
            order_matches = set(order_matches)

            not_order_item = []

            for order in order_matches:
                pair1, pair2 = order_item_dic[order].split(','), prev_order_list
                odd = [s for s in pair1 if s != '' and s not in pair2]
                not_order_item.extend(odd)
            not_order_item = list(set(not_order_item))
            if not not_order_item:
                recomd_prod = random.choice(list(item_order_dic.keys()))
            # Here use Q learning result????
            else:
                recomd_prod = recommend_product(not_order_item, item_price)
            order_store_dic[prev_order] = recomd_prod
    return order_store_dic


# Try Generate All Items Combination Max As 2
def generate_all_comb(item_list, num):
    all_combinations = []
    for r in range(1, num):
        combinations_object = itertools.combinations(item_list, r)
        combinations_list = []
        for item in combinations_object:
            combinations_list.append(','.join(item))
            all_combinations += combinations_list
    return all_combinations


# Add all two paired items into previous result
def all_pair_comb(item_comb, order_store_dic, item_order_dic, order_item_dic, item_price):
    for pair in item_comb:
        order_matches = []
        pair_list = pair.split(",")
        pair_list.sort()
        pair = ','.join(pair_list)
        if pair not in order_store_dic:
            for item in pair_list:
                order_matches.extend(item_order_dic[item])
            order_matches = set(order_matches)

            not_order_item = []

            for order in order_matches:
                pair1, pair2 = order_item_dic[order].split(','), pair_list
                odd = [s for s in pair1 if s != '' and s not in pair2]
                not_order_item.extend(odd)
            not_order_item  = list(set(not_order_item ))
            if not not_order_item or len(not_order_item) == 0:
                recomd_prod = random.choice(list(item_order_dic.keys()))
            # Here use Q learning result????
            else:
                recomd_prod = recommend_product(not_order_item, item_price)
            order_store_dic[pair] = recomd_prod
    return order_store_dic


def main(company_id = 16, branch_id = 23, table_name = 'TESTING_TONGTBL'):
    """
    :param company_id: int
    :param branch_id: int
    :param table_name: str
    :return: pd.DataFrame, upload data set
    """
    # import data
    item_orders_raw = get_sqldata(table_name='item_orders_raw')
    company_order = pd.DataFrame()
    col_generate = ['OrderID', 'ItemID',  'BranchID_x']
    print("import data", item_orders_raw['Price'])
    items = item_orders_raw['ItemID'].unique()
    # get data set with specific companyID and branchID
    for col in col_generate:
        company_order[col] = item_orders_raw[item_orders_raw['CompanyID_y'] == company_id][col]
    train_data = company_order[company_order['BranchID_x'] == branch_id]
    train_data.drop(labels=['BranchID_x'], axis=1, inplace=True)
    train_data['ItemID'] = train_data['ItemID'].astype(str)
    train_data['OrderID'] = train_data['OrderID'].astype(str)
    train_data_comp = train_data.groupby(['OrderID'])['ItemID'].apply(lambda x: ','.join(x)).reset_index()
    train_data.index = pd.RangeIndex(len(train_data.index))
    print("get data set with specific companyID and branchID")

    # generate dictionary
    item_price = item_price_dic_f(branch_id, company_id, item_orders_raw)
    item_order_dic = item_order_dic_f(train_data)
    order_item_dic = order_item_dic_f(train_data_comp)
    order_items_list = list(order_item_dic.values())
    print("generate dictionary: ", order_item_dic)
    print("items list: ", order_items_list)

    """
    # generate recommend product
    order_store_dic_temp = similar_order_dic(item_order_dic, order_item_dic, order_items_list, item_price)
    item_comb = generate_all_comb(list(item_order_dic.keys()), 3)
    order_store_dic_temp = all_pair_comb(item_comb, order_store_dic_temp, item_order_dic, order_item_dic, item_price)
    print("generate recommend prod")

    # generate table
    recomd_prod = pd.DataFrame.from_dict(order_store_dic_temp, orient='index')
    recomd_prod = recomd_prod.reset_index().rename(columns={"index": "Item_comb", 0: 'Recomd_item'})
    recomd_prod['CompanyID'] = company_id
    recomd_prod['BranchID'] = branch_id
    recomd_prod.head(10)

    # upload data set
    insert_table(table_name=table_name, df=recomd_prod)
    """
    return order_items_list, train_data['ItemID'].unique(), item_price


# Added by Alfred for testing
if __name__ == "__main__":
    main()
