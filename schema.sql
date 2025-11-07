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



-- Career Prediction Tables
CREATE TABLE IF NOT EXISTS career_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    required_skills JSON,
    average_salary_min INT,
    average_salary_max INT,
    growth_outlook ENUM('High', 'Medium', 'Low'),
    experience_level ENUM('Entry', 'Mid', 'Senior'),
    domain VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level ENUM('Beginner', 'Intermediate', 'Expert'),
    years_experience FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sample Career Path Data for Your Domains - ALL SIMPLIFIED
INSERT INTO career_paths (title, description, required_skills, average_salary_min, average_salary_max, growth_outlook, experience_level, domain) VALUES
-- Engineering Domain
('Software Engineer', 'Design, develop and maintain software systems and applications', '["Programming", "Algorithms", "System Design", "Problem Solving", "Software Development"]', 70000, 130000, 'High', 'Mid', 'Engineering'),
('Mechanical Engineer', 'Design and analyze mechanical systems and components', '["CAD", "Engineering Design", "Thermodynamics", "Manufacturing", "Project Management"]', 65000, 110000, 'Medium', 'Mid', 'Engineering'),
('Civil Engineer', 'Plan, design and oversee construction projects', '["Structural Analysis", "CAD", "Project Management", "Construction Methods", "Regulatory Compliance"]', 60000, 100000, 'Medium', 'Mid', 'Engineering'),
('Electrical Engineer', 'Design and develop electrical systems and equipment', '["Circuit Design", "Electronics", "Power Systems", "MATLAB", "Technical Documentation"]', 68000, 115000, 'High', 'Mid', 'Engineering'),

-- Information Technology Domain
('Full Stack Developer', 'Develop both front-end and back-end web applications', '["JavaScript", "HTML/CSS", "Python", "SQL", "React"]', 60000, 120000, 'High', 'Mid', 'Information Technology'),
('Data Scientist', 'Extract insights from data using statistical and machine learning techniques', '["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization"]', 80000, 140000, 'High', 'Mid', 'Information Technology'),
('DevOps Engineer', 'Bridge development and operations with automation and infrastructure management', '["Linux", "Docker", "AWS", "Python", "CI/CD"]', 70000, 130000, 'High', 'Mid', 'Information Technology'),
('IT Support Specialist', 'Provide technical assistance and support for computer systems', '["Troubleshooting", "Networking", "Hardware", "Customer Service", "Operating Systems"]', 45000, 75000, 'Medium', 'Entry', 'Information Technology'),

-- Healthcare Domain
('Registered Nurse', 'Provide patient care and support in healthcare settings', '["Patient Care", "Medical Knowledge", "Communication", "Emergency Response", "Medical Documentation"]', 55000, 85000, 'High', 'Mid', 'Healthcare'),
('Medical Researcher', 'Conduct research to improve healthcare outcomes', '["Research Methodology", "Data Analysis", "Scientific Writing", "Laboratory Techniques", "Statistics"]', 60000, 100000, 'High', 'Mid', 'Healthcare'),
('Healthcare Administrator', 'Manage healthcare facilities and services', '["Healthcare Management", "Budgeting", "Regulatory Compliance", "Leadership", "Strategic Planning"]', 65000, 110000, 'High', 'Mid', 'Healthcare'),

-- Education Domain
('Teacher', 'Educate students in specific subject areas', '["Teaching", "Curriculum Development", "Classroom Management", "Communication", "Student Assessment"]', 40000, 70000, 'Medium', 'Entry', 'Education'),
('Education Administrator', 'Manage educational institutions and programs', '["Educational Leadership", "Budget Management", "Policy Development", "Staff Management", "Strategic Planning"]', 60000, 95000, 'Medium', 'Mid', 'Education'),
('Curriculum Developer', 'Design and develop educational materials and programs', '["Curriculum Design", "Educational Technology", "Assessment Design", "Research", "Instructional Design"]', 50000, 85000, 'Medium', 'Mid', 'Education'),

