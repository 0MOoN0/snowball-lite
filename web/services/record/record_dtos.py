from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class RecordGroupDTO:
    group_type: int
    group_id: int

@dataclass
class RecordImportDTO:
    asset_id: int
    transactions_date: datetime
    transactions_price: int
    transactions_share: int
    transactions_amount: int
    transactions_fee: int
    transactions_direction: int
    groups: List[RecordGroupDTO] = field(default_factory=list)
