SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `arrosage`
--

DROP DATABASE IF EXISTS arrosage;
CREATE DATABASE arrosage;

USE arrosage; 

-- --------------------------------------------------------

--
-- Table structure for table `Categories`
--

CREATE TABLE `Categories` (
  `id_category` int(11) NOT NULL,
  `lower_limit` int(11) NOT NULL,
  `upper_limit` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Categories`
--

INSERT INTO `Categories` (`id_category`, `lower_limit`, `upper_limit`) VALUES
(1, 30, 50),
(2, 40, 70),
(3, 50, 90);

-- --------------------------------------------------------

--
-- Table structure for table `Flowerpot`
--

CREATE TABLE `Flowerpot` (
  `id_flowerpot` int(11) NOT NULL,
  `id_plant` int(11) NOT NULL,
  `id_sensor` int(11) NOT NULL,
  `id_solenoid` int(11) NOT NULL,
  `mode` enum('real','model') NOT NULL DEFAULT 'real',
  `is_irrigated` tinyint(1) NOT NULL DEFAULT 1,
  `volume` float NOT NULL,
  `area` float NOT NULL,
  `rest_moisture` float NOT NULL DEFAULT 0
) ;

-- --------------------------------------------------------

--
-- Table structure for table `PinSensor`
--

CREATE TABLE `PinSensor` (
  `Number` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `PinSensor`
--

INSERT INTO `PinSensor` (`Number`) VALUES
(0),
(1),
(2),
(3),
(4),
(5),
(6),
(7);

-- --------------------------------------------------------

--
-- Table structure for table `PinSolenoid`
--

CREATE TABLE `PinSolenoid` (
  `Number` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `PinSolenoid`
--

INSERT INTO `PinSolenoid` (`Number`) VALUES
(14),
(15),
(17),
(18),
(22),
(23),
(24),
(27);

-- --------------------------------------------------------

--
-- Table structure for table `Plant`
--

CREATE TABLE `Plant` (
  `id_plant` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `id_category` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Sensor`
--

CREATE TABLE `Sensor` (
  `id_sensor` int(11) NOT NULL,
  `pin_sensor` int(11) NOT NULL,
  `max_humidity` int(11) NOT NULL,
  `min_humidity` int(11) NOT NULL,
  `isTrusted` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Session`
--

CREATE TABLE `Session` (
  `id_session` int(11) NOT NULL,
  `datetime` datetime NOT NULL,
  `id_flowerpot` int(11) NOT NULL,
  `duration` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Solenoide`
--

CREATE TABLE `Solenoide` (
  `id_solenoid` int(11) NOT NULL,
  `pin_solenoid` int(11) NOT NULL,
  `capacity` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `TemperatureData`
--

CREATE TABLE `TemperatureData` (
  `id_category` int(11) NOT NULL,
  `temperature` int(11) NOT NULL,
  `water` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `TemperatureData`
--

INSERT INTO `TemperatureData` (`id_category`, `temperature`, `water`) VALUES
(1, 10, 4.23);
(1, 20, 8.46);
(1, 30, 12.7);
(1, 40, 16.93);
(1, 50, 25.39);
(2, 10, 35.71);
(2, 20, 71.43);
(2, 30, 107.14);
(2, 40, 142.86);
(2, 50, 214.29);
(3, 10, 214.29);
(3, 20, 428.57);
(3, 30, 571.43);
(3, 40, 714.29);
(3, 50, 1142.86);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Categories`
--
ALTER TABLE `Categories`
  ADD PRIMARY KEY (`id_category`);

--
-- Indexes for table `Flowerpot`
--
ALTER TABLE `Flowerpot`
  ADD PRIMARY KEY (`id_flowerpot`),
  ADD KEY `fk_id_plant` (`id_plant`),
  ADD KEY `fk_id_sensor` (`id_sensor`),
  ADD KEY `fk_id_solenoid` (`id_solenoid`);

--
-- Indexes for table `PinSensor`
--
ALTER TABLE `PinSensor`
  ADD PRIMARY KEY (`Number`);

--
-- Indexes for table `PinSolenoid`
--
ALTER TABLE `PinSolenoid`
  ADD PRIMARY KEY (`Number`);

--
-- Indexes for table `Plant`
--
ALTER TABLE `Plant`
  ADD PRIMARY KEY (`id_plant`),
  ADD KEY `fk_id_category` (`id_category`);

--
-- Indexes for table `Sensor`
--
ALTER TABLE `Sensor`
  ADD PRIMARY KEY (`id_sensor`),
  ADD KEY `fk_pin_sensor` (`pin_sensor`);

--
-- Indexes for table `Session`
--
ALTER TABLE `Session`
  ADD PRIMARY KEY (`id_session`),
  ADD KEY `fk_id_flowerpot` (`id_flowerpot`);

--
-- Indexes for table `Solenoide`
--
ALTER TABLE `Solenoide`
  ADD PRIMARY KEY (`id_solenoid`),
  ADD KEY `fk_pin_solenoid` (`pin_solenoid`);

--
-- Indexes for table `TemperatureData`
--
ALTER TABLE `TemperatureData`
  ADD KEY `fk_id_category_td` (`id_category`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Categories`
--
ALTER TABLE `Categories`
  MODIFY `id_category` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Flowerpot`
--
ALTER TABLE `Flowerpot`
  MODIFY `id_flowerpot` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Plant`
--
ALTER TABLE `Plant`
  MODIFY `id_plant` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Sensor`
--
ALTER TABLE `Sensor`
  MODIFY `id_sensor` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Session`
--
ALTER TABLE `Session`
  MODIFY `id_session` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Solenoide`
--
ALTER TABLE `Solenoide`
  MODIFY `id_solenoid` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Flowerpot`
--
ALTER TABLE `Flowerpot`
  ADD CONSTRAINT `fk_id_plant` FOREIGN KEY (`id_plant`) REFERENCES `Plant` (`id_plant`),
  ADD CONSTRAINT `fk_id_sensor` FOREIGN KEY (`id_sensor`) REFERENCES `Sensor` (`id_sensor`),
  ADD CONSTRAINT `fk_id_solenoid` FOREIGN KEY (`id_solenoid`) REFERENCES `Solenoide` (`id_solenoid`);

--
-- Constraints for table `Plant`
--
ALTER TABLE `Plant`
  ADD CONSTRAINT `fk_id_category` FOREIGN KEY (`id_category`) REFERENCES `Categories` (`id_category`);

--
-- Constraints for table `Sensor`
--
ALTER TABLE `Sensor`
  ADD CONSTRAINT `fk_pin_sensor` FOREIGN KEY (`pin_sensor`) REFERENCES `PinSensor` (`Number`);

--
-- Constraints for table `Session`
--
ALTER TABLE `Session`
  ADD CONSTRAINT `fk_id_flowerpot` FOREIGN KEY (`id_flowerpot`) REFERENCES `Flowerpot` (`id_flowerpot`);

--
-- Constraints for table `Solenoide`
--
ALTER TABLE `Solenoide`
  ADD CONSTRAINT `fk_pin_solenoid` FOREIGN KEY (`pin_solenoid`) REFERENCES `PinSolenoid` (`Number`);

--
-- Constraints for table `TemperatureData`
--
ALTER TABLE `TemperatureData`
  ADD CONSTRAINT `fk_id_category_td` FOREIGN KEY (`id_category`) REFERENCES `Categories` (`id_category`);
COMMIT;
