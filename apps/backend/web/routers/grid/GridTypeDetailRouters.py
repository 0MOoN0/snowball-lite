import io
import logging
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
from web.models.grid.GridTypeDetail import GridTypeDetail, GridTypeDetailVOSchema, GridTypeDetailDomainSchema, \
    GridTypeDetailExportSchema

grid_type_detail_list_bp = Blueprint("grid_type_detail_list", __name__, url_prefix="/grid_type_detail_list")
grid_type_detail_api = Api(grid_type_detail_list_bp)
grid_type_detail_current_bp = Blueprint('grid_type_detail_current', __name__, url_prefix="/grid_type_detail")
grid_type_detail_current_api = Api(grid_type_detail_current_bp)
grid_type_detail_file_bp = Blueprint('grid_type_detail_file', __name__, url_prefix="/grid_type_detail_list/file")
grid_type_detail_file_api = Api(grid_type_detail_file_bp)
grid_type_detail_file_sync_bp = Blueprint('grid_type_detail_file_sync', __name__,
                                          url_prefix="/grid_type_detail_file_sync/file")
grid_type_detail_file_sync_api = Api(grid_type_detail_file_sync_bp)


class GridTypeDetailCurrentRouters(Resource):
    """
    更新网格类型详情当前数据
    """

    def put(self, grid_type_detail_id: int):
        """
        根据网格类型ID更新网格类型详情数据，将is_current设置为true
        Returns:

        """
        grid_type_detail: GridTypeDetail = GridTypeDetail.query.filter(GridTypeDetail.id == grid_type_detail_id).first()
        if grid_type_detail is None:
            logging.error('更新网格类型详情当前数据错误，网格类型详情数据 id : %s 不存在' % grid_type_detail_id)
            return R.fail(msg='数据不存在，请检查')
        GridTypeDetail.query.filter(GridTypeDetail.grid_type_id == grid_type_detail.grid_type_id) \
            .update({GridTypeDetail.is_current: False})
        GridTypeDetail.query.filter(GridTypeDetail.id == grid_type_detail_id).update({GridTypeDetail.is_current: True})
        db.session.commit()
        return R.ok(msg='更新成功')


class GridTypeDetailListRouters(Resource):
    """
    列表操作路由：/grid_type_detail_list
    """

    def get(self):
        """
        获取网格详情列表

        Returns:

        """
        parse = reqparse.RequestParser()
        parse.add_argument('gridTypeId', dest='grid_type_id', type=int, required=True, location='args')
        params = parse.parse_args().copy()
        grid_type_details = GridTypeDetail.query.filter_by(**params).order_by(GridTypeDetail.gear.desc()).all()
        return R.ok(data=GridTypeDetailVOSchema().dump(grid_type_details, many=True))

    def post(self):
        """
        批量新增或更新网格类型详情
        Returns:

        """
        parse = reqparse.RequestParser()
        parse.add_argument('gridTypeDetailList', dest='grid_type_detail_list', required=True,
                           type=list, location='json')
        data = parse.parse_args().copy().get('grid_type_detail_list')
        grid_type_detail_list = GridTypeDetailVOSchema().load(data, many=True, unknown="EXCLUDE")
        save_list = [grid_type_detail for grid_type_detail in grid_type_detail_list if grid_type_detail.id is None]
        update_list = [grid_type_detail for grid_type_detail in grid_type_detail_list if
                       grid_type_detail.id is not None]
        with db.session.no_autoflush as session:
            if len(save_list) > 0:
                session.execute(GridTypeDetail.__table__.insert(),
                                GridTypeDetailDomainSchema().dump(save_list, many=True),
                                bind=db.engines['snowball'])
            if len(update_list) > 0:
                session.bulk_update_mappings(GridTypeDetail, GridTypeDetailDomainSchema().dump(update_list, many=True))
        session.commit()
        return R.ok(msg='操作成功')

    def delete(selfs):
        """
        删除网格类型详情数据

        参数：
        {
            "ids":[id] (要删除的ID列表，not null)
        }
        Returns:

        """
        parse = reqparse.RequestParser()
        parse.add_argument('ids', dest='ids', required=True, type=list, location='json')
        ids = parse.parse_args().copy().get('ids')
        GridTypeDetail.query.filter(GridTypeDetail.id.in_(ids)).delete()
        db.session.commit()
        return R.ok(msg='删除成功')

    def put(self):
        """
        批量更新网格数据，目前支持从上传的CSV中获取
        参数：
        {
            grid_type_id:网格类型
            grid_id：网格ID
        }
        Returns:

        """
        # parse = reqparse.RequestParser()
        # parse.add_argument('gridTypeDetailList', dest='grid_type_detail_list', type=FileStorage, location='files')
        # parse.add_argument('sheetName', dest='sheet_name', type=str)
        # parse.add_argument('gridTypeId', required=True, type=int)
        # parse.add_argument('gridId', required=True, typ=int)
        # args = parse.parse_args()
        # type_detail_args = GridTypeDetailSchema.load(args, unknown='EXCLUDE')
        # if args.get('grid_type_detail_list') is None:
        #     return R.fail(msg='无法解析的请求，数据不足，需要上传数据文件')
        # df: pd.DataFrame = pd.read_csv(args.get('grid_type_detail_list'), header=0, encoding='utf8')
        return R.fail(msg='未实现该功能')


