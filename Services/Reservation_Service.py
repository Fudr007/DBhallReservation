from datetime import datetime

import cx_Oracle

from Table_Gateways.Hall import Hall
from Table_Gateways.Reservation import Reservation
from Table_Gateways.Reservation_Hall import ReservationHall
from Table_Gateways.Reservation_Service import ServiceReservation


class ReservationService:
    def __init__(self, connection):
        self.connection = connection

    def create_reservation(self, customer_id:int, start_time:datetime, end_time:datetime, optional_services:dict, not_optional_services, halls:dict):
        try:
            available = self.check_halls(halls, start_time, end_time)
            if type(available) is str:
                raise Exception(f"Hall {available} is unavailable in selected time")
            total_price = self.calc_price(optional_services, not_optional_services, halls, end_time, start_time)

            reservation = Reservation(self.connection)
            reservation_id = reservation.create(customer_id, start_time, end_time, total_price)

            combined_services = {}
            for service in optional_services.keys():
                combined_services[service] = optional_services[service]
            for service in not_optional_services:
                combined_services[service[0]] = service[1]

            hours = int((end_time - start_time).total_seconds() / 3600)
            service_reservation = ServiceReservation(self.connection)
            for service in combined_services.keys():
                service_reservation.create(reservation_id, service, hours)

            reservation_hall = ReservationHall(self.connection)
            for hall in halls.keys():
                reservation_hall.create(reservation_id, hall)

        except cx_Oracle.DatabaseError as e:
            return e
        except Exception as e:
            return e

    def check_halls(self, halls:dict, time_from:datetime, time_to:datetime):
        hall = Hall(self.connection)
        available_halls = hall.read_available_in_date(time_from, time_to)
        if type(available_halls) is list:
            for hall_id, hall_data in halls.items():
                if hall_id not in available_halls:
                    return hall_data[1]

        return True

    def calc_price(self, services_optional:dict, services_not_optional, halls:dict, end_time:datetime, start_time:datetime):
        reservation_price = 0
        hours = (end_time - start_time).total_seconds() / 3600

        for hall in halls.values():
            reservation_price += hall[3] * hours

        for services_not_optional in services_not_optional:
            reservation_price += services_not_optional[2] * hours

        for services_optional in services_optional.values():
            reservation_price += services_optional

        return reservation_price