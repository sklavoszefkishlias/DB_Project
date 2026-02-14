import actions as cl
import db
import sqlite3
import front as fr
import streamlit as st
import db_init as di


def generate_query(att_array, table_type, action_type):
    match action_type:
        case 0:
            return cl.add_to_db(att_array, table_type)
        case 1:
            return cl.edit_db(att_array, table_type)
        case 2:
            return cl.delete_from_db(att_array, table_type)

def main():
    # 1. Initialize Database ONLY ONCE to avoid wiping data on every click
    if di.FIRST_TIME == False:
        db.generate()
        di.FIRST_TIME =True
    # 2. Render the Frontend
    # This captures the return value from your frontend() function
    action_inputs = fr.frontend() 

    # 3. Execute Logic only if input is received
    # action_inputs format: [att_array, table_type, action_type]
    if action_inputs:
        att_array = action_inputs[0]
        table_type = action_inputs[1]
        action_type = action_inputs[2]

        # Generate the SQL query string
        query = generate_query(att_array, table_type, action_type)
        
        # specific fix for actions.py syntax if needed, 
        # otherwise pass directly to execute
        try:
            # Execute
            db.execute_query(query)
            
            # success message
            st.success(f"Action executed successfully on {fr.KEY_ATT[table_type]}!")
            
            # Show the SQL that was run (for debugging)
            st.code(query, language="sql")
            
            # Optional: Show new table state immediately
            st.write("### Current Table State:")
            con = fr.sqlite3.connect('final.db')
            df = fr.pd.read_sql_query(f"SELECT * FROM {fr.KEY_ATT[table_type]}", con)
            st.dataframe(df)
            con.close()
            
        except Exception as e:
            st.error(f"Error executing query: {e}")


if __name__ == "__main__":
    main()


