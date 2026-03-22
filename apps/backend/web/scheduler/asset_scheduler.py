import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Union

from sqlalchemy import and_, or_

from web.common.utils.WebUtils import web_utils
from web.databox import databox
from web.decorator.scheduler_timeout import scheduler_timeout
from web.models import db
from web.models.asset.asset import Asset, AssetStockDTO, AssetCurrentDTO
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetHoldingData import AssetHoldingDataDTO
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.notice.Notification import Notification
from web.models.record.record import Record
from web.scheduler.base import scheduler
from web.scheduler.notification_dispatch import dispatch_notification
from web.services.async_task.notification_outbox_service import (
    notification_outbox_service,
)
from web.services.analysis.transaction_analysis_service import GridStrategyTransactionAnalysisService, \
    GridTypeTransactionAnalysisService, TradeAnalysisService
from web.services.grid.grid_service import GridService
from web.services.notice.notification_service import notification_service, NotificationService
from web.weblogger import error, logger, info


@scheduler.task(id='AssetScheduler.update_asset_holding', name='季度基金持仓数据同步（每季度1号1:00）', trigger='cron', hour=1,
                day='1-31',
                month='1,4,7,10',
                misfire_grace_time=60 * 10)
def update_asset_holding():
    """
    方法内容：更新所有持仓数据方法，每季度当月每天1点更新持仓数据，每次更新多只基金的持仓数据
       注意：1.在更新的过程中，如果发现持仓数据对应的资产数据不存在，会自动创建对应资产数据和资产代码数据
    流程:1. 此方法会查询数据库中已经存在目标季度持仓数据的证券，排除掉这些证券，筛选出需要查询的资产代码数据，遍历资产代码数据，
                然后通过DataBox获取对应的证券股票持仓数据DTO。
        2. 遍历证券股票持仓数据DTO，用for循环推导式获取code列表，根据code判断数据库中是否存在对应资产代码数据，筛选出不存在的code，
    Returns:

    """

    def do_update_asset_holding():
        info('开始执行季度基金持仓数据同步任务')
        start_time = datetime.now()
        # 查询需要更新持仓数据的基金代码列表，排除掉在数据库中已经存在目标季度持仓数据的证券
        year, quarter = web_utils.get_previous_quarter(datetime.now())
        logger.info(f'目标季度: {year}年第{quarter}季度')
        
        with db.session.no_autoflush as session:
            asset_id_list_stmt = session.query(AssetFundDailyData.ah_holding_asset_id.label('asset_id')) \
                .filter(and_(AssetFundDailyData.ah_year == year, AssetFundDailyData.ah_quarter == quarter)) \
                .group_by(AssetFundDailyData.ah_holding_asset_id).subquery()
            wait_to_update_list: List[AssetCode] = session.query(AssetCode) \
                .join(Asset, AssetCode.asset_id == Asset.id, isouter=True) \
                .join(AssetFundDailyData, AssetFundDailyData.ah_holding_asset_id == Asset.id, isouter=True) \
                .filter(Asset.asset_type == Asset.get_asset_type_enum().FUND.value) \
                .filter(Asset.id.notin_(asset_id_list_stmt)) \
                .all()
            
            logger.info(f'需要更新持仓数据的基金数量: {len(wait_to_update_list)}')
            if len(wait_to_update_list) == 0:
                logger.info('没有需要更新的基金持仓数据')
                return
                
        # 查询数据库中AssetCode的code_xq字段列表
        asset_code_list: List[str] = [row[0] for row in session.query(AssetCode.code_xq).all()]
        logger.info(f'当前数据库中已有资产代码总数: {len(asset_code_list)}')
        
        # 统计变量
        total_processed = 0
        total_new_assets = 0
        total_new_holdings = 0
        
        # 遍历资产代码
        for index, asset_code in enumerate(wait_to_update_list):
            logger.info(f'处理基金 [{index+1}/{len(wait_to_update_list)}]: {asset_code.code_xq}')
            # 获取持仓数据
            holding_data_list: List[AssetHoldingDataDTO] = databox.get_stock_holdings(asset_code, year, quarter)
            # 判断当前获取的持仓数据是否存在，如果不存在，说明持仓数据还没有更新，跳过当前循环
            if not holding_data_list:
                logger.info(f'基金 {asset_code.code_xq} 的持仓数据不存在，跳过处理')
                continue
                
            logger.info(f'基金 {asset_code.code_xq} 持仓数量: {len(holding_data_list)}')
            # 获取code字段不在asset_code_all_list中的数据
            no_asset_holding_data: List[AssetHoldingDataDTO] = [holding_data for holding_data in holding_data_list if
                                                                holding_data.code not in asset_code_list]
            logger.info(f'需要新建的资产数量: {len(no_asset_holding_data)}')
            
            # 从no_asset_holding_data构建Asset对象和AssetCode对象列表
            asset_list: List[Asset] = [
                Asset(asset_name=holding_data.name, asset_type=Asset.get_asset_type_enum().STOCK.value)
                for holding_data in no_asset_holding_data]
            with db.session.no_autoflush as session:
                session.add_all(asset_list)
                session.flush()
                total_new_assets += len(asset_list)
                
            # 从asset_list和no_asset_holding_data构建AssetCode对象列表
            asset_code_save_list: List[AssetCode] = [AssetCode(asset_id=asset.id, code_xq=holding_data.code) for
                                                     asset, holding_data in zip(asset_list, no_asset_holding_data)]
            session.add_all(asset_code_save_list)
            session.flush()
            # 将asset_code_save_list添加到asset_code_all_list和asset_code_list中
            asset_code_list.extend([asset_code.code_xq for asset_code in asset_code_save_list])
            # 获取持仓数据的code列表
            holding_data_code_list: List[str] = [holding_data.code for holding_data in holding_data_list]
            # 查询根据code列表查询AssetCode
            asset_code_list: List[AssetCode] = db.session.query(AssetCode).filter(  # type: List[AssetCode]
                AssetCode.code_xq.in_(holding_data_code_list)).all()
            # 将asset_code列表与holding_data_list根据code字段进行匹配，转换成AssetHoldingData对象列表
            asset_holding_data_list: List[AssetFundDailyData] = [
                _convert_to_asset_holding_data(holding_data, year, quarter,
                                               holding_asset_code.asset_id,
                                               asset_code.asset_id) for
                holding_asset_code, holding_data in
                zip(asset_code_list, holding_data_list)]
            # 将AssetHoldingData对象列表保存到数据库中
            session.add_all(asset_holding_data_list)
            session.flush()
            
            total_processed += 1
            total_new_holdings += len(asset_holding_data_list)
            logger.info(f'基金 {asset_code.code_xq} 持仓数据处理完成')
            
        session.commit()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'季度基金持仓数据同步任务完成，处理基金数: {total_processed}，新增资产数: {total_new_assets}，新增持仓记录: {total_new_holdings}，耗时: {duration:.2f}秒')

    with scheduler.app.app_context():
        do_update_asset_holding()


