import actions as cl
import db
import sqlite3
import front as fr
import streamlit as st
import db_init as di
import failsafe

def generate_query(att_array, table_type, action_type):
    match action_type:
        case 0:
            return cl.add_to_db(att_array, table_type)
        case 1:
            return cl.edit_db(att_array, table_type)
        case 2:
            return cl.delete_from_db(att_array, table_type)

def main():

    if di.FIRST_TIME == False:
        db.generate()
        di.FIRST_TIME =True

    action_inputs = fr.frontend() 


    if action_inputs:
        att_array = action_inputs[0]
        table_type = action_inputs[1]
        action_type = action_inputs[2]


        is_valid, validation_result = failsafe.validate(att_array, table_type, action_type)

        if not is_valid:
            st.error(f"Validation Error: {validation_result}")
            return
        

        query = generate_query(att_array, table_type, action_type)
        

        try:
        
            db.execute_query(query)
            

            st.success(f"Action executed successfully on {fr.KEY_ATT[table_type]}!")
            

            st.code(query, language="sql")
            

            st.write("### Current Table State:")
            con = fr.sqlite3.connect('final.db')
            df = fr.pd.read_sql_query(f"SELECT * FROM {fr.KEY_ATT[table_type]}", con)
            st.dataframe(df)
            con.close()
            
        except Exception as e:
            st.error(f"Error executing query: {e}")


if __name__ == "__main__":
    main()


