import { ref, onMounted } from 'vue'
import { useEnum } from '@/hooks/web/useEnum'

/**
 * 指数管理枚举数据加载Hook
 * 统一管理所有枚举数据的加载和状态
 */
export const useIndexEnumLoader = () => {
  // 加载状态
  const enumLoading = ref(false)
  const enumError = ref<string | null>(null)

  // 枚举Hook实例
  const indexTypeEnumHook = useEnum('IndexTypeEnum')
  const investmentStrategyEnumHook = useEnum('InvestmentStrategyEnum')
  const currencyEnumHook = useEnum('CurrencyEnum')
  const marketEnumHook = useEnum('MarketEnum')
  const indexStatusEnumHook = useEnum('IndexStatusEnum')
  const weightMethodEnumHook = useEnum('WeightMethodEnum')
  const calculationMethodEnumHook = useEnum('CalculationMethodEnum')
  const rebalanceFrequencyEnumHook = useEnum('RebalanceFrequencyEnum')

  /**
   * 加载所有枚举数据
   */
  const loadEnums = async () => {
    enumLoading.value = true
    enumError.value = null

    try {
      await Promise.all([
        indexTypeEnumHook.loadEnum(),
        investmentStrategyEnumHook.loadEnum(),
        currencyEnumHook.loadEnum(),
        marketEnumHook.loadEnum(),
        indexStatusEnumHook.loadEnum(),
        weightMethodEnumHook.loadEnum(),
        calculationMethodEnumHook.loadEnum(),
        rebalanceFrequencyEnumHook.loadEnum(),
      ])

      console.log('所有枚举数据加载完成')
    } catch (error) {
      console.error('加载枚举数据失败:', error)
      enumError.value = '加载枚举数据失败，请刷新页面重试'
    } finally {
      enumLoading.value = false
    }
  }

  /**
   * 重新加载枚举数据
   */
  const reloadEnums = () => {
    loadEnums()
  }

  /**
   * 获取所有枚举数据的对象
   */
  const getAllEnums = () => ({
    indexTypeEnum: indexTypeEnumHook.enumData.value,
    investmentStrategyEnum: investmentStrategyEnumHook.enumData.value,
    currencyEnum: currencyEnumHook.enumData.value,
    marketEnum: marketEnumHook.enumData.value,
    indexStatusEnum: indexStatusEnumHook.enumData.value,
    weightMethodEnum: weightMethodEnumHook.enumData.value,
    calculationMethodEnum: calculationMethodEnumHook.enumData.value,
    rebalanceFrequencyEnum: rebalanceFrequencyEnumHook.enumData.value,
  })

  /**
   * 检查枚举数据是否已加载完成
   */
  const isEnumsLoaded = () => {
    return (
      indexTypeEnumHook.isLoaded.value &&
      currencyEnumHook.isLoaded.value &&
      marketEnumHook.isLoaded.value &&
      indexStatusEnumHook.isLoaded.value
    )
  }

  // 组件挂载时自动加载枚举数据
  onMounted(() => {
    loadEnums()
  })

  return {
    // 枚举数据 (computed refs)
    indexTypeEnum: indexTypeEnumHook.enumData,
    investmentStrategyEnum: investmentStrategyEnumHook.enumData,
    currencyEnum: currencyEnumHook.enumData,
    marketEnum: marketEnumHook.enumData,
    indexStatusEnum: indexStatusEnumHook.enumData,
    weightMethodEnum: weightMethodEnumHook.enumData,
    calculationMethodEnum: calculationMethodEnumHook.enumData,
    rebalanceFrequencyEnum: rebalanceFrequencyEnumHook.enumData,
    
    // 枚举Hook实例 (用于获取标签等)
    indexTypeEnumHook,
    investmentStrategyEnumHook,
    currencyEnumHook,
    marketEnumHook,
    indexStatusEnumHook,
    weightMethodEnumHook,
    calculationMethodEnumHook,
    rebalanceFrequencyEnumHook,
    
    // 状态
    enumLoading,
    enumError,
    
    // 方法
    loadEnums,
    reloadEnums,
    getAllEnums,
    isEnumsLoaded,
  }
}