# 每天晚上十点更新基金的日线数据，最长延迟执行时间23小时
@scheduler.task('cron', id='AssetScheduler.update_fund_daily_data', name='基金日线数据同步（每日22:00）', hour=22,
                minute=0,
                misfire_grace_time=60 * 60 * 23)
def update_fund_daily_data():
    """
    方法内容：每天晚上十点获取并同步所有基金的日线数据，最长延迟执行时间23小时 \n
    设计目的：自动更新基金的日线数据，方便观察市场 \n
    方法实现：获取基金资产代码数据，遍历资产代码数据，查询数据库中该基金最近一天的日线数据，如果数据不存在，则从databox获取365天基金日线数据，并保存到数据库中。
        如果数据存在，则判断最近一天的日线数据是否为当天，如果不是当天，则通过databox获取最新数据的下一天到今天的数据，并保存到数据库中 \n
    Returns:

    """

    def do_update_fund_daily_data():
        logger.info('开始执行基金日线数据同步任务')
        start_time = datetime.now()
        
        # 使用LEFT JOIN获取基金资产代码数据
        asset_code_list: List[AssetCode] = db.session.query(AssetCode).join(Asset, Asset.id == AssetCode.asset_id) \
            .filter(Asset.asset_type == Asset.get_asset_type_enum().FUND.value) \
            .all()
        logger.info(f'需要更新的基金总数: {len(asset_code_list)}')
        
        # 统计变量
        total_new_records = 0
        total_updated_funds = 0
        total_new_funds = 0
        
        with db.session.no_autoflush as session:
            session = session
            
        # 遍历资产代码
        for index, asset_code in enumerate(asset_code_list):
            logger.info(f'处理基金 [{index+1}/{len(asset_code_list)}]: {asset_code.code_xq}, 资产ID: {asset_code.asset_id}')
            
            # 获取最近一天的日线数据
            last_day_fund_daily_data: AssetFundDailyData = session.query(AssetFundDailyData) \
                .filter(AssetFundDailyData.asset_id == asset_code.asset_id) \
                .order_by(AssetFundDailyData.f_date.desc()).first()
                
            # 如果数据不存在，则从databox获取365天基金日线数据，并保存到数据库中
            if last_day_fund_daily_data is None:
                logger.info(f'基金 {asset_code.code_xq} 无历史日线数据，将获取近365天数据')
                # 获取当前时间
                end_date = datetime.now().date()
                # 获取365天前的时间
                start_date = end_date - timedelta(days=365)
                
                # 获取365天基金日线数据
                try:
                    fund_daily_data_list: List[AssetFundDailyData] = databox.fetch_daily_data(asset_code=asset_code,
                                                                                           start_date=start_date,
                                                                                           end_date=end_date)
                    
                    if fund_daily_data_list:
                        logger.info(f'成功获取基金 {asset_code.code_xq} 的日线数据，记录数: {len(fund_daily_data_list)}')
                        # 将FundDailyData对象列表保存到数据库中
                        session.add_all(fund_daily_data_list)
                        session.flush()
                        total_new_records += len(fund_daily_data_list)
                        total_new_funds += 1
                    else:
                        logger.warning(f'基金 {asset_code.code_xq} 的日线数据为空')
                except Exception as e:
                    logger.exception(f'获取基金 {asset_code.code_xq} 日线数据异常: {str(e)}')
                    continue
            # 如果数据存在，则判断最近一天的日线数据是否为当天，如果不是当天，则通过databox获取最新数据的下一天到今天的数据，并保存到数据库中
            else:
                # 将最近一天的日线数据的日期转换为date类型
                last_day_fund_daily_date = last_day_fund_daily_data.f_date.date()
                current_date = datetime.now().date()
                
                # 如果最近一天的日线数据的日期不是当天，则通过databox获取最新数据的下一天到今天的数据，并保存到数据库中
                if last_day_fund_daily_date != current_date:
                    start_date = last_day_fund_daily_date + timedelta(days=1)
                    end_date = current_date
                    date_diff = (end_date - start_date).days
                    if date_diff <= 0:
                        logger.info(f'基金 {asset_code.code_xq} 的日线数据已是最新')
                        continue
                        
                    logger.info(f'基金 {asset_code.code_xq} 最后更新日期: {last_day_fund_daily_date}，需更新 {date_diff} 天数据')
                    
                    try:
                        # 获取下一天到今天的数据
                        fund_daily_data_list: List[AssetFundDailyData] = databox.fetch_daily_data(asset_code=asset_code,
                                                                                               start_date=start_date,
                                                                                               end_date=end_date)
                        
                        if fund_daily_data_list:
                            logger.info(f'成功获取基金 {asset_code.code_xq} 的增量日线数据，记录数: {len(fund_daily_data_list)}')
                            session.add_all(fund_daily_data_list)
                            session.flush()
                            total_new_records += len(fund_daily_data_list)
                            total_updated_funds += 1
                        else:
                            logger.info(f'基金 {asset_code.code_xq} 无新增日线数据')
                    except Exception as e:
                        logger.exception(f'获取基金 {asset_code.code_xq} 增量日线数据异常: {str(e)}')
                        continue
                else:
                    logger.info(f'基金 {asset_code.code_xq} 的日线数据已是最新')
        
        session.commit()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'基金日线数据同步任务完成。新增基金: {total_new_funds}，更新基金: {total_updated_funds}，总新增记录: {total_new_records}，耗时: {duration:.2f}秒')

    with scheduler.app.app_context():
        do_update_fund_daily_data()


