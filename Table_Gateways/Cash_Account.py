import cx_Oracle

class CashAccountError(Exception):
    pass

class CashAccount:
    def __init__(self, connection):
        self.connection = connection

    def create(self, balance:float=0.0, account_type:str='CUSTOMER'):
        if account_type.upper() not in ['CUSTOMER', 'SYSTEM']:
            raise CashAccountError('Invalid account type')
        if balance < 0:
            raise CashAccountError('Balance cannot be negative')

        try:
            cursor = self.connection.cursor()
            if account_type.upper() == 'SYSTEM':
                cursor.execute("SELECT id FROM account WHERE account_type = 'SYSTEM'")
                row = cursor.fetchone()
                if row is not None:
                    raise CashAccountError('System account already exists')
            account_id_var = cursor.var(cx_Oracle.NUMBER)
            cursor.execute("INSERT INTO CASH_ACCOUNT (BALANCE, ACCOUNT_TYPE) VALUES (:balance, :account_type) RETURNING id INTO :id",
                           {
                               'balance': balance,
                               'account_type': account_type.upper(),
                                'id' : account_id_var
                           })
            self.connection.commit()
            account_id = account_id_var.getvalue()[0]
            return int(account_id)
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise CashAccountError(f'Cash account error: {e}')

    def update(self, balance:float, id:int, operation:str='+'):
        try:
            cursor = self.connection.cursor()
            if operation == '+':
                sql = "UPDATE CASH_ACCOUNT SET BALANCE = BALANCE + :balance WHERE id = :id"
            elif operation == '-':
                sql = "UPDATE CASH_ACCOUNT SET BALANCE = BALANCE - :balance WHERE id = :id"
            else:
                raise ValueError("Invalid operation")

            cursor.execute(sql, {"balance": balance, "id": id})
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise CashAccountError(f'Cash account error: {e}')

    def delete(self, id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM CASH_ACCOUNT WHERE id = :id",
                           {
                               'id': id
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise CashAccountError(f'Cash account error: {e}')

    def check_balance(self, id:int, amount:float):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM cash_account WHERE id = :account_id AND balance >= :amount",
                           {
                               'account_id': id,
                               'amount': amount
                           })
            boolean = cursor.fetchone()[0]
            return boolean == 1
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            raise CashAccountError(f'Cash account error: {e}')

    def transfer_to_system_account(self, amount:float, id_from:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE CASH_ACCOUNT SET BALANCE = BALANCE - :amount WHERE id = :id",
                           {
                               'amount': amount,
                               'id': id_from
                           })
            cursor.execute("UPDATE CASH_ACCOUNT SET BALANCE = BALANCE + :amount WHERE ACCOUNT_TYPE = 'SYSTEM'",
                           {
                               'amount': amount
                           })
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.connection.rollback()
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            self.connection.rollback()
            raise CashAccountError(f'Cash account error: {e}')

    def read(self, id:int):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM CASH_ACCOUNT WHERE id = :id",
                           {
                               'id': id
                           })
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            raise CashAccountError(f'Cash account error: {e}')

    def read_all(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM CASH_ACCOUNT")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise CashAccountError(f'Cash account database error: {error_obj.message}')
        except Exception as e:
            raise CashAccountError(f'Cash account error: {e}')