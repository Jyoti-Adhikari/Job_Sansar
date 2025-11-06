CREATE DATABASE job_portal;
USE job_portal;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('candidate', 'jobgiver', 'admin') NOT NULL,
    address TEXT,
    company_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidate_cvs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    domain VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE job_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    domain VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert fixed admin user
INSERT INTO users (username, password, role) VALUES ('jyoti', 'jyoti', 'admin');


-- 1. Applications (Apply Now)
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_requirements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (candidate_id, job_id)
);

-- 2. Messages (Inquiry + Invite)
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message TEXT NOT NULL,
    file_type ENUM('cv', 'job') NOT NULL,
    file_id INT NOT NULL,
    message_type ENUM('inquiry', 'invite') NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read TINYINT(1) DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Notifications (Real-time)
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    type ENUM('application', 'inquiry', 'invite') NOT NULL,
    related_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Remove old inquiry table
DROP TABLE IF EXISTS messages;

-- Remove notifications related to inquiry
DELETE FROM notifications WHERE type = 'inquiry';

-- New: Shortlisted CVs (Job Giver)
CREATE TABLE shortlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jobgiver_id INT NOT NULL,
    cv_id INT NOT NULL,
    shortlisted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jobgiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cv_id) REFERENCES candidate_cvs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_shortlist (jobgiver_id, cv_id)
);

-- New: Saved Jobs (Candidate)
CREATE TABLE saved_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_requirements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_save (candidate_id, job_id)
);















-- New
USE job_portal;

-- Create new tables if they don't exist (same as above)
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_requirements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message TEXT NOT NULL,
    file_type ENUM('cv', 'job') NOT NULL,
    file_id INT NOT NULL,
    message_type ENUM('inquiry', 'invite') NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read TINYINT(1) DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    type ENUM('application', 'inquiry', 'invite', 'shortlist', 'save') NOT NULL,
    related_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shortlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jobgiver_id INT NOT NULL,
    cv_id INT NOT NULL,
    shortlisted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jobgiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cv_id) REFERENCES candidate_cvs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_shortlist (jobgiver_id, cv_id)
);

CREATE TABLE IF NOT EXISTS saved_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_requirements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_save (candidate_id, job_id)
);

-- Safe foreign key updates (check if constraints exist before dropping)
SET @candidate_cvs_fk := (
    SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_NAME = 'candidate_cvs' AND TABLE_SCHEMA = 'job_portal' 
    AND REFERENCED_TABLE_NAME = 'users'
);
SET @sql1 = IF(@candidate_cvs_fk IS NOT NULL, 
    CONCAT('ALTER TABLE candidate_cvs DROP FOREIGN KEY ', @candidate_cvs_fk), 
    'SELECT "No candidate_cvs foreign key to drop"');
PREPARE stmt1 FROM @sql1;
EXECUTE stmt1;
DEALLOCATE PREPARE stmt1;

SET @job_requirements_fk := (
    SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_NAME = 'job_requirements' AND TABLE_SCHEMA = 'job_portal' 
    AND REFERENCED_TABLE_NAME = 'users'
);
SET @sql2 = IF(@job_requirements_fk IS NOT NULL, 
    CONCAT('ALTER TABLE job_requirements DROP FOREIGN KEY ', @job_requirements_fk), 
    'SELECT "No job_requirements foreign key to drop"');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

SET @feedback_fk := (
    SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_NAME = 'feedback' AND TABLE_SCHEMA = 'job_portal' 
    AND REFERENCED_TABLE_NAME = 'users'
);
SET @sql3 = IF(@feedback_fk IS NOT NULL, 
    CONCAT('ALTER TABLE feedback DROP FOREIGN KEY ', @feedback_fk), 
    'SELECT "No feedback foreign key to drop"');
PREPARE stmt3 FROM @sql3;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

-- Add new foreign keys with CASCADE
ALTER TABLE candidate_cvs ADD CONSTRAINT fk_candidate_cvs_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE job_requirements ADD CONSTRAINT fk_job_requirements_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE feedback ADD CONSTRAINT fk_feedback_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Make username unique
ALTER TABLE users ADD UNIQUE KEY IF NOT EXISTS unique_username (username);

-- Update notifications type enum if table exists
SET @notifications_exists = (SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'job_portal' AND table_name = 'notifications');
SET @sql4 = IF(@notifications_exists > 0, 
    'ALTER TABLE notifications MODIFY COLUMN type ENUM(\'application\', \'inquiry\', \'invite\', \'shortlist\', \'save\') NOT NULL', 
    'SELECT "Notifications table does not exist"');
PREPARE stmt4 FROM @sql4;
EXECUTE stmt4;
DEALLOCATE PREPARE stmt4;

-- Ensure admin user exists
INSERT IGNORE INTO users (username, password, role) VALUES ('jyoti', 'jyoti', 'admin');


-- Add the new columns
ALTER TABLE messages 
ADD COLUMN related_job_id INT NULL,
ADD COLUMN related_cv_id INT NULL;

-- Add foreign key constraints
ALTER TABLE messages 
ADD FOREIGN KEY (related_job_id) REFERENCES job_requirements(id),
ADD FOREIGN KEY (related_cv_id) REFERENCES candidate_cvs(id);

USE job_portal;

-- Update messages table to include application type and proper file linking
ALTER TABLE messages 
MODIFY COLUMN message_type ENUM('inquiry', 'invite', 'application') NOT NULL,
MODIFY COLUMN file_type ENUM('cv', 'job') NOT NULL;

-- Add columns for proper file linking if they don't exist
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS related_job_id INT NULL,
ADD COLUMN IF NOT EXISTS related_cv_id INT NULL;

-- Add foreign key constraints
ALTER TABLE messages 
ADD FOREIGN KEY (related_job_id) REFERENCES job_requirements(id),
ADD FOREIGN KEY (related_cv_id) REFERENCES candidate_cvs(id);