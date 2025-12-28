import cx_Oracle


class Customer:
    def __init__(self, db):
        self.db = db

    def create(self, name:str, email:str, phone:str, customer_type:str, active:int):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("INSERT INTO CUSTOMER (NAME, EMAIL, PHONE, CUSTOMER_TYPE, ACTIVE) "
                           "VALUES (:name, :email, :phone, :customer_type, :active)",
                           {
                               "name": name,
                                "email": email,
                                "phone": phone,
                                "customer_type": customer_type,
                                "active": active
                            })
            self.db.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db.connection.rollback()
            return f'Error: {error_obj.message}'

        except Exception as e:
            return f'Error: {e}'

    def update(self, attribute:str, value):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"UPDATE CUSTOMER SET {attribute} = :value WHERE ID = :id",
                           {
                               "value": value,
                               "id": id
                           })
            self.db.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db.connection.rollback()
            return f'Error: {error_obj.message}'

        except Exception as e:
            return f'Error: {e}'

    def delete(self, email:str):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"DELETE FROM CUSTOMER WHERE EMAIL = :email",
                           {
                               "email": email
                            })
            self.db.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db.connection.rollback()
            return f'Error: {error_obj.message}'

        except Exception as e:
            return f'Error: {e}'