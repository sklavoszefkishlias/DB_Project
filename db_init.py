FIRST_TIME = False
#set this to False before sending

# db_init.py
def get_query(index, arr):
    queries = [
        f"SELECT customer_id, first_name, last_name, email, phone FROM Customer WHERE first_name={arr[0]} AND last_name = {arr[1]}",
        f"SELECT customer_id, first_name, last_name, email, phone FROM Customer WHERE first_name={arr[0]} AND last_name = {arr[1]}",
        f"SELECT team, number_of_players FROM Customer WHERE team = {arr[0]}",
        f"SELECT name, description, category FROM Item WHERE name = {arr[0]}",
        f"SELECT item_id, price, stock FROM Item WHERE price > {arr[0]} AND price < {arr[1]}",
        f"SELECT customer_id, address, city, country FROM Customer WHERE city = {arr[0]} OR city = {arr[1]}",
        "SELECT e.employee_id, e.total_commission, COUNT(c.customer_id) AS customer_count, e.total_commission / COUNT(c.customer_id) AS average_commission FROM Employee e LEFT JOIN Customer c ON e.employee_id = c.employee_id GROUP BY e.employee_id, e.total_commission;",
        "SELECT e.*, c.* FROM Orders o JOIN Customer c ON o.customer_id = c.customer_id JOIN Employee e ON c.employee_id = e.employee_id WHERE o.total_price = (SELECT MAX(total_price) FROM Orders)"
    ]
    return queries[index]