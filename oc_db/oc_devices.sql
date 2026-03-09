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

 Date: 08/03/2026 14:37:41
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for oc_devices
-- ----------------------------
DROP TABLE IF EXISTS `oc_devices`;
CREATE TABLE `oc_devices` (
  `device_id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `device_type` varchar(40) NOT NULL,
  `device_name` varchar(40) NOT NULL,
  `device_serial` varchar(40) NOT NULL,
  `register_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `comment` text,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=175 DEFAULT CHARSET=latin1;

SET FOREIGN_KEY_CHECKS = 1;
