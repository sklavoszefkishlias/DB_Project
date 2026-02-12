import classes as cl
import sqlite3






if __name__ == "__main__":
    
    connection_obj = sqlite3.connect('geek.db')
    executor = connection_obj.cursor()

    
    arr = ['big', 'daddy', 'scary_street', 'chicago' , 'usa', '210-666', 'scaryguygmail.com', 0.2, 1389]
    p1 = cl.Employee(arr)
    query = p1.add_to_db()
    executor.execute(query)

    executor.execute("select * from employee")
    rows = executor.fetchall()

    for row in rows:
        print(row)