from flask_marshmallow import Schema
from marshmallow import fields, EXCLUDE, validate
from web.common.enum.NotificationEnum import NotificationBusinessTypeEnum


class NotificationBatchReadBodySchema(Schema):
    ids = fields.List(
        fields.Integer(error_messages={"invalid": "ids必须为整数"}),
        required=False,
        data_key="ids",
        validate=validate.Length(min=1, error="ids不能为空"),
        error_messages={"invalid": "ids必须为整数列表"},
    )
    business_type = fields.Integer(
        required=False,
        data_key="businessType",
        validate=validate.OneOf([e.value for e in NotificationBusinessTypeEnum], error="businessType不合法"),
        error_messages={"invalid": "businessType必须为整数"},
    )

    class Meta:
        unknown = EXCLUDE