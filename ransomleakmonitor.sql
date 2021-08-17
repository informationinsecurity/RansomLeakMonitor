-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 17, 2021 at 02:12 PM
-- Server version: 8.0.26-0ubuntu0.20.04.2
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ransom`
--
CREATE DATABASE IF NOT EXISTS `ransom` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ransom`;

-- --------------------------------------------------------

--
-- Table structure for table `rw_images`
--

CREATE TABLE `rw_images` (
  `id` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `actor` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `photo` longblob NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `rw_status`
--

CREATE TABLE `rw_status` (
  `id` int NOT NULL,
  `actor` text NOT NULL,
  `last_seen` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `rw_victims`
--

CREATE TABLE `rw_victims` (
  `id` int NOT NULL,
  `actor` text NOT NULL,
  `url` text NOT NULL,
  `victim` text NOT NULL,
  `date` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `rw_images`
--
ALTER TABLE `rw_images`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `rw_status`
--
ALTER TABLE `rw_status`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `rw_victims`
--
ALTER TABLE `rw_victims`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `victim` (`victim`(128));

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `rw_images`
--
ALTER TABLE `rw_images`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `rw_status`
--
ALTER TABLE `rw_status`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `rw_victims`
--
ALTER TABLE `rw_victims`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

