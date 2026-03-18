应用启动环境: default
配置类型: development
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 6239f6413907

ALTER TABLE menu CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE stock_fund CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '删除时间';

ALTER TABLE tb_apscheduler_log CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '数据创建时间';

ALTER TABLE tb_asset CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_asset_code CHANGE create_time create_time DATETIME NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_asset_fund_daily_data CHANGE create_time create_time DATETIME NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_asset_fund_fee_rule CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_asset_holding_data CHANGE ah_date ah_date DATETIME NOT NULL DEFAULT now() COMMENT '统计日期';

ALTER TABLE tb_grid_transaction_analysis_data CHANGE record_date record_date DATETIME NOT NULL DEFAULT now() COMMENT '记录时间，一类交易一般来说一条只有一条数据';

ALTER TABLE tb_grid_transaction_analysis_data CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_grid_type MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键';

ALTER TABLE tb_grid_type COMMENT '网格类型表';

ALTER TABLE tb_grid_type_detail MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';

ALTER TABLE tb_grid_type_detail MODIFY monitor_type INTEGER NOT NULL DEFAULT '0' COMMENT '监控类型：0-买入，1-卖出';

ALTER TABLE tb_grid_type_grid_analysis_data MODIFY grid_analysis_data_id BIGINT(20) NOT NULL COMMENT '网格交易数据分析表';

ALTER TABLE tb_grid_type_grid_analysis_data MODIFY transaction_analysis_data_id BIGINT(20) NOT NULL COMMENT '交易数据分析ID';

ALTER TABLE tb_grid_type_grid_analysis_data CHANGE create_time create_time DATETIME NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_notification MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT;

ALTER TABLE tb_notification MODIFY business_type TINYINT(2) NOT NULL DEFAULT '0' COMMENT '通知的业务类型，0-网格交易通知,1-消息处理提醒通知,2-系统运行通知,3-日常报告通知';

ALTER TABLE tb_notification MODIFY content TEXT NULL COMMENT '通知的内容';

ALTER TABLE tb_notification CHANGE timestamp timestamp DATETIME NULL COMMENT '通知的时间';

ALTER TABLE tb_notification CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_notification CHANGE update_time update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

ALTER TABLE tb_notification ALTER COLUMN notice_level SET DEFAULT now();

ALTER TABLE tb_notification_log CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '数据创建时间';

ALTER TABLE tb_notification_log COMMENT '通知日志表';

ALTER TABLE tb_record MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键';

ALTER TABLE tb_record MODIFY strategy_type INTEGER(11) NULL COMMENT '策略类型：0-网格';

ALTER TABLE tb_record MODIFY strategy_key BIGINT(20) NULL COMMENT '策略类型对应的具体策略ID';

ALTER TABLE tb_record COMMENT '交易记录表';

ALTER TABLE tb_task MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';

ALTER TABLE tb_task CHANGE update_time update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

ALTER TABLE tb_task CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_task_log MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';

ALTER TABLE tb_task_log ALTER COLUMN execute_time DROP DEFAULT;

ALTER TABLE tb_task_log ALTER COLUMN execute_result DROP DEFAULT;

ALTER TABLE tb_task_log ALTER COLUMN time_consuming DROP DEFAULT;

ALTER TABLE tb_task_log CHANGE create_time create_time DATETIME NOT NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_task_log MODIFY remark VARCHAR(500) NOT NULL COMMENT '备注';

ALTER TABLE tb_transaction_analysis_data MODIFY id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';

ALTER TABLE tb_transaction_analysis_data CHANGE record_date record_date DATETIME NOT NULL DEFAULT now() COMMENT '记录时间';

ALTER TABLE tb_transaction_analysis_data MODIFY irr INTEGER(11) NULL COMMENT '内部收益率（万倍）';

ALTER TABLE tb_transaction_analysis_data MODIFY attributable_share INTEGER(11) NULL COMMENT '持有份额（百倍）';

ALTER TABLE tb_transaction_analysis_data CHANGE create_time create_time DATETIME NULL DEFAULT now() COMMENT '创建时间';

ALTER TABLE tb_transaction_analysis_data CHANGE update_time update_time DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

INSERT INTO alembic_version (version_num) VALUES ('6239f6413907');

