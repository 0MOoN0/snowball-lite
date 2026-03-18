from typing import Optional, Dict, Union

from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import MarketEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.databox.adapter.data.AkShareAdapter import AkShareAdapter
from web.databox.adapter.data.DataBoxDataAdapter import DataBoxDataAdapter
from web.databox.adapter.data.TorxiongAdapter import TorxiongAdapter
from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.databox.adapter.data.xa_service import XaServiceAdapter
from web.databox.enum.IndicatorEnum import IndicatorEnum
from web.databox.interfaces.security_index_valuation_interface import SecurityIndexValuationInterface
from web.databox.models.provider_metadata import AdapterProviderMetadata
from web.databox.registry.providers import PROVIDERS
from web.web_exception.WebException import WebBaseException
from web.weblogger import error


class AdapterService:
    """
    适配器服务
    负责管理和提供各种数据适配器的访问
    """
    
    def __init__(self, external_adapters: Optional[Dict[str, DataBoxDataAdapter]] = None):
        """
        初始化适配器服务
        
        Args:
            external_adapters: 外部传入的适配器实例字典，如果提供则使用这些实例
        """
        self._adapters: Dict[str, DataBoxDataAdapter] = {}
        # 注册的提供者元数据（由 PROVIDERS 驱动）
        self._provider_registry: Dict[str, AdapterProviderMetadata] = {}
        if external_adapters:
            self._adapters.update(external_adapters)
        else:
            self._initialize_adapters()
        self.register_provider_from_registry()
    
    def _initialize_adapters(self):
        """
        初始化所有可用的适配器
        """
        try:
            self._adapters[DataBoxAdapterEnum.AKSHARE.value] = AkShareAdapter()
        except Exception as e:
            error(f"Failed to initialize AkShare adapter: {str(e)}")
            
        try:
            self._adapters[DataBoxAdapterEnum.TORXIONG.value] = TorxiongAdapter()
        except Exception as e:
            error(f"Failed to initialize Torxiong adapter: {str(e)}")
            
        try:
            self._adapters[DataBoxAdapterEnum.XA.value] = XaDataAdapter()
        except Exception as e:
            error(f"Failed to initialize XA adapter: {str(e)}")
            
        try:
            self._adapters[DataBoxAdapterEnum.XA_SERVICE.value] = XaServiceAdapter()
        except Exception as e:
            error(f"Failed to initialize XA Service adapter: {str(e)}")
        # 初始化后，不进行自动注册（完全由外部注册驱动）

    def _ensure_adapter_instance(
        self,
        adapter_key: str,
        adapter: Optional[Union[DataBoxDataAdapter, type[DataBoxDataAdapter]]] = None,
    ) -> Optional[DataBoxDataAdapter]:
        """确保指定 key 对应的适配器实例存在，必要时根据类创建实例。"""
        if adapter_key in self._adapters:
            return self._adapters[adapter_key]
        if adapter is None:
            return None
        if isinstance(adapter, type):
            try:
                instance = adapter()  # type: ignore[call-arg]
            except Exception as e:
                error(f"Failed to instantiate adapter {adapter}: {e}")
                return None
        else:
            instance = adapter
        self._adapters[adapter_key] = instance
        return instance

    def register_provider_from_registry(self) -> None:
        """从全局 PROVIDERS 读取配置，构建元数据，按需实例化适配器类。"""
        for key, entry in PROVIDERS.items():
            adapter_class = entry.adapter_class
            meta: AdapterProviderMetadata = entry.metadata
            # 实例化适配器类
            instance = self._ensure_adapter_instance(key, adapter_class)
            if instance is None:
                error(f"Failed to create adapter instance for {key}")
                continue
            self._provider_registry[key] = meta

    def _get_registered_providers_for(
        self,
        indicator: IndicatorEnum,
        asset_type: Optional[AssetTypeEnum],
        market: Optional[MarketEnum],
    ) -> Dict[str, DataBoxDataAdapter]:
        """按指标/资产类型/市场筛选注册的提供者，返回 key->adapter 实例映射。"""
        result: Dict[str, DataBoxDataAdapter] = {}
        for key, meta in self._provider_registry.items():
            if indicator not in meta.supported_metrics:
                continue
            if asset_type is not None and meta.supported_asset_types and asset_type not in meta.supported_asset_types:
                continue
            if market is not None and meta.supported_markets and market not in meta.supported_markets:
                continue
            adapter = self._adapters.get(key)
            if adapter is not None:
                result[key] = adapter
        return result
    
    def get_adapter(self, adapter_type: str | DataBoxAdapterEnum) -> Optional[DataBoxDataAdapter]:
        """
        获取指定类型的适配器
        
        Args:
            adapter_type: 适配器类型
            
        Returns:
            DataBoxDataAdapter: 适配器实例，如果不存在返回None
        """
        if isinstance(adapter_type, DataBoxAdapterEnum):
            adapter_key = adapter_type.value
        else:
            adapter_key = str(adapter_type)
            
        return self._adapters.get(adapter_key)
    
    def has_capability(self, adapter_type: str | DataBoxAdapterEnum, interface_class: type) -> bool:
        """
        检查指定适配器是否具有某种能力（实现了某个接口）
        
        Args:
            adapter_type: 适配器类型
            interface_class: 接口类
            
        Returns:
            bool: 如果适配器实现了指定接口返回True，否则返回False
        """
        adapter = self.get_adapter(adapter_type)
        if adapter is None:
            return False
            
        return isinstance(adapter, interface_class)
    
    def get_available_adapters(self) -> Dict[str, DataBoxDataAdapter]:
        """
        获取所有可用的适配器
        
        Returns:
            Dict[str, DataBoxDataAdapter]: 适配器字典
        """
        return self._adapters.copy()
    
    def get_adapters_with_capability(self, interface_class: type) -> Dict[str, DataBoxDataAdapter]:
        """
        获取具有指定能力的所有适配器
        
        Args:
            interface_class: 接口类
            
        Returns:
            Dict[str, DataBoxDataAdapter]: 具有指定能力的适配器字典
        """
        capable_adapters = {}
        for adapter_key, adapter in self._adapters.items():
            if isinstance(adapter, interface_class):
                capable_adapters[adapter_key] = adapter
        return capable_adapters

    def get_adapter_by_capability(
        self,
        interface_class: type,
        market: Optional[MarketEnum] = None,
        preferred: Optional[DataBoxAdapterEnum] = None,
    ) -> Optional[DataBoxDataAdapter]:
        """
        按接口能力选择适配器（能力驱动方案B）。

        - 若提供 preferred（严格模式）：
          - 如果该适配器实现了指定接口能力，直接返回；否则抛出异常。
        - 未指定 preferred：
          - 在注册中心中筛选具备能力的适配器，并按 cost_level 升序返回首选。
        """

        # 严格模式优先
        if preferred is not None:
            adapter = self.get_adapter(preferred)
            if adapter is not None and isinstance(adapter, interface_class):
                return adapter
            raise WebBaseException(msg=f"Preferred adapter {preferred} does not implement capability {interface_class.__name__}")

        # 自动模式：从注册中心筛选
        candidates: Dict[str, DataBoxDataAdapter] = {}
        for key, meta in self._provider_registry.items():
            # 仅保留实现了指定接口的适配器
            adapter = self._adapters.get(key)
            if adapter is None or not isinstance(adapter, interface_class):
                continue
            # 市场过滤（如配置了 supported_markets）
            if market is not None and meta.supported_markets and market not in meta.supported_markets:
                continue
            candidates[key] = adapter

        if not candidates:
            error(f"No adapters implement capability: {interface_class.__name__}")
            return None

        def sort_key(item: tuple[str, DataBoxDataAdapter]) -> int:
            key, _ = item
            meta = self._provider_registry.get(key)
            return meta.cost_level if meta is not None else 99

        sorted_candidates = sorted(candidates.items(), key=sort_key)
        return sorted_candidates[0][1] if sorted_candidates else None

    def get_indicator_adapter(
        self,
        indicator: IndicatorEnum,
        symbol: str,
        asset_type: Optional[AssetTypeEnum],
        market: Optional[MarketEnum] = None,
        preferred: Optional[DataBoxAdapterEnum] = None,
    ) -> Optional[DataBoxDataAdapter]:
        """
        根据指标/代码/资产类型/市场选择合适的适配器。
        
        选择策略：
        - 若传入 preferred（严格模式）：
          - 若该适配器实现了对应接口能力，直接返回该适配器；
          - 否则抛出 WebBaseException，提示指定的数据源不支持该指标；
        - 未指定 preferred：仅使用手动注册的 PROVIDERS 信息进行筛选；
          - 按注册元数据中的 cost_level 升序排序，选择成本最低的一个适配器返回；
          - 若无符合条件的适配器，返回 None。
        
        参数：
        - indicator (IndicatorEnum, required): 指标类型，如 DIVIDEND_YIELD
        - symbol (str, required): 证券/指数代码（用于未来可能的精细筛选，当前不参与排序）
        - asset_type (AssetTypeEnum, required): 资产类型，用于筛选支持的适配器
        - market (MarketEnum, optional): 市场，用于进一步过滤符合市场的适配器
        - preferred (DataBoxAdapterEnum, optional): 首选适配器（严格模式）
        
        返回：
        - DataBoxDataAdapter | None: 返回满足条件的适配器实例；当无合适适配器时返回 None
        
        异常：
        - WebBaseException: 在严格模式下，当 preferred 不具备对应指标能力时抛出
        """
        
        # 将指标映射到接口类型（仅用于数值型/轻量指标）
        # 说明：表格型数据集（如可转债发行）改为能力驱动选择，不再通过 IndicatorEnum 映射。
        indicator_to_interface: Dict[IndicatorEnum, type] = {
            IndicatorEnum.DIVIDEND_YIELD: SecurityIndexValuationInterface,
        }

        interface_cls = indicator_to_interface.get(indicator)
        if interface_cls is None:
            error(f"No interface mapping for indicator: {indicator}")
            return None

        # 首选适配器检查
        if preferred is not None:
            if self.has_capability(preferred, interface_cls):
                return self.get_adapter(preferred)
            raise WebBaseException(msg=f"Preferred adapter {preferred} does not support indicator {indicator}")

        # 仅使用注册中心进行筛选（外部在 PROVIDERS 中手动配置）
        capable = self._get_registered_providers_for(indicator, asset_type, market)
        if not capable:
            error(f"No adapters support indicator: {indicator}")
            return None

        # 按 cost_level 排序
        def sort_key(item: tuple[str, DataBoxDataAdapter]) -> int:
            key, _ = item
            # 只按 cost_level 排序，不再按市场偏好
            meta = self._provider_registry.get(key)
            return meta.cost_level if meta is not None else 99

        # 依据策略选择
        sorted_capable = sorted(capable.items(), key=sort_key)
        if sorted_capable:
            return sorted_capable[0][1]
        return None