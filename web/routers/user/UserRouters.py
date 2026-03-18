from flask import Blueprint
from flask_restful import Resource, Api

from web.common.utils import R

user_bp = Blueprint("user", __name__, url_prefix="/user")
user_api = Api(user_bp)


class UserLoginRouters(Resource):

    def post(self):
        return R.ok(
            data={'username': 'admin',
                  'password': 'admin',
                  'role': 'admin',
                  'roleId': 1,
                  'permissions': ['*.*.*']
                  }
        )


user_api.add_resource(UserLoginRouters, '/login')
