import cx_Oracle

def load_sql(connection, path="db.sql", ):
    try:
        cursor = connection.cursor()

        with open(path, "r") as f:
            sql_script = f.read()

        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if not stmt:
                continue

            try:
                cursor.execute(stmt)
            except cx_Oracle.DatabaseError as e:
                error_obj, = e.args
                if error_obj.code == 955:
                    continue
                else:
                    raise cx_Oracle.DatabaseError(e)

        connection.commit()
        cursor.close()
        return True

    except cx_Oracle.DatabaseError as e:
        return e
    except Exception as e:
        return e