import streamlit as st
import sqlite3
import pandas as pd
from db_init import get_query  


ATT_DICT = {
    "Employee" : ["employee_id", "first_name" , "last_name" , "address", "city", "country", "phone", "email", "supply_percentage", "total_commission"],
    "Customer" : ["customer_id","first_name" , "last_name" , "address", "city", "country", "phone", "email", "team", "number_of_players", "balance", "employee_id"],
    "Discount" : ["discount_id","discount_percent", "max_amount_kit1", "max_amount_kit2", "max_amount_kit3", "number_of_players"],
    "Item" :["item_id","name", "description", "color", "size", "category", "kit_type", "price", "wholesale_cost", "stock"],
    "Orders":["order_id","customer_id","order_date", "total_price"], 
    "Order_Item" : [["order_id", "item_id"],"item_amount"]
}


REPORT_MAP = {
    "Search Customer (First & Last Name)": 0,
    "Search Customer by Team": 2,
    "Search Item by Name": 3,
    "Filter Items by Price Range": 4,
    "Search Customers by City (OR)": 5,
    "Employee Commission Report": 6,
    "Highest Value Order": 7
}

KEY_ATT = list(ATT_DICT.keys())
TABLE_MAP = {name: i for i, name in enumerate(KEY_ATT)}
ACTION_MAP = {"Add": 0, "Edit": 1, "Delete": 2, "Run Report": 3}



def run_db_command(sql):
    try:
        con = sqlite3.connect('final.db')
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()
        return True, "Success"
    except Exception as e:
        return False, str(e)

def process_crud_action(data):

    if not data: return
    
    att_array, table_idx, action_idx = data
    table_name = KEY_ATT[table_idx]
    cols = ATT_DICT[table_name]
    
    sql = ""
    

    if action_idx == 0:
        if table_name == "Order_Item":

            sql = f"INSERT INTO Order_Item (order_id, item_id, item_amount) VALUES ({att_array[0][0]}, {att_array[0][1]}, {att_array[1]})"
        else:

            vals = ", ".join([str(x) for x in att_array])
            col_names = ", ".join(cols[1:])
            sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({vals})"


    elif action_idx == 1:
        if table_name == "Order_Item":
            sql = f"UPDATE Order_Item SET item_amount = {att_array[1]} WHERE order_id = {att_array[0][0]} AND item_id = {att_array[0][1]}"
        else:
            pk_val = att_array[0]
            updates = []

            for i, val in enumerate(att_array[1:], 1):
                if val != "noval":
                    updates.append(f"{cols[i]} = {val}")
            
            if not updates:
                st.warning("No changes detected.")
                return
                
            sql = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {cols[0]} = {pk_val}"


    elif action_idx == 2:
        if table_name == "Order_Item":
            sql = f"DELETE FROM Order_Item WHERE order_id = {att_array[0][0]} AND item_id = {att_array[0][1]}"
        else:
            sql = f"DELETE FROM {table_name} WHERE {cols[0]} = {att_array[0]}"

    if sql:
        success, msg = run_db_command(sql)
        if success:
            st.success(f"Operation Successful on {table_name}!")
        else:
            st.error(f"Database Error: {msg}")



def format_value_for_sql(value, is_string=True):

    if value is None or str(value).strip() == "":
        return "NULL"
    if is_string:
        return f"'{value}'"
    return value

def get_existing_ids(table_name):

    try:
        con = sqlite3.connect('final.db')
        if table_name == "Order_Item":
            df = pd.read_sql_query("SELECT order_id, item_id FROM Order_Item", con)
            ids = df.apply(lambda x: (x['order_id'], x['item_id']), axis=1).tolist()
        else:
            pk = ATT_DICT[table_name][0]
            df = pd.read_sql_query(f"SELECT {pk} FROM {table_name}", con)
            ids = df[pk].tolist()
        con.close()
        return ids
    except:
        return []



