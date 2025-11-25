-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 25, 2025 at 06:05 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `job_portal`
--

-- --------------------------------------------------------

--
-- Table structure for table `applications`
--

CREATE TABLE `applications` (
  `id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `applied_at` datetime DEFAULT current_timestamp(),
  `status` enum('pending','accepted','rejected') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `applications`
--

INSERT INTO `applications` (`id`, `candidate_id`, `job_id`, `applied_at`, `status`) VALUES
(14, 51, 40, '2025-11-20 07:58:31', 'pending'),
(15, 91, 27, '2025-11-20 15:36:23', 'pending'),
(16, 89, 43, '2025-11-20 15:45:30', 'pending'),
(17, 89, 22, '2025-11-20 15:45:32', 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `candidate_cvs`
--

CREATE TABLE `candidate_cvs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `filename` varchar(255) NOT NULL,
  `upload_date` datetime DEFAULT current_timestamp(),
  `domain` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_cvs`
--

INSERT INTO `candidate_cvs` (`id`, `user_id`, `filename`, `upload_date`, `domain`) VALUES
(45, 45, 'John_cv_it.pdf', '2025-11-07 04:42:00', 'Information Technology'),
(46, 47, 'sarah_cv_mar.pdf', '2025-11-07 04:48:31', 'Marketing'),
(48, 51, 'EMILY-cv-f.pdf', '2025-11-07 04:57:29', 'Finance'),
(49, 54, 'DAVID-cv-s.pdf', '2025-11-07 10:48:16', 'Sales'),
(50, 56, 'LISA-cv-e.pdf', '2025-11-07 12:05:30', 'Education'),
(52, 58, 'ALEXANDER-cv-d.pdf', '2025-11-07 12:20:59', 'Design'),
(53, 58, 'empty.pdf', '2025-11-07 12:36:27', 'Design'),
(54, 61, 'RACHEL-cv-l.pdf', '2025-11-07 12:38:38', 'Legal'),
(55, 64, 'BRIAN-cv-o.pdf', '2025-11-07 13:49:58', 'Operations / Management'),
(57, 66, 'MICHELLE_TAN-cv-it.pdf', '2025-11-09 02:01:31', 'Information Technology'),
(58, 68, 'KEVIN_PATEL-cv-er.pdf', '2025-11-09 02:07:12', 'Engineering'),
(59, 50, 'MICHAEL-cv-er.pdf', '2025-11-09 02:12:21', 'Engineering'),
(60, 70, 'AMANDA_ROBERTS-cv-h.pdf', '2025-11-09 02:19:03', 'Healthcare'),
(61, 53, 'JESSICA-cv-h.pdf', '2025-11-09 02:24:18', 'Healthcare'),
(62, 72, 'JASON_CHEN-cv-f.pdf', '2025-11-09 02:33:00', 'Finance'),
(63, 73, 'OLIVIA_MARTIN-cv-m.pdf', '2025-11-09 03:01:52', 'Marketing'),
(64, 75, 'SOPHIA_LEE-cv-d.pdf', '2025-11-09 03:59:46', 'Design'),
(65, 79, 'NATALIE_CHANG-cv-er.pdf', '2025-11-10 14:20:30', 'Engineering'),
(66, 81, 'MARCUS_JOHNSON-cv-h.pdf', '2025-11-10 14:23:05', 'Healthcare'),
(67, 83, 'ROBERT_MCDONALD-cv-e.pdf', '2025-11-10 14:30:33', 'Education'),
(68, 85, 'PRIYA_SHARMA-cv-f.pdf', '2025-11-11 15:29:59', 'Finance'),
(69, 87, 'ETHAN_CARTER-cv-m.pdf', '2025-11-11 15:33:06', 'Marketing'),
(70, 89, 'CHLOE_BENNETT-cv-s.pdf', '2025-11-13 08:53:14', 'Sales'),
(71, 91, 'REBECCA_MARTINEZ-cv-l.pdf', '2025-11-20 15:36:02', 'Legal');

-- --------------------------------------------------------

--
-- Table structure for table `career_paths`
--

CREATE TABLE `career_paths` (
  `id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `required_skills` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`required_skills`)),
  `average_salary_min` int(11) DEFAULT NULL,
  `average_salary_max` int(11) DEFAULT NULL,
  `growth_outlook` enum('High','Medium','Low') DEFAULT NULL,
  `experience_level` enum('Entry','Mid','Senior') DEFAULT NULL,
  `domain` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `career_paths`
