import datetime
import os

import pandas as pd
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from sqlalchemy import and_

from web.common.utils import R
from web.models import db
from web.models.GridRecord import GridRecord
from web.models.IRecord import IRecordSchema, IRecord

irecord_bp = Blueprint("irecord", __name__, url_prefix="/irecord")
irecord_api = Api(irecord_bp)


class IRecordRouter(Resource):

    def get(self, irecord_id=None):
        """
        @@@
        ### doc
        ```
        获取交易记录，返回单条记录或记录列表
        使用方法：
        根据网格ID获取交易记录，URL加上grid_id参数，返回一个list
        根据交易记录ID获取交易记录，URL加上record_id参数，返回单条record数据
        ```
        ### Example
        根据网格ID获取交易记录数据<br/>
        GET : localhost:5000/irecord?page=1&pageSize=10&grid_id=10

        根据记录ID获取交易记录数据<br/>
        GET : irecord/<int: record_id>
        @@@
        """
        if irecord_id is not None:
            irecord = IRecord.query.get(irecord_id)
            return R.ok(data=IRecordSchema().dump(irecord))
        args = request.args.to_dict()
        # 分页查询
        if request.args.get("page") is not None and request.args.get("pageSize") is not None:
            page = args.pop("page")
            page_size = args.pop("pageSize")
            if request.args is not None:
                # 根据网格id查询
                if request.args.get("grid_id") is not None:
                    grid_id = request.args.get("grid_id")
                    page_records = db.session.query(IRecord).join(GridRecord, GridRecord.record_id == IRecord.id) \
                        .filter(GridRecord.grid_id == grid_id).order_by(IRecord.trade_date.desc()) \
                        .paginate(int(page), int(page_size))
                    return R.ok(data={"items": IRecordSchema().dump(page_records.items, many=True),
                                      "total": page_records.total})
                if request.args.get("record_id") is not None:
                    record_id = request.args.get("record_id")
                    irecord = IRecord.query.filter(IRecord.id == record_id).first()
                    return R.ok(data=IRecordSchema().dump(irecord))
        # 不分页
        grids = IRecord.query.filter_by(**args).all()
        return R.ok(data=IRecordSchema().dump(grids, many=True))

    def post(self):
        """
        @@@
        ### doc
        ```
        IRecord文件上传接口，上传格式为CSV，包含date,code,value,share,fee列，不区分种类
        上传的文件记录如果与数据库的记录有重复，则默认使用上传文件的记录
        ```
        ### Example
        #### URL
        POST : `localhost:5000/irecord/`
        #### Body
        `file`
        #### params
        `None`
        @@@
        """
        f = request.files['file']
        save_path = os.path.join(current_app.root_path,
                                 current_app.config["UPLOAD_DIR_IRECORD"],
                                 f.filename)
        # 保存文件
        f.save(save_path)
        # 将文件转为DF
        df = pd.read_csv(save_path, header=0, encoding='utf8')
        df = df.dropna(axis=0, how='all')
        df['date'] = pd.to_datetime(df['date']).dt.date
        # 数据清洗，删除nan行
        # 将date转为string类型.string在dataframe对应object类型
        df['date'] = df['date'].astype('string')
        df['type'] = 1
        df['notice_date'] = str(datetime.datetime.now())
        schema = IRecordSchema()
        for index, row in df.iterrows():
            record_dict = row.to_dict()
            grid_id = record_dict.pop('grid_id')
            record = schema.load(record_dict)
            record_data = IRecord.query.filter(and_(IRecord.code == record.code,
                                                    IRecord.trade_date == record.trade_date,
                                                    IRecord.value.like(record.value))).first()
            if record_data is not None:
                record_data.value = record.value
                record_data.share = record.share
                record_data.fee = record.fee
                record_data.notice_date = record.notice_date
                db.session.add(record_data)
                continue
            db.session.add(record)
            db.session.flush()
            grid_record = GridRecord(grid_id=grid_id, record_id=record.id)
            db.session.add(grid_record)
        db.session.commit()
        return R.ok()

    def put(self):
        """
        @@@
        新增或更新IRecord，根据请求体中是否包含ID字段判断新增或更新操作
        @@@
        """
        irecord_json = request.json
        if irecord_json is None:
            return R.fail(msg='请求体不能为空')
        irecord_schema = IRecordSchema()
        irecord = irecord_schema.load(irecord_json)
        if irecord.id is not None:
            irecord.query.filter(IRecord.id == irecord.id).update(irecord_json)
            # 更新数据
            db.session.commit()
            return R.ok()
        # 新增数据
        db.session.add(irecord)
        db.session.commit()
        return R.ok(data=irecord.id)


irecord_api.add_resource(IRecordRouter, "", "/<int:irecord_id>")
