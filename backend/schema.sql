CREATE DATABASE IF NOT EXISTS manutencar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE manutencar;

CREATE TABLE users (
  id CHAR(36) PRIMARY KEY,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(320) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cars (
  id CHAR(36) PRIMARY KEY,
  brand VARCHAR(120) NOT NULL DEFAULT '',
  model VARCHAR(120) NOT NULL DEFAULT '',
  owners_ids JSON NOT NULL,
  parts_ids JSON NOT NULL,
  weekly_usage DECIMAL(10, 2) NOT NULL DEFAULT 0
);

CREATE TABLE parts (
  id CHAR(36) PRIMARY KEY,
  last_maintenance DATE NOT NULL,
  part_type_id VARCHAR(80) NOT NULL,
  car_id CHAR(36) NULL,
  CONSTRAINT fk_part_car FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_parts_type (part_type_id)
);

CREATE TABLE user_cars (
  user_id CHAR(36) NOT NULL,
  car_id CHAR(36) NOT NULL,
  PRIMARY KEY (user_id, car_id),
  CONSTRAINT fk_user_cars_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_user_cars_car FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE maintenance_records (
  id CHAR(36) PRIMARY KEY,
  vehicle_id CHAR(36) NOT NULL,
  part_id CHAR(36) NULL,
  service_date DATE NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT NULL,
  category VARCHAR(100) NULL,
  status VARCHAR(50) NULL,
  CONSTRAINT fk_maintenance_vehicle FOREIGN KEY (vehicle_id) REFERENCES cars(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_maintenance_part FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_maintenance_vehicle (vehicle_id),
  INDEX idx_maintenance_status (status)
);

CREATE TABLE support_tickets (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  category VARCHAR(80) NOT NULL,
  subject VARCHAR(160) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Open',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_support_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_support_category CHECK (category IN ('Account/Login','Vehicle & Maintenance Calculations','System Bug','General Question')),
  CONSTRAINT chk_support_status CHECK (status IN ('Open','In Progress','Resolved')),
  INDEX idx_support_user (user_id),
  INDEX idx_support_category (category),
  INDEX idx_support_status (status)
);
