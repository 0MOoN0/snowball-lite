# -*- coding: UTF-8 -*-
"""
AssetInheritanceUpdateService 测试类

测试覆盖范围：
- _get_current_instance 方法的核心功能测试
- 多态继承查询的正确性验证
- 不同Asset子类的数据获取测试
- 边界条件和异常情况处理

测试策略：
- 使用TestBaseForAssetModels确保数据库事务隔离
- 测试Asset基类及其所有子类的查询功能
- 验证SQLAlchemy多态继承的查询机制
- 测试方法返回值的正确性和完整性
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import MarketEnum, CurrencyEnum
from web.models.asset.asset import Asset, AssetExchangeFund
from web.models.asset.asset_fund import AssetFund, AssetFundETF, AssetFundLOF
from web.services.asset.asset_inheritance_update_service import AssetInheritanceUpdateService
from web.webtest.test_base import TestBaseForAssetModels


class TestAssetInheritanceUpdateService(TestBaseForAssetModels):
    """
    AssetInheritanceUpdateService 测试类
    
    测试覆盖范围：
    - _get_current_instance 方法在不同Asset子类上的查询功能
    - 多态继承查询的数据完整性验证
    - 方法返回值的正确性和类型验证
    - 边界条件处理（不存在的ID、无效参数等）
    
    使用TestBaseForAssetModels基类的原因：
    - 专门针对Asset模型及其子类的测试
    - 确保数据库事务隔离，避免测试数据相互影响
    - 绑定到'snowball'数据库，与Asset模型的__bind_key__一致
    - 测试结束后自动清理数据，保持数据库清洁状态
    """

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 注意：不在这里初始化service，而是在每个测试方法中传入正确的session
        pass

    # ==================== 基础功能测试 ====================

    def test_get_current_instance_with_base_asset(self, test_db_session):
        """
        测试获取Asset基类实例
        
        验证点:
        - 能够正确查询并返回Asset基类实例
        - 返回的实例类型正确
        - 实例数据完整性验证
        - polymorphic_identity为'asset'
        """
        # 使用正确的数据库会话创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建Asset基类测试数据
        base_asset = Asset(
            asset_name="基础资产测试",
            asset_type=AssetTypeEnum.STOCK.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="TEST001",
            asset_short_code="T001",
            asset_status=0,
            create_time=datetime.now(),
        )
        test_db_session.add(base_asset)
        test_db_session.flush()  # 获取ID
        asset_id = base_asset.id

        # 调用被测试方法
        result = service._get_current_instance(asset_id)

        # 验证返回结果
        assert result is not None, "应该返回Asset实例"
        assert isinstance(result, Asset), "返回的应该是Asset类型的实例"
        assert result.id == asset_id, "返回实例的ID应该匹配"
        assert result.asset_name == "基础资产测试", "资产名称应该匹配"
        assert result.asset_type == AssetTypeEnum.STOCK.value, "资产类型应该匹配"
        assert result.asset_subtype == "asset", "多态标识应该为'asset'"

    def test_get_current_instance_with_asset_fund(self, test_db_session):
        """
        测试获取AssetFund子类实例
        
        验证点:
        - 能够正确查询并返回AssetFund子类实例
        - 返回的实例包含基类和子类的所有字段
        - 多态继承查询的正确性
        - polymorphic_identity为'fund'
        """
        # 使用正确的数据库会话创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建AssetFund测试数据
        fund_asset = AssetFund(
            asset_name="测试基金",
            asset_type=AssetTypeEnum.FUND.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="FUND001",
            asset_short_code="F001",
            asset_status=0,
            fund_type="STOCK_FUND",
            trading_mode="OPEN_END",
            fund_company="测试基金公司",
            fund_manager="测试基金经理",
            fund_status=1,
            create_time=datetime.now(),
        )
        test_db_session.add(fund_asset)
        test_db_session.flush()
        asset_id = fund_asset.id

        # 调用被测试方法
        result = service._get_current_instance(asset_id)

        # 验证返回结果
        assert result is not None, "应该返回AssetFund实例"
        assert isinstance(result, AssetFund), "返回的应该是AssetFund类型的实例"
        assert result.id == asset_id, "返回实例的ID应该匹配"
        
        # 验证基类字段
        assert result.asset_name == "测试基金", "资产名称应该匹配"
        assert result.asset_type == AssetTypeEnum.FUND.value, "资产类型应该匹配"
        assert result.asset_subtype == "asset_fund", "多态标识应该为'asset_fund'"
        
        # 验证子类特有字段
        assert result.fund_type == "STOCK_FUND", "基金类型应该匹配"
        assert result.trading_mode == "OPEN_END", "交易模式应该匹配"
        assert result.fund_company == "测试基金公司", "基金公司应该匹配"
        assert result.fund_manager == "测试基金经理", "基金经理应该匹配"

    def test_get_current_instance_with_asset_fund_etf(self, test_db_session):
        """
        测试获取AssetFundETF子类实例
        
        验证点:
        - 能够正确查询并返回AssetFundETF子类实例
        - 返回的实例包含完整的继承链数据（Asset -> AssetFund -> AssetFundETF）
        - ETF特有字段的正确性
        - polymorphic_identity为'fund_etf'
        """
        # 使用正确的数据库会话创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建AssetFundETF测试数据
        etf_asset = AssetFundETF(
            asset_name="测试ETF基金",
            asset_type=AssetTypeEnum.FUND_ETF.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="ETF001",
            asset_short_code="E001",
            asset_status=0,
            fund_type="INDEX_FUND",
            trading_mode="ETF",
            fund_company="测试ETF公司",
            fund_manager="测试ETF经理",
            fund_status=1,
            tracking_index_code="000300",
            tracking_index_name="沪深300指数",
            primary_exchange="SH",
            dividend_frequency="QUARTERLY",
            create_time=datetime.now(),
        )
        test_db_session.add(etf_asset)
        test_db_session.flush()
        asset_id = etf_asset.id

        # 调用被测试方法
        result = service._get_current_instance(asset_id)

        # 验证返回结果
        assert result is not None, "应该返回AssetFundETF实例"
        assert isinstance(result, AssetFundETF), "返回的应该是AssetFundETF类型的实例"
        assert result.id == asset_id, "返回实例的ID应该匹配"
        
        # 验证基类字段（Asset）
        assert result.asset_name == "测试ETF基金", "资产名称应该匹配"
        assert result.asset_type == AssetTypeEnum.FUND_ETF.value, "资产类型应该匹配"
        assert result.asset_subtype == "asset_fund_etf", "多态标识应该为'asset_fund_etf'"
        
        # 验证中间类字段（AssetFund）
        assert result.fund_type == "INDEX_FUND", "基金类型应该匹配"
        assert result.trading_mode == "ETF", "交易模式应该匹配"
        assert result.fund_company == "测试ETF公司", "基金公司应该匹配"
        
        # 验证子类特有字段（AssetFundETF）
        assert result.tracking_index_code == "000300", "跟踪指数代码应该匹配"
        assert result.tracking_index_name == "沪深300指数", "跟踪指数名称应该匹配"
        assert result.primary_exchange == "SH", "主要交易所应该匹配"
        assert result.dividend_frequency == "QUARTERLY", "分红频率应该匹配"

    def test_get_current_instance_with_asset_fund_lof(self, test_db_session):
        """
        测试获取AssetFundLOF子类实例
        
        验证点:
        - 能够正确查询并返回AssetFundLOF子类实例
        - 返回的实例包含完整的继承链数据（Asset -> AssetFund -> AssetFundLOF）
        - LOF特有字段的正确性
        - polymorphic_identity为'fund_lof'
        """
        # 使用正确的数据库会话创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建AssetFundLOF测试数据
        lof_asset = AssetFundLOF(
            asset_name="测试LOF基金",
            asset_type=AssetTypeEnum.FUND_LOF.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="LOF001",
            asset_short_code="L001",
            asset_status=0,
            fund_type="MIXED_FUND",
            trading_mode="LOF",
            fund_company="测试LOF公司",
            fund_manager="测试LOF经理",
            fund_status=1,
            listing_exchange="SZ",
            subscription_fee_rate=Decimal("0.015"),
            redemption_fee_rate=Decimal("0.005"),
            create_time=datetime.now(),
        )
        test_db_session.add(lof_asset)
        test_db_session.flush()
        asset_id = lof_asset.id

        # 调用被测试方法
        result = service._get_current_instance(asset_id)

        # 验证返回结果
        assert result is not None, "应该返回AssetFundLOF实例"
        assert isinstance(result, AssetFundLOF), "返回的应该是AssetFundLOF类型的实例"
        assert result.id == asset_id, "返回实例的ID应该匹配"
        
        # 验证基类字段（Asset）
        assert result.asset_name == "测试LOF基金", "资产名称应该匹配"
        assert result.asset_type == AssetTypeEnum.FUND_LOF.value, "资产类型应该匹配"
        assert result.asset_subtype == "asset_fund_lof", "多态标识应该为'asset_fund_lof'"
        
        # 验证中间类字段（AssetFund）
        assert result.fund_type == "MIXED_FUND", "基金类型应该匹配"
        assert result.trading_mode == "LOF", "交易模式应该匹配"
        assert result.fund_company == "测试LOF公司", "基金公司应该匹配"
        
        # 验证子类特有字段（AssetFundLOF）
        assert result.listing_exchange == "SZ", "上市交易所应该匹配"
        assert result.subscription_fee_rate == Decimal("0.015"), "申购费率应该匹配"
        assert result.redemption_fee_rate == Decimal("0.005"), "赎回费率应该匹配"


    # ==================== 多态继承查询测试 ====================

    def test_get_current_instance_polymorphic_query_correctness(self, test_db_session):
        """
        测试多态继承查询的正确性
        
        验证点:
        - 使用with_polymorphic查询能够正确获取子类完整数据
        - 不同子类的实例类型正确
        - 查询结果包含所有继承链的字段
        - polymorphic_identity字段的正确性
        """
        # 使用正确的数据库会话创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建不同类型的资产实例
        assets_data = []
        
        # 基础资产
        base_asset = Asset(
            asset_name="基础资产",
            asset_type=AssetTypeEnum.STOCK.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            create_time=datetime.now(),
        )
        test_db_session.add(base_asset)
        test_db_session.flush()
        assets_data.append((base_asset.id, Asset, "asset"))
        
        # 基金资产
        fund_asset = AssetFund(
            asset_name="基金资产",
            asset_type=AssetTypeEnum.FUND.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            fund_type="STOCK_FUND",
            trading_mode="OPEN_END",
            fund_status=1,
            create_time=datetime.now(),
        )
        test_db_session.add(fund_asset)
        test_db_session.flush()
        assets_data.append((fund_asset.id, AssetFund, "asset_fund"))
        
        # ETF资产
        etf_asset = AssetFundETF(
            asset_name="ETF资产",
            asset_type=AssetTypeEnum.FUND_ETF.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            fund_type="INDEX_FUND",
            trading_mode="ETF",
            fund_status=1,
            tracking_index_code="000300",
            create_time=datetime.now(),
        )
        test_db_session.add(etf_asset)
        test_db_session.flush()
        assets_data.append((etf_asset.id, AssetFundETF, "asset_fund_etf"))

        # 测试每个资产的查询结果
        for asset_id, expected_type, expected_subtype in assets_data:
            result = service._get_current_instance(asset_id)
            
            assert result is not None, f"资产ID {asset_id} 应该返回实例"
            assert isinstance(result, expected_type), f"资产ID {asset_id} 应该返回 {expected_type.__name__} 类型"
            assert result.id == asset_id, f"资产ID {asset_id} 的ID应该匹配"
            assert result.asset_subtype == expected_subtype, f"资产ID {asset_id} 的多态标识应该为 {expected_subtype}"

    def test_get_polymorphic_identity_with_valid_instances(self, test_db_session):
        """
        测试_get_polymorphic_identity方法在有效模型实例上的功能
        
        验证点:
        - Asset基类实例返回'asset'
        - AssetFund实例返回'asset_fund'
        - AssetFundETF实例返回'asset_fund_etf'
        - AssetFundLOF实例返回'asset_fund_lof'
        - AssetExchangeFund实例返回'exchange_fund'
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 创建Asset基类实例
        base_asset = Asset(
            asset_name="测试基础资产",
            asset_type=AssetTypeEnum.ASSET.value,
            asset_subtype="asset",
            create_time=datetime.now(),
        )
        test_db_session.add(base_asset)
        test_db_session.flush()
        
        # 创建AssetFund实例
        fund_asset = AssetFund(
            asset_name="测试基金",
            asset_type=AssetTypeEnum.FUND.value,
            fund_type="INDEX_FUND",
            trading_mode="OPEN_END",
            fund_status=1,
            create_time=datetime.now(),
        )
        test_db_session.add(fund_asset)
        test_db_session.flush()
        
        # 创建AssetFundETF实例
        etf_asset = AssetFundETF(
            asset_name="测试ETF基金",
            asset_type=AssetTypeEnum.FUND_ETF.value,
            fund_type="INDEX_FUND",
            trading_mode="ETF",
            fund_status=1,
            tracking_index_code="000300",
            create_time=datetime.now(),
        )
        test_db_session.add(etf_asset)
        test_db_session.flush()
        
        # 创建AssetFundLOF实例
        lof_asset = AssetFundLOF(
            asset_name="测试LOF基金",
            asset_type=AssetTypeEnum.FUND_LOF.value,
            fund_type="INDEX_FUND",
            trading_mode="LOF",
            fund_status=1,
            create_time=datetime.now(),
        )
        test_db_session.add(lof_asset)
        test_db_session.flush()
        
        # 测试各种实例的多态标识
        test_cases = [
            (base_asset, "asset"),
            (fund_asset, "asset_fund"),
            (etf_asset, "asset_fund_etf"),
            (lof_asset, "asset_fund_lof"),
        ]
        
        for instance, expected_identity in test_cases:
            result = service._get_polymorphic_identity(instance)
            assert result == expected_identity, f"{instance.__class__.__name__} 实例的多态标识应该为 {expected_identity}，实际为 {result}"

    def test_derive_target_polymorphic_identity_comprehensive(self, test_db_session):
        """
        测试derive_target_polymorphic_identity方法的综合功能
        
        验证点:
        - 支持整数类型的asset_type输入并正确映射到polymorphic_identity
        - 支持AssetTypeEnum枚举类型的asset_type输入
        - 不同AssetTypeEnum值到polymorphic_identity的正确映射
        - 无asset_type字段时保持原有polymorphic_identity
        - 无效asset_type时抛出WebBaseException异常
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 测试用例1: 整数类型的asset_type输入
        update_data_int = {"asset_type": AssetTypeEnum.FUND.value}  # 1
        result = service.derive_target_polymorphic_identity(update_data_int, "asset")
        assert result == "asset_fund", f"AssetTypeEnum.FUND({AssetTypeEnum.FUND.value})应该映射到'asset_fund'，实际为{result}"
        
        # 测试用例2: AssetTypeEnum枚举类型的asset_type输入
        update_data_enum = {"asset_type": AssetTypeEnum.FUND_ETF}
        result = service.derive_target_polymorphic_identity(update_data_enum, "asset")
        assert result == "asset_fund_etf", f"AssetTypeEnum.FUND_ETF应该映射到'asset_fund_etf'，实际为{result}"
        
        # 测试用例3: 不同AssetTypeEnum值的映射验证
        asset_type_mappings = [
            (AssetTypeEnum.ASSET, "asset"),
            (AssetTypeEnum.FUND, "asset_fund"),
            (AssetTypeEnum.FUND_ETF, "asset_fund_etf"),
            (AssetTypeEnum.FUND_LOF, "asset_fund_lof"),
            (AssetTypeEnum.STOCK, "asset"),  # 股票归类为基础资产
            (AssetTypeEnum.INDEX, "asset"),  # 指数归类为基础资产
        ]
        
        for asset_type_enum, expected_identity in asset_type_mappings:
            # 测试整数值
            update_data = {"asset_type": asset_type_enum.value}
            result = service.derive_target_polymorphic_identity(update_data, "current_identity")
            assert result == expected_identity, f"AssetTypeEnum.{asset_type_enum.name}({asset_type_enum.value})应该映射到'{expected_identity}'，实际为{result}"
            
            # 测试枚举值
            update_data = {"asset_type": asset_type_enum}
            result = service.derive_target_polymorphic_identity(update_data, "current_identity")
            assert result == expected_identity, f"AssetTypeEnum.{asset_type_enum.name}应该映射到'{expected_identity}'，实际为{result}"
        
        # 测试用例4: 无asset_type字段时保持原有polymorphic_identity
        update_data_empty = {"other_field": "value"}
        current_identity = "asset_fund_lof"
        result = service.derive_target_polymorphic_identity(update_data_empty, current_identity)
        assert result == current_identity, f"无asset_type字段时应该保持原有polymorphic_identity '{current_identity}'，实际为{result}"
        
        # 测试用例5: asset_type为None时保持原有polymorphic_identity
        update_data_none = {"asset_type": None}
        current_identity = "asset_exchange_fund"
        result = service.derive_target_polymorphic_identity(update_data_none, current_identity)
        assert result == current_identity, f"asset_type为None时应该保持原有polymorphic_identity '{current_identity}'，实际为{result}"
        
        # 测试用例6: 无效asset_type类型时抛出WebBaseException
        from web.web_exception import WebBaseException
        
        invalid_asset_types = [
            "invalid_string",
            999,  # 无效的整数值
            [],   # 列表类型
            {},   # 字典类型
        ]
        
        for invalid_type in invalid_asset_types:
            update_data = {"asset_type": invalid_type}
            with pytest.raises(WebBaseException) as exc_info:
                service.derive_target_polymorphic_identity(update_data, "asset")
            assert "无效的资产类型" in str(exc_info.value), f"无效的asset_type '{invalid_type}' 应该抛出包含'无效的资产类型'的WebBaseException"

    # ==================== 多态转换测试 ====================

    def test_perform_polymorphic_conversion_asset_to_fund(self, test_db_session):
        """
        测试从Asset基类转换为AssetFund的完整多态转换流程
        
        验证点:
        - 能够成功执行从asset到fund的多态转换
        - 原有Asset实例被正确删除
        - 新的AssetFund实例被正确创建
        - 转换后的实例包含原有数据和新增数据
        - 字段映射处理正确执行
        - 多态标识正确更新
        - 返回成功状态和正确消息
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 创建原始Asset实例
        original_asset = Asset(
            asset_name="测试基础资产",
            asset_type=AssetTypeEnum.ASSET.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="TEST001",
            asset_short_code="T001",
            asset_status=0,
            create_time=datetime.now(),
        )
        test_db_session.add(original_asset)
        test_db_session.flush()
        original_id = original_asset.id
        
        # 准备转换数据
        update_data = {
            "asset_name": "转换后的基金",
            "asset_type": AssetTypeEnum.FUND.value,
            "fund_type": "STOCK_FUND",
            "trading_mode": "OPEN_END",
            "fund_company": "测试基金公司",
            "fund_manager": "测试基金经理",
            "fund_status": 1,
        }
        
        # 执行完整的多态转换流程（包括字段映射和多态标识更新）
        success, message = service.update_with_polymorphic_conversion(
            original_id, update_data
        )
        
        # 验证转换结果
        assert success is True, f"多态转换应该成功，但返回失败: {message}"

        # 验证原有Asset实例仍然存在（基类不会被删除，只删除子类）
        # 由于原始Asset没有子类，所以Asset实例本身不会被删除
        remaining_asset = test_db_session.query(Asset).filter(Asset.id == original_id).first()
        assert remaining_asset is not None, "Asset基类实例不应该被删除"

        test_db_session.expunge(remaining_asset)

        # 验证新的AssetFund实例被创建
        new_fund = test_db_session.query(AssetFund).filter(AssetFund.id == original_id).first()
        assert new_fund is not None, "应该创建新的AssetFund实例"
        assert isinstance(new_fund, AssetFund), "新实例应该是AssetFund类型"
        
        # 验证字段映射处理正确执行
        assert new_fund.id == original_id, "新实例应该保持原有ID"
        assert new_fund.asset_name == "转换后的基金", "资产名称应该通过字段映射正确更新"
        assert new_fund.asset_type == AssetTypeEnum.FUND.value, "资产类型应该通过字段映射正确更新为FUND"
        assert new_fund.fund_type == "STOCK_FUND", "基金类型应该通过字段映射正确设置"
        assert new_fund.trading_mode == "OPEN_END", "交易模式应该通过字段映射正确设置"
        assert new_fund.fund_company == "测试基金公司", "基金公司应该通过字段映射正确设置"
        assert new_fund.fund_manager == "测试基金经理", "基金经理应该通过字段映射正确设置"
        assert new_fund.fund_status == 1, "基金状态应该通过字段映射正确设置"
        
        # 验证多态标识正确更新
        assert new_fund.asset_subtype == "asset_fund", "多态标识应该正确更新为'asset_fund'"
        
        # 验证原有数据保持不变
        assert new_fund.market == MarketEnum.CN.value, "原有市场信息应该保持不变"
        assert new_fund.currency == CurrencyEnum.CNY.value, "原有货币信息应该保持不变"
        assert new_fund.asset_code == "TEST001", "原有资产代码应该保持不变"
        assert new_fund.asset_short_code == "T001", "原有资产简码应该保持不变"

    def test_perform_polymorphic_conversion_asset_to_fund_etf(self, test_db_session):
        """
        测试从Asset基类转换为AssetFundETF的多态转换
        
        验证点:
        - 能够成功执行从asset到fund_etf的多态转换
        - 原有Asset实例被正确删除
        - 新的AssetFundETF实例被正确创建
        - 转换后的实例包含完整的继承链数据（Asset -> AssetFund -> AssetFundETF）
        - ETF特有字段被正确设置
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 创建原始Asset实例
        original_asset = Asset(
            asset_name="测试基础资产",
            asset_type=AssetTypeEnum.ASSET.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="TEST002",
            asset_short_code="T002",
            asset_status=0,
            create_time=datetime.now(),
        )
        test_db_session.add(original_asset)
        test_db_session.flush()
        original_id = original_asset.id
        
        # 准备转换数据
        update_data = {
            "asset_name": "转换后的ETF基金",
            "asset_type": AssetTypeEnum.FUND_ETF.value,
            "fund_type": "INDEX_FUND",
            "trading_mode": "ETF",
            "fund_company": "测试ETF公司",
            "fund_manager": "测试ETF经理",
            "fund_status": 1,
            "tracking_index_code": "000300",
            "tracking_index_name": "沪深300指数",
            "primary_exchange": "SH",
            "dividend_frequency": "QUARTERLY",
        }
        
        # 执行完整的多态转换流程（包括字段映射和多态标识更新）
        success, message = service.update_with_polymorphic_conversion(
            original_id, update_data
        )
        
        # 验证转换结果
        assert success is True, f"多态转换应该成功，但返回失败: {message}"

        # 验证原有Asset实例仍然存在（基类不会被删除，只删除子类）
        # 由于原始Asset没有子类，所以Asset实例本身不会被删除
        remaining_asset = test_db_session.query(Asset).filter(Asset.id == original_id).first()
        assert remaining_asset is not None, "Asset基类实例不应该被删除"

        test_db_session.expunge(remaining_asset)
        
        # 验证新的AssetFundETF实例被创建
        new_etf = test_db_session.query(AssetFundETF).filter(AssetFundETF.id == original_id).first()
        assert new_etf is not None, "应该创建新的AssetFundETF实例"
        assert isinstance(new_etf, AssetFundETF), "新实例应该是AssetFundETF类型"
        
        # 验证基类数据（Asset）
        assert new_etf.id == original_id, "新实例应该保持原有ID"
        assert new_etf.asset_name == "转换后的ETF基金", "资产名称应该更新"
        assert new_etf.asset_type == AssetTypeEnum.FUND_ETF.value, "资产类型应该更新为FUND_ETF"
        assert new_etf.asset_subtype == "asset_fund_etf", "多态标识应该为'asset_fund_etf'"
        
        # 验证中间类数据（AssetFund）
        assert new_etf.fund_type == "INDEX_FUND", "基金类型应该正确设置"
        assert new_etf.trading_mode == "ETF", "交易模式应该正确设置"
        assert new_etf.fund_company == "测试ETF公司", "基金公司应该正确设置"
        assert new_etf.fund_manager == "测试ETF经理", "基金经理应该正确设置"
        assert new_etf.fund_status == 1, "基金状态应该正确设置"
        
        # 验证子类特有数据（AssetFundETF）
        assert new_etf.tracking_index_code == "000300", "跟踪指数代码应该正确设置"
        assert new_etf.tracking_index_name == "沪深300指数", "跟踪指数名称应该正确设置"
        assert new_etf.primary_exchange == "SH", "主要交易所应该正确设置"
        assert new_etf.dividend_frequency == "QUARTERLY", "分红频率应该正确设置"

    def test_perform_polymorphic_conversion_fund_to_fund_etf(self, test_db_session):
        """
        测试从AssetFund转换为AssetFundETF的多态转换
        
        验证点:
        - 能够成功执行从fund到fund_etf的多态转换
        - 原有AssetFund实例被正确删除
        - 新的AssetFundETF实例被正确创建
        - 转换后的实例保留原有基金数据并添加ETF特有数据
        - 继承链数据的完整性
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 创建原始AssetFund实例
        original_fund = AssetFund(
            asset_name="测试基金",
            asset_type=AssetTypeEnum.FUND.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="FUND003",
            asset_short_code="F003",
            asset_status=0,
            fund_type="MIXED_FUND",
            trading_mode="OPEN_END",
            fund_company="原基金公司",
            fund_manager="原基金经理",
            fund_status=1,
            create_time=datetime.now(),
        )
        test_db_session.add(original_fund)
        test_db_session.flush()
        original_id = original_fund.id
        
        # 准备转换数据
        update_data = {
            "asset_name": "转换后的ETF基金",
            "asset_type": AssetTypeEnum.FUND_ETF.value,
            "fund_type": "INDEX_FUND",  # 更新基金类型
            "trading_mode": "ETF",      # 更新交易模式
            "fund_company": "新ETF公司", # 更新基金公司
            "tracking_index_code": "000905",
            "tracking_index_name": "中证500指数",
            "primary_exchange": "SZ",
            "dividend_frequency": "SEMI_ANNUAL",
        }
        
        # 执行完整的多态转换流程（包括字段映射和多态标识更新）
        success, message = service.update_with_polymorphic_conversion(
            original_id, update_data
        )
        
        # 验证转换结果
        assert success is True, f"多态转换应该成功，但返回失败: {message}"

        # 验证原有Asset实例仍然存在（基类不会被删除，只删除子类）
        # 由于原始AssetFund有子类，所以AssetFund实例会被删除并重新创建为AssetFundETF
        remaining_asset = test_db_session.query(Asset).filter(Asset.id == original_id).first()
        assert remaining_asset is not None, "Asset基类实例不应该被删除"

        test_db_session.expunge(remaining_asset)
        
        # 验证新的AssetFundETF实例被创建
        new_etf = test_db_session.query(AssetFundETF).filter(AssetFundETF.id == original_id).first()
        assert new_etf is not None, "应该创建新的AssetFundETF实例"
        assert isinstance(new_etf, AssetFundETF), "新实例应该是AssetFundETF类型"
        
        # 验证基类数据（Asset）
        assert new_etf.id == original_id, "新实例应该保持原有ID"
        assert new_etf.asset_name == "转换后的ETF基金", "资产名称应该更新"
        assert new_etf.asset_type == AssetTypeEnum.FUND_ETF.value, "资产类型应该更新为FUND_ETF"
        assert new_etf.asset_subtype == "asset_fund_etf", "多态标识应该为'asset_fund_etf'"
        assert new_etf.market == MarketEnum.CN.value, "市场信息应该保留"
        assert new_etf.currency == CurrencyEnum.CNY.value, "货币信息应该保留"
        
        # 验证中间类数据（AssetFund）- 应该使用更新后的数据
        assert new_etf.fund_type == "INDEX_FUND", "基金类型应该更新为INDEX_FUND"
        assert new_etf.trading_mode == "ETF", "交易模式应该更新为ETF"
        assert new_etf.fund_company == "新ETF公司", "基金公司应该更新"
        assert new_etf.fund_manager == "原基金经理", "基金经理应该保留原值（未在更新数据中指定）"
        assert new_etf.fund_status == 1, "基金状态应该保留"
        
        # 验证子类特有数据（AssetFundETF）
        assert new_etf.tracking_index_code == "000905", "跟踪指数代码应该正确设置"
        assert new_etf.tracking_index_name == "中证500指数", "跟踪指数名称应该正确设置"
        assert new_etf.primary_exchange == "SZ", "主要交易所应该正确设置"
        assert new_etf.dividend_frequency == "SEMI_ANNUAL", "分红频率应该正确设置"

    def test_perform_polymorphic_conversion_fund_etf_to_fund_lof(self, test_db_session):
        """
        测试从AssetFundETF转换为AssetFundLOF的多态转换
        
        验证点:
        - 能够成功执行从fund_etf到fund_lof的多态转换
        - 原有AssetFundETF实例被正确删除
        - 新的AssetFundLOF实例被正确创建
        - 转换后的实例保留原有基金和ETF数据并添加LOF特有数据
        - 继承链数据的完整性和正确性
        - 数据无遗失，字段映射正确
        - 多态标识正确更新
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 创建原始AssetFundETF实例
        original_etf = AssetFundETF(
            asset_name="测试ETF基金",
            asset_type=AssetTypeEnum.FUND_ETF.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="ETF004",
            asset_short_code="E004",
            asset_status=0,
            fund_type="INDEX_FUND",
            trading_mode="ETF",
            fund_company="原ETF公司",
            fund_manager="原ETF经理",
            fund_status=1,
            tracking_index_code="000300",
            tracking_index_name="沪深300指数",
            primary_exchange="SH",
            dividend_frequency="QUARTERLY",
            create_time=datetime.now(),
        )
        test_db_session.add(original_etf)
        test_db_session.flush()
        original_id = original_etf.id
        
        # 准备转换数据 - 从ETF转换为LOF
        update_data = {
            "asset_name": "转换后的LOF基金",
            "asset_type": AssetTypeEnum.FUND_LOF.value,
            "fund_type": "MIXED_FUND",      # 更新基金类型
            "trading_mode": "LOF",          # 更新交易模式
            "fund_company": "新LOF公司",     # 更新基金公司
            "fund_manager": "新LOF经理",     # 更新基金经理
            # LOF特有字段
            "listing_exchange": "SZ",
            "subscription_fee_rate": Decimal("0.012"),
            "redemption_fee_rate": Decimal("0.008"),
        }
        
        # 执行完整的多态转换流程
        success, message = service.update_with_polymorphic_conversion(
            original_id, update_data
        )
        
        # 验证转换结果
        assert success is True, f"多态转换应该成功，但返回失败: {message}"

        test_db_session.expunge(original_etf)

        # 验证原有Asset基类实例仍然存在
        remaining_asset = test_db_session.query(Asset).filter(Asset.id == original_id).first()
        assert remaining_asset is not None, "Asset基类实例不应该被删除"

        test_db_session.expunge(remaining_asset)
        
        # 验证原有AssetFundETF实例已被删除
        old_etf = test_db_session.query(AssetFundETF).filter(AssetFundETF.id == original_id).first()
        assert old_etf is None, "原有AssetFundETF实例应该被删除"

        # 验证新的AssetFundLOF实例被创建
        new_lof = test_db_session.query(AssetFundLOF).filter(AssetFundLOF.id == original_id).first()
        assert new_lof is not None, "应该创建新的AssetFundLOF实例"
        assert isinstance(new_lof, AssetFundLOF), "新实例应该是AssetFundLOF类型"
        
        # 验证基类数据（Asset）- 应该保留原有数据并更新指定字段
        assert new_lof.id == original_id, "新实例应该保持原有ID"
        assert new_lof.asset_name == "转换后的LOF基金", "资产名称应该更新"
        assert new_lof.asset_type == AssetTypeEnum.FUND_LOF.value, "资产类型应该更新为FUND_LOF"
        assert new_lof.asset_subtype == "asset_fund_lof", "多态标识应该为'asset_fund_lof'"
        assert new_lof.market == MarketEnum.CN.value, "市场信息应该保留"
        assert new_lof.currency == CurrencyEnum.CNY.value, "货币信息应该保留"
        assert new_lof.asset_code == "ETF004", "资产代码应该保留原值"
        assert new_lof.asset_short_code == "E004", "资产简称应该保留原值"
        assert new_lof.asset_status == 0, "资产状态应该保留原值"
        
        # 验证中间类数据（AssetFund）- 应该使用更新后的数据
        assert new_lof.fund_type == "MIXED_FUND", "基金类型应该更新为MIXED_FUND"
        assert new_lof.trading_mode == "LOF", "交易模式应该更新为LOF"
        assert new_lof.fund_company == "新LOF公司", "基金公司应该更新"
        assert new_lof.fund_manager == "新LOF经理", "基金经理应该更新"
        assert new_lof.fund_status == 1, "基金状态应该保留原值"
        
        # 验证子类特有数据（AssetFundLOF）- 新设置的LOF特有字段
        assert new_lof.listing_exchange == "SZ", "上市交易所应该正确设置"
        assert new_lof.subscription_fee_rate == Decimal("0.012"), "申购费率应该正确设置"
        assert new_lof.redemption_fee_rate == Decimal("0.008"), "赎回费率应该正确设置"
        
        # 验证ETF特有字段不再存在（因为已转换为LOF）
        # 注意：AssetFundLOF不包含ETF特有字段，所以这些字段应该不存在
        assert not hasattr(new_lof, 'tracking_index_code'), "ETF特有字段tracking_index_code不应该存在"
        assert not hasattr(new_lof, 'tracking_index_name'), "ETF特有字段tracking_index_name不应该存在"
        assert not hasattr(new_lof, 'primary_exchange'), "ETF特有字段primary_exchange不应该存在"
        assert not hasattr(new_lof, 'dividend_frequency'), "ETF特有字段dividend_frequency不应该存在"
        
        # 验证数据完整性 - 确保没有数据遗失
        assert new_lof.create_time is not None, "创建时间应该保留"
        
        # 验证转换后的实例能够正常查询和操作
        queried_lof = test_db_session.query(AssetFundLOF).filter(AssetFundLOF.id == original_id).first()
        assert queried_lof is not None, "转换后的LOF实例应该能够正常查询"
        assert queried_lof.asset_name == "转换后的LOF基金", "查询到的实例数据应该正确"
        
        # 验证多态查询的正确性
        polymorphic_query = test_db_session.query(Asset).filter(Asset.id == original_id).first()
        assert polymorphic_query is not None, "多态查询应该能找到实例"
        assert isinstance(polymorphic_query, AssetFundLOF), "多态查询应该返回正确的子类型"
        assert polymorphic_query.asset_subtype == "asset_fund_lof", "多态查询的实例类型应该正确"

    def test_handle_field_mapping_with_snake_case_fields(self, test_db_session):
        """
        测试handle_field_mapping方法的字段映射功能
        
        验证点:
        - 下划线命名字段正确映射到实例属性
        - 只更新实例中存在的属性
        - 不存在的属性被忽略
        - 字段值正确设置到实例属性
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建一个AssetFund实例用于测试
        fund_asset = AssetFund(
            asset_name="测试基金",
            asset_type=AssetTypeEnum.FUND.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="FUND001",
            asset_short_code="F001",
            asset_status=0,
            fund_type="STOCK_FUND",
            trading_mode="OPEN_END",
            fund_company="原基金公司",
            fund_manager="原基金经理",
            fund_status=1,
            create_time=datetime.now(),
        )
        test_db_session.add(fund_asset)
        test_db_session.flush()
        
        # 准备包含下划线命名的更新数据
        update_data = {
            "asset_name": "更新后的基金名称",  # 下划线命名，直接映射
            "fund_company": "更新后的基金公司",  # 下划线命名，直接映射
            "fund_manager": "更新后的基金经理",  # 下划线命名，直接映射
            "non_existent_field": "这个字段不存在",  # 不存在的字段，应被忽略
            "asset_code": "FUND002",  # 下划线命名，直接映射
        }
        
        # 调用被测试方法
        service.handle_field_mapping(fund_asset, update_data)
        
        # 验证字段映射结果
        assert fund_asset.asset_name == "更新后的基金名称", "asset_name字段应该正确更新"
        assert fund_asset.fund_company == "更新后的基金公司", "fund_company字段应该正确更新"
        assert fund_asset.fund_manager == "更新后的基金经理", "fund_manager字段应该正确更新"
        assert fund_asset.asset_code == "FUND002", "asset_code字段应该正确更新"
        
        # 验证不存在的字段被忽略（不会抛出异常）
        assert not hasattr(fund_asset, "non_existent_field"), "不存在的字段不应该被添加到实例中"
        
        # 验证未在update_data中的字段保持不变
        assert fund_asset.fund_type == "STOCK_FUND", "未更新的字段应该保持原值"
        assert fund_asset.trading_mode == "OPEN_END", "未更新的字段应该保持原值"
        assert fund_asset.fund_status == 1, "未更新的字段应该保持原值"

    def test_update_with_polymorphic_conversion_without_type_change(self, test_db_session):
        """
        测试update_with_polymorphic_conversion方法在不改变多态类型时更新其他字段的功能
        
        验证点:
        - 当update_data中不包含asset_type字段时，保持原有多态类型
        - 正确更新其他业务字段（asset_name、asset_code等）
        - 数据库事务正确提交
        - 返回成功状态和消息
        - 验证更新前后的数据变化
        """
        # 使用正确的数据库会话创建服务实例
        service = AssetInheritanceUpdateService(db_session=test_db_session)
        
        # 创建Asset基类测试数据
        original_asset = Asset(
            asset_name="原始资产名称",
            asset_type=AssetTypeEnum.STOCK.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="STOCK001",
            asset_short_code="S001",
            asset_status=0,
            create_time=datetime.now(),
        )
        test_db_session.add(original_asset)
        test_db_session.flush()
        asset_id = original_asset.id
        
        # 记录更新前的状态
        original_polymorphic_identity = original_asset.asset_subtype
        original_asset_type = original_asset.asset_type
        
        # 验证更新前的原始数据状态
        assert original_asset.asset_name == "原始资产名称", f"原始asset_name应该为'原始资产名称'，实际: '{original_asset.asset_name}'"
        assert original_asset.asset_code == "STOCK001", f"原始asset_code应该为'STOCK001'，实际: '{original_asset.asset_code}'"
        assert original_asset.asset_short_code == "S001", f"原始asset_short_code应该为'S001'，实际: '{original_asset.asset_short_code}'"
        assert original_asset.asset_status == 0, f"原始asset_status应该为0，实际: {original_asset.asset_status}"
        assert original_asset.market == MarketEnum.CN.value, f"原始market应该为{MarketEnum.CN.value}，实际: {original_asset.market}"
        assert original_asset.currency == CurrencyEnum.CNY.value, f"原始currency应该为{CurrencyEnum.CNY.value}，实际: {original_asset.currency}"
        assert original_asset.asset_type == AssetTypeEnum.STOCK.value, f"原始asset_type应该为{AssetTypeEnum.STOCK.value}，实际: {original_asset.asset_type}"
        assert original_asset.asset_subtype == "asset", f"原始多态标识应该为'asset'，实际: '{original_asset.asset_subtype}'"
        assert isinstance(original_asset, Asset), "原始实例应该是Asset类型"
        
        # 准备更新数据（不包含asset_type，因此不会改变多态类型）
        update_data = {
            "asset_name": "更新后的资产名称",
            "asset_code": "STOCK002",
            "asset_short_code": "S002",
            "asset_status": 1,
            # 注意：这里故意不包含asset_type字段
        }
        
        # 调用被测试方法
        success, message = service.update_with_polymorphic_conversion(asset_id, update_data)
        
        # 验证返回结果
        assert success is True, "更新操作应该成功"
        assert message == "更新成功", f"应该返回成功消息，实际返回: {message}"
        
        # 重新查询实例以验证更新结果
        updated_asset = service._get_current_instance(asset_id)
        assert updated_asset is not None, "更新后应该能够查询到实例"
        
        # 验证多态类型未改变
        assert updated_asset.asset_subtype == original_polymorphic_identity, f"多态标识应该保持不变，原值: {original_polymorphic_identity}，现值: {updated_asset.asset_subtype}"
        assert updated_asset.asset_type == original_asset_type, f"资产类型应该保持不变，原值: {original_asset_type}，现值: {updated_asset.asset_type}"
        assert isinstance(updated_asset, Asset), "实例类型应该保持为Asset"
        
        # 验证其他字段已正确更新
        assert updated_asset.asset_name == "更新后的资产名称", f"asset_name应该已更新，期望: '更新后的资产名称'，实际: '{updated_asset.asset_name}'"
        assert updated_asset.asset_code == "STOCK002", f"asset_code应该已更新，期望: 'STOCK002'，实际: '{updated_asset.asset_code}'"
        assert updated_asset.asset_short_code == "S002", f"asset_short_code应该已更新，期望: 'S002'，实际: '{updated_asset.asset_short_code}'"
        assert updated_asset.asset_status == 1, f"asset_status应该已更新，期望: 1，实际: {updated_asset.asset_status}"
        
        # 验证未在update_data中的字段保持不变
        assert updated_asset.market == MarketEnum.CN.value, "market字段应该保持原值"
        assert updated_asset.currency == CurrencyEnum.CNY.value, "currency字段应该保持原值"
        assert updated_asset.id == asset_id, "ID应该保持不变"
        
        # 验证数据库中的数据确实已更新（通过新的查询验证）
        db_asset = test_db_session.query(Asset).filter(Asset.id == asset_id).first()
        assert db_asset is not None, "数据库中应该存在更新后的记录"
        assert db_asset.asset_name == "更新后的资产名称", "数据库中的asset_name应该已更新"
        assert db_asset.asset_code == "STOCK002", "数据库中的asset_code应该已更新"
        assert db_asset.asset_subtype == original_polymorphic_identity, "数据库中的多态标识应该保持不变"

    def test_update_etf_without_polymorphic_type_change(self, test_db_session):
        """
        测试ETF类型资产在不改变多态类型情况下的字段更新功能
        
        验证点:
        - ETF实例的字段能够正确更新
        - 多态类型保持为'asset_fund_etf'不变
        - 基类、中间类和子类的字段都能正确更新
        - 数据库事务正确提交
        - 更新前后的数据对比验证
        """
        # 创建服务实例
        service = AssetInheritanceUpdateService(test_db_session)
        
        # 创建原始ETF实例
        original_etf = AssetFundETF(
            asset_name="原始ETF基金",
            asset_type=AssetTypeEnum.FUND_ETF.value,
            market=MarketEnum.CN.value,
            currency=CurrencyEnum.CNY.value,
            asset_code="ETF001",
            asset_short_code="E001",
            asset_status=0,
            fund_type="INDEX_FUND",
            trading_mode="ETF",
            fund_company="原始ETF公司",
            fund_manager="原始ETF经理",
            fund_status=1,
            tracking_index_code="000300",
            tracking_index_name="沪深300指数",
            primary_exchange="SH",
            dividend_frequency="QUARTERLY",
            create_time=datetime.now(),
        )
        test_db_session.add(original_etf)
        test_db_session.flush()
        asset_id = original_etf.id
        
        # 记录原始状态
        original_polymorphic_identity = original_etf.asset_subtype
        original_asset_type = original_etf.asset_type
        original_create_time = original_etf.create_time
        
        # 验证更新前的原始数据状态
        # 基类字段验证
        assert original_etf.asset_name == "原始ETF基金", f"原始asset_name应该为'原始ETF基金'，实际: '{original_etf.asset_name}'"
        assert original_etf.asset_code == "ETF001", f"原始asset_code应该为'ETF001'，实际: '{original_etf.asset_code}'"
        assert original_etf.asset_short_code == "E001", f"原始asset_short_code应该为'E001'，实际: '{original_etf.asset_short_code}'"
        assert original_etf.asset_status == 0, f"原始asset_status应该为0，实际: {original_etf.asset_status}"
        assert original_etf.market == MarketEnum.CN.value, f"原始market应该为{MarketEnum.CN.value}，实际: {original_etf.market}"
        assert original_etf.currency == CurrencyEnum.CNY.value, f"原始currency应该为{CurrencyEnum.CNY.value}，实际: {original_etf.currency}"
        assert original_etf.asset_type == AssetTypeEnum.FUND_ETF.value, f"原始asset_type应该为{AssetTypeEnum.FUND_ETF.value}，实际: {original_etf.asset_type}"
        
        # 中间类字段验证（AssetFund）
        assert original_etf.fund_type == "INDEX_FUND", f"原始fund_type应该为'INDEX_FUND'，实际: '{original_etf.fund_type}'"
        assert original_etf.fund_company == "原始ETF公司", f"原始fund_company应该为'原始ETF公司'，实际: '{original_etf.fund_company}'"
        assert original_etf.fund_manager == "原始ETF经理", f"原始fund_manager应该为'原始ETF经理'，实际: '{original_etf.fund_manager}'"
        assert original_etf.fund_status == 1, f"原始fund_status应该为1，实际: {original_etf.fund_status}"
        
        # 子类字段验证（AssetFundETF）
        assert original_etf.tracking_index_code == "000300", f"原始tracking_index_code应该为'000300'，实际: '{original_etf.tracking_index_code}'"
        assert original_etf.tracking_index_name == "沪深300指数", f"原始tracking_index_name应该为'沪深300指数'，实际: '{original_etf.tracking_index_name}'"
        assert original_etf.primary_exchange == "SH", f"原始primary_exchange应该为'SH'，实际: '{original_etf.primary_exchange}'"
        assert original_etf.dividend_frequency == "QUARTERLY", f"原始dividend_frequency应该为'QUARTERLY'，实际: '{original_etf.dividend_frequency}'"
        
        # 多态类型验证
        assert original_etf.asset_subtype == "asset_fund_etf", f"原始多态标识应该为'asset_fund_etf'，实际: '{original_etf.asset_subtype}'"
        assert isinstance(original_etf, AssetFundETF), "原始实例应该是AssetFundETF类型"
        
        # 准备更新数据（不包含asset_type，因此不会改变多态类型）
        update_data = {
            # 基类字段更新
            "asset_name": "更新后的ETF基金",
            "asset_code": "ETF002",
            "asset_short_code": "E002",
            "asset_status": 1,
            "market": MarketEnum.US.value,
            "currency": CurrencyEnum.USD.value,
            
            # 中间类字段更新（AssetFund）
            "fund_type": "STOCK_FUND",
            "fund_company": "更新后的ETF公司",
            "fund_manager": "更新后的ETF经理",
            "fund_status": 2,
            
            # 子类字段更新（AssetFundETF）
            "tracking_index_code": "SPX",
            "tracking_index_name": "标普500指数",
            "primary_exchange": "NYSE",
            "dividend_frequency": "MONTHLY",
            
            # 注意：这里故意不包含asset_type字段，确保不会改变多态类型
        }
        
        # 调用被测试方法
        success, message = service.update_with_polymorphic_conversion(asset_id, update_data)
        
        # 验证返回结果
        assert success is True, "更新操作应该成功"
        assert message == "更新成功", f"应该返回成功消息，实际返回: {message}"
        
        # 重新查询实例以验证更新结果
        updated_etf = service._get_current_instance(asset_id)
        assert updated_etf is not None, "更新后应该能够查询到实例"
        
        # 验证多态类型未改变
        assert updated_etf.asset_subtype == original_polymorphic_identity, f"多态标识应该保持不变，原值: {original_polymorphic_identity}，现值: {updated_etf.asset_subtype}"
        assert updated_etf.asset_type == original_asset_type, f"资产类型应该保持不变，原值: {original_asset_type}，现值: {updated_etf.asset_type}"
        assert isinstance(updated_etf, AssetFundETF), "实例类型应该保持为AssetFundETF"
        
        # 验证基类字段已正确更新
        assert updated_etf.asset_name == "更新后的ETF基金", f"asset_name应该已更新，期望: '更新后的ETF基金'，实际: '{updated_etf.asset_name}'"
        assert updated_etf.asset_code == "ETF002", f"asset_code应该已更新，期望: 'ETF002'，实际: '{updated_etf.asset_code}'"
        assert updated_etf.asset_short_code == "E002", f"asset_short_code应该已更新，期望: 'E002'，实际: '{updated_etf.asset_short_code}'"
        assert updated_etf.asset_status == 1, f"asset_status应该已更新，期望: 1，实际: {updated_etf.asset_status}"
        assert updated_etf.market == MarketEnum.US.value, f"market应该已更新，期望: {MarketEnum.US.value}，实际: {updated_etf.market}"
        assert updated_etf.currency == CurrencyEnum.USD.value, f"currency应该已更新，期望: {CurrencyEnum.USD.value}，实际: {updated_etf.currency}"
        
        # 验证中间类字段已正确更新（AssetFund）
        assert updated_etf.fund_type == "STOCK_FUND", f"fund_type应该已更新，期望: 'STOCK_FUND'，实际: '{updated_etf.fund_type}'"
        assert updated_etf.fund_company == "更新后的ETF公司", f"fund_company应该已更新，期望: '更新后的ETF公司'，实际: '{updated_etf.fund_company}'"
        assert updated_etf.fund_manager == "更新后的ETF经理", f"fund_manager应该已更新，期望: '更新后的ETF经理'，实际: '{updated_etf.fund_manager}'"
        assert updated_etf.fund_status == 2, f"fund_status应该已更新，期望: 2，实际: {updated_etf.fund_status}"
        
        # 验证子类字段已正确更新（AssetFundETF）
        assert updated_etf.tracking_index_code == "SPX", f"tracking_index_code应该已更新，期望: 'SPX'，实际: '{updated_etf.tracking_index_code}'"
        assert updated_etf.tracking_index_name == "标普500指数", f"tracking_index_name应该已更新，期望: '标普500指数'，实际: '{updated_etf.tracking_index_name}'"
        assert updated_etf.primary_exchange == "NYSE", f"primary_exchange应该已更新，期望: 'NYSE'，实际: '{updated_etf.primary_exchange}'"
        assert updated_etf.dividend_frequency == "MONTHLY", f"dividend_frequency应该已更新，期望: 'MONTHLY'，实际: '{updated_etf.dividend_frequency}'"
        
        # 验证未在update_data中的字段保持不变
        assert updated_etf.trading_mode == "ETF", "trading_mode字段应该保持原值"
        assert updated_etf.id == asset_id, "ID应该保持不变"

        # 验证数据库中的数据确实已更新（通过新的查询验证）
        db_etf = test_db_session.query(AssetFundETF).filter(AssetFundETF.id == asset_id).first()
        assert db_etf is not None, "数据库中应该存在更新后的ETF记录"
        assert isinstance(db_etf, AssetFundETF), "数据库中的记录应该是AssetFundETF类型"
        
        # 验证数据库中基类字段的更新
        assert db_etf.asset_name == "更新后的ETF基金", "数据库中的asset_name应该已更新"
        assert db_etf.asset_code == "ETF002", "数据库中的asset_code应该已更新"
        assert db_etf.asset_subtype == original_polymorphic_identity, "数据库中的多态标识应该保持不变"
        assert db_etf.market == MarketEnum.US.value, "数据库中的market应该已更新"
        
        # 验证数据库中中间类字段的更新
        assert db_etf.fund_type == "STOCK_FUND", "数据库中的fund_type应该已更新"
        assert db_etf.fund_company == "更新后的ETF公司", "数据库中的fund_company应该已更新"
        
        # 验证数据库中子类字段的更新
        assert db_etf.tracking_index_code == "SPX", "数据库中的tracking_index_code应该已更新"
        assert db_etf.tracking_index_name == "标普500指数", "数据库中的tracking_index_name应该已更新"
        assert db_etf.primary_exchange == "NYSE", "数据库中的primary_exchange应该已更新"
        assert db_etf.dividend_frequency == "MONTHLY", "数据库中的dividend_frequency应该已更新"
