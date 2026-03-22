from web.weblogger import debug
from web.common.cons import webcons
from web.models.asset.asset_code import AssetCodeSchema, AssetCode
from web.services.asset.asset_service import asset_service
from web.task.Base import dramatiq


@dramatiq.actor
def init_fund_asset(asset_code_str: str):
    """
    方法内容：初始化基金数据
    Args:
        asset_code_str (str): 基金代码对象的json字符串

    Returns:

    """ 
    asset_code: AssetCode = AssetCodeSchema().loads(asset_code_str)
    asset_service.init_fund_asset_data(asset_code)


@dramatiq.actor
def init_index_asset(asset_code_str: str):
    """
    方法内容：初始化指数数据
    Args:
        asset_code_str (str):  指数代码对象的json字符串

    Returns:

    """
    asset_code: AssetCode = AssetCodeSchema().loads(asset_code_str)
    asset_service.init_index_asset_data(asset_code)


@dramatiq.actor(queue_name=webcons.QueueNames.normal_queue)
def init_asset(asset_code_str: dict):
    """
    方法内容：根据资产类型初始化资产数据
    Args:
        asset_code_str (dict): 资产代码对象的json字符串

    Returns:

    """
    # 打印log
    debug('init_asset start')
    asset_code: AssetCode = AssetCodeSchema().load(asset_code_str)
    asset_service.init_asset_data(asset_code)