@scheduler.task(id='AssetScheduler.update_stock_asset', name='A股股票代码数据同步（每日23:59）', trigger='cron',
                coalesce=False, hour=23, minute=59, second=0,
                misfire_grace_time=60 * 10)
def update_stock_asset():
    """
    方法内容：每天晚上11：59点执行，获取股票数据，并更新数据库内容 \n
    设计目的：初始化股票资产数据，为更新持仓功能做数据支撑 \n
    方法实现：从databox获取股票资产数据传输对象列表，遍历列表，根据code判断数据库中是否存在资产代码数据，筛选出不存在的DTO列表，根据DTO的股票名称，
        将列表转换为Asset资产列表数据，并插入数据库，根据股票资产数据传输对象列表和Asset资产列表数据，新建资产代码数据，并批量插入数据库 \n
    Returns:

    """

    def do_update_stock_asset():
        logger.info('开始执行A股股票代码数据同步任务')
        start_time = datetime.now()
        
        # 判断当前是否为交易日，如果不是交易日则不执行
        current_date = datetime.now()
        if not web_utils.is_trading_day(current_date):
            logger.info(f'当前日期 {current_date.strftime("%Y-%m-%d")} 不是交易日，跳过同步')
            return
            
        logger.info('当前为交易日，开始同步A股股票代码数据')
        
        # 获取股票资产数据传输对象列表
        try:
            stock_asset_dto_list: List[AssetStockDTO] = databox.fetch_all_stock_asset()
            logger.info(f'获取到A股股票数据 {len(stock_asset_dto_list)} 条')
        except Exception as e:
            logger.exception(f'获取A股股票数据异常: {str(e)}')
            return
            
        # 根据code判断数据库中是否存在资产代码数据，筛选出不存在的DTO列表
        asset_code_list = [asset_code.code_xq for asset_code in db.session.query(AssetCode.code_xq).all()]
        logger.info(f'数据库中已有资产代码总数: {len(asset_code_list)}')
        
        stock_asset_dto_list = [stock_asset_dto for stock_asset_dto in stock_asset_dto_list if
                                stock_asset_dto.code not in asset_code_list]
        
        if not stock_asset_dto_list:
            logger.info('没有需要新增的股票代码数据')
            return
            
        logger.info(f'需要新增的股票代码数据: {len(stock_asset_dto_list)} 条')
        
        # 根据DTO的股票名称，将列表转换为Asset资产列表数据，并插入数据库
        asset_list = [Asset(asset_type=Asset.get_asset_type_enum().STOCK.value, asset_name=stock_asset_dto.stock_name)
                      for stock_asset_dto in stock_asset_dto_list]
                      
        with db.session.no_autoflush as session:
            session.add_all(asset_list)
            session.flush()
            logger.info(f'成功新增 {len(asset_list)} 条股票资产数据')
            
            # 根据股票资产数据传输对象列表和Asset资产列表数据，新建资产代码数据，并批量插入数据库
            asset_code_list = [AssetCode(asset_id=asset.id, code_xq=stock_asset_dto.code) for asset, stock_asset_dto in
                               zip(asset_list, stock_asset_dto_list)]
            session.add_all(asset_code_list)
            logger.info(f'成功新增 {len(asset_code_list)} 条股票代码数据')
            session.commit()
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'A股股票代码数据同步完成，新增股票数据: {len(asset_list)}，耗时: {duration:.2f}秒')

    with scheduler.app.app_context():
        do_update_stock_asset()


@scheduler.task(id='AssetScheduler.monitor_grid_type_detail', name='网格交易监控（每日16:30）', trigger='cron',
                hour=16, minute=30, second=0,
                misfire_grace_time=60 * 10)