class GridTypeDetailListFileRouters(Resource):
    """
    网格类型详情文件路由
    """

    def post(self):
        """
        @@@

        ### 功能说明
        根据网格类型ID和文件更新单个网格类型详情数据，如果该网格类型的详情数据已经存在，则会删除旧数据并使用上传文件的数据替代。

        列名需要包含：

        |档位|买入触发价|买入价|买入金额|入股数|卖出触发价|卖出价|出股数|实际出股数|卖出金额|收益|留股收益|留存股数|是否当前档位（可选）|

        如果上传文件中的列名包含'是否当前档位'列，则会根据数据选定是否为当前档位，如果不包含该列，则不会处理该字段，而是使用默认值。
        需要用户手动确认网格的当前档位

        **上传参数：**
        ```json
        data: {
                gridTypeId (int): 网格类型ID,
                sheetName (str): 工作表名
              }
        ```
        ### 返回值
        Returns:
            返回操作结果
        @@@
        """
        parse = reqparse.RequestParser()
        parse.add_argument('gridTypeId', dest='grid_type_id', required=True, type=int, location='form')
        parse.add_argument('sheetName', dest='sheet_name', required=False, type=str, location='form')
        parse.add_argument('file', required=True, type=FileStorage, location='files')
        args = parse.parse_args()
        grid_type_id = args.get('grid_type_id')
        sheet_name = args.get('sheet_name')
        # 查询网格信息是否存在
        grid_info = db.session.query(Grid.grid_name, Grid.id.label('grid_id'), GridType.id.label('grid_type_id'),
                                     GridType.type_name) \
            .join(GridType, GridType.grid_id == Grid.id, isouter=True) \
            .filter(GridType.id == grid_type_id) \
            .first()
        if grid_info is None:
            return R.fail(msg='网格类型ID ：%s 对应的网格数据不存在， 请刷新后重试' % grid_type_id)
        # 如果没有指定工作表名称，则使用网格名称+网格类型名称作为工作表名称
        if sheet_name is None or len(sheet_name) == 0:
            sheet_name = grid_info.grid_name + '_' + grid_info.type_name
        # 读取文件
        df: pd.Datetime = pd.read_excel(args.get('file'), sheet_name=sheet_name)
        column_set = {'档位', '买入触发价', '买入价', '买入金额', '入股数', '卖出触发价', '卖出价', '出股数',
                      '实际出股数', '卖出金额', '收益', '留股收益'}
        if not column_set.issubset(set(df.columns)):
            return R.fail(msg='文件格式不正确，缺少必要的列')
        records = convert_grid_sync_file_to_list(df, grid_info)
        # 清空旧数据
        del_res = GridTypeDetail.query.filter(GridTypeDetail.grid_type_id == grid_type_id).delete()
        # 保存数据
        save_res = db.session.execute(GridTypeDetail.__table__.insert(), records,
                                      bind=db.engines['snowball'])
        db.session.commit()
        return R.ok(
            msg='网格 %s - %s 操作成功， 删除 %d 条数据， 新增 %d 条数据' % (
                grid_info.grid_name, grid_info.type_name, del_res, save_res.rowcount))


