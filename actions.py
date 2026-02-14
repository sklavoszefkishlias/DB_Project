
ATT_DICT = {
    "Employee" : ["employee_id", "first_name" , "last_name" , "address", "city", "country", "phone", "email", "supply_percentage", "total_commission"],
    "Customer" : ["customer_id","first_name" , "last_name" , "address", "city", "country", "phone", "email", "team", "number_of_players", "balance", "employee_id"],
    "Discount" : ["discount_id","discount_percent", "max_amount_kit1", "max_amount_kit2", "max_amount_kit3", "number_of_players"],
    "Item" :["item_id","name", "description", "color", "size", "category", "kit_type", "price", "wholesale_cost", "stock"],
    "Orders":["order_id","customer_id","order_date", "total_price"], #note that this will need some tuning to calculate the cost of the order and connect it to customer.balance employee.comission and commsiion rate and discounts
    "Order_Item" : [["order_id", "item_id"],"item_amount"]
}
KEY_ATT= list(ATT_DICT.keys())


def edit_db(att_array, table_type):  
    table = KEY_ATT[table_type]
    query_str = f"UPDATE {table} SET "
    for x in range(1, len(att_array)):
        if att_array[x] != "noval":
            query_str = query_str + f"{ATT_DICT[table][x]} = {att_array[x]}, "
    query_str = query_str[:len(query_str)-2]
    if table == "Order_Item":
        query_str = query_str + f" WHERE {ATT_DICT[table][0][0]} = {att_array[0][0]} AND {ATT_DICT[table][0][1]} = {att_array[0][1]}" #Very iffy must test it when i get to that table in classes
    else:
        query_str = query_str + f" WHERE {ATT_DICT[table][0]} = {att_array[0]}"
    return query_str



def add_to_db(att_array, table_type):
    table = KEY_ATT[table_type]
    query_str = ""
    if table == "Order_Item":
        query_str = f"INSERT INTO {table}(order_id , item_id ,item_amount) VALUES ({att_array[0][0]}, {att_array[0][1]}, {att_array[1]})"
    else:
        query_str = f"INSERT INTO {table}("
        for x in range(1, len(att_array)+1):
            query_str = query_str + f"{ATT_DICT[table][x]}, "
        query_str = query_str[:len(query_str)-2]
        query_str = query_str + ") VALUES("
        for x in range(0, len(att_array)):
            query_str = query_str + f"{att_array[x]}, "
        query_str = query_str[:len(query_str)-2]
        query_str = query_str + ")"
    return query_str

def delete_from_db(att_array, table_type):
    table = KEY_ATT[table_type]
    if table == "Order_Item":
        query_str = f"DELETE FROM {table} WHERE {ATT_DICT[table][0][0]} = {att_array[0][0]} AND {ATT_DICT[table][0][1]} = {att_array[0][1]}"
    else:
        query_str = f"DELETE FROM {table} WHERE {ATT_DICT[table][0]} = {att_array[0]}"
    return query_str

'''
Delete constraints:
You cant delete a Customer.
Deleting an order or an item deletes on cascade any record of Order_Item with the deleted record's IDs

'''
