-- Bus Ticket Reservation System - Full Schema
-- Works for both local (bus_reservation) and Railway (railway)
-- Run this after connecting to your target database

CREATE TABLE buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(20) NOT NULL UNIQUE,
    operator_name VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    duration VARCHAR(20) NOT NULL,
    total_seats INT NOT NULL DEFAULT 40,
    available_seats INT NOT NULL DEFAULT 40,
    price DECIMAL(10,2) NOT NULL,
    bus_type ENUM('Sleeper','Semi-Sleeper','Seater','AC Sleeper','AC Seater','Volvo AC') NOT NULL DEFAULT 'Seater',
    amenities VARCHAR(255) DEFAULT '',
    rating DECIMAL(2,1) DEFAULT 4.0,
    reviews INT DEFAULT 0
);

CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_email VARCHAR(150) NOT NULL,
    passenger_phone VARCHAR(15) NOT NULL,
    bus_id INT NOT NULL,
    seat_number INT NOT NULL,
    travel_date DATE NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('confirmed','cancelled') DEFAULT 'confirmed',
    FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE CASCADE
);

-- ── Indian Routes ─────────────────────────────────────────────────────────
INSERT INTO buses (bus_number,operator_name,source,destination,departure_time,arrival_time,duration,total_seats,available_seats,price,bus_type,amenities,rating,reviews) VALUES
('TN-001','TNSTC Express','Chennai','Hyderabad','06:00:00','14:30:00','8h 30m',40,38,650.00,'AC Seater','WiFi,Charging,Water',4.2,312),
('TN-002','Orange Travels','Chennai','Hyderabad','21:00:00','05:30:00','8h 30m',36,30,850.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,520),
('TN-003','SRS Travels','Chennai','Hyderabad','22:30:00','07:00:00','8h 30m',40,12,750.00,'Semi-Sleeper','Charging,Water',4.1,198),
('TN-004','Parveen Travels','Chennai','Hyderabad','20:00:00','04:30:00','8h 30m',36,36,950.00,'Volvo AC','WiFi,Blanket,Charging,Snacks',4.7,640),
('TN-005','KPN Travels','Chennai','Bangalore','07:00:00','13:00:00','6h',45,40,450.00,'AC Seater','WiFi,Charging',4.3,280),
('TN-006','VRL Travels','Chennai','Bangalore','22:00:00','04:00:00','6h',40,25,600.00,'AC Sleeper','WiFi,Blanket,Charging',4.6,410),
('TN-007','TNSTC','Chennai','Coimbatore','06:30:00','12:30:00','6h',50,45,350.00,'Seater','Water',3.9,150),
('TN-008','Parveen Travels','Chennai','Coimbatore','22:00:00','04:00:00','6h',40,20,550.00,'AC Sleeper','WiFi,Blanket',4.4,320),
('TN-009','Orange Travels','Chennai','Madurai','07:00:00','14:00:00','7h',45,38,400.00,'AC Seater','Charging,Water',4.2,210),
('TN-010','KPN Travels','Chennai','Madurai','21:30:00','04:30:00','7h',40,15,600.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,380);

INSERT INTO buses (bus_number,operator_name,source,destination,departure_time,arrival_time,duration,total_seats,available_seats,price,bus_type,amenities,rating,reviews) VALUES
('HYD-001','TSRTC Express','Hyderabad','Chennai','06:00:00','14:30:00','8h 30m',40,35,650.00,'AC Seater','WiFi,Charging,Water',4.1,290),
('HYD-002','Kallada Travels','Hyderabad','Chennai','21:00:00','05:30:00','8h 30m',36,28,900.00,'Volvo AC','WiFi,Blanket,Charging,Snacks',4.8,710),
('HYD-003','Orange Travels','Hyderabad','Bangalore','07:00:00','14:00:00','7h',40,32,550.00,'AC Seater','WiFi,Charging',4.3,340),
('HYD-004','VRL Travels','Hyderabad','Bangalore','22:00:00','05:00:00','7h',40,18,750.00,'AC Sleeper','WiFi,Blanket,Charging',4.6,480),
('HYD-005','TSRTC','Hyderabad','Mumbai','18:00:00','10:00:00','16h',45,40,900.00,'Semi-Sleeper','Charging,Water',4.0,220),
('HYD-006','Parveen Travels','Hyderabad','Mumbai','19:30:00','11:30:00','16h',36,20,1200.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,390),
('HYD-007','SRS Travels','Hyderabad','Pune','20:00:00','10:00:00','14h',40,30,850.00,'AC Sleeper','WiFi,Blanket',4.3,260),
('HYD-008','Kallada Travels','Hyderabad','Delhi','17:00:00','19:00:00','26h',36,15,1500.00,'Volvo AC','WiFi,Blanket,Charging,Snacks',4.7,580),
('BLR-001','VRL Travels','Bangalore','Chennai','06:00:00','12:00:00','6h',40,36,450.00,'AC Seater','WiFi,Charging',4.4,360),
('BLR-002','KSRTC','Bangalore','Chennai','07:30:00','13:30:00','6h',50,44,350.00,'Seater','Water',3.8,140);

