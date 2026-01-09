import cx_Oracle


class ReservationServiceException(Exception):
    pass

class ServiceReservation:
    def __init__(self, connection):
        self.connection = connection

    def create(self, reservation_id:int, service_id:int, hours:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Reservation_Service (reservation_id, service_id, hours) "
                           "VALUES (:reservation_id, :service_id, :hours)",
                           {
                               "reservation_id": reservation_id,
                               "service_id": service_id,
                               "hours": hours
                            })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ReservationServiceException(f'Service reservation database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ReservationServiceException(f'Service reservation error: {e}')

    def update(self, reservation_id:int, service_id:int, hours:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Reservation_Service SET hours = :hours WHERE reservation_id = :reservation_id AND service_id = :service_id",
                           {
                               "reservation_id": reservation_id,
                               "service_id": service_id,
                               "hours": hours
                            })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ReservationServiceException(f'Service reservation database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ReservationServiceException(f'Service reservation error: {e}')

    def delete(self, reservation_id:int, service_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Reservation_Service WHERE reservation_id = :reservation_id AND service_id = :service_id",
                           {
                               "reservation_id": reservation_id,
                               "service_id": service_id
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ReservationServiceException(f'Service reservation database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ReservationServiceException(f'Service reservation error: {e}')

    def read(self, reservation_id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Reservation_Service WHERE reservation_id = :reservation_id",
                           {
                               'reservation_id': reservation_id
                           })
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Service reservation database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Service reservation error: {e}')

    def read_all(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Reservation_Service")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Service reservation database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Service reservation error: {e}')