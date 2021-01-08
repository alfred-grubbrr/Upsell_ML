# Package import
from sql_data_interact import get_sqldata
import warnings
import itertools
warnings.filterwarnings("ignore")


def gen_comb(item_list, num):
    combinations_object = itertools.combinations(item_list, num)
    combinations_list = []
    for item in combinations_object:
        combinations_list.append(','.join(item))
    return combinations_list


# If we got a new order
def recomd_f(new_order_str, order_store_dic):
    if new_order_str in order_store_dic:
        recomd_prod = order_store_dic[new_order_str]

        return recomd_prod
    else:
        new_comb = list(set(new_order_str.split(',')))
        new_comb.sort()
        all_combinations = gen_comb(new_comb, 2)

        for comb in all_combinations:
            if comb in order_store_dic and order_store_dic[comb] not in comb.split(','):
                return order_store_dic[comb]
        return "None"


# title main function
def main(new_order_str=None, company_id=None, branch_id=None):
    try:
        if company_id.isdigit():
            company_id = str(company_id)
        if branch_id.isdigit():
            branch_id = str(branch_id)
        table_name = 'comp' + company_id + '_b' + branch_id + '_recomd'
        recomd_prod = get_sqldata(table_name=table_name)
        order_store_dic = dict(zip(recomd_prod['Item_comb'], recomd_prod['Recomd_item']))
        product_id = recomd_f(new_order_str, order_store_dic)
        print(product_id)
        return product_id
    except:
        print('PLZ provide correct info')

