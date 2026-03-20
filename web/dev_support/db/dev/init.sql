-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: snowball_testdb
-- ------------------------------------------------------
-- Server version	5.7.40-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `snowball_testdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `snowball_testdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `snowball_testdb`;

--
-- Table structure for table `apscheduler_jobs`
--

DROP TABLE IF EXISTS `apscheduler_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apscheduler_jobs` (
  `id` varchar(191) NOT NULL,
  `next_run_time` double DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_apscheduler_jobs_next_run_time` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `grid_detail`
--

DROP TABLE IF EXISTS `grid_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grid_detail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fund_id` bigint(20) NOT NULL,
  `grid_name` varchar(255) NOT NULL,
  `fund_name` varchar(255) NOT NULL,
  `gear` varchar(255) NOT NULL,
  `purchase_price` float NOT NULL,
  `purchase_amount` float NOT NULL,
  `purchase_shares` int(11) NOT NULL,
  `trigger_purchase_price` float NOT NULL,
  `trigger_sell_price` float NOT NULL,
  `sell_price` float NOT NULL,
  `sell_shares` int(11) NOT NULL,
  `actual_sell_shares` int(11) NOT NULL,
  `sell_amount` float NOT NULL,
  `profit` float NOT NULL,
  `save_share_profit` float NOT NULL,
  `save_share` int(11) NOT NULL,
  `grid_id` bigint(20) NOT NULL,
  `is_current` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `grid_record`
--

DROP TABLE IF EXISTS `grid_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grid_record` (
  `grid_id` bigint(20) NOT NULL,
  `record_id` bigint(20) NOT NULL,
  PRIMARY KEY (`grid_id`,`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `irecord`
--

DROP TABLE IF EXISTS `irecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `irecord` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `trade_date` datetime NOT NULL,
  `code` varchar(255) NOT NULL,
  `value` float NOT NULL,
  `share` int(11) NOT NULL,
  `fee` float NOT NULL,
  `type` int(11) NOT NULL,
  `notice_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `path` varchar(255) NOT NULL,
  `component` varchar(255) DEFAULT NULL,
  `hidden` int(11) DEFAULT NULL,
  `redirect` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  `is_frame` varchar(255) DEFAULT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notice`
--

DROP TABLE IF EXISTS `notice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notice` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notice_grid`
--

DROP TABLE IF EXISTS `notice_grid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notice_grid` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `notice_id` bigint(20) NOT NULL,
  `direction` int(11) NOT NULL,
  `value` float NOT NULL,
  `msg` varchar(255) NOT NULL,
  `fund_id` bigint(20) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `share` int(11) NOT NULL,
  `gear` varchar(255) NOT NULL,
  `grid_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_fund`
--

DROP TABLE IF EXISTS `stock_fund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_fund` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `base_code` varchar(255) NOT NULL,
  `xq_code` varchar(255) NOT NULL,
  `ttjj_code` varchar(255) NOT NULL,
  `fund_name` varchar(255) NOT NULL,
  `index_code` varchar(255) DEFAULT NULL,
  `index_name` varchar(255) DEFAULT NULL,
  `update_time` datetime NOT NULL,
  `create_time` datetime NOT NULL,
  `of_code` varchar(255) DEFAULT NULL,
  `fund_price` float DEFAULT NULL,
  `fund_value` float DEFAULT NULL,
  `fund_value_date` datetime DEFAULT NULL,
  `fund_price_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset`
--

DROP TABLE IF EXISTS `tb_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `currency` int(11) DEFAULT NULL COMMENT '货币类型,0:人民币,1:美元',
  `asset_type` int(11) NOT NULL DEFAULT '0' COMMENT '资产类型,0:指数，1-基金，2-股票',
  `asset_name` varchar(255) NOT NULL,
  `market` int(11) DEFAULT NULL COMMENT '所在市场:0-CN中国,1-HK香港,2-US美国',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13056 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_category`
--

DROP TABLE IF EXISTS `tb_asset_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_category` (
  `asset_id` bigint(20) NOT NULL COMMENT '证券ID',
  `category_id` bigint(20) NOT NULL COMMENT '分类ID',
  PRIMARY KEY (`asset_id`,`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='证券分类关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_code`
--

DROP TABLE IF EXISTS `tb_asset_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_code` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产类型ID',
  `code_ttjj` varchar(20) DEFAULT NULL COMMENT '天天基金代码',
  `code_xq` varchar(20) DEFAULT NULL COMMENT '雪球代码',
  `code_index` varchar(20) DEFAULT NULL COMMENT '指数代码，指数基金特有',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6539 DEFAULT CHARSET=utf8mb4 COMMENT='证券代码表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_fund_daily_data`
--

DROP TABLE IF EXISTS `tb_asset_fund_daily_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_fund_daily_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL,
  `f_date` datetime DEFAULT NULL,
  `f_open` int(11) DEFAULT NULL COMMENT '开盘价（单位：毫）',
  `f_close` int(11) DEFAULT NULL COMMENT '收盘价（单位：毫）',
  `f_high` int(11) DEFAULT NULL COMMENT '当日最高价（单位：毫）',
  `f_low` int(11) DEFAULT NULL COMMENT '当日最低价（单位：毫）',
  `f_volume` bigint(20) DEFAULT NULL COMMENT '当日成交量',
  `f_close_percent` int(11) DEFAULT NULL COMMENT '日收盘价涨幅（百万倍）',
  `f_totvalue` int(11) DEFAULT NULL COMMENT '累计净值（单位：毫，当资产没有天天基金代码时，无法获取累计净值）',
  `f_netvalue` int(11) DEFAULT NULL COMMENT '当日净值（单位：毫，当资产没有天天基金代码时，无法获取当日净值）',
  `f_comment` int(11) DEFAULT NULL COMMENT '分红或下折（单位：毫）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7101 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_fund_fee_rule`
--

DROP TABLE IF EXISTS `tb_asset_fund_fee_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_fund_fee_rule` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `ge_than` int(11) DEFAULT NULL COMMENT '大于（单位w/day）',
  `less_than` int(11) DEFAULT NULL COMMENT '小于（单位w/day）',
  `fee_rates` int(11) NOT NULL DEFAULT '0' COMMENT '费率（百分比整数）',
  `fee_type` int(11) NOT NULL COMMENT '0:买入,1:卖出',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_holding_data`
--

DROP TABLE IF EXISTS `tb_asset_holding_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_holding_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '证券资产对应的数据库ID',
  `ah_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '统计日期',
  `ah_asset_name` varchar(255) NOT NULL COMMENT '持有资产名称',
  `ah_holding_asset_id` bigint(20) NOT NULL COMMENT '持有者的证券资产ID',
  `ah_holding_percent` int(11) DEFAULT NULL COMMENT '持有百分比（千倍）',
  `ah_percent` int(11) DEFAULT NULL COMMENT '涨跌幅（千倍）',
  `ah_quarter` int(11) NOT NULL COMMENT '季度（1，2，3，4）',
  `ah_year` int(4) NOT NULL COMMENT '年份',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_category`
--

DROP TABLE IF EXISTS `tb_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_category` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(50) NOT NULL,
  `pid` bigint(20) NOT NULL DEFAULT '0',
  `ancestor` varchar(255) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid`
--

DROP TABLE IF EXISTS `tb_grid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `grid_name` varchar(255) NOT NULL COMMENT '网格名称',
  `grid_status` int(11) NOT NULL DEFAULT '0' COMMENT '网格状态,0-启用，1-停用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_grid_analysis_data`
--

DROP TABLE IF EXISTS `tb_grid_grid_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_grid_analysis_data` (
  `grid_id` bigint(20) NOT NULL COMMENT '网格ID',
  `grid_analysis_data_id` bigint(20) NOT NULL COMMENT '网格交易数据表ID',
  `transaction_analysis_data_id` bigint(20) NOT NULL COMMENT '交易数据分析ID',
  PRIMARY KEY (`grid_id`,`grid_analysis_data_id`,`transaction_analysis_data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网格_网格交易数据关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_transaction_analysis_data`
--

DROP TABLE IF EXISTS `tb_grid_transaction_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_transaction_analysis_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `record_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间，一类交易一般来说一条只有一条数据',
  `transaction_analysis_data_id` bigint(20) NOT NULL COMMENT '关联交易分表ID',
  `sell_times` int(10) NOT NULL DEFAULT '0' COMMENT '出售次数',
  `estimate_maximum_occupancy` int(10) NOT NULL DEFAULT '0' COMMENT '预估剩余最大占用金额（单位：分）',
  `holding_times` int(10) NOT NULL DEFAULT '0' COMMENT '待出网次数',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COMMENT='网格交易分析表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type`
--

DROP TABLE IF EXISTS `tb_grid_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `grid_id` bigint(20) NOT NULL,
  `grid_type_status` int(11) NOT NULL DEFAULT '0' COMMENT '0:启用,1:停用,2:只卖出,3只买入',
  `type_name` varchar(255) NOT NULL COMMENT '网格类型名称',
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type_detail`
--

DROP TABLE IF EXISTS `tb_grid_type_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type_detail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `grid_type_id` bigint(20) NOT NULL COMMENT '网格类型ID',
  `grid_id` bigint(20) NOT NULL COMMENT '对应的网格ID',
  `gear` varchar(255) NOT NULL COMMENT '档位',
  `trigger_purchase_price` int(11) NOT NULL COMMENT '买入触发价格（单位:厘）',
  `purchase_price` int(11) NOT NULL COMMENT '买入价格（单位:厘）',
  `purchase_amount` int(11) NOT NULL COMMENT '买入金额（单位:厘）',
  `purchase_shares` int(11) NOT NULL COMMENT '入股数',
  `trigger_sell_price` int(11) NOT NULL COMMENT '卖出触发价（单位:厘）',
  `sell_price` int(11) NOT NULL COMMENT '卖出价格（单位:厘）',
  `sell_shares` int(11) NOT NULL COMMENT '出股数',
  `actual_sell_shares` int(11) NOT NULL COMMENT '实际出股数',
  `sell_amount` int(11) NOT NULL COMMENT '卖出金额（单位:厘）',
  `profit` int(11) NOT NULL COMMENT '收益（单位:厘）',
  `save_share_profit` int(11) NOT NULL COMMENT '留股收益（单位:厘）',
  `save_share` int(11) NOT NULL COMMENT '留存股数',
  `is_current` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否处于当前档位(0否，1是)',
  `monitor_type` tinyint(1) NOT NULL DEFAULT '0' COMMENT '监控类型：0-买入，1-卖出',
  PRIMARY KEY (`id`),
  KEY `uk_grid_type_gear` (`grid_type_id`,`gear`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COMMENT='网格类型详情表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type_grid_analysis_data`
--

DROP TABLE IF EXISTS `tb_grid_type_grid_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type_grid_analysis_data` (
  `grid_type_id` bigint(20) NOT NULL COMMENT '网格类型数据ID',
  `grid_analysis_data_id` bigint(20) NOT NULL COMMENT '网格交易数据分析表ID',
  `transaction_data_id` bigint(20) NOT NULL COMMENT '交易分析数据ID',
  PRIMARY KEY (`grid_type_id`,`grid_analysis_data_id`,`transaction_data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网格类型_网格交易数据关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type_record`
--

DROP TABLE IF EXISTS `tb_grid_type_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type_record` (
  `grid_type_id` bigint(20) NOT NULL COMMENT '网格类型ID',
  `record_id` bigint(20) NOT NULL COMMENT '交易记录ID',
  PRIMARY KEY (`record_id`,`grid_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网格类型与交易记录的关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_notification`
--

DROP TABLE IF EXISTS `tb_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_notification` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `business_type` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知的业务类型，0-网格交易通知,1-消息处理提醒通知,2-系统运行通知,3-日常报告通知',
  `notice_type` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知的类型，0-消息型通知，1-确认型通知',
  `notice_status` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知的状态：0-未发送，1-未读，2-已读，3-已处理',
  `content` text,
  `timestamp` datetime DEFAULT NULL COMMENT '通知的时间，发送的时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
  `notice_level` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知重要性等级，重要性按数字递增，最小为0',
  `title` varchar(255) NOT NULL COMMENT '通知标题',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COMMENT='通知模型';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_record`
--

DROP TABLE IF EXISTS `tb_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `transactions_fee` int(11) NOT NULL DEFAULT '0' COMMENT '交易费用（单位：厘）',
  `transactions_share` int(11) NOT NULL DEFAULT '0' COMMENT '交易份额',
  `transactions_date` datetime NOT NULL COMMENT '交易时间',
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `transactions_price` int(11) NOT NULL DEFAULT '0' COMMENT '交易价格（单位：厘）',
  `transactions_direction` int(11) NOT NULL COMMENT '交易方向，0:卖出,1:买入',
  `transactions_amount` int(11) NOT NULL DEFAULT '0' COMMENT '交易金额（单位：厘）',
  `strategy_type` int(11) DEFAULT NULL,
  `strategy_key` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_task`
--

DROP TABLE IF EXISTS `tb_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_name` varchar(255) NOT NULL COMMENT '任务名称',
  `task_type` int(11) NOT NULL DEFAULT '0' COMMENT '任务类型（0一次性任务，1定时任务）',
  `task_status` int(11) DEFAULT '0' COMMENT '任务状态：0未执行，1等待执行，2执行中，3执行完毕',
  `business_type` int(11) NOT NULL COMMENT '业务类型（0获取资产数据，1更新收益数据，2同步资产数据）',
  `time_expression` varchar(20) DEFAULT NULL COMMENT '时间表达式',
  `next_run_time` datetime DEFAULT NULL COMMENT '下次运行时间',
  `time_consuming` int(11) NOT NULL DEFAULT '0' COMMENT '运行耗时（单位：秒）',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_task_asset`
--

DROP TABLE IF EXISTS `tb_task_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_task_asset` (
  `task_id` bigint(20) NOT NULL COMMENT '任务ID',
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  PRIMARY KEY (`task_id`,`asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_task_log`
--

DROP TABLE IF EXISTS `tb_task_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_task_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `task_id` bigint(20) NOT NULL COMMENT '任务ID',
  `business_type` int(11) NOT NULL COMMENT '业务类型-0初始化资产数据，1更新收益数据，2同步资产数据',
  `execute_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
  `execute_result` tinyint(1) NOT NULL DEFAULT '0' COMMENT '执行结果0-失败，1-成功',
  `time_consuming` int(11) NOT NULL DEFAULT '0' COMMENT '运行耗时（单位：毫秒）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `remark` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_transaction_analysis_data`
--

DROP TABLE IF EXISTS `tb_transaction_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_transaction_analysis_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `maximum_occupancy` int(11) DEFAULT NULL COMMENT '历史最大占用（单位：分）',
  `unit_cost` int(11) DEFAULT NULL COMMENT '单位成本（单位：毫）',
  `purchase_amount` int(11) DEFAULT NULL COMMENT '申购总额（单位：分）',
  `present_value` int(11) DEFAULT NULL COMMENT '基金现值（分）',
  `irr` int(11) DEFAULT NULL,
  `investment_yield` int(11) DEFAULT NULL COMMENT '投资收益率（万倍）',
  `turnover_rate` int(11) DEFAULT NULL COMMENT '换手率（万倍）',
  `analysis_type` int(11) DEFAULT NULL COMMENT '分析类型：0-网格，1-网格类型，2-网格策略',
  `attributable_share` int(11) DEFAULT NULL COMMENT '持有成本（单位：分）',
  `holding_cost` int(11) DEFAULT NULL COMMENT '持有成本（单位：分）',
  `dividend` int(11) DEFAULT NULL COMMENT '分红与赎回（单位：分）',
  `profit` int(11) DEFAULT NULL COMMENT '收益总额（单位：分）',
  `net_value` int(11) DEFAULT NULL COMMENT '当日净值（单位：厘）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `record_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录日期',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COMMENT='交易分析数据表，不包含业务';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `snowball`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `snowball` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `snowball`;

--
-- Table structure for table `apscheduler_jobs`
--

DROP TABLE IF EXISTS `apscheduler_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apscheduler_jobs` (
  `id` varchar(191) NOT NULL,
  `next_run_time` double DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_apscheduler_jobs_next_run_time` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `grid_detail`
--

DROP TABLE IF EXISTS `grid_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grid_detail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fund_id` bigint(20) NOT NULL,
  `grid_name` varchar(255) NOT NULL,
  `fund_name` varchar(255) NOT NULL,
  `gear` varchar(255) NOT NULL,
  `purchase_price` float NOT NULL,
  `purchase_amount` float NOT NULL,
  `purchase_shares` int(11) NOT NULL,
  `trigger_purchase_price` float NOT NULL,
  `trigger_sell_price` float NOT NULL,
  `sell_price` float NOT NULL,
  `sell_shares` int(11) NOT NULL,
  `actual_sell_shares` int(11) NOT NULL,
  `sell_amount` float NOT NULL,
  `profit` float NOT NULL,
  `save_share_profit` float NOT NULL,
  `save_share` int(11) NOT NULL,
  `grid_id` bigint(20) NOT NULL,
  `is_current` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `grid_record`
--

DROP TABLE IF EXISTS `grid_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grid_record` (
  `grid_id` bigint(20) NOT NULL,
  `record_id` bigint(20) NOT NULL,
  PRIMARY KEY (`grid_id`,`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `irecord`
--

DROP TABLE IF EXISTS `irecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `irecord` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `trade_date` datetime NOT NULL,
  `code` varchar(255) NOT NULL,
  `value` float NOT NULL,
  `share` int(11) NOT NULL,
  `fee` float NOT NULL,
  `type` int(11) NOT NULL,
  `notice_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `path` varchar(255) NOT NULL,
  `component` varchar(255) DEFAULT NULL,
  `hidden` int(11) DEFAULT NULL,
  `redirect` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  `is_frame` varchar(255) DEFAULT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notice`
--

DROP TABLE IF EXISTS `notice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notice` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notice_grid`
--

DROP TABLE IF EXISTS `notice_grid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notice_grid` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `notice_id` bigint(20) NOT NULL,
  `direction` int(11) NOT NULL,
  `value` float NOT NULL,
  `msg` varchar(255) NOT NULL,
  `fund_id` bigint(20) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `share` int(11) NOT NULL,
  `gear` varchar(255) NOT NULL,
  `grid_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_fund`
--

DROP TABLE IF EXISTS `stock_fund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_fund` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `base_code` varchar(255) NOT NULL,
  `xq_code` varchar(255) NOT NULL,
  `ttjj_code` varchar(255) NOT NULL,
  `fund_name` varchar(255) NOT NULL,
  `index_code` varchar(255) DEFAULT NULL,
  `index_name` varchar(255) DEFAULT NULL,
  `update_time` datetime NOT NULL,
  `create_time` datetime NOT NULL,
  `of_code` varchar(255) DEFAULT NULL,
  `fund_price` float DEFAULT NULL,
  `fund_value` float DEFAULT NULL,
  `fund_value_date` datetime DEFAULT NULL,
  `fund_price_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset`
--

DROP TABLE IF EXISTS `tb_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `currency` int(11) DEFAULT NULL COMMENT '货币类型,0:人民币,1:美元',
  `asset_type` int(11) NOT NULL DEFAULT '0' COMMENT '资产类型,0:指数，1-基金，2-股票',
  `asset_name` varchar(255) NOT NULL,
  `market` int(11) DEFAULT NULL COMMENT '所在市场:0-CN中国,1-HK香港,2-US美国',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5838 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_category`
--

DROP TABLE IF EXISTS `tb_asset_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_category` (
  `asset_id` bigint(20) NOT NULL COMMENT '证券ID',
  `category_id` bigint(20) NOT NULL COMMENT '分类ID',
  PRIMARY KEY (`asset_id`,`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='证券分类关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_code`
--

DROP TABLE IF EXISTS `tb_asset_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_code` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产类型ID',
  `code_ttjj` varchar(20) DEFAULT NULL COMMENT '天天基金代码',
  `code_xq` varchar(20) DEFAULT NULL COMMENT '雪球代码',
  `code_index` varchar(20) DEFAULT NULL COMMENT '指数代码，指数基金特有',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5827 DEFAULT CHARSET=utf8mb4 COMMENT='证券代码表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_fund_daily_data`
--

DROP TABLE IF EXISTS `tb_asset_fund_daily_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_fund_daily_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL,
  `f_date` datetime DEFAULT NULL,
  `f_open` int(11) DEFAULT NULL COMMENT '开盘价（单位：毫）',
  `f_close` int(11) DEFAULT NULL COMMENT '收盘价（单位：毫）',
  `f_high` int(11) DEFAULT NULL COMMENT '当日最高价（单位：毫）',
  `f_low` int(11) DEFAULT NULL COMMENT '当日最低价（单位：毫）',
  `f_volume` bigint(20) DEFAULT NULL COMMENT '当日成交量',
  `f_close_percent` int(11) DEFAULT NULL COMMENT '日收盘价涨幅（百万倍）',
  `f_totvalue` int(11) DEFAULT NULL COMMENT '累计净值（单位：毫，当资产没有天天基金代码时，无法获取累计净值）',
  `f_netvalue` int(11) DEFAULT NULL COMMENT '当日净值（单位：毫，当资产没有天天基金代码时，无法获取当日净值）',
  `f_comment` int(11) DEFAULT NULL COMMENT '分红或下折（单位：毫）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21820 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_fund_fee_rule`
--

DROP TABLE IF EXISTS `tb_asset_fund_fee_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_fund_fee_rule` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `ge_than` int(11) DEFAULT NULL COMMENT '大于（单位w/day）',
  `less_than` int(11) DEFAULT NULL COMMENT '小于（单位w/day）',
  `fee_rates` int(11) NOT NULL DEFAULT '0' COMMENT '费率（百分比整数）',
  `fee_type` int(11) NOT NULL COMMENT '0:买入,1:卖出',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_asset_holding_data`
--

DROP TABLE IF EXISTS `tb_asset_holding_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_asset_holding_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '证券资产对应的数据库ID',
  `ah_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '统计日期',
  `ah_asset_name` varchar(255) NOT NULL COMMENT '持有资产名称',
  `ah_holding_asset_id` bigint(20) NOT NULL COMMENT '持有者的证券资产ID',
  `ah_holding_percent` int(11) DEFAULT NULL COMMENT '持有百分比（千倍）',
  `ah_percent` int(11) DEFAULT NULL COMMENT '涨跌幅（千倍）',
  `ah_quarter` int(11) NOT NULL COMMENT '季度（1，2，3，4）',
  `ah_year` int(4) NOT NULL COMMENT '年份',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=194 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_category`
--

DROP TABLE IF EXISTS `tb_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_category` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(50) NOT NULL,
  `pid` bigint(20) NOT NULL DEFAULT '0',
  `ancestor` varchar(255) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid`
--

DROP TABLE IF EXISTS `tb_grid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `grid_name` varchar(255) NOT NULL COMMENT '网格名称',
  `grid_status` int(11) NOT NULL DEFAULT '0' COMMENT '网格状态,0-启用，1-停用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_grid_analysis_data`
--

DROP TABLE IF EXISTS `tb_grid_grid_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_grid_analysis_data` (
  `grid_id` bigint(20) NOT NULL COMMENT '网格ID',
  `grid_analysis_data_id` bigint(20) NOT NULL COMMENT '网格交易数据表ID',
  `transaction_analysis_data_id` bigint(20) NOT NULL COMMENT '交易数据分析ID',
  PRIMARY KEY (`grid_id`,`grid_analysis_data_id`,`transaction_analysis_data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网格_网格交易数据关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_transaction_analysis_data`
--

DROP TABLE IF EXISTS `tb_grid_transaction_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_transaction_analysis_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `record_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间，一类交易一般来说一条只有一条数据',
  `transaction_analysis_data_id` bigint(20) NOT NULL COMMENT '关联交易分表ID',
  `sell_times` int(10) NOT NULL DEFAULT '0' COMMENT '出售次数',
  `estimate_maximum_occupancy` int(10) NOT NULL DEFAULT '0' COMMENT '预估剩余最大占用金额（单位：厘）',
  `holding_times` int(10) NOT NULL DEFAULT '0' COMMENT '待出网次数',
  `up_sold_percent` int(10) NOT NULL DEFAULT '0' COMMENT '距离卖出需要上涨的数量（万倍）',
  `down_bought_percent` int(10) NOT NULL DEFAULT '0' COMMENT '距离买入需要下跌的数量（万倍）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COMMENT='网格交易分析表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type`
--

DROP TABLE IF EXISTS `tb_grid_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `grid_id` bigint(20) NOT NULL,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `grid_type_status` int(11) NOT NULL DEFAULT '0' COMMENT '0:启用,1:停用,2:只卖出,3只买入',
  `type_name` varchar(255) NOT NULL COMMENT '网格类型名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type_detail`
--

DROP TABLE IF EXISTS `tb_grid_type_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type_detail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `grid_type_id` bigint(20) NOT NULL COMMENT '网格类型ID',
  `grid_id` bigint(20) NOT NULL COMMENT '对应的网格ID',
  `gear` varchar(255) NOT NULL COMMENT '档位',
  `trigger_purchase_price` int(11) NOT NULL COMMENT '买入触发价格（单位:厘）',
  `purchase_price` int(11) NOT NULL COMMENT '买入价格（单位:厘）',
  `purchase_amount` int(11) NOT NULL COMMENT '买入金额（单位:厘）',
  `purchase_shares` int(11) NOT NULL COMMENT '入股数',
  `trigger_sell_price` int(11) NOT NULL COMMENT '卖出触发价（单位:厘）',
  `sell_price` int(11) NOT NULL COMMENT '卖出价格（单位:厘）',
  `sell_shares` int(11) NOT NULL COMMENT '出股数',
  `actual_sell_shares` int(11) NOT NULL COMMENT '实际出股数',
  `sell_amount` int(11) NOT NULL COMMENT '卖出金额（单位:厘）',
  `profit` int(11) NOT NULL COMMENT '收益（单位:厘）',
  `save_share_profit` int(11) NOT NULL COMMENT '留股收益（单位:厘）',
  `save_share` int(11) NOT NULL COMMENT '留存股数',
  `is_current` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否处于当前档位(0否，1是)',
  `monitor_type` tinyint(1) NOT NULL DEFAULT '0' COMMENT '监控类型：0-买入，1-卖出',
  PRIMARY KEY (`id`),
  KEY `uk_grid_type_gear` (`grid_type_id`,`gear`)
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COMMENT='网格类型详情表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type_grid_analysis_data`
--

DROP TABLE IF EXISTS `tb_grid_type_grid_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type_grid_analysis_data` (
  `grid_type_id` bigint(20) NOT NULL COMMENT '网格类型数据ID',
  `grid_analysis_data_id` bigint(20) NOT NULL COMMENT '网格交易数据分析表ID',
  `transaction_analysis_data_id` bigint(20) NOT NULL COMMENT '交易分析数据ID',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`grid_type_id`,`grid_analysis_data_id`,`transaction_analysis_data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网格类型_网格交易数据关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_grid_type_record`
--

DROP TABLE IF EXISTS `tb_grid_type_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_grid_type_record` (
  `grid_type_id` bigint(20) NOT NULL COMMENT '网格类型ID',
  `record_id` bigint(20) NOT NULL COMMENT '交易记录ID',
  PRIMARY KEY (`record_id`,`grid_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网格类型与交易记录的关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_notification`
--

DROP TABLE IF EXISTS `tb_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_notification` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `business_type` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知的业务类型，0-网格交易通知,1-消息处理通知,2-系统运行通知',
  `notice_type` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知的业务类型，0-网格交易通知,1-消息处理提醒通知,2-系统运行通知,3-日常报告通知',
  `notice_status` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知的状态：0-未发送，1-未读，2-已读，3-已处理',
  `content` text,
  `timestamp` datetime DEFAULT NULL COMMENT '通知的时间，发送的时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
  `notice_level` tinyint(2) NOT NULL DEFAULT '0' COMMENT '通知重要性等级，重要性按数字递增，最小为0',
  `title` varchar(255) NOT NULL COMMENT '通知标题',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COMMENT='通知模型';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_record`
--

DROP TABLE IF EXISTS `tb_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `transactions_fee` int(11) NOT NULL DEFAULT '0' COMMENT '交易费用（单位：厘）',
  `transactions_share` int(11) NOT NULL DEFAULT '0' COMMENT '交易份额',
  `transactions_date` datetime NOT NULL COMMENT '交易时间',
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `transactions_price` int(11) NOT NULL DEFAULT '0' COMMENT '交易价格（单位：厘）',
  `transactions_direction` int(11) NOT NULL COMMENT '交易方向，0:卖出,1:买入',
  `transactions_amount` int(11) NOT NULL DEFAULT '0' COMMENT '交易金额（单位：厘）',
  `strategy_type` int(11) DEFAULT NULL,
  `strategy_key` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=287 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_task`
--

DROP TABLE IF EXISTS `tb_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_name` varchar(255) NOT NULL COMMENT '任务名称',
  `task_type` int(11) NOT NULL DEFAULT '0' COMMENT '任务类型（0一次性任务，1定时任务）',
  `task_status` int(11) DEFAULT '0' COMMENT '任务状态：0未执行，1等待执行，2执行中，3执行完毕',
  `business_type` int(11) NOT NULL COMMENT '业务类型（0获取资产数据，1更新收益数据，2同步资产数据）',
  `time_expression` varchar(20) DEFAULT NULL COMMENT '时间表达式',
  `next_run_time` datetime DEFAULT NULL COMMENT '下次运行时间',
  `time_consuming` int(11) NOT NULL DEFAULT '0' COMMENT '运行耗时（单位：秒）',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_task_asset`
--

DROP TABLE IF EXISTS `tb_task_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_task_asset` (
  `task_id` bigint(20) NOT NULL COMMENT '任务ID',
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  PRIMARY KEY (`task_id`,`asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_task_log`
--

DROP TABLE IF EXISTS `tb_task_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_task_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) NOT NULL COMMENT '资产ID',
  `task_id` bigint(20) NOT NULL COMMENT '任务ID',
  `business_type` int(11) NOT NULL COMMENT '业务类型-0初始化资产数据，1更新收益数据，2同步资产数据',
  `execute_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
  `execute_result` tinyint(1) NOT NULL DEFAULT '0' COMMENT '执行结果0-失败，1-成功',
  `time_consuming` int(11) NOT NULL DEFAULT '0' COMMENT '运行耗时（单位：毫秒）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `remark` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tb_transaction_analysis_data`
--

DROP TABLE IF EXISTS `tb_transaction_analysis_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tb_transaction_analysis_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asset_id` bigint(20) DEFAULT NULL COMMENT '对应的资产ID，部分业务，如总计数据没有资产ID',
  `maximum_occupancy` int(11) DEFAULT NULL COMMENT '历史最大占用（单位：分）',
  `unit_cost` int(11) DEFAULT NULL COMMENT '单位成本（单位：毫）',
  `purchase_amount` int(11) DEFAULT NULL COMMENT '申购总额（单位：分）',
  `present_value` int(11) DEFAULT NULL COMMENT '基金现值（分）',
  `irr` int(11) DEFAULT NULL,
  `investment_yield` int(11) DEFAULT NULL COMMENT '投资收益率（万倍）',
  `turnover_rate` int(11) DEFAULT NULL COMMENT '换手率（万倍）',
  `analysis_type` int(11) DEFAULT NULL COMMENT '分析类型：0-网格，1-网格类型，2-网格策略，3-按仓位分析',
  `attributable_share` int(11) DEFAULT NULL COMMENT '持有成本（单位：分）',
  `holding_cost` int(11) DEFAULT NULL COMMENT '持有成本（单位：分）',
  `dividend` int(11) DEFAULT NULL COMMENT '分红与赎回（单位：分）',
  `profit` int(11) DEFAULT NULL COMMENT '收益总额（单位：分）',
  `net_value` int(11) DEFAULT NULL COMMENT '当日净值（单位：厘）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `record_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录日期',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=255 DEFAULT CHARSET=utf8mb4 COMMENT='交易分析数据表，不包含业务';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `snowball_data`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `snowball_data` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `snowball_data`;

--
-- Table structure for table `xa001403`
--

DROP TABLE IF EXISTS `xa001403`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa001403` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa002027`
--

DROP TABLE IF EXISTS `xa002027`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa002027` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa159920`
--

DROP TABLE IF EXISTS `xa159920`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa159920` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa159938`
--

DROP TABLE IF EXISTS `xa159938`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa159938` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa162411`
--

DROP TABLE IF EXISTS `xa162411`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa162411` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa512880`
--

DROP TABLE IF EXISTS `xa512880`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa512880` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa512980`
--

DROP TABLE IF EXISTS `xa512980`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa512980` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa513050`
--

DROP TABLE IF EXISTS `xa513050`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa513050` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_f006327`
--

DROP TABLE IF EXISTS `xq_f006327`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_f006327` (
  `date` datetime DEFAULT NULL,
  `close` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sh512880`
--

DROP TABLE IF EXISTS `xq_sh512880`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sh512880` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sh512980`
--

DROP TABLE IF EXISTS `xq_sh512980`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sh512980` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sh513050`
--

DROP TABLE IF EXISTS `xq_sh513050`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sh513050` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sz159920`
--

DROP TABLE IF EXISTS `xq_sz159920`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sz159920` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sz162411`
--

DROP TABLE IF EXISTS `xq_sz162411`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sz162411` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `snowball_data_testdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `snowball_data_testdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `snowball_data_testdb`;

--
-- Table structure for table `xa162411`
--

DROP TABLE IF EXISTS `xa162411`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa162411` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xa513050`
--

DROP TABLE IF EXISTS `xa513050`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xa513050` (
  `comment` text,
  `date` datetime DEFAULT NULL,
  `netvalue` double DEFAULT NULL,
  `totvalue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sh513050`
--

DROP TABLE IF EXISTS `xq_sh513050`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sh513050` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xq_sz162411`
--

DROP TABLE IF EXISTS `xq_sz162411`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `xq_sz162411` (
  `date` datetime DEFAULT NULL,
  `open` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `snowball_profiler`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `snowball_profiler` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `snowball_profiler`;

--
-- Table structure for table `flask_profiler_measurements`
--

DROP TABLE IF EXISTS `flask_profiler_measurements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flask_profiler_measurements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `startedAt` decimal(10,0) DEFAULT NULL,
  `endedAt` decimal(10,0) DEFAULT NULL,
  `elapsed` decimal(6,4) DEFAULT NULL,
  `method` text,
  `args` text,
  `kwargs` text,
  `name` text,
  `context` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5817 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-04-22 18:59:38
