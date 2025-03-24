-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Mar 24, 2025 at 03:05 PM
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
-- Database: `gesture_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `gestures`
--

CREATE TABLE `gestures` (
  `id` int(11) NOT NULL,
  `action` varchar(50) DEFAULT NULL,
  `gesture_data` text DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `gestures`
--

INSERT INTO `gestures` (`id`, `action`, `gesture_data`, `image_path`) VALUES
(21, 'next', '[153.82676814406005, 178.78030956652248, 174.80072123963092, 35.193086825525185, 61.21749431402262]', 'gesture_images/next_1740197221.png'),
(22, 'next', '[171.1817695592768, 68.46429727622814, 57.342137461103675, 44.702091200040186, 25.02335201404642]', 'gesture_images/next_1740631784.png'),
(23, 'next', '[176.46859956909987, 177.48288042447285, 178.70453965602533, 178.49098133338634, 178.05146541443315]', 'gesture_images/next_1740664467.png'),
(24, 'next', '[173.5591045328067, 178.01219365590399, 32.04020151085291, 49.00994218235604, 81.92432090972682]', 'gesture_images/next_1740664494.png'),
(25, 'start', '[165.9242075675111, 58.52560979081976, 34.302393673962364, 23.849837356390243, 10.504299380442866]', 'gesture_images/start_1740664526.png'),
(26, 'end', '[170.35585316786856, 176.2046144812126, 158.25539268798315, 148.8482006256773, 139.19186490699894]', 'gesture_images/end_1740664545.png');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`) VALUES
(1, 'abc', 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'),
(2, 'admin', 'admin'),
(3, 'admin1', '$2b$12$0BEAB.T4dItMA0ji0Z8dIeYeGmB0t5VCl5wuogcaaBW4QscG6HW/q');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `gestures`
--
ALTER TABLE `gestures`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `gestures`
--
ALTER TABLE `gestures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
