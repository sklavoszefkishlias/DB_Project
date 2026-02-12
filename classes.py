#att_array is a fixxed 7 size array that has either the values or non-values of data in this order
# 1.fname 2.lanme 3.address 4.city 5.country 6.phone 7.email
#8.suppply percetage/team 9.total_comission/balance 10.employee_id
class Person:
    def __init__(self ,att_array ):  #Caution need to see if i get the None actual value or a None text and handle it with if
        self.att_array = att_array.copy()
    

class Employee(Person):
    
    def add_to_db(self):
        query_str = f"INSERT INTO Employee (first_name,last_name, address, city, country ,phone, email, supply_percentage, total_commission) VALUES('{self.att_array[0]}' ,'{self.att_array[1]}', '{self.att_array[2]}' ,'{self.att_array[3]}','{self.att_array[4]}','{self.att_array[5]}','{self.att_array[6]}',{self.att_array[7]}, {self.att_array[8]})"
        return query_str

class Customer(Person):

    def add_to_db(self):
        query_str = f"INSERT INTO Customer (first_name, last_name, address ,city , country, phone, email, team, number_of_players, balance, employee_id) VALUES('{self.att_array[0]}' ,'{self.att_array[1]}', '{self.att_array[2]}' ,'{self.att_array[3]}','{self.att_array[4]}','{self.att_array[5]}','{self.att_array[6]}','{self.att_array[7]}', {self.att_array[8]}, {self.att_array[9]})"
        return query_str