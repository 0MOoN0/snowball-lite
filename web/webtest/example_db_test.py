"""
示例数据库测试文件，演示如何使用test_db_session fixture
"""
import pytest
from datetime import datetime

from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models import db


# 使用test_db_session fixture确保每个测试都有一个干净的数据库环境
class TestDatabaseOperations:
    """演示数据库测试的示例类"""
    
    def test_create_asset(self, test_db_session):
        """
        测试创建资产记录
        
        Asset模型有__bind_key__ = "snowball"，所以会自动使用snowball绑定的数据库
        """
        # 创建一个新资产
        asset = Asset(
            asset_name="测试资产", 
            asset_type=Asset.get_asset_type_enum().FUND.value,
            market=Asset.get_market_enum().CN.value,  # 设置必填的市场信息
            currency=Asset.get_currency_enum().CNY.value,  # 设置必填的货币类型
            create_time=datetime.now()
        )
        
        try:
            # 保存到数据库 - test_db_session会自动根据Asset的__bind_key__选择正确的数据库
            test_db_session.add(asset)
            test_db_session.flush()  # 获取自动生成的ID
            
            # 验证资产已被创建且有ID
            assert asset.id is not None
            
            # 从数据库查询验证
            saved_asset = test_db_session.query(Asset).filter_by(id=asset.id).first()
            assert saved_asset is not None
            assert saved_asset.asset_name == "测试资产"
            assert saved_asset.market == Asset.get_market_enum().CN.value
            assert saved_asset.currency == Asset.get_currency_enum().CNY.value
            
            # 打印绑定的数据库连接信息，用于调试
            print(f"创建的资产ID: {asset.id}")
            
        except Exception as e:
            print(f"创建资产时发生错误: {str(e)}")
            raise
    
    def test_create_asset_with_code(self, test_db_session):
        """
        测试创建资产和对应的代码
        
        Asset和AssetCode模型都有__bind_key__ = "snowball"，所以会自动使用snowball绑定的数据库
        """
        # 创建一个新资产
        asset = Asset(
            asset_name="测试基金", 
            asset_type=Asset.get_asset_type_enum().FUND.value,
            market=Asset.get_market_enum().CN.value,
            currency=Asset.get_currency_enum().CNY.value,
            create_time=datetime.now()
        )
        
        try:
            # 保存资产到数据库
            test_db_session.add(asset)
            test_db_session.flush()  # 获取自动生成的ID
            
            # 创建资产代码
            asset_code = AssetCode(
                asset_id=asset.id,
                code_xq="SZ123456",
                code_ttjj="123456"
            )
            
            test_db_session.add(asset_code)
            test_db_session.flush()
            
            # 验证资产代码已被创建
            assert asset_code.id is not None
            
            # 查询并验证关联关系
            saved_asset_code = test_db_session.query(AssetCode).filter_by(asset_id=asset.id).first()
            assert saved_asset_code is not None
            assert saved_asset_code.code_xq == "SZ123456"
            assert saved_asset_code.code_ttjj == "123456"
            
            print(f"创建的资产ID: {asset.id}, 资产代码ID: {asset_code.id}")
            
        except Exception as e:
            print(f"创建资产和代码时发生错误: {str(e)}")
            raise
    
    def test_isolation_between_tests(self, test_db_session):
        """
        测试不同测试方法之间的数据隔离性
        
        验证事务隔离机制是否正常工作
        """
        # 查询资产表中的记录数 - 会使用Asset的__bind_key__绑定找到正确的数据库
        asset_count = test_db_session.query(Asset).count()
        
        # 由于每个测试方法都使用独立的事务，并且会在测试结束时回滚
        # 因此即使前面的测试方法创建了资产，在这个方法中也应该看不到
        assert asset_count == 0, "测试方法之间应该是隔离的，不应该看到其他测试创建的数据"
        
        try:
            # 创建一个新资产
            asset = Asset(
                asset_name="隔离测试资产", 
                asset_type=Asset.get_asset_type_enum().STOCK.value,
                market=Asset.get_market_enum().CN.value,
                currency=Asset.get_currency_enum().CNY.value,
                create_time=datetime.now()
            )
            
            test_db_session.add(asset)
            test_db_session.flush()
            
            # 验证资产已被创建
            new_asset_count = test_db_session.query(Asset).count()
            assert new_asset_count == 1
            
            print(f"当前测试中的资产数: {new_asset_count}")
            
        except Exception as e:
            print(f"测试数据隔离性时发生错误: {str(e)}")
            raise 