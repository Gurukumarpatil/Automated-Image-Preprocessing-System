CREATE DATABASE IF NOT EXISTS image_preprocessing;

USE image_preprocessing;

CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    original_s3_key VARCHAR(500) NOT NULL,
    processed_s3_key VARCHAR(500),
    original_size BIGINT,
    processed_size BIGINT,
    compression_percentage DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'PROCESSING',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
