# -*- coding: UTF-8 -*-
"""
IndexInheritanceUpdateService 单元测试

覆盖点：
- 不改变类型时的基础字段更新（IndexBase -> IndexBase）
- 基础指数转换为股票指数（IndexBase -> StockIndex）
- 股票指数转换回基础指数（StockIndex -> IndexBase）
- 无效类型输入的异常处理

测试策略：
- 使用 TestBaseWithRollback + rollback_session，确保每个用例事务隔离、自动回滚
- 直接调用服务层 IndexInheritanceUpdateService.update_with_polymorphic_conversion
- 断言数据库真实数据与返回结果的一致性
"""

import pytest
import uuid

from web.webtest.test_base import TestBaseWithRollback
from web.services.index.index_inheritance_update_service import IndexInheritanceUpdateService
from web.models.index.index_base import IndexBase
from web.models.index.index_stock import StockIndex
from web.common.enum.business.index.index_enum import IndexTypeEnum


class TestIndexInheritanceUpdateService(TestBaseWithRollback):
    def test_update_without_type_change_updates_base_fields(self, rollback_session):
        """
        验证在不改变类型的情况下，基础字段会被正确更新且多态标识保持不变。
        """
        # 预置基础指数
        base = IndexBase(
            index_code=f"UT_SVC_BASE_{uuid.uuid4().hex[:8]}",
            index_name="服务测试-基础指数-更新前",
            index_type=IndexTypeEnum.OTHER.value,
            market=1,
            index_status=0,
        )
        rollback_session.add(base)
        rollback_session.commit()

        service = IndexInheritanceUpdateService(db_session=rollback_session)
        update_data = {
            "index_name": "服务测试-基础指数-更新后",
            "index_type": IndexTypeEnum.OTHER.value,  # 保持基础类型
            "index_status": 1,
            "market": 0,
            # 不提供 index_code，确保不会被覆盖为 None
        }
        success, message = service.update_with_polymorphic_conversion(base.id, update_data)
        assert success is True

        # 校验数据库
        rollback_session.expire_all()
        db_base = rollback_session.query(IndexBase).filter_by(id=base.id).first()
        assert db_base is not None
        assert db_base.index_name == update_data["index_name"]
        assert db_base.index_status == update_data["index_status"]
        assert db_base.market == update_data["market"]
        # 多态标识保持基础
        assert db_base.discriminator in ("index_base", "base")
        # index_code 未提供时保持原值
        assert db_base.index_code == base.index_code

    def test_convert_base_to_stock_success(self, rollback_session):
        """
        验证从基础指数转换为股票指数：创建子类层级并更新子类字段。
        """
        base = IndexBase(
            index_code=f"UT_SVC_CONV_{uuid.uuid4().hex[:8]}",
            index_name="服务测试-转换前-基础指数",
            index_type=IndexTypeEnum.OTHER.value,
            market=0,
            index_status=1,
        )
        rollback_session.add(base)
        rollback_session.commit()
        # 缓存主键与index_code，避免在分离后访问触发刷新
        base_id = base.id
        base_index_code = base.index_code

        service = IndexInheritanceUpdateService(db_session=rollback_session)
        update_data = {
            "index_name": "服务测试-转换后-股票指数",
            "index_type": IndexTypeEnum.STOCK.value,  # 转换到股票指数
            "index_status": 1,
            "market": 0,
            # 股票指数特有字段
            "constituent_count": 50,
            "average_pe": 12.34,
            "rebalance_frequency": "quarterly",
        }
        success, message = service.update_with_polymorphic_conversion(base_id, update_data)
        assert success is True

        # 校验数据库：存在StockIndex层级且字段正确
        rollback_session.expunge_all()
        db_stock = rollback_session.query(StockIndex).filter_by(id=base_id).first()
        assert db_stock is not None
        assert db_stock.index_name == update_data["index_name"]
        assert db_stock.constituent_count == update_data["constituent_count"]
        assert float(db_stock.average_pe) == pytest.approx(update_data["average_pe"], rel=1e-6)
        assert db_stock.rebalance_frequency == update_data["rebalance_frequency"]

        # 基类多态标识更新
        db_base = rollback_session.query(IndexBase).filter_by(id=base_id).first()
        assert db_base is not None
        assert db_base.discriminator == "index_stock"
        # index_code 保持不变
        assert db_base.index_code == base_index_code

    def test_convert_stock_to_base_success(self, rollback_session):
        """
        验证从股票指数转换回基础指数：删除子类层级，保留基础字段。
        """
        stock = StockIndex(
            index_code=f"UT_SVC_STK_{uuid.uuid4().hex[:8]}",
            index_name="服务测试-股票指数-转换前",
            index_type=IndexTypeEnum.STOCK.value,
            market=0,
            index_status=1,
            constituent_count=30,
            average_pe=10.0,
            rebalance_frequency="annual",
        )
        rollback_session.add(stock)
        rollback_session.commit()
        # 缓存主键与index_code，避免在分离后访问触发刷新
        stock_id = stock.id
        stock_index_code = stock.index_code

        service = IndexInheritanceUpdateService(db_session=rollback_session)
        update_data = {
            "index_name": "服务测试-转换后-基础指数",
            "index_type": IndexTypeEnum.OTHER.value,  # 转回基础
            "index_status": 1,
            "market": 1,
        }
        # 先从会话分离已加载的子类实例，避免删除后刷新触发异常
        rollback_session.expunge(stock)
        success, message = service.update_with_polymorphic_conversion(stock_id, update_data)
        assert success is True

        # 子类层级删除
        rollback_session.expire_all()
        db_stock = rollback_session.query(StockIndex).filter_by(id=stock_id).first()
        assert db_stock is None

        # 基类存在且字段更新
        db_base = rollback_session.query(IndexBase).filter_by(id=stock_id).first()
        assert db_base is not None
        assert db_base.index_name == update_data["index_name"]
        assert db_base.market == update_data["market"]
        assert db_base.discriminator in ("index_base", "base")
        # index_code 保持不变
        assert db_base.index_code == stock_index_code

    def test_invalid_index_type_raises(self, rollback_session):
        """
        验证无效类型输入抛出异常。
        """
        base = IndexBase(
            index_code=f"UT_SVC_ERR_{uuid.uuid4().hex[:8]}",
            index_name="服务测试-错误类型",
            index_type=IndexTypeEnum.OTHER.value,
            market=0,
            index_status=1,
        )
        rollback_session.add(base)
        rollback_session.commit()

        service = IndexInheritanceUpdateService(db_session=rollback_session)
        with pytest.raises(Exception):
            service.update_with_polymorphic_conversion(base.id, {"index_type": 99})