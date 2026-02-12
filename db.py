import sqlite3

connection_obj = sqlite3.connect('geek.db')

cursor_obj = connection_obj.cursor()

cursor_obj.execute("DROP TABLE IF EXISTS GEEK")


cursor_obj.executescript("""
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Order_Item;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Item;
DROP TABLE IF EXISTS Discount;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Employee;


CREATE TABLE Employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    supply_percentage REAL NOT NULL,
    total_commission REAL NOT NULL
);


CREATE TABLE Customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    team TEXT,
    number_of_players INTEGER,
    balance REAL NOT NULL,
    employee_id INTEGER,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);


CREATE TABLE Discount (
    discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
    discount_percent REAL NOT NULL,
    max_amount_kit1 INTEGER NOT NULL,
    max_amount_kit2 INTEGER NOT NULL,
    max_amount_kit3 INTEGER NOT NULL,
    number_of_players INTEGER NOT NULL
);

CREATE TABLE Item (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    color TEXT,
    size TEXT,
    category TEXT NOT NULL,
    kit_type INTEGER,
    price REAL NOT NULL,
    wholesale_cost REAL NOT NULL,
    stock INTEGER
);


CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,  -- SQLite stores DATE as TEXT
    total_price REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE Order_Item (
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_amount INTEGER NOT NULL,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);


INSERT INTO Employee (first_name,last_name, address, city, country ,phone, email, supply_percentage, total_commission) VALUES
('George' ,'Morgan', 'Skra 36' ,'Athens','Greece','6900000001', 'gpap@email.com', 10.00, 52.00),
('John', 'White', 'Agias Sofias 3','Thesaloniki', 'Greece','6900000002', 'mkon@email.com', 12.00, 1343.00),
('Tony','Bateman', 'Basiliou 60' ,'Heraklion', 'Greece' ,'6900000003', 'nant@email.com', 8.00, 3000.00);


INSERT INTO Customer (first_name, last_name, address ,city , country, phone, email, team, number_of_players, balance, employee_id) VALUES
('John' ,'Doe' , '896 Chester Road' ,'Starford','UK', '6911111111', 'kdim@email.com', NULL, NULL, 120.00, 1),
('Jane', 'Doe' , '165 North Road','Liverpool', 'UK' ,'6922222222', 'wolves@email.com', 'Wolves', 12, 850.00, 2),
('Jimmy', 'Smith' , 'Vouliagmenhs 76' ,'Athens', 'Greece' ,'6933333333', 'panthers@email.com', 'Panthers', 24, 950.00, 3);


INSERT INTO Discount (discount_percent, max_amount_kit1, max_amount_kit2, max_amount_kit3, number_of_players) VALUES
(10.00, 50, 20, 10, 10),
(15.00, 100, 40, 20, 20),
(20.00, 200, 60, 30, 30);


INSERT INTO Item (name, description, color, size, category, kit_type ,price, wholesale_cost, stock) VALUES
('Μπάλα Μπάσκετ', 'Επαγγελματική μπάλα αγώνα', NULL, NULL, 'equipment', 1, 18.00, 11.00, 40),
('Φανέλα Μπάσκετ', 'Εμφάνιση ομάδας αγώνα', 'Κόκκινο', 'M', 'clothing', 2 ,22.00, 13.00, 35),
('Σορτσάκι Μπάσκετ', 'Αγωνιστικό σορτσάκι', 'Μαύρο', 'L', 'clothing', 2, 16.00, 9.00, 30),
('Τσαντα Γυμναστηριου', 'Ανθεκτικη τσαντα για εξοπλισμο', 'Μπλε', 'L', 'etc', 3 ,35.00, 22.00, 15),
('Μπασκέτα', 'Επαγγελματική μπασκέτα αγώνα', NULL, NULL, 'equipment', NULL ,180.00, 120.00, 5),
('Κορδόνια', 'Κορδόνια για παπούτσια', 'Άσπρο', NULL, 'clothing', 2 ,12.00, 8.00, 67);


INSERT INTO Orders (customer_id, order_date, total_price) VALUES
(1, '2025-01-10', 52.00),
(2, '2025-01-12', 1343.00),
(3, '2025-01-15', 3000.00);


INSERT INTO Order_Item (order_id, item_id, item_amount) VALUES
(1, 1, 2),
(1, 3, 1),
(2, 2, 40),
(2, 4, 20),
(3, 5, 1),
(3, 1, 200);
""")

cursor_obj.execute("SELECT * FROM Employee")

rows = cursor_obj.fetchall()

for row in rows:
    print(row)



# Execute the table creation query

# Confirm that the table has been created
print("Table is Ready")





# Close the connection to the database
connection_obj.close()