@scheduler_timeout(60, '网格交易监控任务超时')
def monitor_grid_type_detail(monitor_date: Union[datetime, str] = None):
    """
    方法内容：每天下午四点半执行，交易日监控网格数据，判断是否有可能成交 \n
    设计目的：1.为交易系统提供数据支撑 2. 及时更新交易分析数据，为交易分析做数据准备 \n
    方法实现：获取所有网格类型的网格数据，遍历列表，并对比价格，判断是否有可能成交，如果有可能成交，发送通知 \n
    Args:
        monitor_date (Union[datetime, str], optional): 需要监控的日期，如果为None，则使用当前日期。如果是字符串格式，应为'YYYY-MM-DD'格式。
    Returns:
        None
    """

    def do_monitor_grid_type_detail():
        logger.info('开始执行网格交易监控任务')
        start_time = datetime.now()
        
        # 处理monitor_date参数
        current_date = datetime.now()
        if monitor_date is not None:
            if isinstance(monitor_date, str):
                try:
                    current_date = datetime.strptime(monitor_date, "%Y-%m-%d")
                    logger.info(f'使用指定日期进行监控: {current_date.strftime("%Y-%m-%d")}')
                except ValueError:
                    logger.error(f"无效的日期格式: {monitor_date}，应为 'YYYY-MM-DD' 格式")
                    return
            else:
                current_date = monitor_date
                logger.info(f'使用指定日期进行监控: {current_date.strftime("%Y-%m-%d")}')
                
        # 判断指定日期是否为交易日
        if not web_utils.is_trading_day(current_date):
            logger.info(f"日期 {current_date.strftime('%Y-%m-%d')} 不是交易日，跳过监控")
            return
            
        logger.info(f"日期 {current_date.strftime('%Y-%m-%d')} 是交易日，开始进行网格监控")
            
        # 获取所有网格类型的网格数据
        grid_type_list: List[GridType] = db.session.query(GridType) \
            .join(Grid, GridType.grid_id == Grid.id, isouter=True) \
            .filter(Grid.grid_status == Grid.get_status_enum().ENABLE.value).all()
            
        logger.info(f'获取到启用状态的网格类型数量: {len(grid_type_list)}')
        
        # 网格类型列表，用来存储监控结果
        grid_type_info_list = []
        
        # 统计变量
        total_processed = 0
        total_possible_trades = 0
        total_monitor_changes = 0
        service: GridService = GridService()
        
        for index, grid_type in enumerate(grid_type_list):
            logger.info(f'处理网格类型 [{index+1}/{len(grid_type_list)}]: {grid_type.type_name}, ID: {grid_type.id}')
            grid_type_info = {'current_change': None, 'trade_list': None}
            
            # 判断网格状态是否停用，如果停用则跳过
            if grid_type.grid_type_status == GridType.get_grid_status_enum().DISABLE.value:
                logger.info(f'网格类型 {grid_type.type_name} 已停用，跳过处理')
                continue
                
            # 获取网格类型的网格详情数据
            grid_type_detail_list: List[GridTypeDetail] = db.session.query(GridTypeDetail) \
                .filter(GridTypeDetail.grid_type_id == grid_type.id).all()
                
            # 如果网格类型的网格详情数据为空，则跳过
            if len(grid_type_detail_list) == 0:
                logger.info(f'网格类型 {grid_type.type_name} 没有网格详情数据，跳过处理')
                continue
                
            logger.info(f'网格类型 {grid_type.type_name} 包含 {len(grid_type_detail_list)} 条网格详情数据')
            
            asset_code: AssetCode = db.session.query(AssetCode).filter(AssetCode.asset_id == grid_type.asset_id).first()
            if not asset_code:
                logger.warning(f'网格类型 {grid_type.type_name} 关联的资产ID {grid_type.asset_id} 没有找到对应的资产代码')
                continue
                
            # 获取指定日期的数据
            try:
                # 使用fetch_daily_data而不是get_daily_data，以避免重复数据问题
                daily_data: List[AssetFundDailyData] = databox.fetch_daily_data(
                    asset_code=asset_code,
                    start_date=current_date,
                    end_date=current_date
                )
                
                if len(daily_data) != 1:
                    # 数据错误，指定日期的数据不止一条，输出错误日志
                    error(
                        f'指定日期 {current_date.strftime("%Y-%m-%d")} 的数据不存在或获取到的数据不止一条，数据错误，asset_code.code_xq: {asset_code.code_xq}')
                    continue
                    
                daily_data = daily_data[0]
                logger.info(f'获取到资产 {asset_code.code_xq} 在 {current_date.strftime("%Y-%m-%d")} 的日线数据，收盘价: {daily_data.f_close}')
            except Exception as e:
                logger.exception(f'获取资产 {asset_code.code_xq} 日线数据异常: {str(e)}')
                continue
                
            trade_list = []
            
            try:
                logger.info(f'开始判断网格类型 {grid_type.type_name} 是否需要生成交易')
                trans = service.to_judge_gen_transaction(grid_type=grid_type,
                                                         daily_data=daily_data,
                                                         grid_type_detail=grid_type_detail_list)
                trade_list.extend(trans)
                
                if trade_list:
                    logger.info(f'网格类型 {grid_type.type_name} 可能产生交易，交易网格数量: {len(trade_list)}')
                    total_possible_trades += len(trade_list)
                else:
                    logger.info(f'网格类型 {grid_type.type_name} 未触发交易条件')
            except Exception as e:
                logger.exception(
                    f'资产类型ID：{grid_type.asset_id}，网格类型：{grid_type.type_name}，判断是否生成交易时发生异常，异常信息：{str(e)}')
                continue
                
            grid_type_info['trade_list'] = trade_list
            monitor_change = []
            
            try:
                logger.info(f'开始判断网格类型 {grid_type.type_name} 档位变化情况')
                change = service.to_judge_monitor_change(today_daily_data=daily_data,
                                                         grid_type_detail=grid_type_detail_list)
                monitor_change.extend(change)
                
                if monitor_change:
                    logger.info(f'网格类型 {grid_type.type_name} 有档位变化，变化档位数量: {len(monitor_change)}')
                    total_monitor_changes += len(monitor_change)
                else:
                    logger.info(f'网格类型 {grid_type.type_name} 无档位变化')
            except Exception as e:
                logger.exception(
                    f'资产类型ID：{grid_type.asset_id}, 网格类型：{grid_type.type_name}，判断是否监控档位变化时异常，异常信息：{str(e)}')
                continue
                
            grid_type_info['current_change'] = monitor_change
            grid_type_info_list.append(grid_type_info)
            total_processed += 1
            logger.info(f'网格类型 {grid_type.type_name} 处理完成')
            
        # 发送通知前记录日志
        if grid_type_info_list:
            logger.info(f'共有 {len(grid_type_info_list)} 个网格类型需要发送通知')
            
        # 构建并发送通知
        _make_grid_monitor_notification(grid_type_info_list)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'网格交易监控任务完成，处理网格类型: {total_processed}，可能产生交易: {total_possible_trades}，档位变化: {total_monitor_changes}，耗时: {duration:.2f}秒')

    with scheduler.app.app_context():
        do_monitor_grid_type_detail()