def convert_grid_sync_file_to_list(grid_type_detail_df, grid_info):
    # 脚本位置：pandas_api_test - 读取网格类型详情信息并转换成对象
    grid_type_detail_df[['档位']] = grid_type_detail_df[['档位']].astype('str')
    # 转换成int类型
    grid_type_detail_df[
        ['买入触发价', '买入价', '买入金额', '卖出触发价', '卖出价', '卖出金额', '留股收益', '收益']] *= 10000
    grid_type_detail_df[
        ['买入触发价', '买入价', '买入金额', '卖出触发价', '卖出价', '卖出金额', '留股收益', '留存股数', '收益']] \
        = grid_type_detail_df[
        ['买入触发价', '买入价', '买入金额', '卖出触发价', '卖出价', '卖出金额', '留股收益', '留存股数',
         '收益']].astype('int64')
    columns = {'档位': 'gear',
               '买入触发价': 'trigger_purchase_price',
               '买入价': 'purchase_price',
               '买入金额': 'purchase_amount',
               '入股数': 'purchase_shares',
               '卖出触发价': 'trigger_sell_price',
               '卖出价': 'sell_price',
               '出股数': 'sell_shares',
               '实际出股数': 'actual_sell_shares',
               '卖出金额': 'sell_amount',
               '收益': 'profit',
               '留股收益': 'save_share_profit',
               '留存股数': 'save_share'}
    # 处理'是否当前档位'字段
    if '是否当前档位' in grid_type_detail_df.columns:
        # 将该列的'是'替换为1，'否'替换为0
        grid_type_detail_df['是否当前档位'] = grid_type_detail_df['是否当前档位'].replace('是', 1)
        grid_type_detail_df['是否当前档位'] = grid_type_detail_df['是否当前档位'].replace('否', 0)
        columns.update({'是否当前档位': 'is_current'})
    # 修改列名
    grid_type_detail_df.rename(columns=columns, inplace=True)
    grid_type_detail_df[['grid_type_id']] = grid_info.grid_type_id
    grid_type_detail_df[['grid_id']] = grid_info.grid_id
    records = grid_type_detail_df.to_dict('records')
    return records


