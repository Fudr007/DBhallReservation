import cx_Oracle

class ServiceException(Exception):
    pass

class Service:
    def __init__(self, connection):
        self.connection = connection

    def create(self, name:str, price_per_hour:float, optional:bool=True):
        is_optional = 1 if optional else 0
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Service (name, price_per_hour, is_optional) VALUES (:name, :price_per_hour, :is_optional)",
                           {
                               "name": name,
                               "price_per_hour": price_per_hour,
                               "is_optional": is_optional
                           })
            self.connection.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise ServiceException("Service database integrity error: Service with duplicate data in database")
            elif error.code == 2290:
                raise ServiceException("Service database integrity error: Invalid values")
            elif error.code == 1400:
                raise ServiceException("Service database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise ServiceException("Service database integrity error: Too large value")
            else:
                raise ServiceException(f'Service database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ServiceException(f'Service error: {e}')

    def update(self, attribute:str, value, name:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Service SET {attribute} = :value WHERE name = :name",
                           {
                               "value": value,
                               "name": name
                           })
            self.connection.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise ServiceException("Service database integrity error: Service with duplicate data in database")
            elif error.code == 2290:
                raise ServiceException("Service database integrity error: Invalid values")
            elif error.code == 1400:
                raise ServiceException("Service database integrity error: Cannot insert NULL values")
            elif error.code == 1438 or error.code == 12899:
                raise ServiceException("Service database integrity error: Too large value")
            else:
                raise ServiceException(f'Service database integrity error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ServiceException(f'Service error: {e}')

    def delete(self, name:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Service WHERE name = :name",
                           {
                               "name": name
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ServiceException(f'Service error: {e}')

    def read(self, name:str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Service WHERE name = :name",
                           {
                               'name': name
                           })
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            raise ServiceException(f'Service error: {e}')

    def read_optional(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Service WHERE is_optional = 1")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            raise ServiceException(f'Service error: {e}')

    def read_not_optional(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Service WHERE is_optional = 0")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            raise ServiceException(f'Service error: {e}')

    def read_all(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Service")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ServiceException(f'Service database error: {error_obj.message}')
        except Exception as e:
            raise ServiceException(f'Service error: {e}')