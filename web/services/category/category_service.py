from numbers import Number
from typing import List, Dict

from web.web_exception import WebBaseException
from web.models.category.Category import Category, CategoryVO


class CategoryService:
    def get_category_list(self) -> List[CategoryVO]:
        category_list = Category.query.filter(Category.is_deleted == False).all()
        category_vo_list = list(map(lambda c: CategoryVO(c), category_list))
        result_list = []
        cate_dict = {0: []}
        # 标记所有分类
        for category_vo in category_vo_list:
            child_list = cate_dict.get(category_vo.pid)
            if child_list is None:
                cate_dict[category_vo.pid] = [category_vo]
                continue
            child_list.append(category_vo)
        # 遍历字典并赋值
        root_node = cate_dict.get(0)
        if root_node is not None and len(root_node) > 0:
            for root in root_node:
                result_list.append(root)
                self._fill_cate_root(root, cate_dict)
        return result_list

    def _fill_cate_root(self, category_vo: CategoryVO, cate_dict: Dict[Number, List[CategoryVO]]):
        if category_vo is None:
            raise WebBaseException(msg='数据错误，分类数据不存在')
        if len(cate_dict) <= 0:
            return
        children_node: List[CategoryVO] = cate_dict.get(category_vo.id)
        if children_node is not None and len(children_node) >= 0:
            category_vo.children.extend(children_node)
        for root in category_vo.children:
            self._fill_cate_root(root, cate_dict)
