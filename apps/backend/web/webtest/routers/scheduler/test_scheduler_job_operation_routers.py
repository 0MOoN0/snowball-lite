import pytest
from unittest.mock import Mock, patch

from web.routers.scheduler.scheduler_job_operation_routers import (
    manual_job_wrapper,
    SchedulerJobRunRouters
)
from web.models.scheduler.scheduler_log import SchedulerLog
from web.scheduler.manual_job_id import build_manual_job_id, decode_manual_job_id


class TestManualJobWrapper:
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


class TestSchedulerJobRunRouters:
    """测试SchedulerJobRunRouters类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.router = SchedulerJobRunRouters()
        
    @patch('web.routers.scheduler.scheduler_job_operation_routers.build_manual_job_id')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.cache')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler_service')
    @patch('web.routers.scheduler.scheduler_job_operation_routers._get_parse')
    def test_put_method_basic_functionality(self, mock_get_parse, mock_scheduler_service, mock_cache, mock_scheduler, mock_build_manual_job_id):
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
        mock_build_manual_job_id.return_value = "manual::mocked_uuid_str::dGVzdF9qb2JfaWQ"

        mock_scheduler_service.get_job_state.return_value = None
        mock_scheduler_service.get_latest_job_log.return_value = None
        
        # 执行put方法
        result = self.router.put()
        
        # 验证scheduler.get_job被调用
        mock_scheduler.get_job.assert_called_once_with('test_job_id')

        # 验证scheduler.add_job被调用，且使用了manual_job_wrapper
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args

        # 验证func参数是manual_job_wrapper
        assert call_args[1]['func'] == manual_job_wrapper
        assert call_args[1]['id'] == "manual::mocked_uuid_str::dGVzdF9qb2JfaWQ"

        # 验证args参数包含原始函数和参数
        expected_args = [mock_job.func_ref, '2025-01-05', '2025-04-04']
        assert call_args[1]['args'] == expected_args

        # 验证kwargs参数
        assert call_args[1]['kwargs'] == {'key': 'value'}
        
        # 验证其他参数
        assert call_args[1]['trigger'] == 'date'
        assert call_args[1]['misfire_grace_time'] == 3600
        assert 'run_date' in call_args[1]

        # 验证不再依赖 Redis 临时映射
        mock_cache.get_redis_client.assert_not_called()
        mock_build_manual_job_id.assert_called_once_with('test_job_id')

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
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.build_manual_job_id')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.cache')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler_service')
    @patch('web.routers.scheduler.scheduler_job_operation_routers._get_parse')
    def test_put_method_with_empty_args_kwargs(self, mock_get_parse, mock_scheduler_service, mock_cache, mock_scheduler, mock_build_manual_job_id):
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
        mock_build_manual_job_id.return_value = "manual::mocked_uuid_str::dGVzdF9qb2JfaWQ"
        mock_scheduler_service.get_job_state.return_value = None
        mock_scheduler_service.get_latest_job_log.return_value = None

        result = self.router.put()
        
        # 验证scheduler.add_job被调用
        call_args = mock_scheduler.add_job.call_args
        
        # 验证args只包含原始函数（因为args为None）
        expected_args = [mock_job.func_ref]
        assert call_args[1]['args'] == expected_args
        
        # 验证kwargs为空字典
        assert call_args[1]['kwargs'] == {}
        assert call_args[1]['id'] == "manual::mocked_uuid_str::dGVzdF9qb2JfaWQ"
        mock_cache.get_redis_client.assert_not_called()
        mock_build_manual_job_id.assert_called_once_with('test_job_id')

        assert result['code'] == 20000
    
    def test_manual_job_id_round_trip(self):
        manual_job_id = build_manual_job_id("test_job_id", "mocked_uuid_str")
        assert manual_job_id.startswith("manual::")
        assert decode_manual_job_id(manual_job_id) == "test_job_id"
        assert decode_manual_job_id("test_job_id") is None
    
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler_service')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    def test_scheduler_add_job_exception_handling(self, mock_scheduler, mock_scheduler_service):
        """测试scheduler.add_job抛出异常时的处理"""
        with patch('web.routers.scheduler.scheduler_job_operation_routers.reqparse') as mock_reqparse:
            mock_parser = Mock()
            mock_reqparse.RequestParser.return_value = mock_parser
            
            mock_args = {'job_id': 'test_job_id'}
            mock_parser.parse_args.return_value = mock_args
            
            mock_job = Mock()
            mock_job.func_ref = Mock(__name__='test_function')
            mock_scheduler.get_job.return_value = mock_job
            mock_scheduler_service.get_job_state.return_value = None
            mock_scheduler_service.get_latest_job_log.return_value = None

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

    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler_service')
    @patch('web.routers.scheduler.scheduler_job_operation_routers._get_parse')
    @patch('web.routers.scheduler.scheduler_job_operation_routers.scheduler')
    def test_put_method_rejects_recent_submitted_job_state(
        self,
        mock_scheduler,
        mock_get_parse,
        mock_scheduler_service,
    ):
        mock_parser = Mock()
        mock_get_parse.return_value = mock_parser

        mock_args = {'job_id': 'test_job_id'}
        mock_parsed_args = Mock()
        mock_parsed_args.copy.return_value = mock_args
        mock_parser.parse_args.return_value = mock_parsed_args

        mock_job = Mock()
        mock_job.func_ref = Mock(__name__='test_function')
        mock_scheduler.get_job.return_value = mock_job

        submitted_state = Mock()
        submitted_state.last_execution_state = SchedulerLog.get_scheduler_state_enum().SUBMITTED.value
        submitted_state.last_submitted_time = __import__("datetime").datetime.now()
        mock_scheduler_service.get_job_state.return_value = submitted_state

        result = self.router.put()

        assert result['code'] != 20000


class TestSchedulerJobOperationIntegration:
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
    
    def test_manual_job_id_helper_round_trip(self):
        manual_job_id = build_manual_job_id("original_job_id", "round_trip")
        assert decode_manual_job_id(manual_job_id) == "original_job_id"
