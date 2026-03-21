# -*- coding: UTF-8 -*-
"""
@File    ：test_index_detail_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27
@Description: 指数详情创建接口测试

覆盖点：
- 成功创建基础指数（indexType 非股票）
- 成功创建股票指数（indexType 为股票）
- 重复 indexCode 导致失败
- 额外未知字段被忽略（unknown=EXCLUDE），不影响创建
- 响应中不包含内部字段 discriminator
"""

import json
import pytest

from web.models.index.index_stock import StockIndex
from web.webtest.test_base import TestBaseWithRollback
from web.models.index.index_base import IndexBase
from web.models import db
import uuid


class TestIndexDetailRouters(TestBaseWithRollback):
    """
    指数详情创建接口测试类
    """

    def test_post_create_index_base_success(self, client, rollback_session):
        """
        验证基础指数创建成功：
        - HTTP状态码为200
        - success 为 true
        - data 包含基本字段，且不包含 discriminator
        """
        payload = {
            "indexCode": f"UT_BASE_{uuid.uuid4().hex[:8]}",
            "indexName": "单元测试-基础指数",
            "indexType": 5,  # 其他类型，映射为 index_base
            "market": 0,
            "baseDate": "2024-01-01",
            "indexStatus": 1
        }
        resp = client.post('/api/index/', json=payload)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is True
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), dict)
        # 验证关键字段
        assert data["data"].get("indexCode") == payload["indexCode"]
        assert data["data"].get("indexName") == payload["indexName"]
        # 不暴露内部字段
        assert "discriminator" not in data["data"]

    def test_post_create_index_stock_success(self, client, rollback_session):
        """
        验证股票指数创建成功：
        - HTTP状态码为200
        - success 为 true
        - data 不包含 discriminator
        """
        payload = {
            "indexCode": f"UT_STOCK_{uuid.uuid4().hex[:8]}",
            "indexName": "单元测试-股票指数",
            "indexType": 0,  # 股票指数 -> index_stock
            "market": 0,
            "rebalanceFrequency": "quarterly"
        }
        resp = client.post('/api/index/', json=payload)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is True
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), dict)
        assert data["data"].get("indexCode") == payload["indexCode"]
        assert "discriminator" not in data["data"]

    def test_post_create_index_duplicate_code_fail(self, client, rollback_session):
        """
        验证重复 indexCode 时返回失败响应：
        - 成功插入第一条记录
        - 第二次创建相同 indexCode 返回 R.fail
        """
        # 使用动态唯一代码避免历史残留影响
        dup_code = f"UT_DUP_{uuid.uuid4().hex[:8]}"
        # 预先插入一条记录（在回滚会话中）
        existing = IndexBase(index_code=dup_code, index_name="重复校验-基础", index_type=5, market=0)
        rollback_session.add(existing)
        rollback_session.commit()

        payload = {
            "indexCode": dup_code,
            "indexName": "单元测试-重复校验",
            "indexType": 5,
            "market": 0
        }
        resp = client.post('/api/index/', json=payload)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "已存在" in data.get("message", "")

    def test_post_create_index_ignores_unknown_fields(self, client, rollback_session):
        """
        验证 payload 包含未知字段时不会报错：
        - 额外的驼峰或下划线字段被忽略
        - 创建成功，响应正确
        """
        payload = {
            "indexCode": f"UT_UNKNOWN_{uuid.uuid4().hex[:8]}",
            "indexName": "单元测试-忽略未知字段",
            "indexType": 5,
            "market": 0,
            # 额外未知字段
            "unknownField": "foo",
            "index_code": "SHOULD_BE_IGNORED"
        }
        resp = client.post('/api/index/', json=payload)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is True
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), dict)
        assert data["data"].get("indexCode") == payload["indexCode"]
        assert "discriminator" not in data["data"]

    def test_get_index_detail_by_id_success(self, client, rollback_session):
        """
        验证按ID查询指数详情成功：
        - 响应HTTP 200
        - success 为 true
        - data 包含基本字段，且不包含 discriminator
        - indexStatus 字段为驼峰命名
        """
        base = IndexBase(index_code=f"UT_GET_ID_{uuid.uuid4().hex[:8]}", index_name="查询ID-基础指数", index_type=5, market=0, index_status=1)
        rollback_session.add(base)
        rollback_session.commit()

        resp = client.get(f"/api/index/?id={base.id}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is True
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), dict)
        body = data["data"]
        assert body.get("id") == base.id
        assert body.get("indexCode") == base.index_code
        assert body.get("indexStatus") == 1
        assert "index_status" not in body
        assert "discriminator" not in body

    def test_get_index_detail_by_code_success(self, client, rollback_session):
        """
        验证按指数代码查询详情成功：
        - 响应HTTP 200
        - success 为 true
        - data 不包含 discriminator
        """
        code = f"UT_GET_CODE_{uuid.uuid4().hex[:8]}"
        base = IndexBase(index_code=code, index_name="查询代码-基础指数", index_type=5, market=0, index_status=1)
        rollback_session.add(base)
        rollback_session.commit()

        resp = client.get(f"/api/index/?indexCode={code}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is True
        assert data.get("code") == 20000
        assert data["data"].get("indexCode") == code
        assert "discriminator" not in data["data"]

    def test_get_index_detail_stock_polymorphic_success(self, client, rollback_session):
        """
        验证股票指数使用with_polymorphic加载子类字段：
        - 响应HTTP 200
        - 返回包含股票指数特有字段（如rebalanceFrequency）
        - 不包含 discriminator
        """
        stock = StockIndex(
            index_code=f"UT_STK_{uuid.uuid4().hex[:8]}",
            index_name="查询-股票指数",
            index_type=0,  # STOCK
            market=0,
            index_status=1,
            constituent_count=50,
            average_pe=12.3,
            rebalance_frequency="quarterly"
        )
        rollback_session.add(stock)
        rollback_session.commit()

        resp = client.get(f"/api/index/?id={stock.id}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is True
        assert data.get("code") == 20000
        body = data.get("data")
        assert body.get("indexCode") == stock.index_code
        # 股票指数字段
        assert body.get("rebalanceFrequency") == "quarterly"
        assert body.get("constituentCount") == 50
        assert "discriminator" not in body

    def test_get_index_detail_filter_unique_match_success(self, client, rollback_session):
        """
        验证仅提供筛选参数时返回失败：
        - 不提供id/indexCode
        - 返回R.fail，提示需要提供其一
        """
        resp = client.get(f"/api/index/?indexName=上证&indexType=5&market=0&indexStatus=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "id 或 indexCode" in data.get("message", "")
        resp = client.get(f"/api/index/?indexName=上证&indexType=5&market=0&indexStatus=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "id 或 indexCode" in data.get("message", "")

    def test_get_index_detail_filter_multiple_match_fail(self, client, rollback_session):
        """
        验证仅提供筛选参数时返回失败：
        - 不提供id/indexCode
        - 返回R.fail，提示需要提供其一
        """
        resp = client.get("/api/index/?indexType=5&market=0&indexStatus=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "id 或 indexCode" in data.get("message", "")
        resp = client.get("/api/index/?indexType=5&market=0&indexStatus=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "id 或 indexCode" in data.get("message", "")

    def test_get_index_detail_missing_required_params_fail(self, client):
        """
        验证缺少必需参数（id/indexCode）时返回失败：
        - 不提供id和indexCode
        - 返回R.fail，提示需要提供其一
        """
        resp = client.get("/api/index/")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "id 或 indexCode" in data.get("message", "")

    def test_get_index_detail_not_found(self, client):
        """
        验证查询不存在的记录返回失败：
        - 使用不存在ID
        """
        resp = client.get("/api/index/?id=999999999")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("success") is False
        assert data.get("code") == 20500
        assert "未找到" in data.get("message", "")

    def test_put_update_index_base_fields_success(self, client, rollback_session):
        """
        验证基础指数字段更新：
        - 初始为 index_base（indexType=5）
        - PUT 更新基础字段（indexName/indexStatus/market），保持类型不变
        - 响应数据与数据库数据一致，不返回 discriminator
        """
        # 预置数据
        base = IndexBase(
            index_code=f"UT_PUT_BASE_{uuid.uuid4().hex[:8]}",
            index_name="更新前-基础指数",
            index_type=5,
            market=1,
            index_status=0
        )
        rollback_session.add(base)
        rollback_session.commit()

        payload = {
            "indexName": "更新后-基础指数",
            "indexType": 5,  # 保持为基础类型
            "indexStatus": 1,
            "market": 0
        }
        resp = client.put(f"/api/index/{base.id}", json=payload)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body.get("success") is True
        assert body.get("code") == 20000

        # 校验数据库
        db_item = rollback_session.query(IndexBase).filter_by(id=base.id).first()
        assert db_item is not None
        assert db_item.index_name == payload["indexName"]
        assert db_item.index_status == payload["indexStatus"]
        assert db_item.market == payload["market"]
        # 类型不变
        assert db_item.discriminator in ("index_base", "base")

    def test_put_convert_base_to_stock_success(self, client, rollback_session):
        """
        验证从基础指数转换为股票指数：
        - 初始为 index_base（indexType=5）
        - PUT 传入 indexType=0 触发多态转换到 StockIndex
        - 响应包含股票指数字段；数据库存在 StockIndex 层级数据
        """
        base = IndexBase(
            index_code=f"UT_PUT_CONV_{uuid.uuid4().hex[:8]}",
            index_name="转换前-基础指数",
            index_type=5,
            market=0,
            index_status=1
        )
        rollback_session.add(base)
        rollback_session.commit()

        payload = {
            "indexName": "转换后-股票指数",
            "indexType": 0,  # STOCK → index_stock
            "indexStatus": 1,
            "market": 0,
            # 股票指数特有字段
            "constituentCount": 30,
            "averagePe": 11.1,
            "rebalanceFrequency": "quarterly"
        }
        resp = client.put(f"/api/index/{base.id}", json=payload)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body.get("success") is True
        assert body.get("code") == 20000

        # 数据库校验：存在StockIndex层级
        base_id = base.id
        rollback_session.expunge(base)
        db_stock = rollback_session.query(StockIndex).filter_by(id=base_id).first()
        assert db_stock is not None, "应存在股票指数子类记录"
        assert db_stock.index_name == payload["indexName"]
        assert db_stock.constituent_count == payload["constituentCount"]
        assert float(db_stock.average_pe) == pytest.approx(payload["averagePe"], rel=1e-6)
        assert db_stock.rebalance_frequency == payload["rebalanceFrequency"]

    def test_delete_index_with_stock_and_alias_success(self, client, rollback_session):
        """
        验证删除股票指数时，联表继承子类与别名关联一并删除：
        - 预置 StockIndex 及 IndexAlias 两条
        - 调用 DELETE /api/index/{id}
        - 校验 tb_index_stock / tb_index_base / tb_index_alias 均被清理
        """
        from web.models.index.index_alias import IndexAlias

        # 1) 预置股票指数（联表继承）
        stock = StockIndex(
            index_code=f"UT_DEL_STK_{uuid.uuid4().hex[:8]}",
            index_name="删除-股票指数",
            index_type=0,
            market=0,
            index_status=1,
            constituent_count=10,
            average_pe=9.99,
            rebalance_frequency="annual",
        )
        rollback_session.add(stock)
        rollback_session.flush()  # 获取ID但不提交

        # 2) 预置别名（外键关联 IndexBase.id）
        alias1 = IndexAlias(index_id=stock.id, provider_code="wind", provider_symbol="000001", provider_name="万得", is_primary=1, status=1)
        alias2 = IndexAlias(index_id=stock.id, provider_code="yahoo", provider_symbol="^GSPC", provider_name="雅虎", is_primary=0, status=1)
        rollback_session.add_all([alias1, alias2])
        rollback_session.commit()

        # 前置断言：数据存在
        assert rollback_session.query(IndexBase).filter_by(id=stock.id).first() is not None
        assert rollback_session.query(StockIndex).filter_by(id=stock.id).first() is not None
        assert len(rollback_session.query(IndexAlias).filter_by(index_id=stock.id).all()) == 2

        # 3) 调用删除接口
        resp = client.delete(f"/api/index/{stock.id}")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body.get("success") is True
        assert body.get("code") == 20000
        assert body.get("data") is True

        # 4) 校验数据库：继承子类与父类、别名均已删除
        assert rollback_session.query(StockIndex).filter_by(id=stock.id).first() is None
        assert rollback_session.query(IndexBase).filter_by(id=stock.id).first() is None
        assert len(rollback_session.query(IndexAlias).filter_by(index_id=stock.id).all()) == 0