--

INSERT INTO `career_paths` (`id`, `title`, `description`, `required_skills`, `average_salary_min`, `average_salary_max`, `growth_outlook`, `experience_level`, `domain`) VALUES
(33, 'Software Engineer', 'Design, develop and maintain software systems and applications', '[\"Programming\", \"Algorithms\", \"System Design\", \"Problem Solving\", \"Software Development\"]', 70000, 130000, 'High', 'Mid', 'Engineering'),
(34, 'Mechanical Engineer', 'Design and analyze mechanical systems and components', '[\"CAD\", \"Engineering Design\", \"Thermodynamics\", \"Manufacturing\", \"Project Management\"]', 65000, 110000, 'Medium', 'Mid', 'Engineering'),
(35, 'Civil Engineer', 'Plan, design and oversee construction projects', '[\"Structural Analysis\", \"CAD\", \"Project Management\", \"Construction Methods\", \"Regulatory Compliance\"]', 60000, 100000, 'Medium', 'Mid', 'Engineering'),
(36, 'Electrical Engineer', 'Design and develop electrical systems and equipment', '[\"Circuit Design\", \"Electronics\", \"Power Systems\", \"MATLAB\", \"Technical Documentation\"]', 68000, 115000, 'High', 'Mid', 'Engineering'),
(37, 'Full Stack Developer', 'Develop both front-end and back-end web applications', '[\"JavaScript\", \"HTML/CSS\", \"Python\", \"SQL\", \"React\"]', 60000, 120000, 'High', 'Mid', 'Information Technology'),
(38, 'Data Scientist', 'Extract insights from data using statistical and machine learning techniques', '[\"Python\", \"Statistics\", \"Machine Learning\", \"SQL\", \"Data Visualization\"]', 80000, 140000, 'High', 'Mid', 'Information Technology'),
(39, 'DevOps Engineer', 'Bridge development and operations with automation and infrastructure management', '[\"Linux\", \"Docker\", \"AWS\", \"Python\", \"CI/CD\"]', 70000, 130000, 'High', 'Mid', 'Information Technology'),
(40, 'IT Support Specialist', 'Provide technical assistance and support for computer systems', '[\"Troubleshooting\", \"Networking\", \"Hardware\", \"Customer Service\", \"Operating Systems\"]', 45000, 75000, 'Medium', 'Entry', 'Information Technology'),
(41, 'Registered Nurse', 'Provide patient care and support in healthcare settings', '[\"Patient Care\", \"Medical Knowledge\", \"Communication\", \"Emergency Response\", \"Medical Documentation\"]', 55000, 85000, 'High', 'Mid', 'Healthcare'),
(42, 'Medical Researcher', 'Conduct research to improve healthcare outcomes', '[\"Research Methodology\", \"Data Analysis\", \"Scientific Writing\", \"Laboratory Techniques\", \"Statistics\"]', 60000, 100000, 'High', 'Mid', 'Healthcare'),
(43, 'Healthcare Administrator', 'Manage healthcare facilities and services', '[\"Healthcare Management\", \"Budgeting\", \"Regulatory Compliance\", \"Leadership\", \"Strategic Planning\"]', 65000, 110000, 'High', 'Mid', 'Healthcare'),
(44, 'Teacher', 'Educate students in specific subject areas', '[\"Teaching\", \"Curriculum Development\", \"Classroom Management\", \"Communication\", \"Student Assessment\"]', 40000, 70000, 'Medium', 'Entry', 'Education'),
(45, 'Education Administrator', 'Manage educational institutions and programs', '[\"Educational Leadership\", \"Budget Management\", \"Policy Development\", \"Staff Management\", \"Strategic Planning\"]', 60000, 95000, 'Medium', 'Mid', 'Education'),
(46, 'Curriculum Developer', 'Design and develop educational materials and programs', '[\"Curriculum Design\", \"Educational Technology\", \"Assessment Design\", \"Research\", \"Instructional Design\"]', 50000, 85000, 'Medium', 'Mid', 'Education'),
(47, 'Financial Analyst', 'Analyze financial data and provide investment recommendations', '[\"Financial Modeling\", \"Excel\", \"Data Analysis\", \"Accounting\", \"Risk Assessment\"]', 60000, 100000, 'High', 'Mid', 'Finance'),
(48, 'Accountant', 'Manage financial records and ensure compliance', '[\"Accounting Principles\", \"Financial Reporting\", \"Tax Preparation\", \"Auditing\", \"Attention to Detail\"]', 50000, 85000, 'Medium', 'Entry', 'Finance'),
(49, 'Investment Banker', 'Advise clients on financial transactions and investments', '[\"Financial Analysis\", \"Deal Structuring\", \"Negotiation\", \"Market Research\", \"Client Management\"]', 80000, 200000, 'High', 'Senior', 'Finance'),
(50, 'Digital Marketing Specialist', 'Develop and implement online marketing strategies', '[\"SEO\", \"Social Media Marketing\", \"Content Creation\", \"Analytics\", \"Campaign Management\"]', 45000, 80000, 'High', 'Entry', 'Marketing'),
(51, 'Marketing Manager', 'Oversee marketing campaigns and strategies', '[\"Strategic Planning\", \"Brand Management\", \"Market Research\", \"Budget Management\", \"Team Leadership\"]', 65000, 120000, 'High', 'Mid', 'Marketing'),
(52, 'Content Strategist', 'Develop content plans to engage target audiences', '[\"Content Creation\", \"SEO\", \"Audience Analysis\", \"Editorial Planning\", \"Social Media\"]', 50000, 90000, 'High', 'Mid', 'Marketing'),
(53, 'UX/UI Designer', 'Design user experiences and interfaces for digital products', '[\"User Research\", \"Wireframing\", \"Prototyping\", \"Figma\", \"UI Design\"]', 60000, 110000, 'High', 'Mid', 'Design'),
(54, 'Graphic Designer', 'Create visual concepts to communicate ideas', '[\"Adobe Creative Suite\", \"Typography\", \"Layout Design\", \"Brand Identity\", \"Creativity\"]', 40000, 75000, 'Medium', 'Entry', 'Design'),
(55, 'Product Designer', 'Design physical or digital products for user needs', '[\"Design Thinking\", \"Prototyping\", \"User Testing\", \"3D Modeling\", \"Market Research\"]', 65000, 115000, 'High', 'Mid', 'Design'),
(56, 'Sales Representative', 'Sell products and services to customers', '[\"Negotiation\", \"Communication\", \"Customer Relationship\", \"Product Knowledge\", \"Persistence\"]', 40000, 90000, 'Medium', 'Entry', 'Sales'),
(57, 'Sales Manager', 'Lead sales team and develop sales strategies', '[\"Team Leadership\", \"Sales Strategy\", \"Performance Analysis\", \"Client Management\", \"Training\"]', 70000, 130000, 'High', 'Mid', 'Sales'),
(58, 'Account Executive', 'Manage key client accounts and relationships', '[\"Account Management\", \"Strategic Planning\", \"Revenue Growth\", \"Presentation\", \"Contract Negotiation\"]', 60000, 120000, 'High', 'Mid', 'Sales'),
(59, 'Corporate Lawyer', 'Provide legal advice for business transactions', '[\"Legal Research\", \"Contract Law\", \"Negotiation\", \"Corporate Law\", \"Analytical Thinking\"]', 80000, 180000, 'High', 'Senior', 'Legal'),
(60, 'Paralegal', 'Assist lawyers with legal research and documentation', '[\"Legal Research\", \"Document Preparation\", \"Case Management\", \"Attention to Detail\", \"Communication\"]', 40000, 65000, 'Medium', 'Entry', 'Legal'),
(61, 'Compliance Officer', 'Ensure organizational compliance with laws and regulations', '[\"Regulatory Knowledge\", \"Risk Assessment\", \"Policy Development\", \"Auditing\", \"Ethical Standards\"]', 60000, 110000, 'High', 'Mid', 'Legal'),
(62, 'Operations Manager', 'Oversee daily business operations and efficiency', '[\"Process Improvement\", \"Team Management\", \"Budgeting\", \"Strategic Planning\", \"Supply Chain\"]', 65000, 120000, 'High', 'Mid', 'Operations / Management'),
(63, 'Project Manager', 'Plan and execute projects to achieve business goals', '[\"Project Planning\", \"Risk Management\", \"Stakeholder Management\", \"Agile Methodology\", \"Leadership\"]', 70000, 130000, 'High', 'Mid', 'Operations / Management'),
(64, 'Business Analyst', 'Analyze business processes and recommend improvements', '[\"Requirements Gathering\", \"Data Analysis\", \"Process Mapping\", \"Stakeholder Communication\", \"Problem Solving\"]', 60000, 105000, 'High', 'Mid', 'Operations / Management');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `submitted_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `user_id`, `message`, `submitted_at`) VALUES
(11, 51, 'hiiii hlooo', '2025-11-20 08:21:14');

-- --------------------------------------------------------

--
-- Table structure for table `job_requirements`
--

CREATE TABLE `job_requirements` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `filename` varchar(255) NOT NULL,
  `upload_date` datetime DEFAULT current_timestamp(),
  `domain` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_requirements`