-- Finance Domain
('Financial Analyst', 'Analyze financial data and provide investment recommendations', '["Financial Modeling", "Excel", "Data Analysis", "Accounting", "Risk Assessment"]', 60000, 100000, 'High', 'Mid', 'Finance'),
('Accountant', 'Manage financial records and ensure compliance', '["Accounting Principles", "Financial Reporting", "Tax Preparation", "Auditing", "Attention to Detail"]', 50000, 85000, 'Medium', 'Entry', 'Finance'),
('Investment Banker', 'Advise clients on financial transactions and investments', '["Financial Analysis", "Deal Structuring", "Negotiation", "Market Research", "Client Management"]', 80000, 200000, 'High', 'Senior', 'Finance'),

-- Marketing Domain
('Digital Marketing Specialist', 'Develop and implement online marketing strategies', '["SEO", "Social Media Marketing", "Content Creation", "Analytics", "Campaign Management"]', 45000, 80000, 'High', 'Entry', 'Marketing'),
('Marketing Manager', 'Oversee marketing campaigns and strategies', '["Strategic Planning", "Brand Management", "Market Research", "Budget Management", "Team Leadership"]', 65000, 120000, 'High', 'Mid', 'Marketing'),
('Content Strategist', 'Develop content plans to engage target audiences', '["Content Creation", "SEO", "Audience Analysis", "Editorial Planning", "Social Media"]', 50000, 90000, 'High', 'Mid', 'Marketing'),

-- Design Domain
('UX/UI Designer', 'Design user experiences and interfaces for digital products', '["User Research", "Wireframing", "Prototyping", "Figma", "UI Design"]', 60000, 110000, 'High', 'Mid', 'Design'),
('Graphic Designer', 'Create visual concepts to communicate ideas', '["Adobe Creative Suite", "Typography", "Layout Design", "Brand Identity", "Creativity"]', 40000, 75000, 'Medium', 'Entry', 'Design'),
('Product Designer', 'Design physical or digital products for user needs', '["Design Thinking", "Prototyping", "User Testing", "3D Modeling", "Market Research"]', 65000, 115000, 'High', 'Mid', 'Design'),

-- Sales Domain
('Sales Representative', 'Sell products and services to customers', '["Negotiation", "Communication", "Customer Relationship", "Product Knowledge", "Persistence"]', 40000, 90000, 'Medium', 'Entry', 'Sales'),
('Sales Manager', 'Lead sales team and develop sales strategies', '["Team Leadership", "Sales Strategy", "Performance Analysis", "Client Management", "Training"]', 70000, 130000, 'High', 'Mid', 'Sales'),
('Account Executive', 'Manage key client accounts and relationships', '["Account Management", "Strategic Planning", "Revenue Growth", "Presentation", "Contract Negotiation"]', 60000, 120000, 'High', 'Mid', 'Sales'),

-- Legal Domain
('Corporate Lawyer', 'Provide legal advice for business transactions', '["Legal Research", "Contract Law", "Negotiation", "Corporate Law", "Analytical Thinking"]', 80000, 180000, 'High', 'Senior', 'Legal'),
('Paralegal', 'Assist lawyers with legal research and documentation', '["Legal Research", "Document Preparation", "Case Management", "Attention to Detail", "Communication"]', 40000, 65000, 'Medium', 'Entry', 'Legal'),
('Compliance Officer', 'Ensure organizational compliance with laws and regulations', '["Regulatory Knowledge", "Risk Assessment", "Policy Development", "Auditing", "Ethical Standards"]', 60000, 110000, 'High', 'Mid', 'Legal'),

-- Operations / Management Domain
('Operations Manager', 'Oversee daily business operations and efficiency', '["Process Improvement", "Team Management", "Budgeting", "Strategic Planning", "Supply Chain"]', 65000, 120000, 'High', 'Mid', 'Operations / Management'),
('Project Manager', 'Plan and execute projects to achieve business goals', '["Project Planning", "Risk Management", "Stakeholder Management", "Agile Methodology", "Leadership"]', 70000, 130000, 'High', 'Mid', 'Operations / Management'),
('Business Analyst', 'Analyze business processes and recommend improvements', '["Requirements Gathering", "Data Analysis", "Process Mapping", "Stakeholder Communication", "Problem Solving"]', 60000, 105000, 'High', 'Mid', 'Operations / Management');