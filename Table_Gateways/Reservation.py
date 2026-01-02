from datetime import datetime
import cx_Oracle

class ReservationException(Exception):
    pass

class Reservation:
    def __init__(self, connection):
        self.connection = connection

    def create(self, customer_id:int, start_time:datetime, end_time:datetime, total_price:float=0, status:str="CREATED"):
        if start_time >= end_time:
            raise ReservationException("Start time must be before end time")
        if total_price <= 0:
            raise ReservationException(f"Invalid total price: {total_price}")


        try:
            cursor = self.connection.cursor()
            new_id = cursor.var(cx_Oracle.NUMBER)
            cursor.execute("INSERT INTO Reservation (customer_id, start_time, end_time, total_price, status) "
                           "VALUES (:customer_id, :start_time, :end_time, :total_price, :status) "
                           "RETURNING id INTO :new_id",
                           {
                               "customer_id": customer_id,
                               "start_time": start_time,
                               "end_time": end_time,
                               "total_price": total_price,
                               "status": status,
                               "new_id": new_id
                           }
            )
            self.connection.commit()
            reservation_id = int(new_id.getvalue()[0])
            return reservation_id
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ReservationException(f'Reservation error: {e}')

    def update(self, attribute:str, value, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Reservation SET {attribute} = :value WHERE reservation_id = :reservation_id",
                           {
                               "value": value,
                               "reservation_id": reservation_id
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ReservationException(f'Reservation error: {e}')

    def delete(self, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Reservation WHERE reservation_id = :reservation_id",
                           {
                               "reservation_id": reservation_id
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ReservationException(f'Reservation error: {e}')

    def read(self, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Reservation WHERE reservation_id = :reservation_id",
                           {
                               'reservation_id': reservation_id
                           })
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            raise ReservationException(f'Reservation error: {e}')

    def read_all(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Reservation")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            raise ReservationException(f'Reservation error: {e}')