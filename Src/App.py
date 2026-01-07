from cx_Oracle import DatabaseError
from Src.Config.Config_load import load_config, load_paths
from Src.DBconnect import DBconnect
from Src.Config.Sql_load import load_sql
from Src.Services.Customer_Service import CustomerService
from Src.Services.Import import Import, ImportingError
from Src.Services.Reservation_Service import ReservationService
from Src.Table_Gateways.Cash_Account import CashAccount
from Src.Table_Gateways.Customer import Customer
from Src.Table_Gateways.Hall import Hall
from Src.Table_Gateways.Reservation import Reservation
from Src.Table_Gateways.Service import Service
from Src.UI import UI

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
        self._is_running = False
        self.run()

    def run(self):
        self._is_running = True
        try:
            self.load_paths()
            self.db_load_connect()
        except AppConfigError as e:
            self.shutdown(f"App crashed when configuring database: {str(e)}")
        except Exception as e:
            self.shutdown(f"App unexpectedly crashed: {str(e)}")

        while self._is_running:
            self.UI.print_line()
            self.UI.message("Welcome in halls management system")
            try:
                self.UI.message("Choose an action and confirm it with Enter key")
                self.UI.menu(self.actions())
                chosen_action = self.UI.user_input("str", "Choose action number: ")
                if chosen_action not in self.actions():
                    raise AppError("Invalid action number")
                self.actions()[chosen_action]()
            except Exception as e:
                self.UI.message(e)
            finally:
                self.UI.user_input("enter", "Press Enter to continue:")
                self.UI.clear_console()

    def add_customer(self):
        try:
            information = self.UI.customer_form()
            customer = CustomerService(self.connection)
            customer.create_customer_and_account(information["name"], information["email"], information["phone"], information["customer_type"])
            self.UI.message("Customer created successfully")
            self.block_import = True
        except Exception as e:
            self.UI.message(e)

    def increase_customers_balance(self):
        try:
            customer = Customer(self.connection)
            all_customers = customer.read_all()
            information = self.UI.change_balance_form(all_customers)
            cash_account = CashAccount(self.connection)
            cash_account.update(information["amount"], information["balance_id"], '+')
            self.UI.message("Balance increased successfully")
        except Exception as e:
            self.UI.message(e)

    def add_hall(self):
        try:
            information = self.UI.hall_form()
            hall = Hall(self.connection)
            hall.create(information["name"], information["sport_type"], information["hourly_rate"], information["capacity"])
            self.UI.message("Hall created successfully")
        except Exception as e:
            self.UI.message(e)

    def add_service(self):
        try:
            information = self.UI.service_form()
            service = Service(self.connection)
            service.create(information["name"], information["price_per_hour"], information["optional"])
            self.UI.message("Service created successfully")
        except Exception as e:
            self.UI.message(e)

    def add_reservation(self):
        try:
            customers = Customer(self.connection).read_all()
            services_optional = Service(self.connection).read_optional()
            services_not_optional = Service(self.connection).read_not_optional()
            halls = Hall(self.connection).read_all()
            information = self.UI.reservation_form(customers, services_optional, halls)
            reservation_service = ReservationService(self.connection)
            reservation_service.create_reservation(information["customer_id"], information["start_dt"], information["end_dt"], information["chosen_services"], services_not_optional, information["halls"])
            self.UI.message("Reservation created successfully")
        except Exception as e:
            self.UI.message(e)

    def delete_reservation(self):
        try:
            reservation_service = ReservationService(self.connection)
            reservation_customer = reservation_service.read_id_name_email()
            information = self.UI.delete_reservation_form(reservation_customer)
            reservation = Reservation(self.connection)
            reservation.delete(information)
            self.UI.message("Reservation deleted successfully")
        except Exception as e:
            self.UI.message(e)

    def pay_reservation(self):
        try:
            reservation_service = ReservationService(self.connection)
            not_paid_reservations = reservation_service.read_not_paid()
            information = self.UI.payment_form(not_paid_reservations)
            accounts = CashAccount(self.connection)

            if not accounts.check_balance(information["account_id"], information["total_price"]):
                raise Exception("Insufficient funds on customer's account")

            reservation_service.pay_and_transfer(information["reservation_id"], information["account_id"], information["total_price"])
            self.UI.message("Reservation paid successfully")
        except Exception as e:
            self.UI.message(e)

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
        try:
            import_class = Import(self.connection)
            import_class.import_csv("customer",self.import_customers)
            import_class.import_csv("hall",self.import_halls)
            import_class.import_csv("service",self.import_services)
            self.UI.message("Import completed successfully")
        except ImportingError as e:
            if str(e) == "Already exists":
                self.UI.message("Import has already been done.")
            else:
                self.UI.message(e)
        except Exception as e:
            self.UI.message(e)

    def load_paths(self):
        try:
            paths = load_paths()
        except Exception as e:
            raise AppConfigError("Configuration error: "+ str(e))

        self.sql_path = paths["db_code"]
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
        self._is_running = False