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

 Date: 08/03/2026 14:37:15
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for oc_tokens
-- ----------------------------
DROP TABLE IF EXISTS `oc_tokens`;
CREATE TABLE `oc_tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(255) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`) USING HASH,
  KEY `id` (`id`) USING BTREE,
  KEY `customer` (`customer_id`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=571 DEFAULT CHARSET=latin1;

SET FOREIGN_KEY_CHECKS = 1;
