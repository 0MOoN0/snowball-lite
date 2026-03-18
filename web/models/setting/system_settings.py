from sqlalchemy import text
import json
from flask_marshmallow import Schema
from marshmallow import fields, post_load, ValidationError

from web.decorator.auto_registry import register_model
from web.models import db


@register_model
class Setting(db.Model):
    """
    系统设置模型
    
    用于存储系统级别的配置参数，支持不同类型的设置值和分组管理。
    所有系统配置都通过此模型进行统一管理和持久化存储。
    """
    __tablename__ = 'system_settings'
    __bind_key__ = "snowball"

    # 主键ID，自增
    id = db.Column(db.Integer, primary_key=True, comment='主键ID，自增')
    key = db.Column(db.String(100), unique=True, nullable=False,
                    comment='设置项唯一标识键，如"email_smtp_host"')
    value = db.Column(db.Text, nullable=False,
                      comment='设置项的值，支持字符串、JSON等格式')
    setting_type = db.Column(db.String(50), nullable=False,
                             comment='设置类型：string/int/float/bool/json/password等')
    group = db.Column(db.String(100), default='general',
                      comment='设置分组：general/email/security/notification等')
    description = db.Column(db.Text,
                            comment='设置项描述，用于管理界面展示和说明')
    default_value = db.Column(db.Text,
                              comment='设置项默认值，用于重置或初始化')
    created_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'),
                             comment='创建时间')
    updated_time = db.Column(
        db.DateTime,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP'),
        comment='最后更新时间',
    )

    def __repr__(self):
        """模型的字符串表示"""
        return f'<Setting {self.key}={self.value}>'

    def to_dict(self):
        """转换为字典格式，便于API返回"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'setting_type': self.setting_type,
            'group': self.group,
            'description': self.description,
            'default_value': self.default_value,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def get_typed_value(self):
        """根据 setting_type 返回正确类型的值"""
        if self.setting_type == 'int':
            return int(self.value)
        elif self.setting_type == 'float':
            return float(self.value)
        elif self.setting_type == 'bool':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'json':
            import json
            return json.loads(self.value)
        else:
            return self.value
    
    def set_typed_value(self, value):
        """根据 setting_type 设置正确格式的值"""
        if self.setting_type == 'json':
            import json
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = str(value)


class SettingSchema(Schema):
    """Setting模型的序列化Schema"""
    id = fields.Integer(dump_only=True)
    key = fields.String(required=True, validate=lambda x: len(x) <= 100)
    value = fields.String(required=True)
    # 修正字段映射：字段名使用下划线，data_key使用驼峰
    setting_type = fields.String(required=True, data_key='settingType', 
                                validate=lambda x: x in ['string', 'int', 'float', 'bool', 'json', 'password'])
    group = fields.String(load_default='general', validate=lambda x: len(x) <= 100)
    description = fields.String(allow_none=True)
    default_value = fields.String(allow_none=True, data_key='defaultValue')
    created_time = fields.DateTime(dump_only=True, data_key='createdTime')
    updated_time = fields.DateTime(dump_only=True, data_key='updatedTime')

    @post_load
    def make_setting(self, data, **kwargs):
        return Setting(**data)


class SettingUpdateSchema(Schema):
    """Setting更新专用Schema"""
    key = fields.String(required=True, validate=lambda x: len(x) <= 100)
    value = fields.String(required=True)
    setting_type = fields.String(allow_none=True, data_key='settingType', 
                                validate=lambda x: x in ['string', 'int', 'float', 'bool', 'json', 'password'] if x else True)
    group = fields.String(allow_none=True, validate=lambda x: len(x) <= 100 if x else True)
    description = fields.String(allow_none=True)
    default_value = fields.String(allow_none=True, data_key='defaultValue')
    
    def validate_json_value(self, data, **kwargs):
        """校验JSON类型的配置值"""
        if data.get('setting_type') == 'json' or (not data.get('setting_type') and hasattr(self, '_current_setting_type') and self._current_setting_type == 'json'):
            try:
                json.loads(data['value'])
            except (json.JSONDecodeError, TypeError) as e:
                raise ValidationError(f'JSON格式校验失败: {str(e)}', field_name='value')
        return data
    
    @post_load
    def validate_and_process(self, data, **kwargs):
        """加载后处理和校验"""
        return self.validate_json_value(data)
