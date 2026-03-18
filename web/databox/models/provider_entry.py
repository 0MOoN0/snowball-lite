from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from web.databox.adapter.data.DataBoxDataAdapter import DataBoxDataAdapter
from web.databox.models.provider_metadata import AdapterProviderMetadata


@dataclass
class ProviderEntry:
    adapter_class: Type[DataBoxDataAdapter]
    metadata: AdapterProviderMetadata


