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

 Date: 08/03/2026 14:37:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for oc_token_to_device
-- ----------------------------
DROP TABLE IF EXISTS `oc_token_to_device`;
CREATE TABLE `oc_token_to_device` (
  `token_id` int(11) NOT NULL,
  `serial` varchar(255) CHARACTER SET latin1 NOT NULL,
  `device_type` varchar(20) CHARACTER SET latin1 NOT NULL,
  `date_added` datetime NOT NULL,
  `comment` text COLLATE utf8mb4_bin,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_serial` (`serial`) USING BTREE,
  KEY `token` (`token_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1124 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

SET FOREIGN_KEY_CHECKS = 1;
