import logging

from flask import Blueprint, current_app
from flask_restful import Api, Resource, reqparse
from sqlalchemy import or_

from web.web_exception import WebBaseException
from web.common.utils import R
from web.models import db
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import AssetSchema, Asset, AssetVOSchema
from web.models.asset.asset_category import AssetCategory
from web.models.asset.asset_code import AssetCodeSchema, AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.models.asset.AssetHoldingData import AssetHoldingData
from web.models.category.Category import Category
from web.models.grid.Grid import Grid
from web.services.asset.asset_service import asset_service

asset_bp = Blueprint("asset", __name__, url_prefix="/asset")
asset_api = Api(asset_bp)


def _is_lite_runtime() -> bool:
    return current_app.config.get("_config_name") == "lite" or current_app.config.get("ENV") == "lite"


class AssetRouter(Resource):

    def get(self, asset_id: int = None):
        """
        根据证券名称或代码搜索相关证券
        Returns:

        """
        if asset_id is not None:
            asset: Asset = Asset.query.get(asset_id)
            return R.ok(data=AssetVOSchema().dump(asset))
        parse = reqparse.RequestParser()
        parse.add_argument('query_like', required=False, type=str, location='args')
        parse.add_argument('id', required=False, type=str, location='args')
        args = parse.parse_args().copy()
        if args.get('query_like') is not None:
            query = args.get('query_like')
            assets = db.session.query(Asset) \
                .join(AssetCode, AssetCode.asset_id == Asset.id) \
                .filter(or_(Asset.asset_name.like("%" + query + "%"), AssetCode.code_xq.like("%" + query + "%"),
                            AssetCode.code_ttjj.like("%" + query + "%"))) \
                .all()
            return R.ok(data=AssetVOSchema().dump(assets, many=True))
        return R.ok(data=[])

    def post(self):
        """
        @@@
        # 接口说明
        新增资产接口，天天基金代码或雪球代码为唯一值
        # 接口参数说明
        ```
        {
            asset_name:资产名称(require),
            currency:货币类型(require),
            asset_type:资产类型(require),
            code_ttjj:天天基金代码,
            code_xq:雪球代码,
            code_index:指数代码
        }
        ```
        # 返回值说明
        :return:
        @@@
        """
        parse = reqparse.RequestParser()
        parse = self._get_req_parse(parse)
        asset_post = parse.parse_args().copy()
        not_null_filters = []
        if asset_post.get('code_xq'):
            not_null_filters.append(AssetCode.code_xq == asset_post.get('code_xq'))
        if asset_post.get('code_ttjj'):
            not_null_filters.append(AssetCode.code_ttjj == asset_post.get('code_ttjj'))
        # 判断是否有相同代码的基金存在
        count = 0
        if len(not_null_filters) > 0:
            count = AssetCode.query.filter(or_(*not_null_filters)).count()
        if count > 0:
            return R.fail(msg='相关代码的基金已经存在，请检查数据是否存在')
        # 新增资产数据
        with db.session.no_autoflush as session:
            # 新增资产数据
            asset: Asset = AssetSchema().load(asset_post, unknown="EXCLUDE")
            session.add(asset)
            session.flush()
            # 新增资产代码数据
            code: AssetCode = AssetCodeSchema().load(asset_post, unknown="EXCLUDE")
            code.asset_id = asset.id
            session.add(code)
            session.flush()
            # 处理资产分类信息
            asset_categories: list = asset_post.get('category_id', [])
            if asset_categories is not None and len(asset_categories) > 0:
                asset_categories = asset_post.get('category_id')
                asset_category_list = [{'asset_id': asset.id, 'category_id': category_id} for category_id in
                                       asset_categories]
                session.execute(AssetCategory.__table__.insert(), asset_category_list,
                                bind=db.engines['snowball'])
            session.commit()
            if _is_lite_runtime():
                asset_service.init_asset_data(code)
            else:
                # 执行初始化任务，让任务在1秒后执行
                from web.task.actors.AssetActors import init_asset

                init_asset.send_with_options(
                    args=(AssetCodeSchema().dump(code, many=False),),
                    delay=1000,
                )
        return R.ok(msg='操作成功')

    def put(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', required=True)
        parse = self._get_req_parse(parse)
        asset_post = parse.parse_args().copy()
        asset: Asset = AssetSchema().load(asset_post, unknown="EXCLUDE")
        count = Asset.query.filter(Asset.id == asset.id).count()
        if count == 0:
            logging.error('资产数据不存在， 请求ID： %s ' % asset.id)
            raise WebBaseException(msg='数据错误，资产数据不存在')
        # 更新资产分类关联
        AssetCategory.query.filter(AssetCategory.asset_id == asset.id).delete()
        asset_categories: list = asset_post.get('category_id', [])
        if asset_categories is not None and len(asset_categories) > 0:
            asset_category_list = [{'asset_id': asset.id, 'category_id': category_id} for category_id in
                                   asset_post.get('category_id', [])]
            with db.session.no_autoflush as session:
                # 批量插入资产与分类数据关联对象
                session.execute(AssetCategory.__table__.insert(), asset_category_list,
                                bind=db.engines['snowball'])
        # 更新资产证券数据
        Asset.query.filter(Asset.id == asset.id).update(AssetSchema().dump(asset, many=False))
        # 新增资产代码数据
        code: AssetCode = AssetCodeSchema().load(asset_post, unknown="EXCLUDE")
        asset_code = AssetCode.query.filter(AssetCode.asset_id == asset.id).first()
        # 如果已经有代码数据，则不需要更新
        if asset_code is None:
            # 新增asset_code
            session.add(code)
            session.commit()
            return R.ok('更新成功')
        # 更新资产数据
        AssetCode.query \
            .filter(AssetCode.asset_id == asset.id) \
            .update(AssetCodeSchema(exclude=['id', 'asset_id']).dump(code, many=False))
        session.commit()
        return R.ok(msg='更新成功')

    def delete(self, asset_id):
        """
        @@@
        根据给定ID删除该ID对应的资产数据
        Args:
            asset_id(int): 资产ID
        Returns:
            操作结果
        @@@
        """
        # 查询是否有网格或网格类型相关联的数据
        relate: int = Grid.query.filter(Grid.asset_id == asset_id).count()
        if relate > 0:
            return R.fail(msg='该资产已关联相关的网格数据，请先解除关联关系')
        # 查询其他证券在数据库中是否有持有该证券的持仓
        relate = AssetHoldingData.query.filter(AssetHoldingData.asset_id == asset_id).count()
        if relate > 0:
            return R.fail(msg='该资产已关联相关的持仓数据，请先解除关联关系')
        # 查询该证券是否与分析数据相关联
        relate = TradeAnalysisData.query. \
            filter(TradeAnalysisData.asset_id == asset_id).count()
        if relate > 0:
            return R.fail(msg='该资产已关联相关的分析数据，请先解除关联关系')
        with db.session.no_autoflush as session:
            # 删除证券分类关联数据
            AssetCategory.query.filter(AssetCategory.asset_id == asset_id).delete()
            # 删除证券日线数据
            AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_id).delete()
            # 删除证券费用关联数据
            AssetFundFeeRule.query.filter(AssetFundFeeRule.asset_id == asset_id).delete()
            # 删除证券持仓数据
            AssetHoldingData.query.filter(AssetHoldingData.asset_id == asset_id).delete()
            # 删除证券数据
            del_res = Asset.query.filter(Asset.id == asset_id).delete()
            # 删除证券代码数据
            AssetCode.query.filter(AssetCode.asset_id == asset_id).delete()
            session.commit()
        return R.ok(msg='操作成功，删除%d 条证券数据' % del_res)

    def _get_req_parse(self, parse):
        parse.add_argument('assetName', dest='asset_name', required=True)
        parse.add_argument('currency', dest='currency', required=True, type=int)
        parse.add_argument('categoryId', dest='category_id', required=False, type=int, action='append')
        parse.add_argument('assetType', dest='asset_type', required=True, type=int)
        parse.add_argument('codeTTJJ', dest='code_ttjj', required=False, type=str)
        parse.add_argument('codeXQ', dest='code_xq', required=False, type=str)
        parse.add_argument('codeIndex', dest='code_index', required=False, type=str)
        return parse

    def _get_ancestor_list(self, category_ids, asset_id: int):
        """
        根据给定的资产ID和资产分类ID获取该资产所有的资产分类关联数据，此关联数据包括指定分类的所有上级分类，
        如分类ID为：3， 分类路径为1-2-3， 则会创建：1，2，3 三条关联数据
        Args:
            category_ids (关联的分类列表):
            asset_id (资产ID):

        Returns:
            关联数据列表：结构：{asset_id, category_id}
        """
        ancestor_objs = Category.query.filter(Category.id.in_(category_ids)).all()
        ancestor_id_set = set()
        for ancestor in ancestor_objs:
            ancestor_id_set.add(str(ancestor.id))
            ancestor_id_set.update(ancestor.ancestor.split(','))
        asset_category_list = [{'asset_id': asset_id, 'category_id': category_id} for category_id in
                               ancestor_id_set]
        return asset_category_list


asset_api.add_resource(AssetRouter, "/", "", "/<int:asset_id>")
