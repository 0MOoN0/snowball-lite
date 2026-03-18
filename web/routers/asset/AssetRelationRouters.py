from flask import Blueprint
from flask_restful import Api, Resource

from web.common.utils import R
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset_category import AssetCategory
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.models.asset.AssetHoldingData import AssetHoldingData
from web.models.asset.AssetRelation import AssetRelation, AssetRelationSchema
from web.models.grid.Grid import Grid
from web.models.record.record import Record

asset_relations_bp = Blueprint("asset_relations", __name__, url_prefix="/asset_relations")
asset_relations_api = Api(asset_relations_bp)


class AssetRelationRouter(Resource):

    def get(self, asset_id: int):
        """
        @@@
        根据给定资产ID，获取资产关联关系
        Args:
            asset_id (int): 资产ID

        Returns:
            dict: 资产关联关系
                example:
                {
                    "dailyData": 2890, # 日线数据
                    "heldData": 0,     # 被其他资产持有数量
                    "recordData": 46,  # 交易记录条数
                    "transactionAnalysisData": 90, # 交易分析条数
                    "category": 1,     # 分类条数
                    "id": 12,          # ID
                    "feeRule": 1,      # 费用数据
                    "gridData": 1,     # 关联的网格数据
                    "holdingData": 30  # 持仓数据条数
                }
        @@@
        """
        asset_relation: AssetRelation = AssetRelation()
        asset_relation.id = asset_id
        # 根据资产ID获取资产分类关联关系
        asset_relation.category = AssetCategory.query.filter(AssetCategory.asset_id == asset_id).count()
        # 根据资产ID获取资产基金日线数据关联关系
        asset_relation.daily_data = AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_id).count()
        # 根据资产ID获取资产费用规则关联关系
        asset_relation.fee_rule = AssetFundFeeRule.query.filter(AssetFundFeeRule.asset_id == asset_id).count()
        # 根据资产ID获取证券的持仓信息
        asset_relation.holding_data = AssetHoldingData.query. \
            filter(AssetHoldingData.ah_holding_asset_id == asset_id).count()
        #  根据资产ID获取该资产作为持仓被持有的数据条数
        asset_relation.held_data = AssetHoldingData.query.filter(AssetHoldingData.asset_id == asset_id).count()
        asset_relation.record_data = Record.query.filter(Record.asset_id == asset_id).count()
        asset_relation.grid_data = Grid.query.filter(Grid.asset_id == asset_id).count()
        asset_relation.transaction_analysis_data = TradeAnalysisData.query. \
            filter(TradeAnalysisData.asset_id == asset_id).count()
        return R.ok(data=AssetRelationSchema().dump(asset_relation))


asset_relations_api.add_resource(AssetRelationRouter, '/<int:asset_id>')
