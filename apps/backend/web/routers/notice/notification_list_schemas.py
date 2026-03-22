from flask_marshmallow import Schema
from marshmallow import fields, EXCLUDE, validate
from web.common.enum.NotificationEnum import NotificationBusinessTypeEnum


class NotificationListQueryArgsSchema(Schema):
    page = fields.Integer(
        required=True,
        data_key="page",
        validate=validate.Range(min=1, error="page必须>=1"),
        error_messages={"required": "page不能为空", "invalid": "page必须为整数"},
    )
    page_size = fields.Integer(
        required=True,
        data_key="pageSize",
        validate=validate.Range(min=1, max=100, error="pageSize必须在1到100之间"),
        error_messages={"required": "pageSize不能为空", "invalid": "pageSize必须为整数"},
    )
    business_type = fields.Integer(
        required=False,
        data_key="businessType",
        validate=validate.OneOf([e.value for e in NotificationBusinessTypeEnum], error="businessType不合法"),
        error_messages={"invalid": "businessType必须为整数"},
    )

    class Meta:
        unknown = EXCLUDE