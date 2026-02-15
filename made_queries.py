import sqlite3
from db_init import get_query



def made_queries(arr, q_code):
    

    con = sqlite3.connect('final.db')
    cur = con.cursor()


    q = get_query(q_code, arr)
    for row in cur.execute(q):
        print(row)







    con.commit()
    con.close()

x= ['\'John\'', '\'Doe\'']
z = [3, 57]
y = 4
made_queries(z, y)