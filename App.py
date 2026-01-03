from cx_Oracle import DatabaseError
from Config.Config_load import load_config, load_paths
from DBconnect import DBconnect
from Config.Sql_load import load_sql
from Services.Customer_Service import CustomerService
from Services.Import import Import
from Services.Reservation_Service import ReservationService
from Table_Gateways.Cash_Account import CashAccount
from Table_Gateways.Customer import Customer
from Table_Gateways.Hall import Hall
from Table_Gateways.Reservation import Reservation
from Table_Gateways.Service import Service
from UI import UI

class AppError(Exception):
    pass

class AppConfigError(Exception):
    pass

class App:
    def __init__(self, path_cfg:str="config.ini"):
        self.connection = None
        self.config_path = path_cfg
        self.sql_path = None
        self.import_cash_accounts = None
        self.import_customers = None
        self.import_halls = None
        self.import_services = None
        self.UI = UI()
        self.run()

    def run(self):
        try:
            self.load_paths()
            self.db_load_connect()
        except AppConfigError as e:
            self.shutdown_error(f"App crashed when configuring database: {str(e)}")
        except Exception as e:
            self.shutdown_error(f"App unexpectedly crashed: {str(e)}")
        self.UI.message("Welcome in halls management system")
        while True:
            try:
                self.UI.message("Choose an action and confirm it with Enter key:")
                self.UI.menu(self.actions())
                chosen_action = input(">")
                self.actions()[chosen_action]()
            except Exception as e:
                self.UI.message(e)

    def add_customer(self):
        try:
            information = self.UI.customer_form()
            customer = CustomerService(self.connection)
            message = customer.create_customer_and_account(information["name"], information["email"], information["phone"], information["customer_type"])
            self.UI.message(message)
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def increase_customers_balance(self):
        try:
            customer = Customer(self.connection)
            all_customers = customer.read_all()
            information = self.UI.change_balance_form(all_customers)
            cash_account = CashAccount(self.connection)
            cash_account.update(information["amount"], information["balance_id"], '+')
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def add_hall(self):
        try:
            information = self.UI.hall_form()
            hall = Hall(self.connection)
            message = hall.create(information["name"], information["sport_type"], information["hourly_rate"], information["capacity"])
            self.UI.message(message)
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def add_service(self):
        try:
            information = self.UI.service_form()
            service = Service(self.connection)
            message = service.create(information["name"], information["price_per_hour"], information["optional"])
            self.UI.message(message)
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def add_reservation(self):
        try:
            customers = Customer(self.connection).read_all()
            services_optional = Service(self.connection).read_optional()
            services_not_optional = Service(self.connection).read_not_optional()
            halls = Hall(self.connection).read_all()
            information = self.UI.reservation_form(customers, services_optional, halls)
            reservation_service = ReservationService(self.connection)
            reservation_service.create_reservation(information["customer_id"], information["start_dt"], information["end_dt"], information["chosen_services"], services_not_optional, information["halls"])
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def delete_reservation(self):
        try:
            reservation_service = ReservationService(self.connection)
            reservation_customer = reservation_service.read_id_name_email()
            information = self.UI.delete_reservation_form(reservation_customer)
            reservation = Reservation(self.connection)
            reservation.delete(information)
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def pay_reservation(self):
        try:
            reservation_service = ReservationService(self.connection)
            not_paid_reservations = reservation_service.read_not_paid()
            information = self.UI.payment_form(not_paid_reservations)
            accounts = CashAccount(self.connection)

            if not accounts.check_balance(information["account_id"], information["total_price"]):
                raise Exception("Insufficient funds on customer's account")

            reservation_service.pay_and_transfer(information["reservation_id"], information["account_id"], information["total_price"])
        except Exception as e:
            self.UI.message(e)
            self.UI.user_input("enter", "Press Enter to continue:")

    def view_now_available_halls(self):
        reservation_service = ReservationService(self.connection)
        available_halls = reservation_service.read_available_halls()
        self.UI.print_halls(available_halls)

    def view_reservations_detail(self):
        reservation_service = ReservationService(self.connection)
        reservations = reservation_service.read_reservation_detail()
        self.UI.print_reservations_detailed(reservations)

    def view_report(self):
        reservation_service = ReservationService(self.connection)
        data = reservation_service.report()
        self.UI.print_report(data)

    def import_data(self):
        import_class = Import(self.connection)
        import_class.import_csv("cash_account",["account_type", "balance"],self.import_cash_accounts)
        import_class.import_csv("customer",["account_id", "name", "email", "phone", "customer_type", "is_active"],self.import_customers)
        import_class.import_csv("hall",["name", "sport_type", "hourly_rate", "capacity"],self.import_halls)
        import_class.import_csv("service",["name", "price_per_hour", "is_optional"],self.import_services)

    def load_paths(self):
        try:
            paths = load_paths()
        except Exception as e:
            raise AppConfigError("Configuration error: "+ str(e))

        self.sql_path = paths["db_code"]
        self.import_cash_accounts = paths["import_account"]
        self.import_customers = paths["import_customer"]
        self.import_halls = paths["import_hall"]
        self.import_services = paths["import_service"]

    def db_load_connect(self):
        try:
            cfg = load_config(self.config_path)
        except Exception as e:
            raise AppConfigError("Configuration error: "+ str(e))

        db = DBconnect(cfg["user"], cfg["password"], cfg["dsn"], cfg["encoding"])
        self.connection = db.connect()
        try:
            load_result = load_sql(self.connection, self.sql_path)
            if type(load_result) == Exception or type(load_result) == DatabaseError:
                raise AppConfigError(str(load_result))
            else:
                self.UI.message("Database imported successfully")
        except Exception as e:
            raise AppConfigError("Error when importing database: "+ str(e))

    def actions(self):
        return {
            "0": self.shutdown,
            "1": self.add_customer,
            "2": self.increase_customers_balance,
            "3": self.add_hall,
            "4": self.add_service,
            "5": self.add_reservation,
            "6": self.delete_reservation,
            "7": self.pay_reservation,
            "8": self.view_now_available_halls,
            "9": self.view_reservations_detail,
            "10": self.import_data,
            "11": self.view_report
        }

    def shutdown(self, message="Thank you for using our service!"):
        if self.connection:
            self.connection.close()
        self.UI.message(message)
        exit(0)

    def shutdown_error(self, message):
        if self.connection:
            self.connection.close()
        self.UI.message(message)
        exit(1)