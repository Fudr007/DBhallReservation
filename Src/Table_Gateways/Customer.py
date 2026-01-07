import cx_Oracle

class CustomerError(Exception):
    pass

class Customer:
    def __init__(self, connection):
        self.connection = connection

    def create(self, id_acc:int, name:str, email:str, phone:str, customer_type:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Customer (account_id, name, email, phone, customer_type) "
                           "VALUES (:account_id, :name, :email, :phone, :customer_type)",
                           {
                               "account_id": id_acc,
                               "name": name,
                                "email": email,
                                "phone": phone,
                                "customer_type": customer_type
                            })
            self.connection.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise CustomerError("Customer database integrity error: Object with duplicate data in database")
            elif error.code == 2290:
                raise CustomerError("Customer database integrity error: Invalid values")
            elif error.code == 1400:
                raise CustomerError("Customer database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise CustomerError("Customer database integrity error: Too large value")
            else:
                raise CustomerError(f'Customer database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CustomerError(f'Customer database error: {error_obj.message}')

        except Exception as e:
            self.connection.rollback()
            raise CustomerError(f'Customer error: {e}')

    def update(self, attribute:str, value, email:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE CUSTOMER SET {attribute} = :value WHERE email = :email",
                           {
                               "value": value,
                               "email": email
                           })
            self.connection.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise CustomerError("Customer database integrity error: Object with duplicate data in database")
            elif error.code == 2290:
                raise CustomerError("Customer database integrity error: Invalid values")
            elif error.code == 1400:
                raise CustomerError("Customer database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise CustomerError("Customer database integrity error: Too large value")
            else:
                raise CustomerError(f'Customer database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CustomerError(f'Customer database error: {error_obj.message}')

        except Exception as e:
            self.connection.rollback()
            raise CustomerError(f'Customer error: {e}')

    def delete(self, email:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM CUSTOMER WHERE EMAIL = :email",
                           {
                               "email": email
                            })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CustomerError(f'Customer database error: {error_obj.message}')

        except Exception as e:
            self.connection.rollback()
            raise CustomerError(f'Customer error: {e}')

    def read(self, email:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM CUSTOMER WHERE email = :email",
                           {
                               'email': email
                           })
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise CustomerError(f'Customer database error: {error_obj.message}')
        except Exception as e:
            raise CustomerError(f'Customer error: {e}')

    def read_all(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM CUSTOMER")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise CustomerError(f'Customer database error: {error_obj.message}')
        except Exception as e:
            raise CustomerError(f'Customer error: {e}')