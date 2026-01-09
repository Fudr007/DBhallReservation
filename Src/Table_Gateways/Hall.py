from datetime import datetime

import cx_Oracle

class HallError(Exception):
    pass

class Hall:
    def __init__(self, connection):
        self.connection = connection

    def create(self, name:str, sport_type:str, hourly_rate:float, capacity:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Hall (name, sport_type, hourly_rate, capacity) "
                           "VALUES (:name, :sport_type, :hourly_rate, :capacity)",
                           {
                               "name": name,
                               "sport_type": sport_type,
                               "hourly_rate": hourly_rate,
                               "capacity": capacity
                            })
            self.connection.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise HallError("Hall database integrity error: Hall with duplicate data in database")
            elif error.code == 2290:
                raise HallError("Hall database integrity error: Invalid values")
            elif error.code == 1400:
                raise HallError("Hall database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise HallError("Hall database integrity error: Too large value")
            else:
                raise HallError(f'Hall database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise HallError(f'Hall database error: {error_obj.message}')

        except Exception as e:
            self.connection.rollback()
            raise HallError(f'Hall error: {e}')

    def update(self, attribute:str, value, name):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Hall SET {attribute} = :value WHERE name = :name",
                           {
                               "value": value,
                               "name": name
                           })
            self.connection.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise HallError("Hall database integrity error: Hall with duplicate data in database")
            elif error.code == 2290:
                raise HallError("Hall database integrity error: Invalid values")
            elif error.code == 1400:
                raise HallError("Hall database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise HallError("Hall database integrity error: Too large value")
            else:
                raise HallError(f'Hall database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise HallError(f'Hall database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise HallError(f'Hall error: {e}')

    def delete(self, name:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Hall WHERE name = :name",
                           {
                               "name": name
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise HallError(f'Hall database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise HallError(f'Hall error: {e}')

    def read(self, name:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Hall WHERE name = :name",
                           {
                               'name': name
                           })
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise HallError(f'Hall database error: {error_obj.message}')
        except Exception as e:
            raise HallError(f'Hall error: {e}')

    def read_available_in_date(self, time_from:datetime, tim_to:datetime):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT h.id, h.name FROM hall h WHERE NOT EXISTS("
                           "SELECT 1 FROM reservation r JOIN reservation_hall rh ON rh.reservation_id = r.id "
                           "WHERE rh.hall_id = h.id AND r.status <> 'CANCELLED' AND :start_time < r.end_time AND :end_time > r.start_time)",
            {
                ":start_time": time_from,
                ":end_time": tim_to
            })
            rows = cursor.fetchall()
            result = {r[0]: r[1] for r in rows}
            return result
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise HallError(f'Hall database error: {error_obj.message}')
        except Exception as e:
            raise HallError(f'Hall error: {e}')

    def read_all(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Hall")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise HallError(f'Hall database error: {error_obj.message}')
        except Exception as e:
            raise HallError(f'Hall error: {e}')