import mysql.connector

def InsertCustomerDetails(first_name, surname, email, phone_number):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            database="pizzabot"
        )

        mycursor = mydb.cursor()

        sql = 'INSERT INTO customers (Customer_first_name, Customer_surname, Customer_email, Customer_phone_number) VALUES (%s, %s, %s, %s)'
        val = (first_name, surname, email, phone_number)
        mycursor.execute(sql, val)
        mydb.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        try:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
        except NameError:
            # mydb is not defined
            pass

def InsertOrderDetails(pizza_flavor, pizza_size, customer):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            database="pizzabot"
        )

        mycursor = mydb.cursor()

        sql = 'INSERT INTO pizza_orders (Customer_ID, Pizza_type , Pizza_size) VALUES (%s, %s, %s)'
        val = (customer, pizza_flavor, pizza_size)
        mycursor.execute(sql, val)
        mydb.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        try:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
        except NameError:
            # mydb is not defined
            pass

def FindCustomer(phone_number):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            database="pizzabot"
        )

        mycursor = mydb.cursor()

        sql = 'SELECT CustomerID FROM customers WHERE VALUE LIKE Customer_phone_number = %s'
        mycursor.execute(sql, (phone_number,))
        result = mycursor.fetchone()

        return result

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        try:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
        except NameError:
            # mydb is not defined
            pass

   