--

INSERT INTO `job_requirements` (`id`, `user_id`, `filename`, `upload_date`, `domain`) VALUES
(18, 46, 'Py_tech-job-it.pdf', '2025-11-07 04:45:33', 'Information Technology'),
(19, 48, 'smart-jobs-er.pdf', '2025-11-07 04:50:24', 'Engineering'),
(20, 49, 'digi_company-job-mar.pdf', '2025-11-07 04:52:14', 'Marketing'),
(21, 52, 'fin_com-jobs-f.pdf', '2025-11-07 04:59:56', 'Finance'),
(22, 55, 'XYZ_com-job-s.pdf', '2025-11-07 10:56:31', 'Sales'),
(23, 57, 'Sagarmatha-job-e.pdf', '2025-11-07 12:07:41', 'Education'),
(26, 60, 'girlX-job-d.pdf', '2025-11-07 12:27:24', 'Design'),
(27, 62, 'CanCounsel-job-l.pdf', '2025-11-07 12:41:46', 'Legal'),
(28, 65, 'freeHand-job-o.pdf', '2025-11-07 13:48:51', 'Operations / Management'),
(29, 67, 'Cloudinary-job-it.pdf', '2025-11-09 02:04:13', 'Information Technology'),
(30, 69, 'Machi-job-er.pdf', '2025-11-09 02:10:14', 'Engineering'),
(32, 59, 'alka-jobs-h.pdf', '2025-11-09 02:25:31', 'Healthcare'),
(33, 71, 'bir-job-h.pdf', '2025-11-09 02:29:52', 'Healthcare'),
(34, 74, 'Hansol-job-m.pdf', '2025-11-09 03:57:58', 'Marketing'),
(35, 76, 'Krish-job-d.pdf', '2025-11-09 04:01:15', 'Design'),
(36, 78, 'Honda-job-it.pdf', '2025-11-09 04:16:40', 'Information Technology'),
(37, 80, 'Koshi-job-er.pdf', '2025-11-09 06:55:26', 'Engineering'),
(38, 82, 'mega-job-h.pdf', '2025-11-10 14:24:32', 'Healthcare'),
(39, 84, 'Padma-kanya-job-e.pdf', '2025-11-10 14:32:43', 'Education'),
(40, 86, 'CoffeeHouse-job-f.pdf', '2025-11-11 15:31:10', 'Finance'),
(41, 88, 'Everest-job-m.pdf', '2025-11-11 15:34:59', 'Marketing'),
(42, 92, 'StarMoon-job-l.pdf', '2025-11-20 15:39:52', 'Legal'),
(43, 93, 'Worldlink-job-s.pdf', '2025-11-20 15:42:40', 'Sales');

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `file_type` enum('cv','job') NOT NULL,
  `file_id` int(11) NOT NULL,
  `message_type` enum('inquiry','invite','application') NOT NULL,
  `sent_at` datetime DEFAULT current_timestamp(),
  `is_read` tinyint(1) DEFAULT 0,
  `related_job_id` int(11) DEFAULT NULL,
  `related_cv_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `sender_id`, `receiver_id`, `message`, `file_type`, `file_id`, `message_type`, `sent_at`, `is_read`, `related_job_id`, `related_cv_id`) VALUES
(41, 51, 86, 'Emily Wilson has applied for your job: CoffeeHouse-job-f.pdf', 'job', 40, 'application', '2025-11-20 07:58:31', 0, NULL, NULL),
(42, 86, 51, 'Coffee House has invited you for a job position.', 'cv', 48, 'invite', '2025-11-20 08:07:14', 0, NULL, NULL),
(43, 91, 62, 'REBECCA MARTINEZ has applied for your job: CanCounsel-job-l.pdf', 'job', 27, 'application', '2025-11-20 15:36:23', 0, NULL, NULL),
(44, 93, 89, 'WorldLink Company has invited you for a job position.', 'cv', 70, 'invite', '2025-11-20 15:43:12', 0, NULL, NULL),
(45, 89, 93, 'Chole Ben  has applied for your job: Worldlink-job-s.pdf', 'job', 43, 'application', '2025-11-20 15:45:30', 0, NULL, NULL),
(46, 89, 55, 'Chole Ben  has applied for your job: XYZ_com-job-s.pdf', 'job', 22, 'application', '2025-11-20 15:45:32', 0, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `body` text NOT NULL,
  `type` enum('application','inquiry','invite','shortlist','save') NOT NULL,
  `related_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_read` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `title`, `body`, `type`, `related_id`, `created_at`, `is_read`) VALUES
(44, 86, 'New Application', 'Emily Wilson applied to your job', 'application', 14, '2025-11-20 07:58:31', 0),
(45, 51, 'Interview Invite', 'Coffee House invited you', 'invite', 42, '2025-11-20 08:07:14', 0),
(46, 62, 'New Application', 'REBECCA MARTINEZ applied to your job', 'application', 15, '2025-11-20 15:36:23', 0),
(47, 89, 'Interview Invite', 'WorldLink Company invited you', 'invite', 44, '2025-11-20 15:43:13', 0),
(48, 93, 'New Application', 'Chole Ben  applied to your job', 'application', 16, '2025-11-20 15:45:30', 0),
(49, 55, 'New Application', 'Chole Ben  applied to your job', 'application', 17, '2025-11-20 15:45:32', 0);

-- --------------------------------------------------------

--
-- Table structure for table `saved_jobs`
--

CREATE TABLE `saved_jobs` (
  `id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `saved_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `saved_jobs`
--

INSERT INTO `saved_jobs` (`id`, `candidate_id`, `job_id`, `saved_at`) VALUES
(16, 51, 21, '2025-11-20 07:58:37'),
(17, 91, 27, '2025-11-20 15:36:25');

-- --------------------------------------------------------

--
-- Table structure for table `shortlists`
--

CREATE TABLE `shortlists` (
  `id` int(11) NOT NULL,
  `jobgiver_id` int(11) NOT NULL,
  `cv_id` int(11) NOT NULL,
  `shortlisted_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shortlists`
--

INSERT INTO `shortlists` (`id`, `jobgiver_id`, `cv_id`, `shortlisted_at`) VALUES
(12, 52, 48, '2025-11-07 05:00:51'),
(15, 62, 54, '2025-11-08 14:36:39'),
(16, 71, 61, '2025-11-09 02:52:19'),
(17, 67, 45, '2025-11-09 03:13:50'),
(19, 80, 59, '2025-11-09 06:55:37'),
(20, 82, 61, '2025-11-10 14:24:42'),
(21, 88, 46, '2025-11-13 08:19:18'),
(22, 86, 48, '2025-11-20 08:07:17');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` enum('candidate','jobgiver','admin') NOT NULL,
  `address` text DEFAULT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `address`, `company_name`, `created_at`) VALUES
