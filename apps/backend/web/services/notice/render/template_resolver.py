# 模板解析器
from typing import Optional
import os
from flask import current_app


class TemplateResolver:
    """
    模板解析器，负责根据业务类型和template_key解析模板路径
    支持三级优先级模板选择机制
    """
    
    # 业务类型到目录名的映射
    BUSINESS_TYPE_MAPPING = {
        0: 'grid_trade',
        1: 'message_remind', 
        2: 'system_runing',
        3: 'daily_report',
        4: 'cb_subscribe'
    }
    
    # 渲染策略类名到render_type的映射
    RENDER_TYPE_MAPPING = {
        'NotificationBotRenderStrategy': 'bot',
        'ServerChenRenderStrategy': 'html',
        'NotificationHTMLRenderStrategy': 'html'
    }
    
    def __init__(self, template_folder: str = None):
        """
        初始化模板解析器
        
        Args:
            template_folder: 模板文件夹路径，默认使用Flask应用的template_folder
        """
        self.template_folder = template_folder or current_app.template_folder
    
    def get_render_type(self, strategy_class_name: str) -> str:
        """
        根据渲染策略类名获取render_type
        
        Args:
            strategy_class_name: 渲染策略类名
            
        Returns:
            str: render_type (bot/html)
        """
        return self.RENDER_TYPE_MAPPING.get(strategy_class_name, 'bot')
    
    def resolve_template_path(self, business_type: int, render_type: str, template_key: Optional[str] = None) -> str:
        """
        解析模板路径，支持三级优先级选择机制
        
        Args:
            business_type: 业务类型 (0-3)
            render_type: 渲染类型 (bot/html)
            template_key: 模板键值，完整文件名（含扩展名）
            
        Returns:
            str: 模板路径
            
        Raises:
            ValueError: 当所有优先级模板都不存在时抛出异常
        """
        # 优先级1：如果指定了template_key，直接使用完整文件名
        if template_key:
            priority1_path = self._build_template_path(business_type, render_type, template_key)
            if self._template_exists(priority1_path):
                return priority1_path
        
        # 优先级2：根据business_type和render_type选择默认模板
        default_ext = 'txt' if render_type == 'bot' else 'html'
        default_template = f'default.{default_ext}'
        priority2_path = self._build_template_path(business_type, render_type, default_template)
        if self._template_exists(priority2_path):
            return priority2_path
        
        # 优先级3：回退到legacy模板（向后兼容）
        legacy_template = 'legacy/bot_notification.txt' if render_type == 'bot' else 'legacy/notification_template.html'
        if self._template_exists(legacy_template):
            return legacy_template
        
        # 所有优先级都失败，抛出异常
        raise ValueError(f"无法找到适合的模板：business_type={business_type}, render_type={render_type}, template_key={template_key}")
    
    def _build_template_path(self, business_type: int, render_type: str, template_filename: str) -> str:
        """
        构建模板路径
        
        Args:
            business_type: 业务类型
            render_type: 渲染类型
            template_filename: 模板文件名
            
        Returns:
            str: 构建的模板路径
        """
        business_type_name = self.BUSINESS_TYPE_MAPPING.get(business_type, 'grid_trade')
        return f'notifications/{business_type_name}/{render_type}/{template_filename}'
    
    def _template_exists(self, template_path: str) -> bool:
        """
        检查模板文件是否存在
        
        Args:
            template_path: 模板路径
            
        Returns:
            bool: 模板是否存在
        """
        full_path = os.path.join(self.template_folder, template_path)
        return os.path.isfile(full_path)
    
    def get_available_templates(self, business_type: int, render_type: str) -> list:
        """
        获取指定业务类型和渲染类型下的所有可用模板
        
        Args:
            business_type: 业务类型
            render_type: 渲染类型
            
        Returns:
            list: 可用模板文件名列表
        """
        business_type_name = self.BUSINESS_TYPE_MAPPING.get(business_type, 'grid_trade')
        template_dir = os.path.join(self.template_folder, 'notifications', business_type_name, render_type)
        
        if not os.path.isdir(template_dir):
            return []
        
        templates = []
        for filename in os.listdir(template_dir):
            if os.path.isfile(os.path.join(template_dir, filename)):
                templates.append(filename)
        
        return sorted(templates)