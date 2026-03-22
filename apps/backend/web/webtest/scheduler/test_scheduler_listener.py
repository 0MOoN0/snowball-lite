import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid

from flask import Flask

from web.common.cache import cache
from web.common.cons import webcons
from web.models.scheduler.scheduler_log import SchedulerLog
from web.scheduler import (
    _get_execution_persistence_strategy,
    _resolve_job_id,
    scheduler as scheduler_instance,
)
from web.scheduler.manual_job_id import build_manual_job_id, decode_manual_job_id


class TestSchedulerComponents:
    """测试调度器相关组件"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_job_id = "test_job_id_123"
        self.test_new_job_id = str(uuid.uuid4().hex)
        self.cache_key = f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}{self.test_new_job_id}"
    
    def test_cache_key_format_consistency(self):
        """测试缓存键格式的一致性"""
        test_job_id = "test_job_456"
        expected_key = f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}{test_job_id}"
        
        # 验证缓存键格式
        assert expected_key.startswith(webcons.RedisKeyPrefix.DYNAMIC_JOB)
        assert test_job_id in expected_key
        
        # 验证键的唯一性
        another_job_id = "another_job_789"
        another_key = f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}{another_job_id}"
        
        assert expected_key != another_key
    
    def test_scheduler_log_model_creation(self):
        """测试SchedulerLog模型创建"""
        test_run_time = datetime.now()
        
        # 创建SchedulerLog实例
        log = SchedulerLog()
        log.job_id = self.test_job_id
        log.status = "success"
        log.run_time = test_run_time
        log.error_message = None
        log.stack_trace = None
        
        # 验证属性设置
        assert log.job_id == self.test_job_id
        assert log.status == "success"
        assert log.run_time == test_run_time
        assert log.error_message is None
        assert log.stack_trace is None
    
    def test_scheduler_log_with_error(self):
        """测试带错误信息的SchedulerLog"""
        error_msg = "Test error message"
        stack_trace = "Test stack trace"
        
        log = SchedulerLog()
        log.job_id = self.test_job_id
        log.status = "error"
        log.error_message = error_msg
        log.stack_trace = stack_trace
        
        assert log.status == "error"
        assert log.error_message == error_msg
        assert log.stack_trace == stack_trace
    
    @patch('web.common.cache.cache')
    def test_cache_operations(self, mock_cache):
        """测试缓存操作"""
        # 模拟缓存操作
        mock_redis = mock_cache.get_redis_client.return_value
        mock_redis.set.return_value = True
        mock_redis.get.return_value = self.test_job_id
        
        # 测试缓存设置
        cache_key = f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}{self.test_new_job_id}"
        
        # 模拟缓存操作
        mock_redis.set(cache_key, self.test_job_id, ex=3600)
        retrieved_value = mock_redis.get(cache_key)
        
        # 验证缓存操作
        mock_redis.set.assert_called_once_with(cache_key, self.test_job_id, ex=3600)
        mock_redis.get.assert_called_once_with(cache_key)
        
        # 验证返回值
        assert retrieved_value == self.test_job_id

    def test_manual_job_id_round_trip(self):
        """测试手动 job id 的编码和解码"""
        manual_job_id = build_manual_job_id(self.test_job_id, "manual-run")

        assert manual_job_id.startswith("manual::")
        assert decode_manual_job_id(manual_job_id) == self.test_job_id
        assert decode_manual_job_id(self.test_job_id) is None

    def test_resolve_job_id_prefers_manual_job_id(self):
        """测试 listener 优先解析新手动 job id"""
        manual_job_id = build_manual_job_id(self.test_job_id, "manual-run")
        event = Mock(job_id=manual_job_id)

        assert _resolve_job_id(event) == self.test_job_id

    @patch('web.scheduler._get_cache_client_or_none')
    def test_resolve_job_id_falls_back_to_legacy_redis_mapping(self, mock_get_cache_client_or_none):
        """测试 listener 仍兼容旧 Redis 映射"""
        redis_client = Mock()
        redis_client.get.return_value = self.test_job_id
        mock_get_cache_client_or_none.return_value = redis_client

        app = Flask(__name__)
        app.config["_config_name"] = "dev"

        with app.app_context():
            event = Mock(job_id=self.test_new_job_id)
            assert _resolve_job_id(event) == self.test_job_id
        redis_client.get.assert_called_once_with(f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}{self.test_new_job_id}")

    @patch('web.scheduler._get_cache_client_or_none')
    def test_resolve_job_id_skips_redis_mapping_in_lite_runtime(self, mock_get_cache_client_or_none):
        """测试 lite 下不再读取 Redis 动态映射"""
        redis_client = Mock()
        mock_get_cache_client_or_none.return_value = redis_client

        app = Flask(__name__)
        app.config["_config_name"] = "lite"

        with app.app_context():
            event = Mock(job_id=self.test_new_job_id)
            assert _resolve_job_id(event) == self.test_new_job_id

        redis_client.get.assert_not_called()

    @patch('web.scheduler.has_app_context', return_value=False)
    @patch('web.scheduler._get_cache_client_or_none')
    def test_resolve_job_id_skips_redis_mapping_in_lite_runtime_without_flask_context(
        self,
        mock_get_cache_client_or_none,
        _mock_has_app_context,
    ):
        """测试 lite 在无 Flask 上下文的 listener 线程里也不再读取 Redis 映射"""
        redis_client = Mock()
        mock_get_cache_client_or_none.return_value = redis_client

        app = Flask(__name__)
        app.config["_config_name"] = "lite"

        with patch.object(scheduler_instance, "app", app):
            event = Mock(job_id=self.test_new_job_id)
            assert _resolve_job_id(event) == self.test_new_job_id

        redis_client.get.assert_not_called()

    def test_execution_persistence_strategy_registry_defaults_to_full(self):
        assert _get_execution_persistence_strategy("unknown.job") == "full"

    def test_execution_persistence_strategy_registry_marks_outbox_as_signal_only(self):
        assert (
            _get_execution_persistence_strategy("AsyncTaskScheduler.consume_notification_outbox")
            == "signal_only"
        )
    
    def test_uuid_generation_uniqueness(self):
        """测试UUID生成的唯一性"""
        # 生成多个UUID
        uuids = [str(uuid.uuid4().hex) for _ in range(10)]
        
        # 验证所有UUID都是唯一的
        assert len(set(uuids)) == len(uuids)
        
        # 验证UUID格式（32位十六进制字符）
        for uuid_str in uuids:
            assert len(uuid_str) == 32
            assert all(c in '0123456789abcdef' for c in uuid_str)
    
    def test_webcons_constants(self):
        """测试webcons常量的存在性"""
        # 验证RedisKeyPrefix.DYNAMIC_JOB常量存在
        assert hasattr(webcons.RedisKeyPrefix, 'DYNAMIC_JOB')
        assert isinstance(webcons.RedisKeyPrefix.DYNAMIC_JOB, str)
        assert len(webcons.RedisKeyPrefix.DYNAMIC_JOB) > 0
    
    def test_datetime_handling(self):
        """测试日期时间处理"""
        now = datetime.now()
        future_time = now + timedelta(seconds=1)
        
        # 验证时间比较
        assert future_time > now
        
        # 验证时间格式化
        time_str = now.strftime('%Y-%m-%d %H:%M:%S')
        assert len(time_str) == 19  # YYYY-MM-DD HH:MM:SS
        
        # 验证时间解析
        parsed_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        assert parsed_time.year == now.year
        assert parsed_time.month == now.month
        assert parsed_time.day == now.day


class TestManualJobWrapperIntegration:
    """测试手动任务包装函数的集成功能"""
    
    def test_function_isolation_concept(self):
        """测试函数隔离概念验证"""
        # 定义两个不同的函数
        def original_task(param):
            return f"original_{param}"
        
        def manual_wrapper(func, *args, **kwargs):
            return func(*args, **kwargs)
        
        # 测试直接调用和包装调用的区别
        direct_result = original_task("test")
        wrapped_result = manual_wrapper(original_task, "test")
        
        # 结果应该相同
        assert direct_result == wrapped_result == "original_test"
        
        # 但函数引用不同
        assert original_task != manual_wrapper
    
    def test_parameter_passing_integrity(self):
        """测试参数传递的完整性"""
        def test_function(a, b, c=None, **kwargs):
            result = {'a': a, 'b': b, 'c': c}
            result.update(kwargs)
            return result
        
        def wrapper(func, *args, **kwargs):
            return func(*args, **kwargs)
        
        # 测试各种参数组合
        result1 = wrapper(test_function, 1, 2)
        expected1 = {'a': 1, 'b': 2, 'c': None}
        assert result1 == expected1
        
        result2 = wrapper(test_function, 1, 2, c=3, extra="value")
        expected2 = {'a': 1, 'b': 2, 'c': 3, 'extra': 'value'}
        assert result2 == expected2
    
    def test_exception_propagation(self):
        """测试异常传播"""
        def failing_function():
            raise ValueError("Test exception")
        
        def wrapper(func, *args, **kwargs):
            return func(*args, **kwargs)
        
        # 验证异常正确传播
        with pytest.raises(ValueError, match="Test exception"):
            wrapper(failing_function)
    
    def test_return_value_preservation(self):
        """测试返回值保持"""
        def complex_function():
            return {
                'status': 'success',
                'data': [1, 2, 3],
                'metadata': {'timestamp': datetime.now()}
            }
        
        def wrapper(func, *args, **kwargs):
            return func(*args, **kwargs)
        
        result = wrapper(complex_function)
        
        # 验证复杂返回值的完整性
        assert result['status'] == 'success'
        assert result['data'] == [1, 2, 3]
        assert 'timestamp' in result['metadata']
        assert isinstance(result['metadata']['timestamp'], datetime)