(45, 'John Doe', 'john', 'candidate', 'Nepal', '', '2025-11-06 22:55:37'),
(46, 'PyTech', 'pytec', 'jobgiver', '', 'PyTech', '2025-11-06 22:58:39'),
(47, 'Sarah Chen', 'sarah', 'candidate', 'Nepal', '', '2025-11-06 23:02:27'),
(48, 'Smart', 'smart', 'jobgiver', '', 'Smart', '2025-11-06 23:04:37'),
(49, 'Digi Company', 'digi', 'jobgiver', '', 'Digi Company', '2025-11-06 23:06:42'),
(50, 'Michael Robert', 'micheal', 'candidate', 'Nepal', '', '2025-11-06 23:09:10'),
(51, 'Emily Wilson', 'emily', 'candidate', 'Nepal', '', '2025-11-06 23:11:41'),
(52, 'Fina Company', 'fina', 'jobgiver', '', 'Fina Company', '2025-11-06 23:14:03'),
(53, 'Jessica Martin', 'jessica', 'candidate', 'Nepal', '', '2025-11-07 04:44:28'),
(54, 'David Thompson', 'david', 'candidate', 'Nepal', '', '2025-11-07 05:02:22'),
(55, 'XYZ Company', 'xyz', 'jobgiver', '', 'XYZ Company', '2025-11-07 05:10:29'),
(56, 'Lisa Parker', 'lisa', 'candidate', 'Nepal', '', '2025-11-07 06:19:01'),
(57, 'Sagarmatha collage', 'sagarmatha', 'jobgiver', '', 'Sagarmatha collage', '2025-11-07 06:22:02'),
(58, 'Alexander Paan', 'alexander', 'candidate', 'Nepal', '', '2025-11-07 06:29:23'),
(59, 'Alka Hospital', 'alka', 'jobgiver', '', 'Alka Hospital', '2025-11-07 06:31:36'),
(60, 'GirlX Company', 'girlx', 'jobgiver', '', 'GirlX Company', '2025-11-07 06:40:45'),
(61, 'Rachel Garcia', 'rachel', 'candidate', 'Nepal', '', '2025-11-07 06:52:13'),
(62, 'CanCounsel Company', 'cancounsel', 'jobgiver', '', 'CanCounsel Company', '2025-11-07 06:55:04'),
(63, 'jyoti', 'jyoti', 'admin', NULL, NULL, '2025-11-07 13:27:46'),
(64, 'Brian Cooper', 'brian', 'candidate', 'Nepal', '', '2025-11-07 08:01:29'),
(65, 'Freehand Company', 'freehand', 'jobgiver', '', 'Freehand Company', '2025-11-07 08:02:07'),
(66, 'Michelle Tan', 'michelle', 'candidate', 'Nepal', '', '2025-11-08 08:13:09'),
(67, 'Cloudinary Company', 'cloudinary', 'jobgiver', '', 'Cloudinary Company', '2025-11-08 20:18:30'),
(68, 'Kevin Patel', 'kevin', 'candidate', 'Nepal', '', '2025-11-08 20:21:11'),
(69, 'Machi Company', 'machi', 'jobgiver', '', 'Machi Company', '2025-11-08 20:23:33'),
(70, 'Amanda Roberts', 'amanda', 'candidate', 'Nepal', '', '2025-11-08 20:31:22'),
(71, 'Bir Hospital', 'bir', 'jobgiver', '', 'Bir Hospital', '2025-11-08 20:43:53'),
(72, 'Jason Chen', 'jason', 'candidate', 'Nepal', '', '2025-11-08 20:46:46'),
(73, 'Oliva Roy', 'oliva', 'candidate', 'Nepal', '', '2025-11-08 21:12:13'),
(74, 'Hansol Company', 'hansol', 'jobgiver', '', 'Hansol Company', '2025-11-08 22:10:48'),
(75, 'Sophia Lee', 'sophia', 'candidate', 'Nepal', '', '2025-11-08 22:14:00'),
(76, 'Krish Company', 'krish', 'jobgiver', '', 'Krish Company', '2025-11-08 22:15:41'),
(77, 'Carlos Rod', 'carlos', 'candidate', 'Nepal', '', '2025-11-08 22:18:25'),
(78, 'Honda Company', 'honda', 'jobgiver', '', 'Honda Company', '2025-11-08 22:19:24'),
(79, 'Natalie Rai', 'natalie', 'candidate', 'Nepal', '', '2025-11-09 00:34:59'),
(80, 'Koshi Company', 'koshi', 'jobgiver', '', 'Koshi Company', '2025-11-09 00:37:02'),
(81, 'Marcus Johnson', 'marcus', 'candidate', 'Nepal', '', '2025-11-10 08:37:03'),
(82, 'Mega Hospital', 'mega', 'jobgiver', '', 'Mega Hospital', '2025-11-10 08:39:03'),
(83, 'Robert Mcdonala', 'robert', 'candidate', 'Nepal', '', '2025-11-10 08:43:18'),
(84, 'PadmaKanya Collage', 'padma', 'jobgiver', '', 'PadmaKanya Collage', '2025-11-10 08:46:40'),
(85, 'Priya Sharma', 'priya', 'candidate', 'N', '', '2025-11-11 09:44:00'),
(86, 'Coffee House', 'coffee', 'jobgiver', '', 'Coffee House', '2025-11-11 09:45:34'),
(87, 'Ethan Carter', 'ethan', 'candidate', 'Nepal', '', '2025-11-11 09:47:25'),
(88, 'Everest Company', 'everest', 'jobgiver', '', 'Everest Company', '2025-11-11 09:49:12'),
(89, 'Chole Ben ', 'chole', 'candidate', 'Nepal', '', '2025-11-13 02:41:16'),
(91, 'REBECCA MARTINEZ', 'rebecca', 'candidate', 'Nepal', '', '2025-11-20 09:50:10'),
(92, 'StarMoon', 'starmoon', 'jobgiver', '', 'StarMoon', '2025-11-20 09:54:21'),
(93, 'WorldLink Company', 'worldlink', 'jobgiver', '', 'WorldLink Company', '2025-11-20 09:56:41');

