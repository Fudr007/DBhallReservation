from datetime import datetime

class UIError(Exception):
    pass

class UIWrongInputError(UIError):
    pass

class UI:

    def message(self, msg):
        print(msg)

    def user_input(self, data_type:str, message:str, enum_options:list=""):
        print(message)
        choice = input(">")
        try:
            if data_type == "enter":
                return ""
            if data_type == "int":
                choice = int(choice)
                if choice < 0:
                    raise UIError("Invalid input")
            if data_type == "float":
                choice = float(choice)
                if choice < 0.0:
                    raise UIError("Invalid input")
            if data_type == "bool":
                if choice.lower() == "Y":
                    return True
                elif choice.lower() == "N":
                    return False
            if data_type == "str":
                return choice
            if data_type == "datetime":
                return datetime.strptime(choice, "%Y-%m-%d %H:%M")
            if data_type == "enum":
                if choice.upper() in enum_options:
                    return choice.upper()
            raise UIError("Invalid input")
        except ValueError:
            raise UIError("Invalid input")
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def customer_form(self):
        print("Customer account creation form")
        try:
            name = self.user_input("str","Enter customers name: ")
            email = self.user_input("str","Enter customers email: ")
            phone = self.user_input("int","Enter customers phone: ")
            customer_type = self.user_input("enum","Enter customers type (INDIVIDUAL, TEAM): ", ["INDIVIDUAL", "TEAM"])
            return {
                "name":name,
                "email":email,
                "phone":phone,
                "customer_type":customer_type
            }
        except UIError as e:
            print(e)
            self.customer_form()
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def change_balance_form(self, customers):
        print("Customer balance change form")
        try:
            customers_dict = {r[0]: r for r in customers}
            for customer in customers:
                print(f"{customer[0]}: {customer[2]}, {customer[3]}")
            customer_id = self.user_input("int","Choose customer id from the list and hit Enter: ")
            if customer_id not in customers_dict:
                raise UIError("Invalid customer id")

            balance_id = customers_dict[customer_id][1]
            amount = self.user_input("float","Enter amount to add to the balance:")
            return {
                "balance_id" : balance_id,
                "amount" : amount
            }
        except UIError as e:
            print(e)
            self.change_balance_form(customers)
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def hall_form(self):
        print("Hall creation form")
        try:
            name = self.user_input("str","Enter hall name: ")
            sport_type = self.user_input("enum","Select hall sport type (options FOOTBALL, BASKETBALL, VOLLEYBALL, BADMINTON, HANDBALL, FLORBALL): ", ["FOOTBALL", "BASKETBALL", "VOLLEYBALL", "BADMINTON", "HANDBALL", "FLORBALL"])
            hourly_rate = self.user_input("float","Enter hall hourly rate: ")
            capacity = self.user_input("int","Enter hall capacity: ")

            return {
                "name": name,
                "sport_type": sport_type.upper(),
                "hourly_rate": hourly_rate,
                "capacity": capacity
            }
        except UIError as e:
            print(e)
            self.hall_form()
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def service_form(self):
        print("Service creation form")
        try:
            name = self.user_input("str","Enter service name: ")
            price_per_hour = self.user_input("float","Enter service price per hour: ")
            optional = self.user_input("bool","Is service optional (Y/N): ")

            return {
                "name":name,
                "price_per_hour":price_per_hour,
                "optional":optional
            }
        except UIError as e:
            print(e)
            self.service_form()
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def reservation_form(self, customers, services_optional, halls):
        print("Reservation creation form")
        try:
            customers_dict = {r[0]: r for r in customers}
            for customer in customers:
                print(f"{customer[0]}: {customer[2]}, {customer[3]}")

            while True:
                customer_id = self.user_input("int","Choose customer id from the list and hit Enter: ")
                if customer_id not in customers_dict:
                    print("Invalid customer id")
                else:
                    break

            halls_dict = {r[0]: r for r in halls}
            for hall in halls:
                print(f"{hall[0]}: {hall[1]}, {hall[3]}/h")

            chosen_halls = {}
            while True:
                hall_id = self.user_input("int","Choose hall id from the list after each hit Enter (0 to finish): ")
                if hall_id == 0:
                    if not chosen_halls:
                        print("No halls chosen")
                        continue
                    break
                if hall_id in halls_dict and hall_id not in chosen_halls:
                    chosen_halls[hall_id] = halls_dict[hall_id]
                else:
                    print("Invalid hall id or hall already added")

            start_dt = self.user_input("datetime","Enter reservation start time (YYYY-MM-DD HH:MM): ")
            end_dt  = self.user_input("datetime","Enter reservation end time (YYYY-MM-DD HH:MM): ")

            hours = (end_dt - start_dt).total_seconds() / 3600

            service_dict = {r[0]: r for r in services_optional}
            for service in services_optional:
                print(f"{service[0]}: {service[1]}, {service[2]}/h")
            chosen_services = {}
            while True:
                service_id = self.user_input("int","Choose optional services id from the list after each hit Enter (0 to finish): ")
                if service_id == 0:
                    break
                elif service_id in service_dict and service_id not in chosen_services:
                    hour_service = self.user_input("int","For how many hours:")
                    if hour_service <= 0:
                        print("Invalid hours")
                        continue
                    if hours < hour_service:
                        print("Hours must be less than total reservation hours")
                        continue
                    chosen_services[service_id] = hour_service * service_dict[service_id][2]
                else:
                    print("Invalid service id or service already added")

            return {
                "customer_id":customer_id,
                "halls":chosen_halls,
                "chosen_services":chosen_services,
                "start_dt":start_dt,
                "end_dt":end_dt
            }
        except UIError as e:
            print(e)
            self.reservation_form(customers, services_optional, halls)
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def delete_reservation_form(self, reservations):
        print("Reservation deletion form")
        try:
            if not reservations:
                raise Exception("No reservations to be deleted")
            reservations_dict = {r[0]: r for r in reservations}
            for reservation in reservations:
                print(f"{reservation[0]}: {reservation[1]}, {reservation[2]}")
            reservation_id = self.user_input("int","Choose reservation id from the list and hit Enter: ")
            if reservation_id not in reservations_dict:
                raise UIError("Invalid reservation id")

            return reservation_id
        except UIError as e:
            print(e)
            self.delete_reservation_form(reservations)
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def payment_form(self, not_paid_reservations):
        print("Payment form")
        try:
            if not not_paid_reservations:
                raise Exception("No unpaid reservations")

            reservations_dict = {r[0]: r for r in not_paid_reservations}
            for reservation in not_paid_reservations:
                print(f"{reservation[0]}: {reservation[3]}, {reservation[4]} total sum of {reservation[5]}czk")
            reservation_id = self.user_input("int","Choose reservation id from the list and hit Enter: ")
            if reservation_id not in reservations_dict:
                raise UIError("Invalid reservation id")

            return {
                "reservation_id":reservation_id,
                "account_id":not_paid_reservations[reservation_id][2],
                "total_price":not_paid_reservations[reservation_id][5],
            }
        except UIError as e:
            print(e)
            self.payment_form(not_paid_reservations)
        except Exception as e:
            raise UIWrongInputError(f"Error in UI: {e}")

    def print_halls(self, halls):
        print("Available halls")
        if not halls:
            print("No halls available")
            return
        for hall in halls:
            print(f"{hall[1]}: {hall[2]} {hall[3]}/h Capacity:{hall[4]}")

    def print_reservations_detailed(self, reservations):
        print("Detailed reservations:")
        if not reservations:
            print("No reservations")
            return

        for reservation in reservations:
            print(f"{reservation[0]}: {reservation[1]}-{reservation[2]}, Status: {reservation[3]}, Total price: {reservation[4]},"
                  f" Customer: {reservation[6]}, {reservation[7]}, Hall: {reservation[9]}")

    def print_report(self, data):
        labels = [
            "Total reservations",
            "Active reservations",
            "Min reservation price",
            "Max reservation price",
            "Avg reservation price",
            "Total paid amount",
            "Total payments",
            "Avg payment",
            "Unique customers",
            "Used halls",
            "Used services",
            "Total service hours"
        ]

        print("\n=== RESERVATION SUMMARY REPORT ===\n")

        for label, value in zip(labels, data):
            print(f"{label:<25}: {value}")

        print("\n===============================\n")

    def menu(self, actions:dict):
        print("Available actions:")
        for key, value in actions.items():
            value = value.__name__
            value = value.replace("_", " ").capitalize()
            print(f"{key}: {value}")