/*
 Navicat Premium Data Transfer

 Source Server         : wifiobd
 Source Server Type    : MySQL
 Source Server Version : 50740
 Source Host           : localhost:3306
 Source Schema         : opencart

 Target Server Type    : MySQL
 Target Server Version : 50740
 File Encoding         : 65001

 Date: 08/03/2026 14:38:05
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for oc_complectation_to_device
-- ----------------------------
DROP TABLE IF EXISTS `oc_complectation_to_device`;
CREATE TABLE `oc_complectation_to_device` (
  `complectation_id` int(11) NOT NULL,
  `serial` varchar(255) NOT NULL,
  `date_added` datetime NOT NULL,
  UNIQUE KEY `complectation_serial` (`complectation_id`,`serial`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

SET FOREIGN_KEY_CHECKS = 1;
