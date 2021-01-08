
"""
Created on Wed Jul  1 16:32:16 2020

@author: dbolja
"""

import flask
# import rec_update
import rec_update1
import time_block
import sqltable_creator
import rec
from flask import request, jsonify
import os
app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route("/api/initialize", methods=['POST'])
def initialize():
    data = request.get_json()
    companyID = int(data['companyID'])
    branchID = int(data['branchID'])
    # try:
    fname = "graph_company_{}_branch_{}_edges.csv".format(companyID,branchID)
    if os.path.exists(fname):
        return "Table already initialized"
        # sqltable_creator.create_sql_table(companyID, branchID)
    sqltable_creator.create_csv_file(companyID, branchID)
    # except:
        
    return "Table created"

@app.route("/api/UpsellRec", methods=['GET'])
def upsell():
    
    companyID = int(request.args.get('companyID'))
    branchID = int(request.args.get('branchID'))
    
    temp = request.args.get('itemIDs').split(",")
    
    id_list = []
    for num in temp:
        id_list.append(num)
        
    # result = rec_update.rec(id_list, companyID, branchID)
    result = rec_update1.rec(id_list, companyID, branchID)

    return jsonify(result)

@app.route("/api/RecordRec", methods=['POST'])
def record():
    
    data = request.get_json()
    
    companyID = data['companyID']
    branchID = data['branchID']
        
    id_list = data['itemIDs']
        
    rec_id = data['recID']
    choice = int(data['accepted'])
    
    try:
        # rec_update.update(companyID, branchID, id_list, rec_id, choice)
        rec_update1.update(companyID, branchID, id_list, rec_id, choice)
    except ValueError: 
        return "Item ID is not in menu or invalid data type (expects string)"
    
    if choice == 1:
        return "Recommendation added"
    # elif choice == 73738:
    #     return "Reset successful"
    else:
        return "Recommendation not added to q-table"

@app.route('/api/menuorder', methods=['GET'])
def sort_by_time():
    branchid = int(request.args.get('branchid'))
    time_interval = int(request.args.get('time_interval'))
    
    result = time_block.popular_by_time(branchid, time_interval)
    
    return jsonify(result)

@app.route('/api/test', methods = ['GET'])
def test():
    result = str(request.args.get('res'))
    return jsonify(result)


#@app.route("/api/StatRec", methods=['GET'])
#def StatRec():
#    order = str(request.args.get('order'))
#    companyID = str(request.args.get('companyID'))
#    branchID = str(request.args.get('branchID'))
    
#    result = rec.main(order, companyID, branchID)

#    return jsonify(result)

@app.errorhandler(404) 
def not_found(e): 
  return "404 Not Found"


if __name__ == "__main__":
    app.run() 