@scheduler.task(id='GridTypeScheduler.grid_type_trade_analysis', name='网格类型交易分析（每日16:00）',
                trigger='cron', hour=16, misfire_grace_time=60 * 14, coalesce=True)
def grid_type_trade_analysis(start: Union[datetime, str] = None, end: Union[datetime, str] = None):
    """
    对网格类型进行交易分析的定时任务。

    Args:
        start (Union[datetime, str], optional): 开始日期，如果为None则使用系统默认。
        end (Union[datetime, str], optional): 结束日期，如果为None则使用系统默认。

    Returns:
        无返回值。

    Raises:
        无特定异常抛出。

    Details:
        该任务被设计为每天下午四点执行，用于对网格类型进行交易分析。如果任务错过执行时间，在之后的14分钟内仍然可以执行，并且会合并错过的执行次数。

        任务的主要目的是为交易分析提供数据支撑。它通过查询数据库获取所有网格类型的数据列表，然后遍历这些网格类型，针对每个网格类型，
        调用GridTypeTransactionAnalysisService的trade_analysis方法，该方法会获取网格类型的交易数据，并调用分析接口进行数据分析，
        最终将分析结果保存到数据库中。

    """

    with scheduler.app.app_context():
        logger.info('开始执行网格类型交易分析任务')
        start_time = datetime.now()
        
        # 日期处理
        date_info = ""
        if start:
            start_str = start.strftime('%Y-%m-%d') if isinstance(start, datetime) else start
            date_info += f"开始日期: {start_str}, "
        if end:
            end_str = end.strftime('%Y-%m-%d') if isinstance(end, datetime) else end
            date_info += f"结束日期: {end_str}"
            
        if date_info:
            logger.info(f"分析日期范围: {date_info}")
        else:
            logger.info("使用系统默认日期范围进行分析")
            
        # 获取所有网格类型
        grid_type_list: List[GridType] = db.session.query(GridType).all()
        logger.info(f'获取到 {len(grid_type_list)} 个网格类型')
        
        # 统计变量
        total_processed = 0
        total_errors = 0
        
        # 遍历列表，获取网格类型数据的交易数据，调用analysis_service的分析接口对网格类型进行数据分析并入库
        for index, grid_type in enumerate(grid_type_list):
            logger.info(f'处理网格类型 [{index+1}/{len(grid_type_list)}]: {grid_type.type_name}, ID: {grid_type.id}')
            
            try:
                trade_transaction_analysis: TradeAnalysisService = GridTypeTransactionAnalysisService(
                    grid_type_id=grid_type.id)
                trade_transaction_analysis.trade_analysis(start=start, end=end)
                total_processed += 1
                logger.info(f'网格类型 {grid_type.type_name} 交易分析完成')
            except Exception as e:
                total_errors += 1
                logger.exception(f'网格类型 {grid_type.type_name} 交易分析异常: {str(e)}')
                continue
                
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'网格类型交易分析任务完成，成功处理: {total_processed}，失败: {total_errors}，总数: {len(grid_type_list)}，耗时: {duration:.2f}秒')


@scheduler.task(id='GridStrategyScheduler.grid_strategy_trade_analysis',
                name='网格策略交易分析（每日16:15）',
                trigger='cron', hour=16, minute=15, misfire_grace_time=60 * 15, coalesce=False)
def grid_strategy_trade_analysis(start: Union[datetime, str] = None, end: Union[datetime, str] = None):
    """
    对网格策略进行交易分析的任务。

    Args:
        start (Union[datetime, str], optional): 开始日期，如果为None则使用系统默认。
        end (Union[datetime, str], optional): 结束日期，如果为None则使用系统默认。

    Returns:
        无返回值。

    说明：
        该方法是一个定时任务，每天下午四点十五分自动执行。当任务错过执行时间15分钟内仍可以执行，不合并错过的执行次数。
        该任务调用GridStrategyTransactionAnalysisService服务中的trade_analysis方法对网格策略进行交易分析，
        为交易分析提供数据支撑。

    """

    with scheduler.app.app_context():
        logger.info('开始执行网格策略交易分析任务')
        start_time = datetime.now()
        
        # 日期处理
        date_info = ""
        if start:
            start_str = start.strftime('%Y-%m-%d') if isinstance(start, datetime) else start
            date_info += f"开始日期: {start_str}, "
        if end:
            end_str = end.strftime('%Y-%m-%d') if isinstance(end, datetime) else end
            date_info += f"结束日期: {end_str}"
            
        if date_info:
            logger.info(f"分析日期范围: {date_info}")
        else:
            logger.info("使用系统默认日期范围进行分析")
        
        try:
            trade_analysis_service = GridStrategyTransactionAnalysisService()
            trade_analysis_service.trade_analysis(start=start, end=end)
            logger.info('网格策略交易分析执行成功')
        except Exception as e:
            logger.exception(f'网格策略交易分析执行异常: {str(e)}')
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'网格策略交易分析任务完成，耗时: {duration:.2f}秒')


@scheduler.task(id='AssetScheduler.complement_asset_data',
                name='资产数据补充（每日23:30）',
                trigger='cron', hour=23, minute=30, misfire_grace_time=60 * 5, coalesce=False)
