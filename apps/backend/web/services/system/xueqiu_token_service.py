from __future__ import annotations

from typing import Dict

from web.decorator import singleton
from web.weblogger import debug
from xalpha.cons import rget


@singleton
class XueqiuTokenService:
    """通过雪球首页响应自动提取匿名访问所需 cookie。"""

    _TOKEN_URL = "https://xueqiu.com/hq"
    _HEADERS = {"user-agent": "Mozilla/5.0"}

    @staticmethod
    def _require_cookie(response, key: str) -> str:
        value = response.cookies.get(key)
        if value:
            return str(value)
        raise ValueError(f"雪球响应里缺少 cookie: {key}")

    def fetch_xq_token(self) -> Dict[str, str]:
        response = rget(self._TOKEN_URL, headers=self._HEADERS)
        payload = {
            "xq_a_token": self._require_cookie(response, "xq_a_token"),
            "u": self._require_cookie(response, "u"),
        }
        debug(
            "自动获取雪球 token 成功: %s",
            {
                "xq_a_token": f"{payload['xq_a_token'][:2]}***{payload['xq_a_token'][-2:]}",
                "u": payload["u"],
            },
        )
        return payload


xueqiu_token_service = XueqiuTokenService()
