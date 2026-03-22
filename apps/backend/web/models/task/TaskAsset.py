from web.models import db


class TaskAsset(db.Model):
    __tablename__ = 'tb_task_asset'
    __bind_key__ = "snowball"

    task_id = db.Column(db.BigInteger, primary_key=True, comment='任务ID')
    asset_id = db.Column(db.BigInteger, primary_key=True, comment='资产ID')
