import cx_Oracle

class PaymentException(Exception):
    pass

class Payment:
    def __init__(self, connection):
        self.connection = connection

    def create(self, reservation_id:int, amount:float):
        try:
            cursor = self.connection.cursor()
            payment_id_var = cursor.var(cx_Oracle.NUMBER)
            cursor.execute("INSERT INTO Payment (reservation_id, amount) VALUES (:reservation_id, :amount) RETURNING id INTO :id",
                           {
                               "reservation_id": reservation_id,
                               "amount": amount,
                               'id': payment_id_var
                            })
            self.connection.commit()
            return int(payment_id_var.getvalue()[0])
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise PaymentException("Payment database integrity error: Payment with duplicate data in database")
            elif error.code == 2290:
                raise PaymentException("Payment database integrity error: Invalid values")
            elif error.code == 1400:
                raise PaymentException("Payment database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise PaymentException("Payment database integrity error: Too large value")
            else:
                raise PaymentException(f'Payment database integrity error: {error.message}')
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
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise PaymentException("Payment database integrity error: Payment with duplicate data in database")
            elif error.code == 2290:
                raise PaymentException("Payment database integrity error: Invalid values")
            elif error.code == 1400:
                raise PaymentException("Payment database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise PaymentException("Payment database integrity error: Too large value")
            else:
                raise PaymentException(f'Payment database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise PaymentException(f'Payment database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise PaymentException(f'Payment error: {e}')

    def delete(self, id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Payment WHERE id = :id",
                           {
                               "id": id
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