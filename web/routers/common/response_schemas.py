from flask_restx import fields
from web.common.api_factory import get_api

# 全局响应模型缓存
_response_models = {}


def get_base_response_model():
    """
    获取基础响应模型（与 R.py 返回值结构同步）

    Returns:
        flask_restx.Model: 基础响应模型
    """
    if "BaseResponse" in _response_models:
        return _response_models["BaseResponse"]

    api = get_api()
    if api is None:
        raise RuntimeError("API实例未初始化，请确保在应用启动后调用此函数")

    model = api.model(
        "BaseResponse",
        {
            "code": fields.Integer(
                required=True,
                description="响应码，20000表示成功，20500表示失败",
                example=20000,
            ),
            "message": fields.String(
                required=True, description="响应消息", example="成功"
            ),
            "data": fields.Raw(description="响应数据，可以是任意类型"),
            "success": fields.Boolean(
                required=True, description="是否成功", example=True
            ),
        },
    )

    _response_models["BaseResponse"] = model
    return model


def create_pagination_model(item_model=None, model_name_suffix=""):
    """
    创建分页数据模型（data部分）

    Args:
        item_model: 列表项的模型
        model_name_suffix: 模型名称后缀

    Returns:
        flask_restx.Model: 分页数据模型
    """
    model_name = f"PaginationData{model_name_suffix}"

    api = get_api()
    if api is None:
        raise RuntimeError("API实例未初始化，请确保在应用启动后调用此函数")

    if item_model:
        if isinstance(item_model, fields.Raw):
            items_field = fields.List(item_model, description="数据列表")
        else:
            items_field = fields.List(fields.Nested(item_model), description="数据列表")
    else:
        items_field = fields.List(fields.Raw(), description="数据列表")

    return api.model(
        model_name,
        {
            "items": items_field,
            "total": fields.Integer(description="总数量", example=100),
            "page": fields.Integer(description="当前页码", example=1),
            "size": fields.Integer(description="每页数量", example=20),
        },
    )


def get_pagination_response_model(item_model=None):
    """
    获取分页响应模型（与 R.paginate 返回值结构同步）

    Args:
        item_model: 列表项的模型（可选）

    Returns:
        flask_restx.Model: 分页响应模型
    """
    model_name = f"PaginationResponse_{item_model.name if item_model else 'Generic'}"

    if model_name in _response_models:
        return _response_models[model_name]

    api = get_api()
    if api is None:
        raise RuntimeError("API实例未初始化，请确保在应用启动后调用此函数")

    # 使用 create_pagination_model 创建 data 部分
    pagination_data_model = create_pagination_model(
        item_model, f"_{item_model.name if item_model else 'Generic'}"
    )

    # 完整的分页响应模型
    model = api.model(
        model_name,
        {
            "code": fields.Integer(required=True, description="响应码", example=20000),
            "message": fields.String(
                required=True, description="响应消息", example="成功"
            ),
            "data": fields.Nested(pagination_data_model, description="分页数据"),
            "success": fields.Boolean(
                required=True, description="是否成功", example=True
            ),
        },
    )

    _response_models[model_name] = model
    return model


def get_charts_response_model():
    """
    获取图表响应模型（与 R.charts_data 返回值结构同步）

    Returns:
        flask_restx.Model: 图表响应模型
    """
    if "ChartsResponse" in _response_models:
        return _response_models["ChartsResponse"]

    api = get_api()
    if api is None:
        raise RuntimeError("API实例未初始化，请确保在应用启动后调用此函数")

    # 图表数据结构（与 R.charts_data 中的 data 结构一致）
    charts_data_model = api.model(
        "ChartsData",
        {
            "xAxis": fields.Raw(description="X轴数据"),
            "series": fields.Raw(description="系列数据"),
            "markPoint": fields.Raw(description="标记点数据", allow_null=True),
        },
    )

    model = api.model(
        "ChartsResponse",
        {
            "code": fields.Integer(required=True, description="响应码", example=20000),
            "message": fields.String(
                required=True, description="响应消息", example="操作成功"
            ),
            "data": fields.Nested(charts_data_model, description="图表数据"),
            "success": fields.Boolean(
                required=True, description="是否成功", example=True
            ),
        },
    )

    _response_models["ChartsResponse"] = model
    return model


def create_typed_response_model(data_model, model_name_suffix=""):
    """
    创建带类型的响应模型

    Args:
        data_model: 数据部分的模型
        model_name_suffix: 模型名称后缀

    Returns:
        flask_restx.Model: 带类型的响应模型
    """
    model_name = f"TypedResponse{model_name_suffix}"

    if model_name in _response_models:
        return _response_models[model_name]

    api = get_api()
    if api is None:
        raise RuntimeError("API实例未初始化，请确保在应用启动后调用此函数")

    if isinstance(data_model, fields.Raw):
        data_field = data_model
    else:
        data_field = fields.Nested(data_model, description="响应数据", allow_null=True)

    model = api.model(
        model_name,
        {
            "code": fields.Integer(required=True, description="响应码", example=20000),
            "message": fields.String(
                required=True, description="响应消息", example="成功"
            ),
            "data": data_field,
            "success": fields.Boolean(
                required=True, description="是否成功", example=True
            ),
        },
    )

    _response_models[model_name] = model
    return model


base_response_model = get_base_response_model()
pagination_response_model = get_pagination_response_model()
charts_response_model = get_charts_response_model()
