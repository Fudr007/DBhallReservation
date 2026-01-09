from datetime import datetime
import cx_Oracle

from Src.Table_Gateways.Cash_Account import CashAccount, CashAccountError
from Src.Table_Gateways.Hall import Hall
from Src.Table_Gateways.Payment import Payment, PaymentException
from Src.Table_Gateways.Reservation import Reservation, ReservationException
from Src.Table_Gateways.Reservation_Hall import ReservationHall, ReservationHallException
from Src.Table_Gateways.Reservation_Service import ServiceReservation

class ReservationServiceException(Exception):
    pass

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
        except ReservationException as e:
            raise ReservationServiceException(f'{e}')
        except ReservationServiceException as e:
            raise ReservationServiceException(f'{e}')
        except ReservationHallException as e:
            raise ReservationServiceException(f'{e}')
        except cx_Oracle.DatabaseError as e:
            raise ReservationServiceException(f'Reservation service database error: {e}')
        except Exception as e:
            raise ReservationServiceException(f'Unexpected error while creating reservation {e}')

    def pay_and_transfer(self, reservation_id:int, account_id:int, amount:float, ):
        payment = None
        payment_id = None
        try:
            payment = Payment(self.connection)
            payment_id = payment.create(reservation_id, amount)
            if payment_id is None:
                raise PaymentException("Payment not created")

            account = CashAccount(self.connection)
            account.transfer_to_system_account(amount, account_id)

            reservation = Reservation(self.connection)
            reservation.update("status", "CONFIRMED", reservation_id)
        except PaymentException as e:
            raise ReservationServiceException(f'{e}')
        except CashAccountError as e:
            if payment and payment_id:
                payment.delete(payment_id)
            raise ReservationServiceException(f'{e}')
        except cx_Oracle.DatabaseError as e:
            raise ReservationServiceException(f'Payment database error: {e}')
        except Exception as e:
            raise ReservationServiceException(f'Unexpected error while paying reservation {e}')

    def read_available_halls(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM free_halls_view")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Reservation service database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Reservation service error: {e}')

    def read_reservation_detail(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM reservation_details_view")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Reservation service database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Reservation service error: {e}')

    def read_id_name_email(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT r.id AS reservation_id, c.name AS customer_name, c.email AS customer_email FROM reservation r JOIN customer c ON c.id = r.customer_id")
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Reservation service database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Reservation service error: {e}')

    def read_not_paid(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT r.id AS reservation_id, "
                "c.id AS customer_id, "
                "c.account_id AS account_id, "
                "c.name AS customer_name, "
                "c.email AS customer_email, "
                "r.total_price "
                "FROM reservation r "
                "JOIN customer c ON c.id = r.customer_id "
                "LEFT JOIN payment p ON p.reservation_id = r.id "
                "WHERE p.id IS NULL"
            )
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Reservation service database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Reservation service error: {e}')

    def report(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM reservation_summary_view")
            return cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            raise ReservationServiceException(f'Reservation service database error: {error_obj.message}')
        except Exception as e:
            raise ReservationServiceException(f'Reservation service error: {e}')

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