def complement_asset_data():
    """
    方法内容：补充资产数据，将资产数据补充到数据库中，每天晚上十一点半执行，任务错过执行时间5分钟内仍可以执行，不合并错过的执行次数 \n
    Returns:

    """
    with scheduler.app.app_context():
        logger.info('开始执行资产数据补充任务')
        start_time = datetime.now()
        
        success_count = 0
        try:
            logger.info('开始补充资产市场和货币类型')
            _complement_asset_market_and_currency()
            success_count += 1
            logger.info('资产市场和货币类型补充完成')
        except Exception as e:
            logger.exception(f'补充资产市场和货币类型时发生异常: {str(e)}')
            
        try:
            logger.info('开始拉取资产日线数据')
            _pull_asset_daily_data()
            success_count += 1
            logger.info('资产日线数据拉取完成')
        except Exception as e:
            logger.exception(f'拉取资产日线数据时发生异常: {str(e)}')
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'资产数据补充任务完成，成功执行子任务: {success_count}/2，耗时: {duration:.2f}秒')


def _pull_asset_daily_data():
    """
    方法内容：拉取资产日线数据，如果当前的资产日线数据小于250个交易日，且有交易，交易日期小于目前数据库的日线数据，则拉取数据，并更新数据库 \n
    Args:
        databox:

    Returns:

    """
    logger.info('开始拉取资产日线数据')
    
    # 查询需要处理的资产列表
    assets: list[Asset] = db.session.query(Asset.id).filter(
        or_(Asset.asset_type == Asset.get_asset_type_enum().INDEX.value,
            Asset.asset_type == Asset.get_asset_type_enum().FUND.value)) \
        .all()
    asset_ids: list[int] = [data.id for data in assets]
    logger.info(f'需要处理的资产总数: {len(asset_ids)}')
    
    # 统计变量
    assets_processed = 0
    assets_updated = 0
    total_records_added = 0
    
    for index, asset_id in enumerate(asset_ids):
        logger.info(f'处理资产 [{index+1}/{len(asset_ids)}], ID: {asset_id}')
        # 拉取结束日期
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(days=365)
        
        # 查询该ID的最后一条数据
        last_data: AssetFundDailyData = db.session.query(AssetFundDailyData) \
            .filter(AssetFundDailyData.asset_id == asset_id) \
            .order_by(AssetFundDailyData.f_date.asc()).first()
            
        need_update = False
        
        if last_data:
            logger.info(f'资产 ID: {asset_id} 的最早日线数据日期: {last_data.f_date}')
            # 根据id获取最早的一条交易数据
            record: Record = Record.query.filter(Record.asset_id == asset_id).order_by(
                Record.transactions_date.asc()).first()
                
            # 如果数据库中的日线数据比交易记录日期小，则不需要拉取旧数据
            if record and last_data.f_date <= record.transactions_date:
                logger.info(f'资产 ID: {asset_id} 的日线数据已覆盖交易日期，不需要更新')
                continue
                
            if record:
                # 如果交易记录存在，并且日期数据比日线数据大，使用交易记录的前180天数据作为开始，使用数据库中日线数据的最早数据的前一天为结束日期
                start_date = record.transactions_date - timedelta(days=180)
                end_date = last_data.f_date - timedelta(days=1)
                logger.info(f'资产 ID: {asset_id} 有交易记录，最早交易日期: {record.transactions_date}，将拉取 {start_date} 到 {end_date} 的数据')
                need_update = True
            # 如果交易记录不存在，但是数据库日线数据没有超过一年的量，更新日线数据
            elif (last_data - datetime.now()).days <= 365:
                start_date = last_data.f_date - timedelta(days=365)
                end_date = last_data.f_date - timedelta(days=1)
                logger.info(f'资产 ID: {asset_id} 日线数据不足一年，将拉取 {start_date} 到 {end_date} 的数据')
                need_update = True
            else:
                logger.info(f'资产 ID: {asset_id} 无需更新日线数据')
        else:
            logger.info(f'资产 ID: {asset_id} 没有日线数据，将拉取近一年数据')
            need_update = True
            
        # 根据start_date和end_date拉取数据
        if need_update:
            try:
                daily_data = databox.fetch_daily_data(asset_id=asset_id, start_date=start_date, end_date=end_date)
                
                if daily_data:
                    records_count = len(daily_data)
                    logger.info(f'成功获取资产 ID: {asset_id} 的日线数据，记录数: {records_count}')
                    db.session.bulk_save_objects(daily_data, return_defaults=False, update_changed_only=True)
                    assets_updated += 1
                    total_records_added += records_count
                else:
                    logger.info(f'资产 ID: {asset_id} 没有获取到日线数据')
            except Exception as e:
                logger.exception(f'获取资产 ID: {asset_id} 日线数据异常: {str(e)}')
        
        assets_processed += 1
        
    db.session.commit()
    logger.info(f'资产日线数据拉取完成，处理资产: {assets_processed}，更新资产: {assets_updated}，新增记录: {total_records_added}')


