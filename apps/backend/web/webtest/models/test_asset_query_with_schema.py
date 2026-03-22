from datetime import datetime
from decimal import Decimal

from web.models.asset.asset import (
    Asset,
    AssetExchangeFund,
    AssetSchema,
    AssetExchangeFundSchema,
)
from web.models.asset.asset_fund import (
    AssetFund,
    AssetFundETF,
    AssetFundLOF,
    AssetFundSchema,
    AssetFundETFSchema,
    AssetFundLOFSchema,
)
from web.webtest.test_base import TestBaseForAssetModels


class TestAssetQueryWithSchema(TestBaseForAssetModels):
    """
    Asset模型查询和Schema序列化测试类

    测试覆盖范围：
    - Asset基类和各子类的数据插入
    - 多态继承查询功能
    - Schema序列化功能
    - 基类和子类数据的完整性验证

    测试策略：
    - 使用TestBaseForAssetModels确保数据库事务隔离
    - 测试Asset基类及其所有子类的CRUD操作
    - 验证SQLAlchemy多态继承的查询机制
    - 测试各种Schema的序列化功能
    """

    def test_insert_and_query_asset_with_schema_serialization(self, test_db_session):
        """
        测试Asset基类和子类数据的插入、查询和Schema序列化

        验证点:
        - Asset基类数据插入和查询
        - AssetExchangeFund子类数据插入和查询
        - AssetFund子类数据插入和查询
        - AssetFundETF子类数据插入和查询
    - AssetFundLOF子类数据插入和查询
        - 多态继承查询功能
        - 各种Schema的序列化功能
        - 数据完整性和关联关系验证

        请求示例:
        无（数据库操作测试）

        返回示例:
        验证序列化后的数据格式正确性

        关键注意事项:
        - 使用test_db_session确保事务隔离
        - 验证多态继承的polymorphic_identity字段
        - 确保Schema序列化包含所有必要字段
        """

        # 1. 插入Asset基类数据
        base_asset = Asset(
            asset_name="基础资产测试",
            asset_type=Asset.get_asset_type_enum().STOCK.value,
            market=Asset.get_market_enum().CN.value,
            currency=Asset.get_currency_enum().CNY.value,
            create_time=datetime.now(),
        )
        test_db_session.add(base_asset)
        test_db_session.flush()  # 获取ID

        # 2. 插入AssetExchangeFund子类数据
        exchange_fund = AssetExchangeFund(
            asset_name="场内基金测试",
            asset_type=Asset.get_asset_type_enum().FUND.value,
            market=Asset.get_market_enum().CN.value,
            currency=Asset.get_currency_enum().CNY.value,
            create_time=datetime.now(),
            exchange_market="SH",
            sub_type="ETF",
            tracking_index="沪深300指数",
        )
        test_db_session.add(exchange_fund)
        test_db_session.flush()

        # 3. 插入AssetFund子类数据
        asset_fund = AssetFund(
            asset_name="基金测试",
            asset_type=Asset.get_asset_type_enum().FUND.value,
            market=Asset.get_market_enum().CN.value,
            currency=Asset.get_currency_enum().CNY.value,
            create_time=datetime.now(),
            fund_type="INDEX_FUND",
            trading_mode="OPEN_END",
            fund_company="测试基金公司",
            fund_manager="测试基金经理",
            establishment_date=datetime.now().date(),
            fund_scale=Decimal("10000.0000"),
        )
        test_db_session.add(asset_fund)
        test_db_session.flush()

        # 4. 插入AssetFundETF子类数据
        asset_etf = AssetFundETF(
            asset_name="ETF测试",
            asset_type=Asset.get_asset_type_enum().FUND.value,
            market=Asset.get_market_enum().CN.value,
            currency=Asset.get_currency_enum().CNY.value,
            create_time=datetime.now(),
            fund_type="INDEX_FUND",
            trading_mode="ETF",
            fund_company="测试ETF公司",
            fund_manager="测试ETF经理",
            establishment_date=datetime.now().date(),
            fund_scale=Decimal("20000.0000"),
            tracking_index_code="000905",
            tracking_index_name="中证500指数",
            primary_exchange="SH",
            dividend_frequency="ANNUAL",
            tracking_error=Decimal("0.0020"),
        )
        test_db_session.add(asset_etf)
        test_db_session.flush()

        # 5. 插入AssetFundLOF子类数据
        asset_lof = AssetFundLOF(
            asset_name="LOF测试",
            asset_type=Asset.get_asset_type_enum().FUND.value,
            market=Asset.get_market_enum().CN.value,
            currency=Asset.get_currency_enum().CNY.value,
            create_time=datetime.now(),
            fund_type="STOCK_FUND",
            trading_mode="LOF",
            fund_company="测试LOF公司",
            fund_manager="测试LOF经理",
            establishment_date=datetime.now().date(),
            fund_scale=Decimal("15000.0000"),
            listing_exchange="SZ",
            subscription_fee_rate=Decimal("0.0150"),
            redemption_fee_rate=Decimal("0.0050"),
        )
        test_db_session.add(asset_lof)
        test_db_session.flush()

        # 提交事务
        test_db_session.commit()

        # 6. 查询所有Asset数据（多态查询）
        all_assets = test_db_session.query(Asset).all()
        # 由于可能存在其他测试数据，我们只验证我们插入的5个记录是否都存在
        inserted_asset_ids = [
            base_asset.id,
            exchange_fund.id,
            asset_fund.id,
            asset_etf.id,
            asset_lof.id,
        ]
        actual_asset_ids = [asset.id for asset in all_assets]
        for asset_id in inserted_asset_ids:
            assert (
                asset_id in actual_asset_ids
            ), f"插入的资产ID {asset_id} 应该在查询结果中"
        assert len(all_assets) >= 5, f"应该至少有5个资产记录，实际有{len(all_assets)}个"

        # 7. 按子类类型查询
        exchange_funds = (
            test_db_session.query(Asset)
            .filter(Asset.asset_subtype == "asset_exchange_fund")
            .all()
        )

        funds = test_db_session.query(Asset).filter(Asset.asset_subtype == "asset_fund").all()

        etfs = test_db_session.query(Asset).filter(Asset.asset_subtype == "asset_fund_etf").all()

        lofs = test_db_session.query(Asset).filter(Asset.asset_subtype == "asset_fund_lof").all()

        # 验证我们插入的记录是否存在
        exchange_fund_ids = [ef.id for ef in exchange_funds]
        fund_ids = [f.id for f in funds]
        etf_ids = [e.id for e in etfs]
        lof_ids = [l.id for l in lofs]

        assert exchange_fund.id in exchange_fund_ids, "插入的场内基金应该在查询结果中"
        assert asset_fund.id in fund_ids, "插入的基金应该在查询结果中"
        assert asset_etf.id in etf_ids, "插入的ETF应该在查询结果中"
        assert asset_lof.id in lof_ids, "插入的LOF应该在查询结果中"

        # 8. 直接查询子类
        exchange_fund_direct = test_db_session.query(AssetExchangeFund).first()
        assert exchange_fund_direct is not None, "应该能直接查询到AssetExchangeFund记录"
        assert exchange_fund_direct.exchange_market == "SH", "场内基金交易市场应该是SH"

        etf_direct = test_db_session.query(AssetFundETF).first()
        assert etf_direct is not None, "应该能直接查询到AssetFundETF记录"
        assert (
            etf_direct.tracking_index_name == "中证500指数"
        ), "ETF跟踪指数应该是中证500指数"

        lof_direct = test_db_session.query(AssetFundLOF).first()
        assert lof_direct is not None, "应该能直接查询到AssetFundLOF记录"
        assert lof_direct.listing_exchange == "SZ", "LOF上市交易所应该是SZ"

        # 9. 使用Schema序列化基类数据
        asset_schema = AssetSchema()
        base_asset_serialized = asset_schema.dump(base_asset)

        # 验证基类序列化结果
        assert "id" in base_asset_serialized, "序列化结果应该包含id字段"
        assert "asset_name" in base_asset_serialized, "序列化结果应该包含asset_name字段"
        assert "asset_type" in base_asset_serialized, "序列化结果应该包含asset_type字段"
        assert "market" in base_asset_serialized, "序列化结果应该包含market字段"
        assert "currency" in base_asset_serialized, "序列化结果应该包含currency字段"
        assert (
            base_asset_serialized["asset_name"] == "基础资产测试"
        ), "资产名称应该正确序列化"

        # 10. 使用Schema序列化子类数据
        exchange_fund_schema = AssetExchangeFundSchema()
        exchange_fund_serialized = exchange_fund_schema.dump(exchange_fund_direct)

        # 验证场内基金序列化结果
        assert (
            "exchange_market" in exchange_fund_serialized
        ), "序列化结果应该包含exchange_market字段"
        assert "sub_type" in exchange_fund_serialized, "序列化结果应该包含sub_type字段"
        assert (
            "tracking_index" in exchange_fund_serialized
        ), "序列化结果应该包含tracking_index字段"
        assert (
            exchange_fund_serialized["exchange_market"] == "SH"
        ), "交易市场应该正确序列化"
        assert exchange_fund_serialized["sub_type"] == "ETF", "子类型应该正确序列化"

        # 11. 使用AssetFundSchema序列化基金数据
        fund_schema = AssetFundSchema()
        fund_serialized = fund_schema.dump(asset_fund)

        # 验证基金序列化结果
        assert "fund_type" in fund_serialized, "序列化结果应该包含fund_type字段"
        assert "trading_mode" in fund_serialized, "序列化结果应该包含trading_mode字段"
        assert "fund_company" in fund_serialized, "序列化结果应该包含fund_company字段"
        assert "fund_manager" in fund_serialized, "序列化结果应该包含fund_manager字段"
        assert fund_serialized["fund_type"] == "INDEX_FUND", "基金类型应该正确序列化"
        assert (
            fund_serialized["fund_company"] == "测试基金公司"
        ), "基金公司应该正确序列化"

        # 12. 使用AssetFundETFSchema序列化ETF数据
        etf_schema = AssetFundETFSchema()
        etf_serialized = etf_schema.dump(etf_direct)

        # 验证ETF序列化结果
        assert (
            "tracking_index_code" in etf_serialized
        ), "序列化结果应该包含tracking_index_code字段"
        assert (
            "tracking_index_name" in etf_serialized
        ), "序列化结果应该包含tracking_index_name字段"
        assert (
            "primary_exchange" in etf_serialized
        ), "序列化结果应该包含primary_exchange字段"
        assert (
            "dividend_frequency" in etf_serialized
        ), "序列化结果应该包含dividend_frequency字段"
        assert (
            etf_serialized["tracking_index_name"] == "中证500指数"
        ), "跟踪指数名称应该正确序列化"
        assert (
            etf_serialized["tracking_index_code"] == "000905"
        ), "跟踪指数代码应该正确序列化"

        # 13. 使用AssetFundLOFSchema序列化LOF数据
        lof_schema = AssetFundLOFSchema()
        lof_serialized = lof_schema.dump(lof_direct)

        # 验证LOF序列化结果
        assert (
            "listing_exchange" in lof_serialized
        ), "序列化结果应该包含listing_exchange字段"
        assert (
            "subscription_fee_rate" in lof_serialized
        ), "序列化结果应该包含subscription_fee_rate字段"
        assert (
            "redemption_fee_rate" in lof_serialized
        ), "序列化结果应该包含redemption_fee_rate字段"
        assert lof_serialized["listing_exchange"] == "SZ", "上市交易所应该正确序列化"
        assert (
            float(lof_serialized["subscription_fee_rate"]) == 0.0150
        ), "申购费率应该正确序列化"

        # 14. 批量序列化测试
        all_assets_serialized = [asset_schema.dump(asset) for asset in all_assets]
        assert (
            len(all_assets_serialized) >= 5
        ), f"应该至少序列化5个资产记录，实际序列化了{len(all_assets_serialized)}个"

        # 验证每个序列化结果都包含基本字段
        for serialized_asset in all_assets_serialized:
            assert "id" in serialized_asset, "每个序列化结果都应该包含id字段"
            assert (
                "asset_name" in serialized_asset
            ), "每个序列化结果都应该包含asset_name字段"
            assert (
                "asset_type" in serialized_asset
            ), "每个序列化结果都应该包含asset_type字段"

        # 15. 验证多态继承的类型识别
        for asset in all_assets:
            if hasattr(asset, "exchange_market"):
                # 这是AssetExchangeFund或其子类
                assert asset.asset_subtype in [
                    "asset_exchange_fund"
                ], f"场内基金的子类型应该是asset_exchange_fund，实际是{asset.asset_subtype}"
            elif hasattr(asset, "fund_type"):
                # 这是AssetFund或其子类
                assert asset.asset_subtype in [
                    "asset_fund",
                    "asset_fund_etf",
                    "asset_fund_lof",
                ], f"基金的子类型应该是asset_fund/asset_fund_etf/asset_fund_lof之一，实际是{asset.asset_subtype}"

        print(
            f"测试完成：成功插入并查询了{len(all_assets)}个资产记录（包含我们插入的5个记录）"
        )
        print(f"基类Asset序列化结果: {base_asset_serialized}")
        print(f"场内基金序列化结果: {exchange_fund_serialized}")
        print(f"ETF序列化结果: {etf_serialized}")
        print(f"LOF序列化结果: {lof_serialized}")
