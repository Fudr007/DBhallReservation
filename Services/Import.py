import csv


class Import:
    def __init__(self, connection):
        self.connection = connection

    def import_csv(self, table, columns, csv_path):
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