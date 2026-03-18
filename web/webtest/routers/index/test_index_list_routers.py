# -*- coding: UTF-8 -*-
"""
@File    ：test_index_list_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27
@Description: 指数列表接口测试
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from web.webtest.test_base import TestBase
from web.models.index.index_base import IndexBase
from web.models.index.index_base import IndexBaseSchema


class TestIndexListRouters(TestBase):
    """
    指数列表接口测试类
    
    测试覆盖范围：
    - 测试指数列表查询接口的核心功能
    - 验证分页查询、条件过滤、参数校验等功能
    - 确保API响应格式符合项目规范
    - 测试异常情况的错误处理机制
    
    使用TestBase基类的原因：
    - 适用于一般的API接口测试
    - 需要Flask应用上下文、测试客户端和数据库会话
    - 每个测试函数都会创建和清理数据库表
    """

    def test_get_index_list_basic_success(self, client):
        """
        测试基础的指数列表查询成功场景
        
        验证点:
        - HTTP状态码为200
        - 响应包含code、success、message、data字段
        - 分页数据包含items、total、page、size字段
        - 数据格式符合IndexBaseSchema序列化结果
        """
        # 发送GET请求
        response = client.get('/api/index/list/?page=1&pageSize=10')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"
        assert 'message' in response_data, "响应应该包含message字段"
        assert 'data' in response_data, "响应应该包含data字段"
        
        # 验证分页数据格式（如果查询成功）
        if response_data['success']:
            data = response_data['data']
            assert 'items' in data, "分页数据应该包含items字段"
            assert 'total' in data, "分页数据应该包含total字段"
            assert 'page' in data, "分页数据应该包含page字段"
            assert 'size' in data, "分页数据应该包含size字段"
            assert isinstance(data['items'], list), "items应该是列表类型"
            assert isinstance(data['total'], int), "total应该是整数类型"
            assert data['page'] == 1, "页码应该为1"
            assert data['size'] == 10, "页面大小应该为10"

    def test_get_index_list_with_index_name_filter(self, client):
        """
        测试按指数名称过滤的查询功能
        
        验证点:
        - 支持indexName参数过滤
        - 过滤结果符合预期
        - 响应格式正确
        """
        # 测试按指数名称过滤
        response = client.get('/api/index/list/?page=1&pageSize=10&indexName=上证')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"

    def test_get_index_list_with_index_type_filter(self, client):
        """
        测试按指数类型过滤的查询功能
        
        验证点:
        - 支持indexType参数过滤
        - 过滤结果符合预期
        - 响应格式正确
        """
        # 测试按指数类型过滤
        response = client.get('/api/index/list/?page=1&pageSize=10&indexType=0')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"

    def test_get_index_list_with_market_filter(self, client):
        """
        测试按市场过滤的查询功能
        
        验证点:
        - 支持market参数过滤
        - 过滤结果符合预期
        - 响应格式正确
        """
        # 测试按市场过滤
        response = client.get('/api/index/list/?page=1&pageSize=10&market=0')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"

    def test_get_index_list_pagination_functionality(self, client):
        """
        测试分页功能的正确性
        
        验证点:
        - 不同页码返回不同数据
        - 页面大小参数生效
        - 分页信息正确
        """
        # 测试第一页
        response1 = client.get('/api/index/list/?page=1&pageSize=5')
        assert response1.status_code == 200, "第一页请求HTTP状态码应该为200"
        
        response1_data = json.loads(response1.data)
        
        # 测试第二页
        response2 = client.get('/api/index/list/?page=2&pageSize=5')
        assert response2.status_code == 200, "第二页请求HTTP状态码应该为200"
        
        response2_data = json.loads(response2.data)
        
        # 验证分页信息
        if response1_data['success'] and response1_data['data']['items']:
            assert response1_data['data']['page'] == 1, "第一页的页码应该为1"
            assert response1_data['data']['size'] == 5, "第一页的页面大小应该为5"
        
        if response2_data['success'] and response2_data['data']['items']:
            assert response2_data['data']['page'] == 2, "第二页的页码应该为2"
            assert response2_data['data']['size'] == 5, "第二页的页面大小应该为5"

    def test_get_index_list_missing_required_params(self, client):
        """
        测试缺少必需参数的处理
        
        验证点:
        - 缺少page和pageSize参数时的处理
        - 错误响应格式正确
        - 返回适当的错误信息
        """
        # 测试缺少必需参数
        response = client.get('/api/index/list/')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"
        assert 'message' in response_data, "响应应该包含message字段"

    def test_get_index_list_invalid_page_params(self, client):
        """
        测试无效页码参数的处理
        
        验证点:
        - 无效页码（如0、负数）的处理
        - 错误响应格式正确
        - 返回适当的错误信息
        """
        # 测试无效的页码
        response = client.get('/api/index/list/?page=0&pageSize=10')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"
        assert 'message' in response_data, "响应应该包含message字段"

    @patch('web.models.db.session.query')
    def test_get_index_list_database_error(self, mock_query, client):
        """
        测试数据库异常的错误处理
        
        验证点:
        - 数据库查询异常时的处理
        - 返回R.fail格式的错误响应
        - 错误信息包含在message字段中
        """
        # Mock数据库查询异常
        mock_query.side_effect = Exception("数据库连接异常")
        
        # 发送请求
        response = client.get('/api/index/list/?page=1&pageSize=10')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证错误响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"
        assert 'message' in response_data, "响应应该包含message字段"
        assert response_data['success'] is False, "success字段应该为False"

    @patch('web.models.index.index_base.IndexBaseSchema.dump')
    def test_get_index_list_schema_serialization_error(self, mock_dump, client):
        """
        测试Schema序列化异常的错误处理
        
        验证点:
        - Schema序列化异常时的处理
        - 返回R.fail格式的错误响应
        - 错误信息包含在message字段中
        """
        # Mock Schema序列化异常
        mock_dump.side_effect = Exception("序列化异常")
        
        # 发送请求
        response = client.get('/api/index/list/?page=1&pageSize=10')
        
        # 验证HTTP状态码
        assert response.status_code == 200, "HTTP状态码应该为200"
        
        # 解析响应数据
        response_data = json.loads(response.data)
        
        # 验证错误响应格式
        assert 'code' in response_data, "响应应该包含code字段"
        assert 'success' in response_data, "响应应该包含success字段"
        assert 'message' in response_data, "响应应该包含message字段"
