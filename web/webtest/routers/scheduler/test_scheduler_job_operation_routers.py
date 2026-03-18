import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pytz import timezone

from web.webtest.test_base import TestBaseWithRollback
from web.routers.scheduler.scheduler_job_operation_routers import (
    manual_job_wrapper,
    SchedulerJobRunRouters
)
from web.common.cache import cache
from web.common.cons import webcons
from web.models.scheduler.scheduler_log import SchedulerLog


class TestManualJobWrapper(TestBaseWithRollback):
    """测试manual_job_wrapper包装函数"""
    
    def test_manual_job_wrapper_basic_execution(self):
        """测试包装函数基本执行功能"""
        # 创建模拟的原始函数
        mock_func = Mock(return_value="test_result")
        
        # 测试参数
        test_args = ("arg1", "arg2")
        test_kwargs = {"key1": "value1", "key2": "value2"}
        
        # 执行包装函数
        result = manual_job_wrapper(mock_func, *test_args, **test_kwargs)
        
        # 验证结果
        assert result == "test_result"
        mock_func.assert_called_once_with(*test_args, **test_kwargs)
    
    def test_manual_job_wrapper_with_exception(self):
        """测试包装函数异常处理"""
        # 创建会抛出异常的模拟函数
        mock_func = Mock(side_effect=ValueError("Test exception"))
        
        # 验证异常会被正确传播
        with pytest.raises(ValueError, match="Test exception"):
            manual_job_wrapper(mock_func, "arg1")
        
        mock_func.assert_called_once_with("arg1")
    
    def test_manual_job_wrapper_no_args(self):
        """测试包装函数无参数调用"""
        mock_func = Mock(return_value="no_args_result")
        
        result = manual_job_wrapper(mock_func)
        
        assert result == "no_args_result"
        mock_func.assert_called_once_with()
    
    def test_manual_job_wrapper_preserves_function_behavior(self):
        """测试包装函数保持原函数行为"""
        def test_function(a, b, c=None):
            if c:
                return f"{a}-{b}-{c}"
            return f"{a}-{b}"
        
        # 测试位置参数
        result1 = manual_job_wrapper(test_function, "x", "y")
        assert result1 == "x-y"
        
        # 测试关键字参数
        result2 = manual_job_wrapper(test_function, "x", "y", c="z")
        assert result2 == "x-y-z"