def frontend():
    st.set_page_config(page_title="DB Management System", layout="wide")
    st.sidebar.title("DB Controls")
    

    action_name = st.sidebar.selectbox("Select Action", list(ACTION_MAP.keys()))
    action_idx = ACTION_MAP[action_name]


    if action_name == "Run Report":
        st.header("Database Reports")
        report_choice = st.selectbox("Choose Report", list(REPORT_MAP.keys()))
        q_code = REPORT_MAP[report_choice]
        


        arr = [] 
        
        if q_code == 0:
            c1, c2 = st.columns(2)
            fn = c1.text_input("First Name")
            ln = c2.text_input("Last Name")
            arr = [format_value_for_sql(fn), format_value_for_sql(ln)]
            
        elif q_code in [2, 3]:
            val = st.text_input("Search Value")

            arr = [format_value_for_sql(val), "''"] 
            
        elif q_code == 4:
            c1, c2 = st.columns(2)
            min_p = c1.number_input("Min Price", 0.0)
            max_p = c2.number_input("Max Price", 1000.0)
            arr = [min_p, max_p]
            
        elif q_code == 5:
            c1, c2 = st.columns(2)
            city1 = c1.text_input("City 1")
            city2 = c2.text_input("City 2")
            arr = [format_value_for_sql(city1), format_value_for_sql(city2)]
            
        elif q_code in [6, 7]:
            arr = []

        if st.button("Run Query"):
            try:
                con = sqlite3.connect('final.db')
                sql_query = get_query(q_code, arr)
                df = pd.read_sql_query(sql_query, con)
                con.close()
                
                if df.empty:
                    st.info("No records found.")
                else:
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Query Error: {e}")
                st.write("Debug info - Array sent:", arr)
        return


    
    table_name = st.sidebar.selectbox("Select Table", KEY_ATT)
    table_idx = TABLE_MAP[table_name]
    columns = ATT_DICT[table_name]
    
    st.subheader(f"{action_name} - {table_name}")
    att_array = []


    if action_name == "Add":
        if table_name == "Order_Item":
            o_id = st.number_input("Order ID", step=1)
            i_id = st.number_input("Item ID", step=1)
            amt = st.number_input("Amount", step=1)
            if st.button("Add Record"):
                process_crud_action([[[o_id, i_id], amt], table_idx, action_idx])
        else:
            for col in columns[1:]:

                is_num = any(x in col for x in ['price','cost','balance','percent','commission','id','number','stock','amount','type'])
                if is_num:
                    val = st.number_input(col, step=1 if 'id' in col or 'stock' in col else 0.01)
                    att_array.append(val)
                else:
                    val = st.text_input(col)
                    att_array.append(format_value_for_sql(val))
            
            if st.button("Add Record"):
                process_crud_action([att_array, table_idx, action_idx])

    # EDIT
    elif action_name == "Edit":
        ids = get_existing_ids(table_name)
        if not ids:
            st.warning("No records available to edit.")
        else:
            sel_id = st.selectbox("Select ID", ids)
            
            if table_name == "Order_Item":
                new_amt = st.number_input("New Amount", step=1)
                if st.button("Update Record"):
                    process_crud_action([[[sel_id[0], sel_id[1]], new_amt], table_idx, action_idx])
            else:
                att_array.append(sel_id)
                for col in columns[1:]:
                    check = st.checkbox(f"Update {col}?", key=f"chk_{col}")
                    if check:
                        is_num = any(x in col for x in ['price','cost','balance','percent','commission','id','number','stock','amount','type'])
                        if is_num:
                            val = st.number_input(f"New {col}", step=1 if 'id' in col else 0.01)
                            att_array.append(val)
                        else:
                            val = st.text_input(f"New {col}")
                            att_array.append(format_value_for_sql(val))
                    else:
                        att_array.append("noval")
                
                if st.button("Update Record"):
                    process_crud_action([att_array, table_idx, action_idx])


    elif action_name == "Delete":
        ids = get_existing_ids(table_name)
        if not ids:
            st.warning("No records available to delete.")
        else:
            sel_id = st.selectbox("Select ID to Delete", ids)
            if st.button("Delete Record"):

                if table_name == "Order_Item":
                    payload = [[[sel_id[0], sel_id[1]]] , table_idx, action_idx]
                else:
                    payload = [[sel_id], table_idx, action_idx]
                process_crud_action(payload)

if __name__ == "__main__":
    frontend()