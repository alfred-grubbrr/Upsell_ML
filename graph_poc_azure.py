import os
import sys
import numpy as np
import graph
import operator as op
# from generate_data import main as get_data
from generate_data_azure import main as get_data
import csv

class UpsellGraph:
	def __init__(self):
		self.g = graph.Graph()	# Graph that stores items as nodes
		self.vert_str = {}		# Vertices as str->vertices dict

	def create_graph(self, orders, prices):
		# Creating graph vertices for every item in all the orders
		for order in orders:
			for item in order:
				if item not in self.vert_str:
					self.vert_str[item] = self.g.add_vertex(item)

		# Creating graph edges for every combination of the items in each order and rewarding the edges
		for order in orders:
			for itemA in order:
        
				itemA_connections = self.vert_str[itemA].get_connections()
				for itemB in order:
					if itemA!=itemB and (self.vert_str[itemB] not in itemA_connections):
						self.g.add_edge(itemA, itemB, prices[itemB])
					elif self.vert_str[itemB] in itemA_connections:
						self.vert_str[itemA].add_neighbor(self.vert_str[itemB],prices[itemB])	# Reward is just the price for now
					if itemB!=itemA and (self.vert_str[itemA] not in self.vert_str[itemB].get_connections()):
						self.g.add_edge(itemB, itemA, prices[itemA])
					elif self.vert_str[itemA] in self.vert_str[itemB].get_connections():
						self.vert_str[itemB].add_neighbor(self.vert_str[itemA],prices[itemA])	# Reward is just the price for now
		return self.g

	def add_new_order(self, order, prices):
		for itemA in order:
			itemA_connections = self.vert_str[itemA].get_connections()
			# print("ITEM : ", itemA, " ITEM CONNECTIONS : ", itemA_connections)
				
			for itemB in order:
				if itemA!=itemB and (self.vert_str[itemB] not in itemA_connections):
					self.g.add_edge(itemA, itemB, prices[itemB])
				elif self.vert_str[itemB] in itemA_connections:
					self.vert_str[itemA].add_neighbor(self.vert_str[itemB],prices[itemB])	# Reward is just the price for now
				if itemB!=itemA and (self.vert_str[itemA] not in self.vert_str[itemB].get_connections()):
					self.g.add_edge(itemB, itemA, prices[itemA])
				elif self.vert_str[itemA] in self.vert_str[itemB].get_connections():
					self.vert_str[itemB].add_neighbor(self.vert_str[itemA],prices[itemA])	# Reward is just the price for now
				# print("vert_str : ", self.vert_str[itemB])
		return self.g

	def penalty(self, items, prod_recom, prices):
		itemA_connections = self.vert_str[prod_recom].get_connections()
		for vert_items in itemA_connections:
			if vert_items.get_id() in items:
				if self.vert_str[prod_recom] in self.vert_str[vert_items.get_id()].get_connections():
					print(self.vert_str[vert_items.get_id()], self.vert_str[prod_recom])
					self.vert_str[vert_items.get_id()].add_neighbor(self.vert_str[vert_items.get_id()],self.vert_str[vert_items.get_id()].get_weight(self.vert_str[prod_recom])-prices[prod_recom])	# Reward is just the price for now
# print("vert_str : ", self.vert_str[itemB])
		return self.g

	def save_graph(self,company_id,branch_id,items):
		fname = "./sample.csv".format(company_id,branch_id)
		with open(fname,"a+") as file_writer:
				fields=["Item1","Item2","Weights"]
				writer=csv.DictWriter(file_writer,fieldnames=fields)
				for itemA in items:
						itemA_connections = self.vert_str[itemA].get_connections()
						for vert_item in itemA_connections:
								writer.writerow({"Item1":itemA, "Item2":vert_item.get_id(),"Weights":self.vert_str[itemA].get_weight(vert_item)})


	# Order recommendation using the most weighted connection among all the items in an order
	# def order_recommend(self, order, prices):
	# 	max_weight = 0
	# 	best_reco = ""
	# 	for itemA in order:
	# 		max_weight_itemA = 0
	# 		best_reco_itemA = ""
	# 		for vert_item in self.vert_str[itemA].get_connections():
	# 			if max_weight_itemA < self.vert_str[itemA].get_weight(vert_item) and vert_item.get_id() not in order:
	# 				max_weight_itemA = self.vert_str[itemA].get_weight(vert_item)
	# 				best_reco_itemA = vert_item.get_id()
	# 		if max_weight < self.vert_str[itemA].get_weight(self.vert_str[best_reco_itemA]):
	# 			max_weight = self.vert_str[itemA].get_weight(self.vert_str[best_reco_itemA])
	# 			best_reco = best_reco_itemA
	# 	return best_reco

	# Order recommendation using the most weighted connection for combined items in an order
	def order_recommend(self, order, prices):
		max_weight = 0
		best_reco = ""
		weights = {}	# Dictionary holding all 'to' connections and their weights to all items in the order
		for itemA in order:
			itemA_connections = self.vert_str[itemA].get_connections()
			# print("ITEM: ", itemA, " connections : ", itemA_connections)			
			for vert_items in itemA_connections:
				if vert_items.get_id() not in order:
					if vert_items.get_id() not in weights:
						weights[vert_items.get_id()] = self.vert_str[itemA].get_weight(vert_items)
					else:
						weights[vert_items.get_id()] += self.vert_str[itemA].get_weight(vert_items)
			# print("WEIGHTS: ", weights)
		best_reco = max(weights.items(), key=op.itemgetter(1))[0]	# returns key with max value in weights dictionary

		return best_reco

