from dataclasses import dataclass

from flask_marshmallow import Schema
from marshmallow import fields


@dataclass
class SchedulerInfo:
    current_host: str = ''
    running: bool = False


class SchedulerInfoSchema(Schema):
    current_host = fields.String()
    running = fields.Boolean()