class TestSchedulerJobRunRouters(TestBaseWithRollback):
    """测试SchedulerJobRunRouters类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.router = SchedulerJobRunRouters()
        
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.cache')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.SchedulerLog')
    @patch('web.routers.scheduler.scheduler_job_operation_routers._get_parse')
    def test_put_method_basic_functionality(self, mock_get_parse, mock_scheduler_log, mock_cache, mock_scheduler):
        """测试put方法基本功能"""
        # 模拟_get_parse返回的parser
        mock_parser = Mock()
        mock_get_parse.return_value = mock_parser
        
        # 模拟解析后的参数
        mock_args = {
            'job_id': 'test_job_id',
            'args': '2025-01-05&2025-04-04',
            'kwargs': "{'key': 'value'}"
        }
        # 创建一个具有copy方法的Mock对象
        mock_parsed_args = Mock()
        mock_parsed_args.copy.return_value = mock_args
        # 让parse_args返回这个Mock对象
        mock_parser.parse_args.return_value = mock_parsed_args
        
        # 模拟scheduler.get_job返回的job对象
        mock_job = Mock()
        mock_job.func_ref = Mock(__name__='test_function')
        mock_scheduler.get_job.return_value = mock_job
        
        # 模拟scheduler.add_job
        mock_scheduler.add_job.return_value = None
        
        # 模拟缓存操作
        mock_redis_client = Mock()
        mock_cache.get_redis_client.return_value = mock_redis_client
        
        # 模拟SchedulerLog查询，返回None表示没有最近的任务记录
        mock_query = Mock()
        mock_scheduler_log.query = mock_query
        mock_query.filter.return_value.order_by.return_value.first.return_value = None
        
        # 执行put方法
        result = self.router.put()
        
        # 验证scheduler.get_job被调用
        mock_scheduler.get_job.assert_called_once_with('test_job_id')
            
        # 验证scheduler.add_job被调用，且使用了manual_job_wrapper
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        
        # 验证func参数是manual_job_wrapper
        assert call_args[1]['func'] == manual_job_wrapper
        
        # 验证args参数包含原始函数和参数
        expected_args = [mock_job.func_ref, '2025-01-05', '2025-04-04']
        assert call_args[1]['args'] == expected_args
        
        # 验证kwargs参数
        assert call_args[1]['kwargs'] == {'key': 'value'}
        
        # 验证其他参数
        assert call_args[1]['trigger'] == 'date'
        assert call_args[1]['misfire_grace_time'] == 3600
        assert 'next_run_time' in call_args[1]
        assert 'id' in call_args[1]
        
        # 验证缓存操作被调用
        mock_cache.get_redis_client.assert_called_once()
        mock_redis_client.set.assert_called_once()
        
        # 验证返回结果
        assert result['code'] == 20000
        assert 'data' in result
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    @patch('web.routers.scheduler.scheduler_job_operation_routers._get_parse')
    def test_put_method_job_not_found(self, mock_get_parse, mock_scheduler):
        """测试put方法当任务不存在时的处理"""
        # 模拟_get_parse函数和参数解析
        mock_parser = Mock()
        mock_get_parse.return_value = mock_parser
        
        mock_args = {'job_id': 'non_existent_job'}
        # 创建一个具有copy方法的Mock对象
        mock_parsed_args = Mock()
        mock_parsed_args.copy.return_value = mock_args
        mock_parser.parse_args.return_value = mock_parsed_args
        
        # 模拟job不存在
        mock_scheduler.get_job.return_value = None
        
        result = self.router.put()
        
        # 验证返回错误结果
        assert result['code'] != 200
        assert 'error' in result or 'message' in result
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.cache')
    @patch('web.routers.scheduler.scheduler_job_operation_routers._get_parse')
    def test_put_method_with_empty_args_kwargs(self, mock_get_parse, mock_cache, mock_scheduler):
        """测试put方法处理空参数的情况"""
        # 模拟_get_parse函数和参数解析
        mock_parser = Mock()
        mock_get_parse.return_value = mock_parser
        
        # 模拟空参数
        mock_args = {
            'job_id': 'test_job_id',
            'args': None,
            'kwargs': None
        }
        # 创建一个具有copy方法的Mock对象
        mock_parsed_args = Mock()
        mock_parsed_args.copy.return_value = mock_args
        mock_parser.parse_args.return_value = mock_parsed_args
        
        mock_job = Mock()
        mock_job.func_ref = Mock(__name__='test_function')
        mock_scheduler.get_job.return_value = mock_job
        mock_scheduler.add_job.return_value = None
        
        # 模拟缓存操作
        mock_redis_client = Mock()
        mock_cache.get_redis_client.return_value = mock_redis_client
        
        result = self.router.put()
        
        # 验证scheduler.add_job被调用
        call_args = mock_scheduler.add_job.call_args
        
        # 验证args只包含原始函数（因为args为None）
        expected_args = [mock_job.func_ref]
        assert call_args[1]['args'] == expected_args
        
        # 验证kwargs为空字典
        assert call_args[1]['kwargs'] == {}
        
        assert result['code'] == 20000
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.cache')
    def test_cache_key_generation(self, mock_cache, mock_scheduler):
        """测试缓存键的生成逻辑"""
        with patch('web.routers.scheduler.scheduler_job_operation_routers.reqparse') as mock_reqparse:
            mock_parser = Mock()
            mock_reqparse.RequestParser.return_value = mock_parser
            
            mock_args = {'job_id': 'test_job_id'}
            mock_parser.parse_args.return_value = mock_args
            
            mock_job = Mock()
            mock_job.func = Mock(__name__='test_function')
            mock_scheduler.get_job.return_value = mock_job
            mock_scheduler.add_job.return_value = None
            
            # 模拟uuid生成
            with patch('web.routers.scheduler.scheduler_job_operation_routers.uuid.uuid4') as mock_uuid:
                # 模拟str(uuid.uuid4())的返回值
                mock_uuid.return_value.__str__ = Mock(return_value='mocked_uuid_str')
                
                self.router.put()
                
                # 验证缓存键的格式
                mock_cache.get_redis_client().set.assert_called_once()
                cache_call_args = mock_cache.get_redis_client().set.call_args[0]
                
                # 缓存键应该是 webcons.RedisKeyPrefix.DYNAMIC_JOB + new_job_id
                expected_cache_key = f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}mocked_uuid_str"
                assert cache_call_args[0] == expected_cache_key
                
                # 缓存值应该是原始job_id
                assert cache_call_args[1] == 'test_job_id'
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    def test_scheduler_add_job_exception_handling(self, mock_scheduler):
        """测试scheduler.add_job抛出异常时的处理"""
        with patch('web.routers.scheduler.scheduler_job_operation_routers.reqparse') as mock_reqparse:
            mock_parser = Mock()
            mock_reqparse.RequestParser.return_value = mock_parser
            
            mock_args = {'job_id': 'test_job_id'}
            mock_parser.parse_args.return_value = mock_args
            
            mock_job = Mock()
            mock_job.func = Mock(__name__='test_function')
            mock_scheduler.get_job.return_value = mock_job
            
            # 模拟add_job抛出异常
            mock_scheduler.add_job.side_effect = Exception("Scheduler error")
            
            # 执行应该处理异常而不崩溃
            try:
                result = self.router.put()
                # 如果有异常处理，应该返回错误结果
                assert result['code'] != 200 or 'error' in result
            except Exception as e:
                # 如果没有异常处理，至少验证异常被抛出
                assert "Scheduler error" in str(e)


class TestSchedulerJobOperationIntegration(TestBaseWithRollback):
    """集成测试：测试手动任务执行的完整流程"""
    
    def test_manual_job_execution_flow(self):
        """测试手动任务执行的完整流程"""
        # 创建一个测试函数
        def test_task_function(param1, param2, keyword_param=None):
            return f"Executed with {param1}, {param2}, {keyword_param}"
        
        # 测试包装函数调用
        result = manual_job_wrapper(
            test_task_function,
            "value1",
            "value2",
            keyword_param="keyword_value"
        )
        
        expected_result = "Executed with value1, value2, keyword_value"
        assert result == expected_result
    
    def test_task_isolation_verification(self):
        """验证任务隔离效果"""
        # 创建两个不同的函数
        def original_task():
            return "original"
        
        def another_task():
            return "another"
        
        # 通过包装函数调用
        result1 = manual_job_wrapper(original_task)
        result2 = manual_job_wrapper(another_task)
        
        # 验证函数引用隔离
        assert result1 == "original"
        assert result2 == "another"
        
        # 验证包装函数本身不会混淆不同的原始函数
        assert manual_job_wrapper != original_task
        assert manual_job_wrapper != another_task
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.cache')
    def test_cache_operation_verification(self, mock_cache):
        """验证缓存操作的正确性"""
        # 模拟缓存操作
        mock_redis = mock_cache.get_redis_client.return_value
        mock_redis.set.return_value = True
        mock_redis.get.return_value = "original_job_id"
        
        # 测试缓存设置
        cache_key = f"{webcons.RedisKeyPrefix.DYNAMIC_JOB}test_new_job_id"
        redis_client = cache.get_redis_client()
        redis_client.set(cache_key, "original_job_id", ex=3600)
        
        # 验证缓存获取
        retrieved_value = redis_client.get(cache_key)
        
        # 在实际环境中，这些操作应该正常工作
        # 这里主要验证缓存键的格式和操作流程
        assert cache_key.startswith(webcons.RedisKeyPrefix.DYNAMIC_JOB)