# 完善资产市场和货币类型
def _complement_asset_market_and_currency():
    """
    方法内容：补充资产市场和货币类型，完善A股市场代码的市场类型和货币类型，以及查询补充其他未标记类型的资产 \n
    Returns:

    """
    logger.info('开始补充资产市场和货币类型')
    start_time = datetime.now()
    
    # 统计变量
    a_stock_updated = 0
    other_assets_updated = 0
    
    # 完善A股市场代码的市场类型和货币类型
    logger.info('开始处理A股资产')
    a_stock_list: List = db.session.query(Asset, AssetCode) \
        .join(AssetCode, Asset.id == AssetCode.asset_id, isouter=True) \
        .filter(or_(Asset.market.is_(None), Asset.currency.is_(None))) \
        .filter(or_(AssetCode.code_xq.like('SZ%'), AssetCode.code_xq.like('SH%'))) \
        .all()
    
    logger.info(f'发现 {len(a_stock_list)} 条A股资产数据需要补充市场和货币类型')
    
    for asset, asset_code in a_stock_list:
        if len(asset_code.code_xq) == 8 and asset_code.code_xq[-6:].isdigit():
            asset.market = Asset.get_market_enum().CN.value
            asset.currency = Asset.get_currency_enum().CNY.value
            a_stock_updated += 1
            
    logger.info(f'成功更新 {a_stock_updated} 条A股资产的市场和货币类型')
    db.session.flush()
    
    # 查询资产数据中，市场为空或货币类型为空的前五十条数据
    logger.info('开始处理其他资产')
    asset_data_list: List = db.session.query(Asset, AssetCode) \
        .join(AssetCode, Asset.id == AssetCode.asset_id, isouter=True) \
        .filter(or_(Asset.market.is_(None), Asset.currency.is_(None))) \
        .filter(AssetCode.code_xq.is_not(None)) \
        .limit(50).all()
        
    logger.info(f'发现 {len(asset_data_list)} 条其他资产数据需要补充市场和货币类型（限制50条）')
    
    # 遍历资产和资产代码数据，将数据补充到数据库中
    for index, asset_data in enumerate(asset_data_list):
        logger.info(f'处理资产 [{index+1}/{len(asset_data_list)}]: {asset_data.AssetCode.code_xq}')
        try:
            rt: AssetCurrentDTO = databox.get_rt(asset_data.AssetCode.code_xq)
            
            if rt is None:
                logger.warning(f'资产 {asset_data.AssetCode.code_xq} 没有获取到实时数据，跳过处理')
                continue
                
            asset_data.Asset.market = rt.market
            asset_data.Asset.currency = rt.currency
            logger.info(f'更新资产 {asset_data.AssetCode.code_xq} 的市场为 {rt.market}，货币为 {rt.currency}')
            
            # 如果市场为香港，并且资产代码为五位数，则将资产代码的前缀设置为HK
            if rt.market == Asset.get_market_enum().HK.value:
                if len(rt.code) == 5:
                    asset_data.AssetCode.code_xq = 'HK' + rt.code
                    logger.info(f'更新香港资产代码为: HK{rt.code}')
                    
            # 如果资产代码为六位纯数字，更新资产代码
            if asset_data.AssetCode.code_xq.isdigit() and len(rt.code) == 6:
                asset_data.AssetCode.code_xq = rt.code
                logger.info(f'更新资产代码为: {rt.code}')
                
            other_assets_updated += 1
            # 休眠1~2秒
            time.sleep(random.randint(1, 2))
        except Exception as e:
            error(f"{asset_data.AssetCode.code_xq}查询实时数据失败: {str(e)}", exc_info=True)
            time.sleep(random.randint(3, 5))
            db.session.commit()
            raise e
            
    db.session.commit()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f'资产市场和货币类型补充完成，A股更新: {a_stock_updated}，其他资产更新: {other_assets_updated}，耗时: {duration:.2f}秒')


# 完善资产日线数据
def _complement_asset_daily_data():
    """
    方法内容：补充资产日线数据，补充数据库中已经存在的日线数据的缺失数据，比如收盘价和净值，将资产日线数据补充到数据库中 \n
    Returns:

    """
    result = AssetFundDailyData.query.with_entities(AssetFundDailyData.asset_id).group_by(AssetFundDailyData.asset_id) \
        .all()
    asset_id_list = [item.asset_id for item in result]
    # 遍历资产ID列表
    for asset_id in asset_id_list:
        asset_code: AssetCode = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
        # 获取f_close为空或f_netvale为空的资产日线数据，根据f_date升序排序
        asset_daily_data_list: List[AssetFundDailyData] = AssetFundDailyData.query \
            .filter(AssetFundDailyData.asset_id == asset_id) \
            .filter(or_(AssetFundDailyData.f_close.is_(None), AssetFundDailyData.f_netvalue.is_(None))) \
            .order_by(AssetFundDailyData.f_date.asc()) \
            .limit(500).all()
        if len(asset_daily_data_list) > 0:
            start_date = asset_daily_data_list[0].f_date
            end_date = asset_daily_data_list[-1].f_date
            # 获取资产日线数据
            asset_daily_data_dto_list: List[AssetFundDailyData] = databox.fetch_daily_data(
                asset_code=asset_code, start_date=start_date, end_date=end_date)
            daily_data_dict: Dict = dict((data.f_date, data) for data in asset_daily_data_dto_list)
            # 遍历asset_daily_data_list，将数据补充到数据库中
            for asset_daily_data in asset_daily_data_list:
                new_data: AssetFundDailyData = daily_data_dict.get(asset_daily_data.f_date)
                if new_data is None:
                    continue
                asset_daily_data.f_close = new_data.f_close
                asset_daily_data.f_open = new_data.f_open
                asset_daily_data.f_high = new_data.f_high
                asset_daily_data.f_low = new_data.f_low
                asset_daily_data.f_netvalue = new_data.f_netvalue
                asset_daily_data.f_close = new_data.f_close
                asset_daily_data.f_volume = new_data.f_volume
                asset_daily_data.f_close_percent = new_data.f_close_percent
                asset_daily_data.f_totvalue = new_data.f_totvalue
                asset_daily_data.f_comment = new_data.f_comment
        db.session.bulk_save_objects(asset_daily_data_list, return_defaults=False, update_changed_only=True)
    db.session.commit()