def main():

    # Assuming this is created for a particular company and branch
    # orders = [["Sushi", "Coke", "Soy sauce", "ice cream"], ["Sushi", "Soy sauce"], ["Biriyani", "Coke"], ["Biriyani", "ice cream"], ["Hamburger", "Fries", "Coke", "Ketchup"], ["Hamburger", "Ketchup"], ["Hamburger", "Coke"]]
    # prices = {"Sushi": 12, "Coke":2, "Soy sauce":2, "ice cream":10, "Biriyani":15, "Hamburger":5, "Fries":3, "Ketchup":1}
    # items = {'1':'1202', '2':'1197', '3':'1213', '4':'1203', '5':'1212', '6':'1196', '7':'1216'}
    items = {}
    cnt=0

    orders_list, itemslist, prices = get_data()
    orders = []
    for i in itemslist:
        items[str(cnt)] = str(i)
        cnt+=1
    # print("ITEMS:", itemslist)
    # prices = {}
    # plist = list(pricelist)
    # for i in plist:
    #     prices[items[cnt]] = int(i)
    #     cnt+=1

    print("ITEMS:", items)
    print(" Prices: ", prices)
    print(items.values())
    orders_list_ = []
    # print("ORDERS LIST : ", orders_list[0])
    for i in range(len(orders_list)):
        lst = orders_list[i].split(',')
        lst_ = []
        for l in lst:
            if str(l) in items.values():
                lst_.append(l)
        # print(lst_)
        
        orders_list_.append(lst_)
    # for o in orders_list:
        # str_to_int_order=[]
        # for i in o:
            # print("i : ", i)
            # if str(i) in items.values():
            # str_to_int_order.append(int(i))
      # str_to_int_order = [i for i in o if i in items.values()]
        # orders.append(str_to_int_order)

    print("orders:", orders_list_)
    # print(orders)
    # Printing all items in the menu
    print("Please choose the item numbers from the following menu\n")
    # for item in items:
    #     print(item)
    
    UG = UpsellGraph()
    g = UG.create_graph(orders_list_,prices)	# Used to create graph for a particular company and particular branch for the first time with a lot of past orders

    i = 0

    while (i<len(orders)):#(i<1):
        # new_order = ["Hamburger", "Fries"]	# New order
        # new_order_inp = input("\nPlease enter item numbers in your order separated by space: ")	# New order
        # new_order_item_nos = new_order_inp.split(" ")
        new_order_item_nos = orders_list_[i]
        new_order = [a for a in new_order_item_nos]
        
        # print("Your order is: ",new_order)
        # new_prices = prices 	# Could be useful when there are price changes
        g = UG.add_new_order(new_order,prices)		# Updating graph with new order
        i+=1
    UG.save_graph(16, 23, items.values())
    while(1):
        # """
        new_order_inp = input("\nPlease enter item numbers in your order separated by space: ")	# New order
        new_order_item_nos = new_order_inp.split(" ")
        new_order = [items[a] for a in new_order_item_nos]
        prod_recom = UG.order_recommend(new_order,prices)	# Obtaining order recommendation

        if prod_recom!="":
        	cust_inp = input("Hi Customer! Would you like to add " + prod_recom.upper() + " to your order too? ")
        	while cust_inp=="yes":
        		new_order.append(prod_recom)
        		print("Your order is: ",new_order)
        		new_prices = prices 	# Could be useful when there are price changes
        		g = UG.add_new_order(new_order,prices)		# Updating graph with new order
        		prod_recom = UG.order_recommend(new_order,prices)	# Obtaining order recommendation
        		cust_inp = input("Hi Customer! Would you like to add " + prod_recom.upper() + " to your order too? ")
        # """
        # i+=1


if __name__ == '__main__':
	main()
