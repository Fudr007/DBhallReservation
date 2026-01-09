CREATE TABLE cash_account (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_type VARCHAR2(20) NOT NULL CHECK (account_type IN ('CUSTOMER', 'SYSTEM')),
    balance NUMBER(10,2) NOT NULL CHECK (balance >= 0)
);

CREATE UNIQUE INDEX ux_one_system_account
ON cash_account ( CASE WHEN account_type = 'SYSTEM' THEN account_type END);

CREATE TABLE customer (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id INT NOT NULL,
    name VARCHAR2(100) NOT NULL CHECK (REGEXP_LIKE(name, '^[a-zA-ZĚŠČŘŽÝÁÍÉÚŮŇĎŤÓěščřžýáíéúňďťó0-9 ]+$')),
    email VARCHAR2(100) NOT NULL CHECK (REGEXP_LIKE(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')) UNIQUE,
    phone VARCHAR2(15) NOT NULL CHECK (REGEXP_LIKE(phone, '^\+?[0-9]{9,15}$')),
    customer_type VARCHAR2(20) NOT NULL CHECK (customer_type IN ('INDIVIDUAL', 'TEAM')),
    is_active NUMBER(1) DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at DATE DEFAULT SYSDATE,
    FOREIGN KEY (account_id) REFERENCES cash_account(id) ON DELETE CASCADE
);

CREATE TABLE hall (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(100) NOT NULL UNIQUE CHECK (REGEXP_LIKE(name, '^[a-zA-ZĚŠČŘŽÝÁÍÉÚŮŇĎŤÓěščřžýáíéúňďťó0-9 ]+$')),
    sport_type VARCHAR2(30) NOT NULL CHECK (sport_type IN ('FOOTBALL', 'BASKETBALL', 'VOLLEYBALL', 'BADMINTON', 'HANDBALL', 'FLORBALL')),
    hourly_rate NUMBER(8,2) NOT NULL CHECK(hourly_rate >=0),
    capacity NUMBER NOT NULL CHECK(capacity > 0)
);

CREATE TABLE reservation (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INT NOT NULL,
    start_time DATE NOT NULL,
    end_time DATE NOT NULL,
    status VARCHAR2(20) NOT NULL CHECK (status IN ('CREATED', 'CONFIRMED')),
    total_price NUMBER(10,2) CHECK(total_price >= 0),
    CHECK(start_time < end_time),
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE SET NULL
);

CREATE TABLE reservation_hall (
    reservation_id INT NOT NULL,
    hall_id INT NOT NULL,
    PRIMARY KEY (reservation_id, hall_id),
    FOREIGN KEY (reservation_id) REFERENCES reservation(id) ON DELETE CASCADE,
    FOREIGN KEY (hall_id) REFERENCES hall(id) ON DELETE CASCADE
);

CREATE TABLE service (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(100) NOT NULL UNIQUE CHECK (REGEXP_LIKE(name, '^[a-zA-ZĚŠČŘŽÝÁÍÉÚŮŇĎŤÓěščřžýáíéúňďťó0-9 ]+$')),
    price_per_hour NUMBER(8,2) NOT NULL CHECK(price_per_hour >=0),
    is_optional NUMBER(1) DEFAULT 1 CHECK (is_optional IN (0,1))
);

CREATE TABLE reservation_service (
    reservation_id INT NOT NULL,
    service_id INT NOT NULL,
    hours NUMBER(5,2) NOT NULL CHECK(hours > 0),
    PRIMARY KEY (reservation_id, service_id),
    FOREIGN KEY (reservation_id) REFERENCES reservation(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(id) ON DELETE CASCADE
);

CREATE TABLE payment (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reservation_id INT NOT NULL,
    amount NUMBER(10,2) NOT NULL CHECK(amount > 0),
    paid_at DATE DEFAULT SYSDATE,
    FOREIGN KEY (reservation_id) REFERENCES reservation(id) ON DELETE SET NULL
);

INSERT INTO cash_account (account_type, balance)
SELECT 'SYSTEM', 0
FROM dual
WHERE NOT EXISTS (
    SELECT 1 FROM cash_account WHERE account_type = 'SYSTEM'
);

CREATE VIEW free_halls_view AS
SELECT h.id AS hall_id,
       h.name AS hall_name,
       h.sport_type,
       h.hourly_rate,
       h.capacity
FROM hall h
WHERE NOT EXISTS (
    SELECT 1
    FROM reservation_hall rh
    JOIN reservation r ON rh.reservation_id = r.id
    WHERE rh.hall_id = h.id
      AND r.status <> 'CANCELLED'
      AND r.start_time <= SYSDATE
      AND r.end_time   >= SYSDATE
);

CREATE VIEW reservation_details_view AS
SELECT r.id AS reservation_id,
       r.start_time,
       r.end_time,
       r.status,
       r.total_price,
       c.id AS customer_id,
       c.name AS customer_name,
       c.email,
       h.id AS hall_id,
       h.name AS hall_name
FROM reservation r
JOIN customer c ON r.customer_id = c.id
JOIN reservation_hall rh ON rh.reservation_id = r.id
JOIN hall h ON rh.hall_id = h.id;

CREATE VIEW reservation_summary_view AS
SELECT
    COUNT(DISTINCT r.id) AS total_reservations,
    COUNT(DISTINCT CASE WHEN r.status <> 'CANCELLED' THEN r.id END) AS active_reservations,
    MIN(r.total_price) AS min_reservation_price,
    MAX(r.total_price) AS max_reservation_price,
    ROUND(AVG(r.total_price), 2) AS avg_reservation_price,

    NVL(SUM(p.amount), 0) AS total_paid_amount,
    COUNT(p.id) AS total_payments,
    ROUND(AVG(p.amount), 2) AS avg_payment,

    COUNT(DISTINCT c.id) AS unique_customers,

    COUNT(DISTINCT rh.hall_id) AS used_halls,

    COUNT(DISTINCT rs.service_id) AS used_services,
    NVL(SUM(rs.hours), 0) AS total_service_hours

FROM reservation r
JOIN customer c ON c.id = r.customer_id
LEFT JOIN payment p ON p.reservation_id = r.id
LEFT JOIN reservation_hall rh ON rh.reservation_id = r.id
LEFT JOIN reservation_service rs ON rs.reservation_id = r.id;