INSERT INTO buses (bus_number,operator_name,source,destination,departure_time,arrival_time,duration,total_seats,available_seats,price,bus_type,amenities,rating,reviews) VALUES
('BLR-003','Orange Travels','Bangalore','Mumbai','20:00:00','12:00:00','16h',40,22,950.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,420),
('BLR-004','Kallada Travels','Bangalore','Hyderabad','07:00:00','14:00:00','7h',36,30,550.00,'AC Seater','WiFi,Charging',4.3,310),
('BLR-005','VRL Travels','Bangalore','Hyderabad','22:00:00','05:00:00','7h',40,18,750.00,'AC Sleeper','WiFi,Blanket,Charging',4.6,490),
('BLR-006','KSRTC','Bangalore','Mysore','06:00:00','08:30:00','2h 30m',50,45,150.00,'Seater','Water',4.0,180),
('BLR-007','SRS Travels','Bangalore','Coimbatore','21:00:00','04:00:00','7h',40,25,600.00,'AC Sleeper','WiFi,Blanket',4.4,290),
('BLR-008','Parveen Travels','Bangalore','Madurai','20:30:00','05:30:00','9h',36,20,700.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,350),
('MUM-001','Neeta Travels','Mumbai','Pune','07:00:00','10:00:00','3h',45,40,250.00,'AC Seater','WiFi,Charging',4.3,420),
('MUM-002','Shivneri','Mumbai','Pune','08:00:00','11:00:00','3h',50,45,200.00,'AC Seater','Charging',4.1,310),
('MUM-003','VRL Travels','Mumbai','Bangalore','19:00:00','11:00:00','16h',40,28,950.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,480),
('MUM-004','Kallada Travels','Mumbai','Hyderabad','18:30:00','10:30:00','16h',36,15,1100.00,'Volvo AC','WiFi,Blanket,Charging,Snacks',4.7,620);

INSERT INTO buses (bus_number,operator_name,source,destination,departure_time,arrival_time,duration,total_seats,available_seats,price,bus_type,amenities,rating,reviews) VALUES
('DEL-001','RedBus Express','Delhi','Mumbai','17:00:00','11:00:00','18h',40,30,1200.00,'Volvo AC','WiFi,Blanket,Charging,Snacks',4.6,540),
('DEL-002','UPSRTC','Delhi','Agra','06:00:00','10:00:00','4h',50,45,300.00,'AC Seater','Charging',4.0,200),
('DEL-003','Parveen Travels','Delhi','Jaipur','07:00:00','12:00:00','5h',45,38,400.00,'AC Seater','WiFi,Charging',4.2,280),
('DEL-004','Kallada Travels','Delhi','Hyderabad','16:00:00','18:00:00','26h',36,20,1500.00,'Volvo AC','WiFi,Blanket,Charging,Snacks',4.7,610),
('DEL-005','HRTC','Delhi','Chandigarh','06:30:00','10:00:00','3h 30m',50,42,250.00,'AC Seater','Charging,Water',4.1,190),
('PUN-001','Neeta Travels','Pune','Mumbai','07:00:00','10:00:00','3h',45,40,250.00,'AC Seater','WiFi,Charging',4.3,380),
('PUN-002','VRL Travels','Pune','Bangalore','19:30:00','11:30:00','16h',40,22,900.00,'AC Sleeper','WiFi,Blanket,Charging',4.5,440),
('PUN-003','Orange Travels','Pune','Hyderabad','20:00:00','10:00:00','14h',36,18,850.00,'AC Sleeper','WiFi,Blanket',4.4,320),
('KOL-001','WBSTC','Kolkata','Bhubaneswar','06:00:00','14:00:00','8h',50,44,500.00,'AC Seater','Charging,Water',4.0,170),
('KOL-002','Kallada Travels','Kolkata','Patna','07:00:00','15:00:00','8h',40,30,550.00,'AC Seater','WiFi,Charging',4.2,240);
