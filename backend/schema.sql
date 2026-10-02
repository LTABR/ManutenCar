CREATE DATABASE IF NOT EXISTS manutencar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE manutencar;

CREATE TABLE users (
  id CHAR(36) PRIMARY KEY,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(320) NOT NULL UNIQUE
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
  INDEX idx_parts_type (part_type_id)
);
