from __future__ import annotations

import json
from typing import Any, Dict

from web.common.cons import webcons
from web.decorator import singleton
from web.models import db
from web.models.setting.system_settings import Setting
from web.weblogger import debug, error


@singleton
class SystemTokenService:
    """系统 token 的 SQLite 持久化服务。"""

    @staticmethod
    def _mask_secret(value: Any) -> Any:
        if not isinstance(value, str) or not value:
            return value
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}***{value[-2:]}"

    def _load_setting(self, key: str) -> Setting | None:
        return Setting.query.filter_by(key=key).first()

    def _upsert_setting(self, key: str, value: str, setting_type: str) -> Setting:
        setting = self._load_setting(key)
        if setting is None:
            setting = Setting(
                key=key,
                value=value,
                setting_type=setting_type,
                group="system",
                description=f"{key} system token setting",
            )
            db.session.add(setting)
            return setting

        setting.value = value
        setting.setting_type = setting_type
        if not setting.group:
            setting.group = "system"
        return setting

    def get_xq_token(self) -> Dict[str, Any]:
        setting = self._load_setting(webcons.DataBoxTokenKey.XQ_TOKEN)
        if setting is None or not setting.value:
            return {}

        try:
            if setting.setting_type == "json":
                payload = json.loads(setting.value)
                return payload if isinstance(payload, dict) else {}
            if setting.setting_type == "string":
                payload = json.loads(setting.value)
                return payload if isinstance(payload, dict) else {}
        except Exception as exc:
            error(f"读取 XQ_TOKEN 失败: {exc}", exc_info=True)
        return {}

    def get_serverchan_sendkey(self) -> str | None:
        setting = self._load_setting(webcons.RedisKey.SERVERCHAN_SENDKEY)
        if setting is None or setting.value is None:
            return None
        return str(setting.value)

    def get_token_payload(self) -> Dict[str, Any]:
        xq_token = self.get_xq_token()
        payload = {
            "xq_a_token": xq_token.get("xq_a_token"),
            "u": xq_token.get("u"),
            "serverchen_sendkey": self.get_serverchan_sendkey(),
        }
        debug(
            "读取系统 token 成功: %s",
            {
                "xq_a_token": self._mask_secret(payload.get("xq_a_token")),
                "u": payload.get("u"),
                "serverchen_sendkey": self._mask_secret(payload.get("serverchen_sendkey")),
            },
        )
        return payload

    def save_xq_token(self, xq_token: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self._upsert_setting(
                webcons.DataBoxTokenKey.XQ_TOKEN,
                json.dumps(xq_token, ensure_ascii=False),
                "json",
            )
            db.session.commit()
            return self.get_token_payload()
        except Exception as exc:
            db.session.rollback()
            error(f"保存雪球 token 失败: {exc}", exc_info=True)
            raise

    def save_token_payload(self, xq_token: Dict[str, Any], serverchen_sendkey: str) -> Dict[str, Any]:
        try:
            self._upsert_setting(
                webcons.DataBoxTokenKey.XQ_TOKEN,
                json.dumps(xq_token, ensure_ascii=False),
                "json",
            )
            self._upsert_setting(
                webcons.RedisKey.SERVERCHAN_SENDKEY,
                serverchen_sendkey,
                "string",
            )
            db.session.commit()
            return self.get_token_payload()
        except Exception as exc:
            db.session.rollback()
            error(f"保存系统 token 失败: {exc}", exc_info=True)
            raise


system_token_service = SystemTokenService()
