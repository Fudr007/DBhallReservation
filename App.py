from datetime import datetime

from cx_Oracle import DatabaseError
from Config.Config_load import load_config
from DBconnect import DBconnect
from Config.Sql_load import load_sql
from Services.Customer_Service import CustomerService
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
    def __init__(self, path_cfg:str="config.ini", path_sql:str="db.sql"):
        self.connection = None
        self.config_path = path_cfg
        self.sql_path = path_sql
        self.UI = UI()
        self.run()

    def run(self):
        try:
            self.db_load_connect()
        except Exception as e:
            self.shutdown_error(str(e))

        while True:
            try:
                self.UI.message("Welcome in halls management system \n Choose an action and confirm it with Enter key:")
                self.UI.menu(self.actions())
                choosen_action = input()
                self.actions()[choosen_action]()
            except Exception as e:
                self.UI.message(e)


    def add_customer(self):
        information = self.UI.customer_form()
        customer = CustomerService(self.connection)
        message = customer.create_customer_and_account(information["name"], information["email"], information["phone"], information["customer_type"])
        self.UI.message(message)

    def add_hall(self):
        information = self.UI.hall_form()
        hall = Hall(self.connection)
        message = hall.create(information["name"], information["sport_type"], information["hourly_rate"], information["capacity"])
        self.UI.message(message)

    def add_service(self):
        information = self.UI.service_form()
        service = Service(self.connection)
        message = service.create(information["name"], information["price_per_hour"], information["optional"])
        self.UI.message(message)

    def add_reservation(self):
        customers = Customer(self.connection).read_all()
        services_optional = Service(self.connection).read_optional()
        services_not_optional = Service(self.connection).read_not_optional()
        halls = Hall(self.connection).read_all()
        information = self.UI.reservation_form(customers, services_optional, halls)
        halls_ok = self.check_halls(information["halls"], information["start_dt"], information["end_dt"])
        if type(halls_ok) == str:
            self.UI.message(f"Hall {halls_ok} is unavailable in selected time")
            return

        reservation = Reservation(self.connection)
        reservation.create(information["customer_id"], information["start_dt"], information["end_dt"])


    def check_halls(self, halls:list, time_from:datetime, time_to:datetime):
        available_halls_in_time_range = Hall(self.connection).read_available_in_date(time_from, time_to)
        for hall in halls:
            if hall.id not in available_halls_in_time_range:
                return available_halls_in_time_range[hall.id]

        return True

    def calc_price(self, services_id_time:dict, halls:list, start_time:datetime, end_time:datetime):
        reservation_price = 0


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
                print("Database imported successfully")
        except Exception as e:
            raise AppConfigError("Error when importing database: "+ str(e))

    def actions(self):
        return {
            "1": self.add_customer,
            "2": self.add_hall,
            "3": self.add_service,
            "4": self.add_reservation,
            "5": self.shutdown
        }

    def shutdown(self, message="Thank you for using our service!"):
        self.connection.close()
        print(message)
        exit(0)

    def shutdown_error(self, message):
        self.connection.rollback()
        print(message)
        exit(1)