import actions as cl
import db
import sqlite3


def generate_query(att_array, table_type, action_type):
    match action_type:
        case 0:
            return cl.add_to_db(att_array, table_type)
        case 1:
            return cl.edit_db(att_array, table_type)
        case 2:
            return cl.delete_from_db(att_array, table_type)

if __name__ == "__main__":
    
    db.generate()

    #action_inputs = fr.frontend()     #Returned values :att_array, table_type, action_type

    action_inputs = [['\'hi\'', '\'dude\'', '\'my street\'', '\'chicago\'' , '\'usa\'', '\'210-666\'', '\'scaryguygmail.com\'', 0.2, 1389],0, 0]



    query = generate_query(action_inputs[0], action_inputs[1], action_inputs[2])


    print("Before Action")
    db.check(action_inputs[1])
    
    db.execute_query(query)
    
    print("After Action")
    db.check(action_inputs[1])

