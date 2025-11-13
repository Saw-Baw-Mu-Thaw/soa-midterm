-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 11, 2025 at 02:36 PM
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
-- Database: `ibanking_db`
--
CREATE DATABASE IF NOT EXISTS `ibanking_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `ibanking_db`;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `customer_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `full_name` varchar(50) NOT NULL,
  `phone_number` varchar(10) NOT NULL,
  `email` varchar(50) NOT NULL,
  `available_balance` decimal(15,0) DEFAULT NULL,
  `program` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`customer_id`, `username`, `password_hash`, `full_name`, `phone_number`, `email`, `available_balance`, `program`) VALUES
(1, 'Saw Baw', '$argon2id$v=19$m=65536,t=3,p=4$X2AllK8coV7nAPK/WGsbkQ$svi3K2YxtZG9GRK601IagHI/TzVZi93A/dokpPeQlq0', 'Saw Baw Mu Thaw', '0122334455', 'thawthibaw@gmail.com', 25000000, 'Software Engineering'),
(2, 'Saw Harry', '$argon2id$v=19$m=65536,t=3,p=4$7uG15o/JLg6TlmNunfTUEw$vHzQAGwW0P3oq4Vq/2Uvb0AU3kyWNFguhGnHcmZ+//M', 'Saw Harry', '0322442211', 'vestarex20@gmail.com', 25000000, 'Software Engineering');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `transaction_id` int(11) NOT NULL,
  `payer_id` int(11) NOT NULL,
  `receiver_id` varchar(8) NOT NULL,
  `debt_id` int(11) NOT NULL,
  `amount` decimal(12,0) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `initiated_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `failure_reason` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tuition_debt`
--

CREATE TABLE `tuition_debt` (
  `debt_id` int(11) NOT NULL,
  `student_id` varchar(8) NOT NULL,
  `amount` decimal(12,0) DEFAULT NULL,
  `semester` varchar(20) DEFAULT NULL,
  `academic_year` varchar(10) DEFAULT NULL,
  `status` varchar(10) DEFAULT 'UNPAID',
  `due_date` datetime DEFAULT NULL,
  `paid_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tuition_debt`
--

INSERT INTO `tuition_debt` (`debt_id`, `student_id`, `amount`, `semester`, `academic_year`, `status`, `due_date`, `paid_date`, `created_at`, `updated_at`) VALUES
(1, '523K0077', 2500000, 'SEMESTER 1', '2025-2026', 'UNPAID', '2025-12-30 18:00:00', NULL, '2025-10-30 19:57:17', NULL),
(2, '523K0034', 2500000, 'SEMESTER 2', '2025-2026', 'UNPAID', '2025-12-30 18:00:00', NULL, '2025-10-30 19:57:17', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`customer_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`transaction_id`);

--
-- Indexes for table `tuition_debt`
--
ALTER TABLE `tuition_debt`
  ADD PRIMARY KEY (`debt_id`),
  ADD UNIQUE KEY `student_id` (`student_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `transaction_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tuition_debt`
--
ALTER TABLE `tuition_debt`
  MODIFY `debt_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
