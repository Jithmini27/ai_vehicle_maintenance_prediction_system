SELECT * FROM users;
SELECT * FROM vehicles;
SELECT * FROM service_records;
SELECT * FROM predictions;
SELECT * FROM bookings;
SELECT * FROM notifications;

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
);

USE vehicle_maintenance_db;
SHOW TABLES;

USE vehicle_maintenance_db;

INSERT INTO users (full_name, email, password_hash, phone, role, status)
VALUES
('Nimal Perera', 'nimal@gmail.com', '8d969eef6ecad3c29a3a629280e686cff8fabd8c3e3c0c1e1f6d7a7a7a7a7a', '0771111111', 'owner', 'active'),
('Sunil Silva', 'sunil@gmail.com', '8d969eef6ecad3c29a3a629280e686cff8fabd8c3e3c0c1e1f6d7a7a7a7a7a', '0772222222', 'technician', 'active');

INSERT INTO vehicles
(user_id, plate_no, brand, model, year, fuel_type, last_service_date, current_mileage)
VALUES
(1, 'WP AA 1234', 'Toyota', 'Vitz', 2020, 'Petrol', '2026-01-10', 52000),
(1, 'WP BB 5678', 'Toyota', 'Hilux', 2018, 'Diesel', '2026-02-15', 175000);

INSERT INTO service_records
(vehicle_id, service_date, odometer_reading, service_type, parts_replaced, cost, notes, next_service_suggested_km)
VALUES
(1, '2026-03-01', 52000, 'Full Service', 'Engine Oil, Filter', 15000, 'Normal service', 57000),

(2, '2026-03-05', 175000, 'Major Service', 'Brake Pads, Oil, Belt', 55000, 'High mileage service', 180000);

USE vehicle_maintenance_db;

DELETE FROM service_records
WHERE vehicle_id IN (1,2);

DELETE FROM predictions
WHERE vehicle_id IN (8,9);

DELETE FROM bookings
WHERE vehicle_id IN (8,9);

DELETE FROM vehicles
WHERE plate_no IN ('WP AA 1234', 'WP BB 5678');

DELETE FROM users
WHERE email IN ('nimal@gmail.com', 'sunil@gmail.com');

SELECT notification_id, is_read FROM notifications;

UPDATE notifications
SET is_read = 1
WHERE notification_id = 1;

SELECT notification_id, is_read FROM notifications;

SELECT * FROM predictions ORDER BY prediction_id DESC;
SELECT * FROM notifications ORDER BY notification_id DESC;
