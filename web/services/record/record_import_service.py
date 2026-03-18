from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional, TYPE_CHECKING

from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.common.cons import webcons
from web.weblogger import logger
from web.web_exception import WebBaseException
from web.common.enum.record_enum import RecordDirectionEnum, RecordImportModeEnum
if TYPE_CHECKING:
    from web.services.record.record_dtos import RecordImportDTO


class RecordImportService:
    REQUIRED_COLUMNS = {
        "成交日期",
        "成交时间",
        "证券代码",
        "证券名称",
        "委托类别",
        "成交价格",
        "成交数量",
        "发生金额",
        "佣金",
        "成交编号",
    }

    @classmethod
    def parse_and_preview(
        cls, file_stream, provider_code: Optional[str] = None
    ) -> List[Dict]:
        """
        解析上传的文件并生成预览数据
        :param file_stream: 文件流
        :param provider_code: 数据提供商代码 (可选，用于辅助匹配)
        :return: 预览数据列表
        """
        try:
            # 根据文件名后缀决定读取方式
            filename = getattr(file_stream, "filename", "").lower()
            if filename.endswith(".csv"):
                # 尝试读取 CSV
                try:
                    df = pd.read_csv(file_stream, encoding="utf-8")
                except UnicodeDecodeError:
                    # 如果 utf-8 失败，尝试 gbk
                    file_stream.seek(0)
                    df = pd.read_csv(file_stream, encoding="gbk")
            else:
                # 默认尝试读取 Excel
                df = pd.read_excel(file_stream)
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            raise WebBaseException("文件格式错误或无法读取")

        # 1. 检查必要列
        columns = set(df.columns)

        # 0. 预处理：清洗空行
        # 去除全空的行
        df.dropna(how="all", inplace=True)
        # 去除关键字段为空的行 (证券代码是必须的，否则无法匹配)
        if "证券代码" in columns:
            df.dropna(subset=["证券代码"], inplace=True)

        # 1. 检查必要列

        missing_cols = []
        for req_col in cls.REQUIRED_COLUMNS:
            if req_col not in columns:
                missing_cols.append(req_col)

        if missing_cols:
            raise WebBaseException(f"缺少必要列: {', '.join(missing_cols)}")

        preview_list = []

        # 0. 准备基础数据
        # 加载所有资产和别名
        # TODO: 这里如果数据量很大可能会有性能问题，建议加缓存或优化
        assets = db.session.query(Asset).all()

        # 如果指定了 provider_code，优先匹配该 provider 下的别名
        alias_query = db.session.query(AssetAlias).filter(AssetAlias.status == 1)
        if provider_code:
            alias_query = alias_query.filter(AssetAlias.provider_code == provider_code)
        aliases = alias_query.all()

        # 另外加载一份全局别名作为兜底（如果 provider_code 匹配失败）
        all_aliases = db.session.query(AssetAlias).filter(AssetAlias.status == 1).all()

        asset_map = {a.asset_name: a.id for a in assets}  # name -> id

        # symbol -> id (基于特定 provider)
        alias_map = {a.provider_symbol: a.asset_id for a in aliases}

        # symbol -> id (全局兜底)
        global_alias_map = {a.provider_symbol: a.asset_id for a in all_aliases}

        for index, row in df.iterrows():
            item = {
                "row_index": index,
                "raw_data": {
                    k: str(v) if pd.notna(v) else "" for k, v in row.to_dict().items()
                },
                "status": "valid",
                "message": "匹配成功",
                "parsed_data": {},
            }

            try:
                # 2. 匹配资产 (优先使用 证券代码)
                symbol_val = (
                    str(row["证券代码"]).strip() if pd.notna(row["证券代码"]) else ""
                )
                if symbol_val.endswith(".0"):
                    symbol_val = symbol_val[:-2]

                name_val = (
                    str(row["证券名称"]).strip() if pd.notna(row["证券名称"]) else ""
                )

                asset_id = None
                match_source = None

                # 策略1: 精确匹配 Provider 下的 Symbol
                if symbol_val and symbol_val in alias_map:
                    asset_id = alias_map[symbol_val]
                    match_source = "provider_symbol"

                # 策略2: 全局匹配 Symbol
                if not asset_id and symbol_val and symbol_val in global_alias_map:
                    asset_id = global_alias_map[symbol_val]
                    match_source = "global_symbol"

                # 策略3: 匹配资产名称
                if not asset_id and name_val and name_val in asset_map:
                    asset_id = asset_map[name_val]
                    match_source = "asset_name"

                if not asset_id:
                    item["status"] = "error"
                    item["message"] = f"未找到匹配的资产: {symbol_val} / {name_val}"
                else:
                    item["parsed_data"]["asset_id"] = asset_id
                    item["parsed_data"]["asset_name"] = name_val
                    item["parsed_data"]["match_source"] = match_source

                # 3. 解析数值和日期
                # 交易时间 = 成交日期 + 成交时间
                try:
                    date_str = str(row["成交日期"])  # e.g. 20230101 or 2023-01-01
                    if date_str.endswith(".0"):
                        date_str = date_str[:-2]

                    time_str = str(row["成交时间"])  # e.g. 14:00:00 or 140000

                    # 简单清洗
                    date_str = date_str.replace("-", "").replace("/", "")
                    time_str = time_str.replace(":", "")

                    # 补全时间格式 (假设 HHmmss)
                    if len(time_str) < 6:
                        time_str = time_str.zfill(6)

                    full_time_str = f"{date_str} {time_str}"
                    # 尝试解析 YYYYMMDD HHmmss
                    try:
                        date_obj = (
                            datetime.strptime(full_time_str, "%Y%m%d %H%M%S")
                            if len(date_str) == 8
                            else pd.to_datetime(f"{row['成交日期']} {row['成交时间']}")
                        )
                    except ValueError:
                        date_obj = pd.to_datetime(
                            f"{row['成交日期']} {row['成交时间']}"
                        )

                    # 使用 pandas 解析更稳健
                    if not isinstance(date_obj, datetime):
                        date_obj = pd.to_datetime(
                            f"{row['成交日期']} {row['成交时间']}"
                        )

                    item["parsed_data"]["transactions_date"] = date_obj.strftime(
                        webcons.DataFormatStr.Y_m_d_H_M_S
                    )
                except Exception:
                    # Fallback: 尝试直接解析
                    try:
                        date_obj = pd.to_datetime(
                            f"{row['成交日期']} {row['成交时间']}"
                        )
                        item["parsed_data"]["transactions_date"] = date_obj.strftime(
                            webcons.DataFormatStr.Y_m_d_H_M_S
                        )
                    except Exception:
                        item["status"] = "error"
                        item["message"] = "交易时间格式错误"

                # 交易方向 (委托类别)
                cls._parse_direction(row, item)

                # 份额 (成交数量)
                try:
                    share = abs(float(row["成交数量"]))
                    item["parsed_data"]["transactions_share"] = int(share)
                except Exception:
                    item["status"] = "error"
                    item["message"] = "成交数量格式错误"

                # 价格 (成交价格)
                cls._parse_price(row, item, asset_id)

                # 费用 (佣金)
                try:
                    fee = float(row["佣金"]) if pd.notna(row["佣金"]) else 0
                    item["parsed_data"]["transactions_fee"] = int(fee * 1000)
                except Exception:
                    item["status"] = "error"
                    item["message"] = "佣金格式错误"

                # 计算总金额 (发生金额) -> 也可以直接用发生金额，但为了保持一致性建议重新计算或校验
                # 这里优先使用文件中的发生金额
                try:
                    amount = float(row["发生金额"])
                    item["parsed_data"]["transactions_amount"] = int(abs(amount) * 1000)
                except Exception:
                    # Fallback to calc
                    if item["status"] != "error":
                        item["parsed_data"]["transactions_amount"] = (
                            item["parsed_data"]["transactions_price"]
                            * item["parsed_data"]["transactions_share"]
                        )

            except Exception as e:
                item["status"] = "error"
                item["message"] = f"解析异常: {str(e)}"

            preview_list.append(item)

        return preview_list

    @classmethod
    def import_records(cls, records_data: List["RecordImportDTO"], import_mode: int = 0, range_start: Optional[datetime] = None, range_end: Optional[datetime] = None) -> int:
        """
        批量导入确认后的记录

        :param records_data: 前端确认后的数据列表 (RecordImportDTO 对象列表)
        :param import_mode: 导入模式, 对应 web.common.enum.webEnum.RecordImportModeEnum
            - 0 (APPEND): 增量模式 (默认). 直接追加新记录, 不删除任何旧数据.
            - 1 (OVERWRITE): 全量覆盖模式. 删除导入数据中涉及的所有资产的全部旧记录, 然后插入新记录.
            - 2 (REPLACE): 部分替换模式. 删除导入数据中涉及资产在导入时间范围内的旧记录, 然后插入新记录.
            - 3 (REPLACE_RANGE): 范围替换模式. 删除导入数据中涉及资产在指定时间范围[range_start, range_end]内的旧记录, 然后插入新记录.
        :param range_start: 若 import_mode=3, 必填. 替换范围开始时间.
        :param range_end: 若 import_mode=3, 必填. 替换范围结束时间.
        :return: 成功导入条数
        """
        if not records_data:
            return 0

        success_count = 0
        try:
            record_objects = []

            # 预处理：资产ID校验
            asset_ids = {r.asset_id for r in records_data}
            existing_assets = (
                db.session.query(Asset.id).filter(Asset.id.in_(asset_ids)).all()
            )
            existing_asset_ids = {a.id for a in existing_assets}

            # 根据导入模式处理旧数据
            if import_mode == RecordImportModeEnum.OVERWRITE.value:
                # 全量覆盖：删除涉及资产的所有记录
                db.session.query(Record).filter(Record.asset_id.in_(asset_ids)).delete(synchronize_session=False)

            elif import_mode == RecordImportModeEnum.REPLACE.value:
                # 部分替换：按资产和时间范围删除
                # 计算每个资产的时间范围
                asset_time_ranges = {}
                for r in records_data:
                    if r.asset_id not in asset_time_ranges:
                        asset_time_ranges[r.asset_id] = {'min': r.transactions_date, 'max': r.transactions_date}
                    else:
                        if r.transactions_date < asset_time_ranges[r.asset_id]['min']:
                            asset_time_ranges[r.asset_id]['min'] = r.transactions_date
                        if r.transactions_date > asset_time_ranges[r.asset_id]['max']:
                            asset_time_ranges[r.asset_id]['max'] = r.transactions_date

                # 对每个资产执行范围删除
                for asset_id, time_range in asset_time_ranges.items():
                    db.session.query(Record).filter(
                        Record.asset_id == asset_id,
                        Record.transactions_date >= time_range['min'],
                        Record.transactions_date <= time_range['max']
                    ).delete(synchronize_session=False)

            elif import_mode == RecordImportModeEnum.REPLACE_RANGE.value:
                # 范围替换：按指定时间范围删除
                if not range_start or not range_end:
                    raise WebBaseException("使用范围替换模式时, 必须指定开始时间和结束时间")

                # 删除涉及资产在范围内的记录
                db.session.query(Record).filter(
                    Record.asset_id.in_(asset_ids),
                    Record.transactions_date >= range_start,
                    Record.transactions_date <= range_end
                ).delete(synchronize_session=False)

            for item in records_data:
                asset_id = item.asset_id
                if asset_id not in existing_asset_ids:
                    raise WebBaseException(f"资产ID {asset_id} 不存在")

                record = Record(
                    asset_id=asset_id,
                    transactions_date=item.transactions_date,
                    transactions_price=item.transactions_price,
                    transactions_share=item.transactions_share,
                    transactions_amount=item.transactions_amount,
                    transactions_fee=item.transactions_fee,
                    transactions_direction=item.transactions_direction,
                )
                record_objects.append(record)

            # 由于需要获取ID来建立关联，我们逐个添加或先添加Record再添加Reference
            # 为了性能，如果数据量大应该优化，但这里为了逻辑清晰：

            for idx, record in enumerate(record_objects):
                db.session.add(record)
                db.session.flush()  # 获取ID

                item = records_data[idx]
                if item.groups:
                    for group in item.groups:
                        trade_ref = TradeReference(
                            record_id=record.id,
                            group_type=group.group_type,
                            group_id=group.group_id
                        )
                        db.session.add(trade_ref)

            success_count = len(record_objects)

        except Exception as e:
            logger.error(f"批量导入失败: {e}")
            raise e

        return success_count

    @classmethod
    def _parse_direction(cls, row, item):
        """
        解析交易方向
        """
        try:
            direction_str = str(row["委托类别"])
            # 默认
            direction = RecordDirectionEnum.BUY.value

            # 结合成交编号判断
            deal_no = str(row.get("成交编号", ""))

            # 1. 基金申购无效判断
            if (
                "申购" in direction_str or "认购" in direction_str
            ) and "无效" in deal_no:
                item["status"] = "error"
                item["message"] = f"申购/认购无效，成交编号: {deal_no}"
                # 仍需设置一个方向以免后续逻辑报错，但status已置为error
                direction = RecordDirectionEnum.BUY.value

            # 2. 转托管方向判断
            elif "托管" in direction_str or "转" in direction_str:
                # 优先检查成交编号中的转入/转出
                # 即使有空格等字符，只要包含关键字即可
                deal_no_clean = deal_no.replace(" ", "")
                direction_str_clean = direction_str.replace(" ", "")

                if "转入" in deal_no_clean or "入" in direction_str_clean:
                    direction = RecordDirectionEnum.TRANSFER_IN.value
                    item["message"] = "转托管入，视为虚拟买入"
                elif "转出" in deal_no_clean or "出" in direction_str_clean:
                    direction = RecordDirectionEnum.TRANSFER_OUT.value
                    item["message"] = "转托管出，视为虚拟卖出"
                else:
                    # 无法从委托类别和成交编号明确判断方向
                    direction = RecordDirectionEnum.TRANSFER_IN.value

            # 3. 基金申购/认购判断
            elif "申购" in direction_str or "认购" in direction_str:
                direction = RecordDirectionEnum.SUBSCRIPTION.value

            # 4. 基金赎回判断
            elif "赎回" in direction_str:
                direction = RecordDirectionEnum.REDEMPTION.value

            # 5. 普通买卖判断
            elif "买" in direction_str or "Buy" in direction_str:
                direction = RecordDirectionEnum.BUY.value
            elif "卖" in direction_str or "Sell" in direction_str:
                direction = RecordDirectionEnum.SELL.value
            else:
                # 默认或无法识别
                direction = RecordDirectionEnum.BUY.value
                item["message"] += f"; 无法识别交易方向: {direction_str}，默认为买入"

            item["parsed_data"]["transactions_direction"] = direction
        except Exception:
            item["status"] = "error"
            item["message"] = "交易方向格式错误"

    @classmethod
    def _parse_price(cls, row, item, asset_id):
        """
        解析并处理价格
        注意：此处只解析文件中的价格，不进行外部数据的补全（如转托管净值），以保证预览接口的响应速度。
        """
        try:
            price_val = float(row["成交价格"])
            item["parsed_data"]["transactions_price"] = int(price_val * 1000)
        except Exception:
            item["status"] = "error"
            item["message"] = "成交价格格式错误"