-- --------------------------------------------------------

--
-- Table structure for table `user_skills`
--

CREATE TABLE `user_skills` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `skill_name` varchar(100) NOT NULL,
  `proficiency_level` enum('Beginner','Intermediate','Expert') DEFAULT NULL,
  `years_experience` float DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_skills`
--

INSERT INTO `user_skills` (`id`, `user_id`, `skill_name`, `proficiency_level`, `years_experience`, `created_at`) VALUES
(6, 51, 'Content Creation SEO', '', 3, '2025-11-07 05:24:54'),
(7, 58, 'Python', '', 4, '2025-11-07 13:10:28'),
(8, 58, 'MERN stack', 'Intermediate', 2, '2025-11-07 13:13:27'),
(9, 53, 'seo', 'Intermediate', 2, '2025-11-09 02:53:40'),
(10, 45, 'Python', 'Intermediate', 3, '2025-11-09 03:16:27'),
(11, 77, 'seo', 'Intermediate', 2, '2025-11-09 04:20:49'),
(12, 79, 'seo', 'Intermediate', 1, '2025-11-09 06:56:27'),
(13, 81, 'Biology', 'Intermediate', 4, '2025-11-10 14:25:35'),
(14, 83, 'Staff Management', 'Intermediate', 3, '2025-11-10 14:29:12'),
(15, 87, 'python', 'Intermediate', 2, '2025-11-13 08:20:51'),
(16, 89, 'python', 'Beginner', 2, '2025-11-13 08:53:50'),
(17, 51, 'python', 'Beginner', 2, '2025-11-20 08:20:24'),
(18, 91, 'seo', 'Beginner', 3, '2025-11-20 15:36:52');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `applications`
--
ALTER TABLE `applications`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_application` (`candidate_id`,`job_id`),
  ADD KEY `job_id` (`job_id`);

