import cx_Oracle

class PaymentException(Exception):
    pass

class Payment:
    def __init__(self, connection):
        self.connection = connection

    def create(self, reservation_id:int, amount:float):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Payment (reservation_id, amount) "
                           "VALUES (:reservation_id, :amount)",
                           {
                               "reservation_id": reservation_id,
                               "amount": amount,
                            })
            self.connection.commit()
            return True
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise PaymentException(f'Payment database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise PaymentException(f'Payment error: {e}')

    def update(self, attribute:str, value, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Payment SET {attribute} = :value WHERE reservation_id = :reservation_id",
                           {
                               "value": value,
                               "reservation_id": reservation_id
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise PaymentException(f'Payment database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise PaymentException(f'Payment error: {e}')

    def delete(self, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Payment WHERE reservation_id = :reservation_id",
                           {
                               "reservation_id": reservation_id
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise PaymentException(f'Payment database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise PaymentException(f'Payment error: {e}')

    def read(self, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Payment WHERE reservation_id = :reservation_id",
                           {
                               'reservation_id': reservation_id
                           })
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise PaymentException(f'Payment database error: {error_obj.message}')
        except Exception as e:
            raise PaymentException(f'Payment error: {e}')