from web.common.enum import webEnum
from web.models import db
from web.models.GridRecord import GridRecord
from web.models.IRecord import IRecord


class IRecordService:
    def get_irecord(self, grid_id=None, page=None, page_size=None, order_by_date=None):
        """
        根据网格ID获取交易记录
        :param grid_id: 网格ID
        :param page:  页号
        :param page_size: 每页大小
        :param order_by_date:  日期排序方式
        :return:  网格的交易记录
        """
        query = db.session.query(IRecord).join(GridRecord, GridRecord.record_id == IRecord.id) \
            .filter(GridRecord.grid_id == grid_id)
        # 判断是否排序
        if order_by_date is not None and order_by_date == webEnum.OrderTypeEnum.DESC:
            query = query.order_by(IRecord.trade_date.desc())
        else:
            query = query.order_by(IRecord.trade_date.asc())
        # 分页查询
        if page is not None and page_size is not None:
            # 分页查询
            return query.paginate(int(page), int(page_size))
        # 不分页查询
        return query.all()





irecord_service = IRecordService()
