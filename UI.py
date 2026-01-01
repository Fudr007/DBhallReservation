from datetime import datetime

from Table_Gateways.Customer import Customer


class UI:

    def message(self, msg):
        print(msg)

    def customer_form(self):
        print("Customer account creation form")
        name = input("Enter customers name: ")
        email = input("Enter customers email: ")
        phone = input("Enter customers phone: ")
        customer_type = input("Enter customers type (INDIVIDUAL, TEAM): ")
        return {
            "name":name,
            "email":email,
            "phone":phone,
            "customer_type":customer_type
        }

    def hall_form(self):
        print("Hall creation form")
        name = input("Enter hall name: ")
        sport_type = input("Select hall sport type (options FOOTBALL, BASKETBALL, VOLLEYBALL, BADMINTON, HANDBALL, FLORBALL): ")
        if sport_type.upper() not in ["FOOTBALL", "BASKETBALL", "VOLLEYBALL", "BADMINTON", "HANDBALL", "FLORBALL"]:
            print("Invalid sport type")
            self.hall_form()
        hourly_rate = float(input("Enter hall hourly rate: "))
        if hourly_rate < 0:
            print("Invalid hourly rate")
            self.hall_form()
        capacity = int(input("Enter hall capacity: "))
        if capacity <= 0:
            print("Invalid capacity")
            self.hall_form()
        return {
            "name":name,
            "sport_type":sport_type.upper(),
            "hourly_rate":hourly_rate,
            "capacity":capacity
        }

    def service_form(self):
        print("Service creation form")
        name = input("Enter service name: ")
        price_per_hour = float(input("Enter service price per hour: "))
        if price_per_hour < 0:
            print("Invalid price per hour")
            self.service_form()
        optional = input("Is service optional (Y/N): ")
        if optional.upper() == "Y":
            optional = True
        elif optional.upper() == "N":
            optional = False
        else:
            print("Invalid input")
            self.service_form()

        return {
            "name":name,
            "price_per_hour":price_per_hour,
            "optional":optional
        }

    def reservation_form(self, customers:dict, services_optional:dict, halls:dict):
        print("Reservation creation form")

        for customer in customers:
            print(f"{customer['customer_id']}: {customer['name']}")

        while True:
            customer_id = int(input("Choose customer id from the list: "))
            if customer_id not in customers:
                print("Invalid customer id")
            else:
                break

        for hall in halls:
            print(f"{hall['hall_id']}: {hall['name']}")
        chosen_halls = []
        while True:
            hall_id = int(input("Choose services id from the list after each  (0 to finish): "))
            if hall_id == 0:
                break
            if hall_id in halls and hall_id not in chosen_halls:
                chosen_halls.append(hall_id)
            else:
                print("Invalid hall id or hall already added")

        start_time = input("Enter reservation start time (YYYY-MM-DD HH:MM): ")
        end_time = input("Enter reservation end time (YYYY-MM-DD HH:MM): ")

        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

        hours = (end_dt - start_dt).total_seconds() / 3600

        for service in services_optional:
            print(f"{service['service_id']}: {service['name']} ({service['price_per_hour']})")
        service_id_time = {}
        while True:
            service_id = int(input("Choose services id from the list after each  (0 to finish): "))
            if service_id == 0:
                break
            elif service_id in services_optional and service_id not in service_id_time:
                hour_service = int(input("For how many hours:"))
                if hour_service <= 0:
                    print("Invalid hours")
                    continue
                if hours < hour_service:
                    print("Hours must be less than total reservation hours")
                    continue
                service_id_time[service_id] = hour_service
            else:
                print("Invalid service id or service already added")

        return {
            "customer_id":customer_id,
            "halls_ids":chosen_halls,
            "service_id_time":service_id_time,
            "start_dt":start_dt,
            "end_dt":end_dt
        }

    def menu(self, actions:dict):
        print("Available actions:")
        for key, value in actions.items():
            print(f"{key}: {value.__name__}")