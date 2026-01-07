import csv
import cx_Oracle

from Src.Table_Gateways.Cash_Account import CashAccount


class ImportingError(Exception):
    pass

class Import:
    def __init__(self, connection):
        self.connection = connection

    def import_csv(self, table:str, csv_path:str):
        try:
            cursor = self.connection.cursor()

            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if not reader.fieldnames:
                    raise ImportingError("CSV file has no header")

                columns = reader.fieldnames

                if table == "customer":
                    columns = ["account_id"] + columns

                cols = ", ".join(columns)
                placeholders = ", ".join(f":{c}" for c in columns)

                sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

                for row in reader:
                    if table == "customer":
                        account = CashAccount(self.connection)
                        account_id = account.create()
                        row["account_id"] = account_id

                    cursor.execute(sql, row)

            self.connection.commit()
            cursor.close()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            self.connection.rollback()
            if error.code == 1:
                raise ImportingError("Already exists")
            else:
                raise ImportingError(f'Import error: {error.message}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise ImportingError(f'Import database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise ImportingError(f'Import error: {e}')