def _convert_to_asset_holding_data(asset_holding_data_dto: AssetHoldingDataDTO, year: int,
                                   quarter: int, asset_id: int, holding_asset_id: int) -> AssetFundDailyData:
    """
    用于将AssetHoldingDataDTO转换为AssetHoldingData对象，参数为AssetHoldingDataDTO对象、year、quarter，返回值为AssetHoldingData对象
    Args:
        asset_holding_data_dto (AssetHoldingDataDTO):  资产持仓数据传输对象
        year (int): 年份
        quarter (int): 季度
        asset_id (int): 当前记录的对应的资产ID
        holding_asset_id (int): 当前记录的持有者的资产ID

    Returns:
        AssetFundDailyData: 资产持仓数据对象
    """
    return AssetFundDailyData(ah_holding_asset_id=holding_asset_id,
                              ah_asset_name=asset_holding_data_dto.name,
                              ah_holding_percent=asset_holding_data_dto.ratio,
                              asset_id=asset_id,
                              ah_year=year,
                              ah_quarter=quarter)


def _make_grid_monitor_notification(grid_type_info_list: List[Dict]):
    """
    方法内容：根据监控数据结果，将数据封装为通知，并添加到消息发送任务队列， 网格通知内容包含资产名称(asset_name)，网格类型名称(grid_type_name)，
        可能发生交易网格类型详情数据ID列表(trade_list)，可能发生变化的网格监控档位(current_change)
    设计目的：用于定时方法任务内部调用，生成通知对象并发送到任务队列
    方法实现：遍历网格类型信息列表，分析字典列表内容，根据id获取资产名称和网格类型名称，生成通知对象
    Args:
        grid_type_info_list (List[Dict]): 网格类型信息列表，包含trade_list和current_change的字典列表，trade_list和current_change不能同时为空
    Returns:

    """
    logger.info('开始生成网格监控通知')
    
    # 判断网格类型信息列表是否为空
    if len(grid_type_info_list) == 0:
        logger.info('网格类型信息列表为空，不生成通知')
        return
        
    grid_info_list = []
    # 遍历网格类型信息列表
    for index, grid_type_info in enumerate(grid_type_info_list):
        logger.info(f'处理网格类型信息 [{index+1}/{len(grid_type_info_list)}]')
        
        # 判断trade_list与current_change是否同时为空
        if not grid_type_info['trade_list'] and not grid_type_info['current_change']:
            logger.info('当前网格类型信息的交易列表和变化列表均为空，跳过处理')
            continue
            
        # 获取trade_list或current_change的第一个值
        grid_type_detail_id = grid_type_info['trade_list'][0] if grid_type_info['trade_list'] else \
            grid_type_info['current_change'][0]
            
        # 根据id获取网格类型详情
        try:
            grid_type_detail: GridTypeDetail = db.session.query(GridTypeDetail).filter(
                GridTypeDetail.id == grid_type_detail_id).first()
                
            if not grid_type_detail:
                logger.warning(f'网格类型详情ID {grid_type_detail_id} 不存在，跳过处理')
                continue
                
            # 根据网格类型详情获取网格类型
            grid_type: GridType = db.session.query(GridType).filter(
                GridType.id == grid_type_detail.grid_type_id).first()
                
            if not grid_type:
                logger.warning(f'网格类型ID {grid_type_detail.grid_type_id} 不存在，跳过处理')
                continue
                
            # 根据网格类型获取资产
            asset: Asset = db.session.query(Asset).filter(Asset.id == grid_type.asset_id).first()
            
            if not asset:
                logger.warning(f'资产ID {grid_type.asset_id} 不存在，跳过处理')
                continue
                
            # 生成通知内容字典
            grid_info = {
                'asset_name': asset.asset_name,
                'grid_type_name': grid_type.type_name,
                'trade_list': grid_type_info['trade_list'],
                'current_change': grid_type_info['current_change']
            }
            
            trade_count = len(grid_type_info['trade_list']) if grid_type_info['trade_list'] else 0
            change_count = len(grid_type_info['current_change']) if grid_type_info['current_change'] else 0
            
            logger.info(f'添加通知: 资产={asset.asset_name}, 网格类型={grid_type.type_name}, 交易数={trade_count}, 变化数={change_count}')
            grid_info_list.append(grid_info)
        except Exception as e:
            logger.exception(f'处理网格类型通知数据异常: {str(e)}')
            continue
            
    # 判断通知内容字典列表是否为空
    if len(grid_info_list) == 0:
        logger.info('没有有效的网格通知内容，不发送通知')
        return
        
    logger.info(f'准备发送通知，包含 {len(grid_info_list)} 个网格信息')
    
    # 通知内容字典
    notification_content = {
        'title': '网格交易确认通知'
    }
    notification_content.update({'grid_info': grid_info_list})
    notice_service: NotificationService = notification_service
    
    try:
        # 创建通知并持久化到数据库
        notification = notice_service.make_notification(
            business_type=Notification.get_business_type_enum().GRID_TRADE.value,
            notice_type=Notification.get_notice_type_enum().CONFIRM_MESSAGE.value,
            content=notification_content,
            title='网格交易确认通知')

        sent, channel = _deliver_grid_monitor_notification(notification)
        if sent:
            if channel == "actor":
                logger.info('网格交易确认通知发送成功')
            elif channel == "outbox":
                logger.info('网格交易确认通知已写入 lite outbox，等待 scheduler 消费')
            else:
                logger.info('网格交易确认通知同步发送成功')
        else:
            logger.error('网格交易确认通知发送失败')
    except Exception as e:
        logger.exception(f'发送网格交易确认通知异常: {str(e)}')


def _deliver_grid_monitor_notification(notification: Notification):
    if notification_outbox_service.is_lite_runtime():
        notification_outbox_service.enqueue_notification(notification)
        return True, "outbox"

    return dispatch_notification(notification)
