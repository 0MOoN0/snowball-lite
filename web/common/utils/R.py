import json
from datetime import datetime, date


def ok(code=20000, data=True, msg="成功", **kwargs):
    return {"code": code, "data": data, "message": msg, 'success': True, **kwargs}


def paginate(data={}, total=0, page=0, size=0, msg='成功', **kwargs):
    return ok(data={'items': data, 'total': total, "page": page, "size": size}, msg=msg, **kwargs)


def fail(code=20500, data=False, msg="失败", **kwargs):
    return {"code": code, "data": data, "message": msg, 'success': False, **kwargs}


def charts_data(x_axis, series, mark_point=None, **kwargs):
    data = {'xAxis': x_axis, 'series': series, 'markPoint': mark_point, **kwargs}
    return {"code": 20000, "data": data, "message": '操作成功', 'success': True}


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
