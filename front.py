import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE ENGINE ---
DB_FILE = 'business_pro.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Δημιουργία των 5 βασικών πινάκων (αφαιρέθηκε ο Order_Item)
    c.executescript('''
        CREATE TABLE IF NOT EXISTS Employee (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL, address TEXT NOT NULL,
            city TEXT NOT NULL, country TEXT NOT NULL, phone TEXT NOT NULL,
            email TEXT NOT NULL, supply_percentage REAL NOT NULL, total_commission REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Customer (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL, address TEXT NOT NULL,
            city TEXT NOT NULL, country TEXT NOT NULL, phone TEXT NOT NULL,
            email TEXT NOT NULL, team TEXT, number_of_players INTEGER,
            balance REAL NOT NULL, employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
        );
        CREATE TABLE IF NOT EXISTS Discount (
            discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
            discount_percent REAL NOT NULL, max_amount_kit1 INTEGER NOT NULL,
            max_amount_kit2 INTEGER NOT NULL, max_amount_kit3 INTEGER NOT NULL,
            number_of_players INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Item (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, description TEXT NOT NULL, color TEXT,
            size TEXT, category TEXT NOT NULL, kit_type INTEGER,
            price REAL NOT NULL, wholesale_cost REAL NOT NULL, stock INTEGER
        );
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL, order_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        );
    ''')
    conn.commit()
    conn.close()

def run_query(query, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn, params=params)

def execute_db(query, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        conn.cursor().execute(query, params)
        conn.commit()

# --- 2. LOGIN SYSTEM ---
st.set_page_config(page_title="Business ERP", layout="wide")
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 System Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# --- 3. MAIN APP ---
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    # Επιλογή πίνακα (Customer αντί για Customers για αποφυγή σφάλματος)
    option = st.sidebar.selectbox("Select Table", ["Employee", "Customer", "Item", "Discount", "Orders"])
    
    st.title(f"📂 {option} Management")
    data = run_query(f"SELECT * FROM {option}")

    pk_map = {
        "Employee": "employee_id", 
        "Customer": "customer_id", 
        "Item": "item_id", 
        "Discount": "discount_id", 
        "Orders": "order_id"
    }
    pk = pk_map[option]

    col1, col2, col3 = st.columns(3)

    # --- ➕ ADD SECTION ---
    with col1:
        with st.expander(f"➕ Add New {option}", expanded=True):
            with st.form(f"add_{option}", clear_on_submit=True):
                if option == "Orders":
                    cust_df = run_query("SELECT customer_id, first_name, last_name FROM Customer")
                    if not cust_df.empty:
                        c_choice = st.selectbox("Select Customer", cust_df.index, 
                                              format_func=lambda x: f"{cust_df.iloc[x]['first_name']} {cust_df.iloc[x]['last_name']}")
                        c_id = int(cust_df.iloc[c_choice]['customer_id'])
                        date = st.date_input("Order Date", value=datetime.now())
                        price = st.number_input("Total Price", min_value=0.0)
                        if st.form_submit_button("Save Order"):
                            execute_db("INSERT INTO Orders (customer_id, order_date, total_price) VALUES (?,?,?)", (c_id, str(date), price))
                            st.rerun()
                    else:
                        st.warning("Please add a Customer first.")
                        st.form_submit_button("Save", disabled=True)
                
                else:
                    # Αυτόματη δημιουργία πεδίων για τους άλλους πίνακες
                    fields = [c for c in data.columns if c != pk]
                    new_vals = {}
                    for f in fields:
                        if "percentage" in f or "price" in f or "balance" in f:
                            new_vals[f] = st.number_input(f, value=0.0)
                        elif "id" in f or "stock" in f or "number" in f or "max" in f:
                            new_vals[f] = st.number_input(f, value=0, step=1)
                        else:
                            new_vals[f] = st.text_input(f)
                    
                    if st.form_submit_button("Save"):
                        cols_sql = ", ".join(new_vals.keys())
                        placeholders = ", ".join(["?"] * len(new_vals))
                        execute_db(f"INSERT INTO {option} ({cols_sql}) VALUES ({placeholders})", tuple(new_vals.values()))
                        st.rerun()

    # --- 📝 EDIT SECTION ---
    with col2:
        if not data.empty:
            with st.expander(f"📝 Edit {option}", expanded=True):
                edit_idx = st.selectbox("Select Row Index", options=data.index, key="edit_sel")
                row = data.iloc[edit_idx]
                
                with st.form(f"edit_form_{option}"):
                    updated_values = {}
                    edit_cols = [c for c in data.columns if c != pk]
                    for c in edit_cols:
                        val = row[c]
                        if isinstance(val, (float, int)):
                            updated_values[c] = st.number_input(f"New {c}", value=val)
                        else:
                            updated_values[c] = st.text_input(f"New {c}", value=str(val) if val else "")
                    
                    if st.form_submit_button("Update"):
                        set_clause = ", ".join([f"{c}=?" for c in updated_values.keys()])
                        execute_db(f"UPDATE {option} SET {set_clause} WHERE {pk}=?", tuple(updated_values.values()) + (int(row[pk]),))
                        st.rerun()

    # ---  DELETE SECTION ---
    with col3:
        if not data.empty:
            with st.expander(f"🗑️ Delete {option}", expanded=True):
                del_idx = st.selectbox("Select Row Index", options=data.index, key="del_sel")
                id_to_del = int(data.iloc[del_idx][pk])
                if st.button("Confirm Delete", type="primary"):
                    execute_db(f"DELETE FROM {option} WHERE {pk}=?", (id_to_del,))
                    st.rerun()

    # --- TABLE VIEW & KPI ---
    st.markdown("---")
    st.subheader(f"Current {option} Records")
    st.dataframe(data, use_container_width=True)

    if option == "Orders":
        # Διόρθωση του σφάλματος NoneType (image_5c1280.png)
        total_rev = data['total_price'].sum() if not data.empty else 0.0
        st.metric("Total Revenue", f"€{total_rev:,.2f}")