import io
import time

import pandas as pd
from flask import Blueprint, send_file
from flask_restful import Resource, reqparse, Api
from pandas import DataFrame
from werkzeug.datastructures import FileStorage

from web.common.cons import webcons
from web.common.utils import R
from web.models import db
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record, RecordSchema, RecordExportSchema

grid_record_all_sync_bp = Blueprint("grid_record_all_sync", __name__, url_prefix="/grid_record_all_sync")
grid_record_all_sync_api = Api(grid_record_all_sync_bp)


class GridRecordAllSyncRouters(Resource):
    def post(self):
        """
        @@@
        根据上传的交易记录文件，同步所有网格交易。
        ### 上传文件格式说明
        上传文件的格式为xlsx，文件名称不限，每一个工作簿对应一个网格类型，工作簿名称格式如下：网格名称_网格类型名称

        **列格式如下：**

        | 交易时间 | 交易价格 | 交易份额 | 交易费用 |

        **格式说明：**

        交易时间：格式为符合datetime-like格式，只要是to_datetime()能转换的格式都可以

        交易价格：以元为单位

        交易份额：买入为正数，卖出为负数

        交易费用：以元为单位

        **注意：这个方法只用于更新网格交易记录，上传文件中的所有数据都会被认为是网格的交易记录**

        ### 返回值

        ```
        :return:
        {
            data: 未处理的工作簿名称
            meg:  处理结果
        }
        ```
        @@@
        """
        parse = reqparse.RequestParser()
        parse.add_argument('file', required=True, type=FileStorage, location='files')
        args = parse.parse_args()
        from web.routers.record.record_routers import convert_record_sync_file_to_list
        file = pd.ExcelFile(args.file)
        sheet_names = file.sheet_names
        not_exist_sheet_names = []
        update_counts = 0
        with db.session.no_autoflush as session:
            # 遍历工作簿
            for sheet_name in sheet_names:
                # 判断sheet_name是否符合格式，names[0]为网格名称，names[1]为网格类型名称
                names = sheet_name.split('_')
                if len(names) != 2:
                    continue
                grid_record: DataFrame = file.parse(sheet_name)
                if len(grid_record) == 0:
                    continue
                # 查询数据库中是否有对应的网格名称和网格类型名称
                grid_type_data = session.query(Grid.id.label('grid_id'), GridType.id.label('grid_type_id'),
                                               Grid.asset_id.label(Grid.asset_id.key)) \
                    .join(Grid, Grid.id == GridType.grid_id) \
                    .filter(Grid.grid_name == names[0], GridType.type_name == names[1]) \
                    .first()
                # 工作簿对应的网格类型数据不存在
                if not grid_type_data:
                    not_exist_sheet_names.append(sheet_name)
                    continue
                # 将Excel数据转为List数据
                df: pd.Datetime = pd.read_excel(args.get('file'), sheet_name=sheet_name)
                record_list: list = convert_record_sync_file_to_list(df, grid_type_data)
                # 查询数据库中是否有对应的网格交易记录
                sub_query = session.query(GridTypeRecord.record_id) \
                    .filter(GridTypeRecord.grid_type_id == grid_type_data.grid_type_id) \
                    .subquery()
                Record.query.filter(Record.id.in_(sub_query)).delete(synchronize_session=False)
                # 转换对象
                schema = RecordSchema()
                grid_record_objects = schema.load(record_list, many=True, partial=True)
                # 批量插入交易记录
                session.bulk_save_objects(grid_record_objects, return_defaults=True, update_changed_only=False)
                # 创建网格类型交易记录关联对象
                grid_type_records: list = [GridTypeRecord(record_id=record.id, grid_type_id=grid_type_data.grid_type_id)
                                           for record in grid_record_objects]
                # 批量插入网格类型交易记录关联对象
                session.bulk_save_objects(grid_type_records, return_defaults=True, update_changed_only=False)
                update_counts += len(grid_type_records)
            session.commit()
        return R.ok(data=not_exist_sheet_names, msg='成功同步 %s 条网格交易数据' % update_counts)

    def get(self):
        """
        @@@
        ### 功能说明
        下载网格交易记录数据接口，下载的文件格式与上传的文件格式相同，因此可以用于数据迁移或备份

        **列格式如下：**

        | 交易时间 | 交易价格 | 交易份额 | 交易费用 |

        **格式说明：**

        交易时间：格式为符合datetime-like格式，只要是to_datetime()能转换的格式都可以

        交易价格：以元为单位

        交易份额：买入为正数，卖出为负数

        交易费用：以元为单位

        ### 返回值
        Returns:    网格交易记录数据文件
        @@@
        """
        # 查询所有网格数据
        grid_all: list[Grid] = Grid.query.all()
        # 创建内存中的流
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        for grid in grid_all:
            # 查询该网格下的所有网格类型数据
            grid_type_all: list[GridType] = GridType.query.filter(GridType.grid_id == grid.id).all()
            # 遍历网格类型数据
            for grid_type in grid_type_all:
                # 查询该网格类型下的所有交易记录
                grid_type_records: list = Record.query.join(GridTypeRecord, Record.id == GridTypeRecord.record_id) \
                    .filter(GridTypeRecord.grid_type_id == grid_type.id) \
                    .all()
                if len(grid_type_records) == 0:
                    continue
                record_list: list = RecordExportSchema().dump(grid_type_records, many=True)
                df: DataFrame = pd.DataFrame(record_list)
                # 删除transactions_direction列
                df.drop('transactions_direction', axis=1, inplace=True)
                df.rename(columns={'transactions_fee': '交易费用',
                                   'transactions_share': '交易份额',
                                   'transactions_date': '交易时间', 'transactions_price': '交易价格'}
                          , inplace=True)
                df.to_excel(writer, sheet_name=grid.grid_name + '_' + grid_type.type_name, index=False)
        writer.save()
        output.seek(0)
        return send_file(output, mimetype='application/vnd.ms-excel', as_attachment=True,
                         download_name='网格交易数据' + time.strftime(webcons.DataFormatStr.FORMAT_2, time.localtime()) + '.xlsx')


grid_record_all_sync_api.add_resource(GridRecordAllSyncRouters, '/file')
