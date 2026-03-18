from flask import Blueprint
from flask_restful import Api, Resource

from web.models.Menu import Menu, MenuSchema
from web.common.utils import R

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")
menu_api = Api(menu_bp)


# 获取菜单
class MenuRouter(Resource):
    def get(self):
        # 获取顶级菜单
        menus = Menu.query.filter(Menu.parent_id == 0).all()
        self.get_child_menu(menus)
        return R.ok(data=MenuSchema().dump(menus, many=True))

    def get_child_menu(self, menus):
        if menus is None:
            return None
        for menu in menus:
            # 查找当前菜单的子菜单
            child_menus = Menu.query.filter(Menu.parent_id == menu.id).all()
            menu.children = child_menus
            self.get_child_menu(menu.children)


menu_api.add_resource(MenuRouter, "")
