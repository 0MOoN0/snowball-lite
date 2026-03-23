from dataclasses import dataclass

from flask_marshmallow import Schema
from marshmallow import fields


@dataclass
class SchedulerInfo:
    current_host: str = ''
    running: bool = False
    healthy: bool = False
    health_message: str = ''
    runtime_backend: str = ''


class SchedulerInfoSchema(Schema):
    current_host = fields.String()
    running = fields.Boolean()
    healthy = fields.Boolean()
    health_message = fields.String()
    runtime_backend = fields.String()
