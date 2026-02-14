import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURATION FROM ACTIONS.PY ---
ATT_DICT = {
    "Employee" : ["employee_id", "first_name" , "last_name" , "address", "city", "country", "phone", "email", "supply_percentage", "total_commission"],
    "Customer" : ["customer_id","first_name" , "last_name" , "address", "city", "country", "phone", "email", "team", "number_of_players", "balance", "employee_id"],
    "Discount" : ["discount_id","discount_percent", "max_amount_kit1", "max_amount_kit2", "max_amount_kit3", "number_of_players"],
    "Item" :["item_id","name", "description", "color", "size", "category", "kit_type", "price", "wholesale_cost", "stock"],
    "Orders":["order_id","customer_id","order_date", "total_price"], 
    "Order_Item" : [["order_id", "item_id"],"item_amount"]
}

KEY_ATT = list(ATT_DICT.keys())

# Map string names to the integer indices used in actions.py
TABLE_MAP = {name: i for i, name in enumerate(KEY_ATT)}

ACTION_MAP = {
    "Add": 0,
    "Edit": 1,
    "Delete": 2
}

def format_value_for_sql(value, is_string=True):
    """
    Helper to format values because actions.py uses raw string concatenation.
    Strings must be wrapped in quotes: 'value'
    Numbers should remain as is.
    """
    if value is None or value == "":
        return "NULL"
    if is_string:
        return f"'{value}'"
    return value

def get_existing_ids(table_name):
    """Helper to fetch IDs for Dropdowns in Edit/Delete to make UI usable"""
    try:
        con = sqlite3.connect('final.db')
        # Handle composite key for Order_Item
        if table_name == "Order_Item":
            query = "SELECT order_id, item_id FROM Order_Item"
            df = pd.read_sql_query(query, con)
            # Create a tuple representation for the dropdown
            ids = df.apply(lambda x: (x['order_id'], x['item_id']), axis=1).tolist()
        else:
            pk = ATT_DICT[table_name][0]
            query = f"SELECT {pk} FROM {table_name}"
            df = pd.read_sql_query(query, con)
            ids = df[pk].tolist()
        con.close()
        return ids
    except:
        return []

def frontend():
    st.set_page_config(page_title="DB Actions", layout="centered")
    st.title("Database Action Input")

    # 1. Select Table
    table_name = st.selectbox("Select Table", KEY_ATT)
    table_idx = TABLE_MAP[table_name]
    columns = ATT_DICT[table_name]

    # 2. Select Action
    action_name = st.selectbox("Select Action", list(ACTION_MAP.keys()))
    action_idx = ACTION_MAP[action_name]

    st.divider()

    att_array = []
    
    # --- ADD FUNCTIONALITY ---
    if action_name == "Add":
        st.subheader(f"Add new {table_name}")
        
        if table_name == "Order_Item":
            # Order_Item has a weird structure in actions.py: [["order_id", "item_id"],"item_amount"]
            # But add_to_db expects: att_array[0][0], att_array[0][1], att_array[1]
            o_id = st.number_input("Order ID", step=1)
            i_id = st.number_input("Item ID", step=1)
            amt = st.number_input("Item Amount", step=1)
            
            if st.button("Generate Input"):
                # Structure specific to actions.py add_to_db logic for Order_Item
                att_array = [[o_id, i_id], amt]
                return [att_array, table_idx, action_idx]
                
        else:
            # Standard Tables
            # Skip index 0 (Primary Key is Auto Increment)
            for col in columns[1:]:
                # Check data types roughly by name to decide if we need quotes
                is_text = any(x in col for x in ['name', 'date', 'desc', 'color', 'size', 'city', 'country', 'phone', 'email', 'team', 'address'])
                
                if 'price' in col or 'cost' in col or 'balance' in col or 'percent' in col or 'commission' in col:
                    val = st.number_input(col, step=0.01)
                    att_array.append(val)
                elif 'id' in col or 'number' in col or 'stock' in col or 'amount' in col or 'type' in col:
                    val = st.number_input(col, step=1)
                    att_array.append(val)
                else:
                    val = st.text_input(col)
                    # For actions.py, strings MUST be quoted
                    att_array.append(format_value_for_sql(val, is_string=True))
            
            if st.button("Generate Input"):
                return [att_array, table_idx, action_idx]

    # --- EDIT FUNCTIONALITY ---
    elif action_name == "Edit":
        st.subheader(f"Edit {table_name}")
        existing_ids = get_existing_ids(table_name)
        
        if not existing_ids:
            st.error("No records found to edit.")
            return None

        if table_name == "Order_Item":
            # Special Composite Key Handling
            selected_id = st.selectbox("Select (Order ID, Item ID)", existing_ids)
            st.info("Order_Item updates require a very specific nested ID structure.")
            
            # actions.py edit_db logic for Order_Item checks att_array[0][0] and [0][1]
            # Then iterates the rest.
            new_amount = st.number_input("New Amount (or leave same)", step=1)
            
            if st.button("Generate Input"):
                # Nested ID list as first element, then values
                att_array = [[selected_id[0], selected_id[1]], new_amount]
                return [att_array, table_idx, action_idx]
        else:
            selected_id = st.selectbox(f"Select {columns[0]} to Edit", existing_ids)
            att_array.append(selected_id) # ID is always first in att_array for Edit
            
            # Loop through rest of columns
            for col in columns[1:]:
                is_text = any(x in col for x in ['name', 'date', 'desc', 'color', 'size', 'city', 'country', 'phone', 'email', 'team', 'address'])
                
                # actions.py supports "noval" to skip updates. 
                # We will default to "noval" and only change if user enters data.
                check = st.checkbox(f"Update {col}?", key=f"chk_{col}")
                
                if check:
                    if 'price' in col or 'cost' in col or 'balance' in col or 'percent' in col or 'commission' in col:
                        val = st.number_input(f"New {col}", step=0.01)
                        att_array.append(val)
                    elif 'id' in col or 'number' in col or 'stock' in col or 'amount' in col or 'type' in col:
                        val = st.number_input(f"New {col}", step=1)
                        att_array.append(val)
                    else:
                        val = st.text_input(f"New {col}")
                        att_array.append(format_value_for_sql(val, is_string=True))
                else:
                    att_array.append("noval")

            if st.button("Generate Input"):
                return [att_array, table_idx, action_idx]

    # --- DELETE FUNCTIONALITY ---
    elif action_name == "Delete":
        st.subheader(f"Delete from {table_name}")
        existing_ids = get_existing_ids(table_name)
        
        if not existing_ids:
            st.error("No records found to delete.")
            return None

        if table_name == "Order_Item":
            selected_id = st.selectbox("Select (Order ID, Item ID) to Delete", existing_ids)
            if st.button("Generate Input"):
                # actions.py expects [[order_id, item_id]] for delete on this table
                return [[[selected_id[0], selected_id[1]]], table_idx, action_idx]
        else:
            selected_id = st.selectbox(f"Select {columns[0]} to Delete", existing_ids)
            
            if st.button("Generate Input"):
                # actions.py expects [id]
                return [[selected_id], table_idx, action_idx]

    return None

