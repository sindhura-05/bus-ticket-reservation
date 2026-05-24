-- Run this on both local (bus_reservation) and Railway (railway) databases
-- to add user authentication support

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link reservations to users (optional foreign key)
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS user_id INT DEFAULT NULL;