--
-- Indexes for table `candidate_cvs`
--
ALTER TABLE `candidate_cvs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_candidate_cvs_user` (`user_id`);

--
-- Indexes for table `career_paths`
--
ALTER TABLE `career_paths`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_feedback_user` (`user_id`);

--
-- Indexes for table `job_requirements`
--
ALTER TABLE `job_requirements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_job_requirements_user` (`user_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`),
  ADD KEY `related_job_id` (`related_job_id`),
  ADD KEY `related_cv_id` (`related_cv_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `saved_jobs`
--
ALTER TABLE `saved_jobs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_save` (`candidate_id`,`job_id`),
  ADD KEY `job_id` (`job_id`);

--
-- Indexes for table `shortlists`
--
ALTER TABLE `shortlists`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_shortlist` (`jobgiver_id`,`cv_id`),
  ADD KEY `cv_id` (`cv_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_username` (`username`);

--
-- Indexes for table `user_skills`
--
ALTER TABLE `user_skills`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `applications`
--
ALTER TABLE `applications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `candidate_cvs`
--
ALTER TABLE `candidate_cvs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=72;

--
-- AUTO_INCREMENT for table `career_paths`
--
ALTER TABLE `career_paths`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `job_requirements`
--
ALTER TABLE `job_requirements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=44;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- AUTO_INCREMENT for table `saved_jobs`
--
ALTER TABLE `saved_jobs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `shortlists`
--
ALTER TABLE `shortlists`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=94;

--
-- AUTO_INCREMENT for table `user_skills`
--
ALTER TABLE `user_skills`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `applications`
--
ALTER TABLE `applications`
  ADD CONSTRAINT `applications_ibfk_1` FOREIGN KEY (`candidate_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `applications_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `job_requirements` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `candidate_cvs`
--
ALTER TABLE `candidate_cvs`
  ADD CONSTRAINT `fk_candidate_cvs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `fk_feedback_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `job_requirements`
--
ALTER TABLE `job_requirements`
  ADD CONSTRAINT `fk_job_requirements_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`related_job_id`) REFERENCES `job_requirements` (`id`),
  ADD CONSTRAINT `messages_ibfk_4` FOREIGN KEY (`related_cv_id`) REFERENCES `candidate_cvs` (`id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `saved_jobs`
--
ALTER TABLE `saved_jobs`
  ADD CONSTRAINT `saved_jobs_ibfk_1` FOREIGN KEY (`candidate_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `saved_jobs_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `job_requirements` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `shortlists`
--
ALTER TABLE `shortlists`
  ADD CONSTRAINT `shortlists_ibfk_1` FOREIGN KEY (`jobgiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `shortlists_ibfk_2` FOREIGN KEY (`cv_id`) REFERENCES `candidate_cvs` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_skills`
--
ALTER TABLE `user_skills`
  ADD CONSTRAINT `user_skills_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
