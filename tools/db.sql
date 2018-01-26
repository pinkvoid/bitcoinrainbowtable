-- phpMyAdmin SQL Dump
-- version 4.6.6deb4
-- https://www.phpmyadmin.net/
--
-- Host: chip.log4.eu:33666
-- Generation Time: Jan 20, 2018 at 08:12 PM
-- Server version: 10.0.32-MariaDB-0+deb8u1
-- PHP Version: 7.0.27-0+deb9u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `rbt`
--

-- --------------------------------------------------------

--
-- Table structure for table `archive`
--

CREATE TABLE `archive` (
  `public_id` bigint(20) UNSIGNED NOT NULL,
  `pkey` binary(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin COMMENT='Private keys' ROW_FORMAT=COMPRESSED;

-- --------------------------------------------------------

--
-- Table structure for table `incoming`
--

CREATE TABLE `incoming` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `address` binary(24) NOT NULL,
  `private` binary(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=binary COMMENT='address 24 bytes without net prefix and private key';

-- --------------------------------------------------------

--
-- Table structure for table `public`
--

CREATE TABLE `public` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `address` varchar(33) NOT NULL COMMENT 'without 1 prefix'
) ENGINE=InnoDB DEFAULT CHARSET=ascii COMMENT='Addresses';

--
-- Indexes for dumped tables
--

--
-- Indexes for table `archive`
--
ALTER TABLE `archive`
  ADD KEY `public_id` (`public_id`);

--
-- Indexes for table `incoming`
--
ALTER TABLE `incoming`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `public`
--
ALTER TABLE `public`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `address` (`address`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `incoming`
--
ALTER TABLE `incoming`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
--
-- AUTO_INCREMENT for table `public`
--
ALTER TABLE `public`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
