import csv
import cx_Oracle

class ImportingError(Exception):
    pass

class Import:
    def __init__(self, connection):
        self.connection = connection

    def import_csv(self, table, columns, csv_path):
        try:
            cursor = self.connection.cursor()
            placeholders = ", ".join(f":{c}" for c in columns)
            cols = ", ".join(columns)

            sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute(sql, row)

            self.connection.commit()
            cursor.close()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            if error.code == 1:  # ORA-00001
                raise ImportingError("Import Error in database: Object with those values already exists")
            else:
                raise ImportingError(f'Import error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ImportingError(f'Import database error: {error_obj.message}')
        except Exception as e:
            raise ImportingError(f'Import error: {e}')
        finally:
            cursor.rollback()
            cursor.close()