class GridTypeDetailListFileSyncAllRouters(Resource):
    """
    网格类型详情文件同步接口
    """

    def post(self):
        """
        @@@
        ### 功能说明
        根据上传文件中的网格名称和网格类型名称更新网格类型数据，如果该网格类型的详情数据已经存在，则会删除旧数据并使用上传文件的数据替代。
        ### 文件格式说明
        **工作簿格式**
        上传文件格式为Excel，工作簿的格式为：网格名称_网格类型名称，包含以下列：

        |档位|买入触发价|买入价|买入金额|入股数|卖出触发价|卖出价|出股数|实际出股数|卖出金额|收益|留股收益|留存股数|是否为当前档位（可选）|

        如果上传文件中的列名包含'是否当前档位'列，则会根据数据选定是否为当前档位，如果不包含该列，则不会处理该字段，而是使用默认值。
        需要用户手动确认网格的当前档位

        **注：如果工作薄对应的网格类型数据不存在，则将跳过该工作簿的数据**

        **上传数据：**

            file：要进行同步的文件
        ### 返回值说明
        Returns:
            返回操作结果
        @@@
        """
        parse = reqparse.RequestParser()
        parse.add_argument('file', required=True, type=FileStorage, location='files')
        args = parse.parse_args()
        file = pd.ExcelFile(args.file)
        sheet_names = file.sheet_names
        not_exist_sheet_names = []
        grid_type_detail_list = []
        with db.session.no_autoflush as session:
            # 遍历工作簿
            for sheet_name in sheet_names:
                # 判断sheet_name是否符合格式，names[0]为网格名称，names[1]为网格类型名称
                names = sheet_name.split('_')
                if len(names) != 2:
                    continue
                grid_type_detail: DataFrame = file.parse(sheet_name)
                if len(grid_type_detail) == 0:
                    continue
                # 查询数据库中是否有对应的网格名称和网格类型名称
                grid_type_data = session.query(Grid.id.label('grid_id'), GridType.id.label('grid_type_id')) \
                    .join(Grid, Grid.id == GridType.grid_id) \
                    .filter(Grid.grid_name == names[0], GridType.type_name == names[1]) \
                    .first()
                # 工作簿对应的网格类型数据不存在
                if not grid_type_data:
                    not_exist_sheet_names.append(sheet_name)
                    continue
                # 如果数据存在，则先删除旧数据，然后添加新数据
                detail_list: list = convert_grid_sync_file_to_list(grid_type_detail, grid_type_data)
                grid_type_detail_list.extend(detail_list)
                # 删除旧数据
                # 清空旧数据
                GridTypeDetail.query.filter(GridTypeDetail.grid_type_id == grid_type_data.grid_type_id).delete()
            # 批量插入新数据
            save_res = session.execute(GridTypeDetail.__table__.insert(), grid_type_detail_list,
                                       bind=db.engines['snowball'])
            session.commit()
            # db.session.rollback()
        return R.ok(data=not_exist_sheet_names, msg='成功更新 %s 条数据' % save_res.rowcount)

    def get(self):
        """
        @@@
        ### 功能说明
        下载/导出网格数据，下载的网格数据可以直接用于上传同步接口，用于数据备份或同步。

        ### 返回值说明

        Returns:
            file: 下载文件内容
        @@@
        """
        # 查询所有网格数据
        grid_all: list[Grid] = Grid.query.all()
        # 创建内存中的流
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        # 遍历所有网格数据
        for grid in grid_all:
            # 查询该网格下的所有网格类型数据
            grid_type_all: list[GridType] = GridType.query.filter(GridType.grid_id == grid.id).all()
            # 遍历网格类型数据
            for grid_type in grid_type_all:
                # 查询网格类型的详情数据
                grid_type_details = (GridTypeDetail.query.filter(GridTypeDetail.grid_type_id == grid_type.id)
                                     .order_by(GridTypeDetail.gear.desc())
                                     .all())
                if len(grid_type_details) == 0:
                    continue
                grid_type_detail_dict_list = GridTypeDetailExportSchema().dump(grid_type_details, many=True)
                df: pd.DataFrame = pd.DataFrame(grid_type_detail_dict_list)
                df.rename(columns=GridTypeDetailExportSchema.field_data_keys, inplace=True)
                df.to_excel(writer, sheet_name=grid.grid_name + '_' + grid_type.type_name, index=False)
        writer.save()
        output.seek(0)
        return send_file(output, mimetype='application/vnd.ms-excel', as_attachment=True,
                         download_name='网格数据' + time.strftime(webcons.DataFormatStr.FORMAT_2,
                                                                      time.localtime()) + '.xlsx')


grid_type_detail_api.add_resource(GridTypeDetailListRouters, "")
grid_type_detail_current_api.add_resource(GridTypeDetailCurrentRouters, "/is_current/<int:grid_type_detail_id>")
grid_type_detail_file_api.add_resource(GridTypeDetailListFileRouters, "")
grid_type_detail_file_sync_api.add_resource(GridTypeDetailListFileSyncAllRouters, "")
