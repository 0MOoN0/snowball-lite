# -*- coding: UTF-8 -*-
"""
@File    ：token_test_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：1/19/2025 1:02 PM
"""
from flask import Blueprint, request
from flask_restful import Api, Resource

from web import weblogger
from web.common.utils import R
from web.databox import databox
from web.common.cons import webcons

token_test_bp = Blueprint("token_test", __name__, url_prefix="/token_test")
token_test_api = Api(token_test_bp)


class TokenTestRouters(Resource):

    def get(self):
        """
        @@@
        ```
        处理GET请求，测试token
        Args:
            xq_a_token (str, optional): 用户传入的 xq_a_token，用于临时替换当前token进行测试.
            u (str, optional): 用户传入的 u 参数，用于临时替换当前token进行测试.
        Returns:
            R.ok(): 操作成功返回的状态码、消息和测试结果 (True/False)
        ```
        @@@
        """
        xq_a_token_arg = request.args.get("xq_a_token")
        u_arg = request.args.get("u")

        original_token = None
        test_success = False
        new_token_provided = bool(xq_a_token_arg and u_arg)

        try:
            if new_token_provided:
                # 获取当前token
                original_token = databox.get_token(webcons.DataBoxTokenKey.XQ_TOKEN)
                weblogger.info(f"当前token: {original_token}")

                # 设置传入的token
                try:
                    new_token_dict = {"xq_a_token": xq_a_token_arg, "u": u_arg}
                    databox.set_token(webcons.DataBoxTokenKey.XQ_TOKEN, new_token_dict)
                    weblogger.info(f"已设置新token: {new_token_dict}")
                except Exception as e:
                    weblogger.error(f"设置新token失败: {e}", exc_info=True)
                    return R.fail(msg=f"设置新token失败: {e}")

            # 测试token
            databox.get_rt("SH501018") # 使用一个测试代码
            test_success = True
            weblogger.info("Token 测试成功")

        except Exception as e:
            weblogger.error(f"Token 测试失败: {e}", exc_info=True)
            test_success = False
        finally:
            if new_token_provided and original_token is not None:
                # 恢复原始token
                try:
                    databox.set_token(webcons.DataBoxTokenKey.XQ_TOKEN, original_token)
                    weblogger.info(f"已恢复原始token: {original_token}")
                except Exception as e:
                    weblogger.error(f"恢复原始token失败: {e}", exc_info=True)
                    # 即使恢复失败，也应返回测试结果
                    return R.fail(msg=f"恢复原始token失败: {e}, 但测试结果为: {test_success}")

        return R.ok(data=test_success)


token_test_api.add_resource(TokenTestRouters, "/result")
