import pytest
from datetime import datetime
from web.services.record.record_import_service import RecordImportService
from web.services.record.record_dtos import RecordImportDTO, RecordGroupDTO
from web.models import db
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.models.asset.asset import Asset
from web.webtest.test_base import TestBaseWithRollback
from web.web_exception import WebBaseException
from web.common.enum.record_enum import RecordImportModeEnum

class TestRecordImportService(TestBaseWithRollback):
    def test_import_records_success(self):
        """测试正常导入记录"""
        # 1. 准备基础数据
        asset = Asset(asset_name="测试资产", asset_type=1)
        db.session.add(asset)
        db.session.flush()
        
        # 使用 DTO 构造数据
        dt = datetime(2023, 1, 1, 10, 0, 0)
        records_data = [
            RecordImportDTO(
                asset_id=asset.id,
                transactions_date=dt,
                transactions_price=1000,
                transactions_share=100,
                transactions_amount=100000,
                transactions_fee=5,
                transactions_direction=1,
                groups=[
                    RecordGroupDTO(group_type=1, group_id=1001),
                    RecordGroupDTO(group_type=2, group_id=2002)
                ]
            )
        ]
        
        # 2. 执行导入
        count = RecordImportService.import_records(records_data)
        
        # 3. 验证
        assert count == 1
        
        # 验证 Record 是否生成
        db.session.flush() 
        record = db.session.query(Record).filter_by(asset_id=asset.id).first()
        assert record is not None
        assert record.transactions_price == 1000
        assert record.transactions_share == 100
        assert record.transactions_date == dt
        
        # 验证 TradeReference 是否生成
        trade_refs = db.session.query(TradeReference).filter_by(record_id=record.id).all()
        assert len(trade_refs) == 2
        
        # 验证包含两个特定的分组
        group_keys = {(r.group_type, r.group_id) for r in trade_refs}
        assert (1, 1001) in group_keys
        assert (2, 2002) in group_keys

    def test_import_records_invalid_asset(self):
        """测试不存在的资产ID"""
        dt = datetime(2023, 1, 1, 10, 0, 0)
        records_data = [
            RecordImportDTO(
                asset_id=9999999,  # 不存在的ID
                transactions_date=dt,
                transactions_price=1000,
                transactions_share=100,
                transactions_amount=100000,
                transactions_fee=5,
                transactions_direction=1
            )
        ]
        
        with pytest.raises(WebBaseException) as excinfo:
            RecordImportService.import_records(records_data)
        assert "不存在" in str(excinfo.value)

    def test_import_records_modes(self):
        """测试不同导入模式"""
        # 1. 准备数据
        asset = Asset(asset_name="模式测试资产", asset_type=1)
        db.session.add(asset)
        db.session.flush()

        dt1 = datetime(2023, 1, 1, 10, 0, 0)
        dt2 = datetime(2023, 1, 2, 10, 0, 0)
        dt3 = datetime(2023, 1, 3, 10, 0, 0)

        # 插入两条旧数据
        old_record1 = Record(asset_id=asset.id, transactions_date=dt1, transactions_price=100, transactions_share=100, transactions_amount=10000, transactions_fee=0, transactions_direction=1)
        old_record2 = Record(asset_id=asset.id, transactions_date=dt3, transactions_price=300, transactions_share=100, transactions_amount=30000, transactions_fee=0, transactions_direction=1)
        db.session.add_all([old_record1, old_record2])
        db.session.flush()

        # 新数据 (时间为 dt2)
        new_records = [
            RecordImportDTO(
                asset_id=asset.id,
                transactions_date=dt2,
                transactions_price=200,
                transactions_share=200,
                transactions_amount=40000,
                transactions_fee=0,
                transactions_direction=1
            )
        ]

        # 2. 测试 APPEND (默认)
        # 先清除旧数据状态以免混淆，重新插入
        # 这里为了简单，我们使用不同的 asset 或者清除现有记录
        # 我们选择清理并重置
        db.session.query(Record).filter_by(asset_id=asset.id).delete()
        db.session.add_all([
            Record(asset_id=asset.id, transactions_date=dt1, transactions_price=100, transactions_share=100, transactions_amount=10000, transactions_fee=0, transactions_direction=1),
            Record(asset_id=asset.id, transactions_date=dt3, transactions_price=300, transactions_share=100, transactions_amount=30000, transactions_fee=0, transactions_direction=1)
        ])
        db.session.flush()

        RecordImportService.import_records(new_records, import_mode=RecordImportModeEnum.APPEND.value)
        
        all_records = db.session.query(Record).filter_by(asset_id=asset.id).order_by(Record.transactions_date).all()
        assert len(all_records) == 3
        assert all_records[0].transactions_date == dt1
        assert all_records[1].transactions_date == dt2
        assert all_records[2].transactions_date == dt3

        # 3. 测试 OVERWRITE
        # 重置环境
        db.session.query(Record).filter_by(asset_id=asset.id).delete()
        db.session.add_all([
            Record(asset_id=asset.id, transactions_date=dt1, transactions_price=100, transactions_share=100, transactions_amount=10000, transactions_fee=0, transactions_direction=1),
            Record(asset_id=asset.id, transactions_date=dt3, transactions_price=300, transactions_share=100, transactions_amount=30000, transactions_fee=0, transactions_direction=1)
        ])
        db.session.flush()

        RecordImportService.import_records(new_records, import_mode=RecordImportModeEnum.OVERWRITE.value)

        all_records = db.session.query(Record).filter_by(asset_id=asset.id).all()
        assert len(all_records) == 1
        assert all_records[0].transactions_date == dt2

        # 4. 测试 REPLACE (按时间范围)
        # 重置环境
        db.session.query(Record).filter_by(asset_id=asset.id).delete()
        db.session.add_all([
            Record(asset_id=asset.id, transactions_date=dt1, transactions_price=100, transactions_share=100, transactions_amount=10000, transactions_fee=0, transactions_direction=1),
            # dt2 是我们要插入的时间
            Record(asset_id=asset.id, transactions_date=dt2, transactions_price=250, transactions_share=250, transactions_amount=62500, transactions_fee=0, transactions_direction=1), # 这个应该被替换
            Record(asset_id=asset.id, transactions_date=dt3, transactions_price=300, transactions_share=100, transactions_amount=30000, transactions_fee=0, transactions_direction=1)
        ])
        db.session.flush()

        # new_records 只有一个记录，时间是 dt2
        # REPLACE 模式应该删除所有在 new_records 时间范围内的数据
        # new_records 范围是 [dt2, dt2]
        # 所以旧的 dt2 记录应该被删除，dt1 和 dt3 应该保留
        
        RecordImportService.import_records(new_records, import_mode=RecordImportModeEnum.REPLACE.value)
        
        all_records = db.session.query(Record).filter_by(asset_id=asset.id).order_by(Record.transactions_date).all()
        assert len(all_records) == 3
        # 验证结果
        dates = [r.transactions_date for r in all_records]
        assert dt1 in dates
        assert dt3 in dates
        # dt2 存在，且是我们新插入的那个 (price=200)
        record_dt2 = [r for r in all_records if r.transactions_date == dt2][0]
        assert record_dt2.transactions_price == 200 # 新数据的价格

    def test_import_records_replace_range(self):
        """测试 REPLACE_RANGE 模式"""
        # 1. 准备数据
        asset = Asset(asset_name="范围替换测试资产", asset_type=1)
        db.session.add(asset)
        db.session.flush()

        dt1 = datetime(2023, 1, 1, 10, 0, 0)
        dt2 = datetime(2023, 1, 2, 10, 0, 0)
        dt3 = datetime(2023, 1, 3, 10, 0, 0)
        dt4 = datetime(2023, 1, 4, 10, 0, 0)

        # 插入旧数据: dt1, dt2, dt3
        db.session.add_all([
            Record(asset_id=asset.id, transactions_date=dt1, transactions_price=100, transactions_share=100, transactions_amount=10000, transactions_fee=0, transactions_direction=1),
            Record(asset_id=asset.id, transactions_date=dt2, transactions_price=200, transactions_share=100, transactions_amount=20000, transactions_fee=0, transactions_direction=1),
            Record(asset_id=asset.id, transactions_date=dt3, transactions_price=300, transactions_share=100, transactions_amount=30000, transactions_fee=0, transactions_direction=1)
        ])
        db.session.flush()

        # 新数据: dt4 (在 dt3 之后)
        new_records = [
            RecordImportDTO(
                asset_id=asset.id,
                transactions_date=dt4,
                transactions_price=400,
                transactions_share=100,
                transactions_amount=40000,
                transactions_fee=0,
                transactions_direction=1
            )
        ]

        # 2. 测试范围替换 [dt2, dt3]
        # 预期：dt2, dt3 被删除，插入 dt4。结果应为 dt1, dt4
        range_start = dt2
        range_end = dt3
        
        RecordImportService.import_records(
            new_records, 
            import_mode=RecordImportModeEnum.REPLACE_RANGE.value,
            range_start=range_start,
            range_end=range_end
        )

        all_records = db.session.query(Record).filter_by(asset_id=asset.id).order_by(Record.transactions_date).all()
        assert len(all_records) == 2
        dates = [r.transactions_date for r in all_records]
        assert dt1 in dates
        assert dt4 in dates
        assert dt2 not in dates
        assert dt3 not in dates

    def test_import_records_replace_range_invalid_args(self):
        """测试 REPLACE_RANGE 模式缺参数"""
        asset = Asset(asset_name="参数测试资产", asset_type=1)
        db.session.add(asset)
        db.session.flush()
        
        new_records = [
            RecordImportDTO(
                asset_id=asset.id,
                transactions_date=datetime.now(),
                transactions_price=100,
                transactions_share=100,
                transactions_amount=10000,
                transactions_fee=0,
                transactions_direction=1
            )
        ]

        with pytest.raises(WebBaseException) as excinfo:
            RecordImportService.import_records(
                new_records,
                import_mode=RecordImportModeEnum.REPLACE_RANGE.value,
                # 缺少 range_start/end
            )
        assert "必须指定开始时间和结束时间" in str(excinfo.value)
