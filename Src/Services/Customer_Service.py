import cx_Oracle

from Src.Table_Gateways.Cash_Account import CashAccount, CashAccountError
from Src.Table_Gateways.Customer import Customer, CustomerError


class CustomerServiceException(Exception):
    pass

class CustomerService:
    def __init__(self, db):
        self.db = db

    def create_customer_and_account(self, name:str, email:str, phone:str, customer_type:str):
        try:
            account = CashAccount(self.db)
            acc_id = account.create()
            customer = Customer(self.db)
            customer.create(acc_id, name, email, phone, customer_type)
        except CustomerError as e:
            raise CustomerServiceException(f'{e}')
        except CashAccountError as e:
            raise CustomerServiceException(f'{e}')
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise CustomerServiceException(f'Error in database while creating customer and his account: {error_obj.message}')
        except Exception as e:
            raise CustomerServiceException(f'Unexpected error while creating customer and his account:{e}')