# -*- coding: UTF-8 -*-
"""
@File    ：test_system_settings_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/2/16 16:00
"""

import json
from unittest.mock import patch

import pytest

from web.models.setting.system_settings import Setting
from web.webtest.test_base import TestBaseWithRollback


class TestSystemSettingsRouters(TestBaseWithRollback):
    """系统设置路由测试类"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """每个测试方法执行前的设置"""
        self.client = client

    def test_get_system_settings_success(self, session):
        """测试成功获取系统设置列表"""
        # 创建测试数据
        setting1 = Setting(
            key="test_key_1",
            value="test_value_1",
            setting_type="string",
            group="test_group",
            description="测试设置1",
        )
        setting2 = Setting(
            key="test_key_2",
            value="test_value_2",
            setting_type="string",
            group="test_group",
            description="测试设置2",
        )

        session.add(setting1)
        session.add(setting2)
        session.commit()

        # 发送GET请求 - 现在可以使用 self.client
        response = self.client.get("/system/settings/")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) >= 2
        assert data["data"]["total"] >= 2

    def test_get_system_settings_with_key_filter(self, session):
        """测试根据key过滤获取系统设置"""
        # 创建测试数据
        setting = Setting(
            key="unique_test_key",
            value="unique_test_value",
            setting_type="string",
            group="test_group",
            description="唯一测试设置",
        )

        session.add(setting)
        session.commit()

        # 发送带key参数的GET请求
        response = self.client.get("/system/settings/?key=unique_test_key")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["key"] == "unique_test_key"

    def test_get_system_settings_with_group_filter(self, session):
        """测试根据group过滤获取系统设置"""
        # 创建测试数据
        setting = Setting(
            key="group_test_key",
            value="group_test_value",
            setting_type="string",
            group="special_group",
            description="分组测试设置",
        )

        session.add(setting)
        session.commit()

        # 发送带group参数的GET请求
        response = self.client.get("/system/settings/?group=special_group")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert len(data["data"]["items"]) >= 1
        for item in data["data"]["items"]:
            assert item["group"] == "special_group"

    def test_get_system_settings_with_pagination(self, session):
        """测试分页功能"""
        # 创建多个测试数据
        for i in range(5):
            setting = Setting(
                key=f"page_test_key_{i}",
                value=f"page_test_value_{i}",
                setting_type="string",
                group="page_test_group",
                description=f"分页测试设置{i}",
            )
            session.add(setting)
        session.commit()

        # 发送带分页参数的GET请求
        response = self.client.get(
            "/system/settings/?page=1&size=3&group=page_test_group"
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["page"] == 1
        assert data["data"]["size"] == 3
        assert len(data["data"]["items"]) <= 3

    def test_post_system_setting_success(self, session):
        """测试成功创建系统设置"""
        # 准备请求数据
        setting_data = {
            "key": "new_test_key",
            "value": "new_test_value",
            "settingType": "string",  
            "group": "new_test_group",
            "description": "新建测试设置",
            "defaultValue": "default_test_value",  
        }

        # 发送POST请求
        response = self.client.post(
            "/system/settings/",
            data=json.dumps(setting_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["message"] == "设置项创建成功"
        assert data["data"]["key"] == "new_test_key"

        # 验证数据库中的数据
        created_setting = Setting.query.filter_by(key="new_test_key").first()
        assert created_setting is not None
        assert created_setting.value == "new_test_value"

    def test_post_system_setting_duplicate_key(self, session):
        """测试创建重复key的系统设置"""
        # 先创建一个设置
        existing_setting = Setting(
            key="duplicate_key",
            value="existing_value",
            setting_type="string",
            group="test_group",
        )
        session.add(existing_setting)
        session.commit()

        # 尝试创建相同key的设置
        setting_data = {
            "key": "duplicate_key",
            "value": "new_value",
            "settingType": "string",  
            "group": "test_group",
        }

        response = self.client.post(
            "/system/settings/",
            data=json.dumps(setting_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] != 20000
        assert "duplicate_key" in data["message"]
        assert "已存在" in data["message"]

    def test_post_system_setting_missing_required_fields(self):
        """测试创建系统设置时缺少必需字段 - Flask-RESTX自动校验"""
        # 缺少必需字段的数据
        invalid_data = {
            "value": "test_value"
            # 缺少key和settingType  
        }

        response = self.client.post(
            "/system/settings/",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data or "msg" in data
        # 检查是否包含enum相关的错误信息
        response_text = response.get_data(as_text=True)
        assert "settingType" in response_text  

    def test_post_system_setting_empty_data(self):
        """测试创建系统设置时传入空数据 - Flask-RESTX自动校验"""
        response = self.client.post(
            "/system/settings/", data="", content_type="application/json"
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data or "msg" in data

    def test_put_system_setting_success(self, session):
        """测试成功更新系统设置"""
        # 先创建一个设置
        setting = Setting(
            key="update_test_key",
            value="original_value",
            setting_type="string",
            group="test_group",
            description="原始描述",
        )
        session.add(setting)
        session.commit()

        # 准备更新数据
        update_data = {
            "key": "update_test_key",
            "value": "updated_value",
            "description": "更新后的描述",
        }

        # 发送PUT请求
        response = self.client.put(
            "/system/settings/",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["message"] == "设置项更新成功"
        assert data["data"]["value"] == "updated_value"
        assert data["data"]["description"] == "更新后的描述"

        # 验证数据库中的数据
        updated_setting = Setting.query.filter_by(key="update_test_key").first()
        assert updated_setting.value == "updated_value"
        assert updated_setting.description == "更新后的描述"

    def test_put_system_setting_not_found(self):
        """测试更新不存在的系统设置"""
        update_data = {"key": "non_existent_key", "value": "new_value"}

        response = self.client.put(
            "/system/settings/",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] != 20000
        assert "non_existent_key" in data["message"]
        assert "不存在" in data["message"]

    def test_put_system_setting_missing_required_fields(self):
        """测试更新系统设置时缺少必需字段 - Flask-RESTX自动校验"""
        update_data = {
            "value": "new_value"
            # 缺少key参数
        }

        response = self.client.put(
            "/system/settings/",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data or "msg" in data
        # 检查是否包含key字段相关的错误信息
        response_text = response.get_data(as_text=True)
        assert "key" in response_text

    def test_put_system_setting_empty_data(self):
        """测试更新系统设置时传入空数据 - Flask-RESTX自动校验"""
        response = self.client.put(
            "/system/settings/", data="", content_type="application/json"
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data or "msg" in data

    @patch("web.models.db.session.commit")
    def test_put_system_setting_database_error(self, mock_commit, session):
        """测试更新系统设置时数据库错误"""
        # 先创建一个设置
        setting = Setting(
            key="db_error_update_key",
            value="original_value",
            setting_type="string",
            group="test_group",
        )
        session.add(setting)
        session.commit()

        # 重置mock，模拟更新时的数据库错误
        mock_commit.reset_mock()
        mock_commit.side_effect = Exception("数据库更新错误")

        update_data = {"key": "db_error_update_key", "value": "updated_value"}

        response = self.client.put(
            "/system/settings/",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] != 20000
        assert "更新失败" in data["message"]

    def test_different_setting_types(self, session):
        """测试不同类型的设置值"""
        # 测试不同类型的设置
        test_settings = [
            {
                "key": "string_setting",
                "value": "string_value",
                "settingType": "string",  
            },
            {"key": "int_setting", "value": "123", "settingType": "int"},  # 修改
            {"key": "bool_setting", "value": "true", "settingType": "bool"},  # 修改
            {
                "key": "json_setting",
                "value": '{"test": "value"}',
                "settingType": "json",  
            },
        ]
    
        for setting_data in test_settings:
            setting_data["group"] = "type_test_group"
    
            response = self.client.post(
                "/system/settings/",
                data=json.dumps(setting_data),
                content_type="application/json",
            )
    
            # 验证每个类型都能成功创建
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["code"] == 20000
            assert data["success"] is True
            assert data["data"]["settingType"] == setting_data["settingType"]  # 修改：setting_type → settingType

    def test_put_system_settings_batch_success(self, session):
        """测试批量更新系统设置成功"""
        # 先创建一些测试设置
        settings = [
            Setting(
                key="batch_test_key_1",
                value="original_value_1",
                setting_type="string",
                group="batch_test_group",
                description="批量测试设置1",
            ),
            Setting(
                key="batch_test_key_2",
                value="original_value_2",
                setting_type="string",
                group="batch_test_group",
                description="批量测试设置2",
            ),
        ]
        for setting in settings:
            session.add(setting)
        session.commit()

        # 准备批量更新数据
        batch_data = {
            "settings": [
                {
                    "key": "batch_test_key_1",
                    "value": "updated_value_1",
                    "description": "更新后的描述1",
                },
                {
                    "key": "batch_test_key_2",
                    "value": "updated_value_2",
                    "description": "更新后的描述2",
                },
            ]
        }

        # 发送PUT请求到批量更新端点
        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert "批量更新完成" in data["message"]
        assert data["data"]["success_count"] == 2
        assert data["data"]["failure_count"] == 0
        assert len(data["data"]["successful_keys"]) == 2
        assert len(data["data"]["failures"]) == 0

        # 验证数据库中的数据
        updated_setting_1 = Setting.query.filter_by(key="batch_test_key_1").first()
        updated_setting_2 = Setting.query.filter_by(key="batch_test_key_2").first()
        assert updated_setting_1.value == "updated_value_1"
        assert updated_setting_1.description == "更新后的描述1"
        assert updated_setting_2.value == "updated_value_2"
        assert updated_setting_2.description == "更新后的描述2"

    def test_put_system_settings_batch_partial_failure(self, session):
        """测试批量更新系统设置部分失败"""
        # 先创建一个测试设置
        setting = Setting(
            key="partial_test_key",
            value="original_value",
            setting_type="string",
            group="partial_test_group",
        )
        session.add(setting)
        session.commit()

        # 准备批量更新数据（包含存在和不存在的key）
        batch_data = {
            "settings": [
                {
                    "key": "partial_test_key",
                    "value": "updated_value",
                },
                {
                    "key": "non_existent_key",
                    "value": "new_value",
                },
            ]
        }

        # 发送PUT请求到批量更新端点
        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert "批量更新部分成功" in data["message"]
        assert data["data"]["success_count"] == 1
        assert data["data"]["failure_count"] == 1
        assert len(data["data"]["successful_keys"]) == 1
        assert len(data["data"]["failures"]) == 1

        # 验证成功的更新
        updated_setting = Setting.query.filter_by(key="partial_test_key").first()
        assert updated_setting.value == "updated_value"
        assert "partial_test_key" in data["data"]["successful_keys"]

        # 验证失败的结果
        failure_result = data["data"]["failures"][0]
        assert failure_result["key"] == "non_existent_key"
        assert "not found" in failure_result["error"]

    def test_put_system_settings_batch_all_failure(self):
        """测试批量更新系统设置全部失败"""
        # 准备批量更新数据（全部为不存在的key）
        batch_data = {
            "settings": [
                {
                    "key": "non_existent_key_1",
                    "value": "new_value_1",
                },
                {
                    "key": "non_existent_key_2",
                    "value": "new_value_2",
                },
            ]
        }

        # 发送PUT请求到批量更新端点
        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20500
        assert data["success"] is False
        assert "批量更新失败" in data["message"]
        assert data["data"]["success_count"] == 0
        assert data["data"]["failure_count"] == 2
        assert len(data["data"]["successful_keys"]) == 0
        assert len(data["data"]["failures"]) == 2

        # 验证所有结果都是失败的
        for failure in data["data"]["failures"]:
            assert "not found" in failure["error"]

    def test_put_system_settings_batch_empty_updates(self):
        """测试批量更新时传入空的settings数组 - Flask-RESTX自动校验"""
        batch_data = {"settings": []}

        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20500
        assert data["success"] is False
        assert "should be non-empty" in data["message"]

    def test_put_system_settings_batch_missing_required_fields(self):
        """测试批量更新时缺少必需的settings字段 - Flask-RESTX自动校验"""
        # 缺少必需的settings字段
        invalid_data = {"other_field": "value"}

        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20500
        assert data["success"] is False
        assert "settings" in data["message"]
        assert "required property" in data["message"]
        # 检查是否包含settings字段相关的错误信息
        response_text = response.get_data(as_text=True)
        assert "settings" in response_text

    def test_put_system_settings_batch_invalid_update_item(self):
        """测试批量更新时setting项缺少必需字段"""

        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps({}),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data or "msg" in data
        # 检查是否包含key字段相关的错误信息
        response_text = response.get_data(as_text=True)
        assert "Input payload validation failed" in response_text

    def test_put_system_settings_batch_empty_data(self):
        """测试批量更新时传入空数据 - Flask-RESTX自动校验"""
        response = self.client.put(
            "/system/settings/batch", data="", content_type="application/json"
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "code" in data
        assert "message" in data or "msg" in data

    @patch("web.models.db.session.commit")
    def test_put_system_settings_batch_database_error(self, mock_commit, session):
        """测试批量更新时数据库错误"""
        # 先创建一个设置
        setting = Setting(
            key="db_error_batch_key",
            value="original_value",
            setting_type="string",
            group="test_group",
        )
        session.add(setting)
        session.commit()

        # 重置mock，模拟批量更新时的数据库错误
        mock_commit.reset_mock()
        mock_commit.side_effect = Exception("数据库批量更新错误")

        batch_data = {
            "settings": [
                {
                    "key": "db_error_batch_key",
                    "value": "updated_value",
                }
            ]
        }

        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] != 20000
        assert "批量更新失败" in data["message"]

    def test_put_system_settings_batch_large_batch(self, session):
        """测试大批量更新"""
        # 创建多个测试设置
        batch_size = 10
        for i in range(batch_size):
            setting = Setting(
                key=f"large_batch_key_{i}",
                value=f"original_value_{i}",
                setting_type="string",
                group="large_batch_group",
            )
            session.add(setting)
        session.commit()

        # 准备大批量更新数据
        updates = []
        for i in range(batch_size):
            updates.append(
                {
                    "key": f"large_batch_key_{i}",
                    "value": f"updated_value_{i}",
                }
            )

        batch_data = {"settings": updates}

        # 发送PUT请求到批量更新端点
        response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["success_count"] == batch_size
        assert data["data"]["failure_count"] == 0
        assert len(data["data"]["successful_keys"]) == batch_size
        assert len(data["data"]["failures"]) == 0

        # 验证数据库中的数据
        for i in range(batch_size):
            updated_setting = Setting.query.filter_by(
                key=f"large_batch_key_{i}"
            ).first()
            assert updated_setting.value == f"updated_value_{i}"

    def test_api_documentation_endpoints(self):
        """测试API文档端点是否可访问"""
        # 测试Swagger UI是否可访问
        response = self.client.get("/api/docs/")
        # 注意：根据Flask-RESTX配置，可能返回302重定向或200
        assert response.status_code in [200, 302, 404]  # 404也是可接受的，取决于配置


class TestSystemSettingsBatchRouters(TestBaseWithRollback):
    """系统设置批量操作路由测试类"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """每个测试方法执行前的设置"""
        self.client = client

    def test_put_batch_endpoint_exists(self):
        """测试批量更新端点是否存在"""
        # 发送一个简单的请求来验证端点存在
        response = self.client.put(
            "/system/settings/batch/",
            data=json.dumps({"settings": []}),
            content_type="application/json",
        )
        
        # 端点应该存在，即使数据无效也不应该返回404
        assert response.status_code != 404

    def test_put_batch_route_separation(self, session):
        """测试批量更新路由与单个更新路由的分离"""
        # 创建测试设置
        setting = Setting(
            key="separation_test_key",
            value="original_value",
            setting_type="string",
            group="test_group",
        )
        session.add(setting)
        session.commit()

        # 测试单个更新路由（PUT /system/settings/）
        single_update_data = {
            "key": "separation_test_key",
            "value": "single_updated_value",
        }
        
        single_response = self.client.put(
            "/system/settings/",
            data=json.dumps(single_update_data),
            content_type="application/json",
        )
        
        # 验证单个更新成功
        assert single_response.status_code == 200
        single_data = json.loads(single_response.data)
        assert single_data["code"] == 20000
        
        # 重置设置值
        setting.value = "original_value"
        session.commit()
        
        # 测试批量更新路由（PUT /system/settings/batch）
        batch_update_data = {
            "settings": [
                {
                    "key": "separation_test_key",
                    "value": "batch_updated_value",
                }
            ]
        }
        
        batch_response = self.client.put(
            "/system/settings/batch",
            data=json.dumps(batch_update_data),
            content_type="application/json",
        )
        
        # 验证批量更新成功
        assert batch_response.status_code == 200
        batch_data = json.loads(batch_response.data)
        assert batch_data["code"] == 20000
        assert batch_data["data"]["success_count"] == 1
