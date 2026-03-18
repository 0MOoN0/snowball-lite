# core/enum_utils.py
import json
import time
from enum import Enum
from typing import Type, Dict, Any, List, Optional, Tuple
from web.common.enum.version_enum import VersionKeyEnum


def register_labels_by_name(labels: Dict[str, str]):
    """
    基于“枚举成员名”注册人类可读的标签，并将映射挂载到枚举类的 `_label_map` 属性。

    用途:
    - 作为类装饰器使用，为 API/序列化提供成员的展示文本（如中文标签）。

    工作原理:
    - 将 `labels` 中的 name -> label 按 name 在枚举类中查找对应成员，构造 {成员对象: 标签} 并保存为 `cls._label_map`。

    参数:
    - labels: Dict[str, str] 枚举成员名到标签的映射（区分大小写，未匹配到的键将被忽略）。

    返回:
    - 一个装饰器，该装饰器接收枚举类并返回同一个类，副作用是为其添加 `_label_map` 字段。

    限制与注意:
    - 仅按“成员名”匹配：若成员名变更或不存在，对应标签会被忽略，不会抛错。
    - 标签快照在装饰时生成：后续动态增删成员不会自动更新 `_label_map`。
    - 不包含 i18n：若需要多语言，建议在 `_label_map` 中存储文案 key，由外层国际化组件翻译。
    - 适用于 Enum/IntEnum 等；与成员值类型无关。
    """

    def decorator(cls: Type[Enum]) -> Type[Enum]:
        label_map = {cls[name]: label for name, label in labels.items()}
        setattr(cls, "_label_map", label_map)
        return cls

    return decorator


def serialize_enum(enum_class: Type[Enum]) -> List[Dict[str, Any]]:
    """
    将一个枚举类序列化为 [{"value": 成员值, "label": 展示文本}] 的列表。

    用途:
    - 为 API 返回或前端字典/下拉选项提供统一的数据结构。

    标签来源优先级:
    1) 若枚举类存在 `_label_map` 且包含该成员，则使用其中的标签（推荐通过 `@register_labels_by_name` 装饰器设置）。
    2) 否则回退为成员名 `member.name`。

    参数:
    - enum_class: Type[Enum] 任意 Python Enum 类。

    返回:
    - List[Dict[str, Any]]，形如 `[{"value": ..., "label": ...}, ...]` 的列表。返回顺序与枚举定义顺序一致。

    限制与注意:
    - 成员的 `value` 需可被 JSON 序列化；否则对外返回时可能需要自定义序列化过程。
    - 若存在“别名”（同值多名），Python 的枚举迭代仅返回主成员，别名不会出现在结果中。
    - 本函数不做排序或去重；如需按业务排序，请在调用方处理。
    """
    # 尝试从类中获取已注册的标签字典，如果不存在则返回一个空字典
    label_map = getattr(enum_class, "_label_map", {})

    serialized_list = []
    for member in enum_class:
        # 优先从 label_map 中获取标签，如果找不到，就用成员的名称作为备用
        label = label_map.get(member, member.name)
        serialized_list.append({"value": member.value, "label": label})

    return serialized_list


def record_enum_version(
    redis_client: Any,
    key: str = VersionKeyEnum.ENUM.value,
    scope: str = "global",
    timestamp: Optional[int] = None,
    ttl: Optional[int] = None,
    logger: Optional[Any] = None,
    merge: bool = False,
) -> Tuple[bool, Dict[str, int]]:
    """
    将枚举版本信息写入 Redis，支持作用域、TTL 与合并策略，避免循环依赖（通过显式传入 redis 客户端与 logger）。

    参数:
    - redis_client: 已初始化的 Redis 客户端实例（必填）。
    - key: 写入的 Redis Key，默认 "version:enum"。
    - scope: 作用域/命名空间（如 "global"、"tenant_x"），默认 "global"。
    - timestamp: 指定写入的时间戳（秒），默认 None 时使用当前时间戳。
    - ttl: 过期时间（秒），None 表示不过期。
    - logger: 可选日志记录器，若提供将输出成功/失败日志。
    - merge: 为 True 时，读取已存在 JSON 并合并当前 scope 字段；为 False 时直接覆盖。

    返回:
    - Tuple[bool, Dict[str, int]]: (是否写入成功, 实际写入的 payload 字典)
    """
    if redis_client is None:
        raise ValueError("redis_client is required")

    ts = int(timestamp if timestamp is not None else time.time())
    payload: Dict[str, int] = {scope: ts}

    try:
        if merge:
            prev_raw = redis_client.get(key)
            if prev_raw:
                try:
                    prev = json.loads(prev_raw)
                    if isinstance(prev, dict):
                        prev[scope] = ts
                        payload = prev
                except Exception:
                    # 忽略历史数据损坏或非 JSON 的情况
                    pass

        data = json.dumps(payload, ensure_ascii=False)
        if ttl is not None and ttl > 0:
            redis_client.setex(key, ttl, data)
        else:
            redis_client.set(key, data)

        if logger:
            logger.info(f"已写入枚举版本信息到 Redis，key={key}, value={payload}")
        return True, payload
    except Exception as e:
        if logger:
            try:
                import redis as _redis  # 局部导入，避免模块级强依赖引入循环
                if isinstance(e, _redis.ConnectionError):
                    logger.warning(f"写入枚举版本信息到 Redis 失败（连接错误）: {e}")
                else:
                    logger.error(f"写入枚举版本信息到 Redis 失败: {e}", exc_info=True)
            except Exception:
                logger.error(f"写入枚举版本信息到 Redis 失败: {e}", exc_info=True)
        return False, payload
