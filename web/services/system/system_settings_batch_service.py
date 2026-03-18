from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from web import error
from web.models.setting.system_settings import Setting


class SystemSettingsBatchService:
    """系统设置批量操作服务类"""
    
    def __init__(self, db: Session):
        self.db: Session = db

    def batch_update_settings(self, settings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量更新系统设置
        
        Args:
            settings_data: 设置数据列表，每个元素包含key和要更新的字段
            
        Returns:
            Dict[str, Any]: 包含成功数量、失败数量、成功键列表和失败详情的字典
        """
        success_count: int = 0
        failure_count: int = 0
        successful_keys: List[str] = []
        failures: List[Dict[str, str]] = []

        # 收集所有要更新的键，用于批量查询
        keys_to_update: List[str] = [item.get('key') for item in settings_data if item.get('key')]
        
        # 批量查询现有设置
        existing_settings: List[Setting] = self.db.query(Setting).filter(
            Setting.key.in_(keys_to_update)
        ).all()
        
        # 创建键到设置对象的映射
        existing_settings_map: Dict[str, Setting] = {
            setting.key: setting for setting in existing_settings
        }

        # 处理每个设置项
        for item in settings_data:
            key: Optional[str] = item.get('key')
            if not key:
                failure_count += 1
                failures.append({
                    "key": "unknown", 
                    "error": "Missing required field 'key'"
                })
                continue
                
            try:
                setting: Optional[Setting] = existing_settings_map.get(key)
                if not setting:
                    failure_count += 1
                    failures.append({
                        "key": key, 
                        "error": f"Setting with key '{key}' not found."
                    })
                    continue

                # 更新字段（排除key字段，因为key不应该被更新）
                updated: bool = False
                for field, value in item.items():
                    if field != 'key' and hasattr(setting, field) and value is not None:
                        # 处理字段名映射
                        if field == 'settingType':
                            field = 'setting_type'
                        elif field == 'defaultValue':
                            field = 'default_value'
                            
                        setattr(setting, field, value)
                        updated = True

                if updated:
                    self.db.add(setting)
                    success_count += 1
                    successful_keys.append(key)
                else:
                    failure_count += 1
                    failures.append({
                        "key": key, 
                        "error": "No valid fields to update"
                    })

            except Exception as e:
                failure_count += 1
                failures.append({
                    "key": key, 
                    "error": f"Failed to update setting with key '{key}': {str(e)}"
                })
                error(f"批量更新系统设置，处理key '{key}' 失败：{str(e)}")

        # 提交成功的更新
        if success_count > 0:
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                # 如果提交失败，将所有成功的更新回滚并添加到失败列表
                failure_count += success_count
                success_count = 0
                for key in successful_keys:
                    failures.append({
                        "key": key, 
                        "error": f"Transaction commit failed for key '{key}': {str(e)}"
                    })
                successful_keys = []
                error(f"批量更新系统设置，事务提交失败：{str(e)}")

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "successful_keys": successful_keys,
            "failures": failures
        }