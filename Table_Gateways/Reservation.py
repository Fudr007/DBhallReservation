from datetime import datetime
import cx_Oracle

class ReservationException(Exception):
    pass

class Reservation:
    def __init__(self, db):
        self.db = db

    def create(self, customer_id:int, start_time:datetime, end_time:datetime, total_price:float=0, status:str="CREATED" ):
        if start_time >= end_time:
            raise ReservationException("Start time must be before end time")
        if total_price <= 0:
            raise ReservationException(f"Invalid total price: {total_price}")
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("INSERT INTO Reservation (customer_id, start_time, end_time, total_price, status) "
                           "VALUES (:customer_id, :start_time, :end_time, :total_price, :status)",
                           {
                               "customer_id": customer_id,
                               "start_time": start_time,
                               "end_time": end_time,
                               "total_price": total_price,
                               "status": status
                           }
            )
            self.db.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db.connection.rollback()
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            self.db.connection.rollback()
            raise ReservationException(f'Reservation error: {e}')

    def update(self, attribute:str, value, reservation_id:int):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"UPDATE Reservation SET {attribute} = :value WHERE reservation_id = :reservation_id",
                           {
                               "value": value,
                               "reservation_id": reservation_id
                           })
            self.db.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db.connection.rollback()
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            self.db.connection.rollback()
            raise ReservationException(f'Reservation error: {e}')

    def delete(self, reservation_id:int):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"DELETE FROM Reservation WHERE reservation_id = :reservation_id",
                           {
                               "reservation_id": reservation_id
                           })
            self.db.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db.connection.rollback()
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            self.db.connection.rollback()
            raise ReservationException(f'Reservation error: {e}')

    def read(self, reservation_id:int):
        try:
            cursor = self.db.connection.cursor()
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
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM Reservation")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationException(f'Reservation database error: {error_obj.message}')
        except Exception as e:
            raise ReservationException(f'Reservation error: {e}')