import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createIndex, getIndexDetail, updateIndex } from '@/api/snow/index/IndexApi'
import type { IndexFormData } from '@/views/Snow/Index/types'

/**
 * 指数数据处理器Hook
 * 负责数据转换、API调用等业务逻辑
 */
export function useIndexDataProcessor() {
  const isSubmitting = ref(false)
  const isLoading = ref(false)

  /**
   * 将表单数据转换为API请求格式
   * @param formData 表单数据
   * @returns 转换后的API请求数据
   */
  const transformFormDataToApi = (formData: IndexFormData) => {
    const apiData = {
      // 基础字段（保持字符串类型）
      indexCode: formData.indexCode,
      indexName: formData.indexName,
      description: formData.description,
      publisher: formData.publisher,
      
      // 必需的枚举字段（string -> number）
      indexType: Number(formData.indexType),
      market: Number(formData.market),
      investmentStrategy:
        formData.investmentStrategy !== null && formData.investmentStrategy !== undefined
          ? Number(formData.investmentStrategy)
          : undefined,
      currency:
        formData.currency !== null && formData.currency !== undefined ? Number(formData.currency) : undefined,
      weightMethod:
        formData.weightMethod !== null && formData.weightMethod !== undefined ? Number(formData.weightMethod) : undefined,
      calculationMethod:
        formData.calculationMethod !== null && formData.calculationMethod !== undefined
          ? Number(formData.calculationMethod)
          : undefined,
      indexStatus:
        formData.indexStatus !== null && formData.indexStatus !== undefined ? Number(formData.indexStatus) : undefined,
      
      // 日期与数值
      baseDate: formData.baseDate || undefined,
      basePoint:
        formData.basePoint !== null && formData.basePoint !== undefined ? Number(formData.basePoint) : undefined,
      publishDate: formData.publishDate || undefined,
      
      // 股票指数特有字段（与后端一致）
      ...(formData.constituentCount !== null && formData.constituentCount !== undefined
        ? { constituentCount: Number(formData.constituentCount) }
        : {}),
      ...(formData.marketCap !== null && formData.marketCap !== undefined
        ? { marketCap: Number(formData.marketCap) }
        : {}),
      ...(formData.freeFloatMarketCap !== null && formData.freeFloatMarketCap !== undefined
        ? { freeFloatMarketCap: Number(formData.freeFloatMarketCap) }
        : {}),
      ...(formData.averagePe !== null && formData.averagePe !== undefined
        ? { averagePe: Number(formData.averagePe) }
        : {}),
      ...(formData.averagePb !== null && formData.averagePb !== undefined
        ? { averagePb: Number(formData.averagePb) }
        : {}),
      ...(formData.dividendYield !== null && formData.dividendYield !== undefined
        ? { dividendYield: Number(formData.dividendYield) }
        : {}),
      ...(formData.turnoverRate !== null && formData.turnoverRate !== undefined
        ? { turnoverRate: Number(formData.turnoverRate) }
        : {}),
      ...(formData.volatility !== null && formData.volatility !== undefined
        ? { volatility: Number(formData.volatility) }
        : {}),
      ...(formData.beta !== null && formData.beta !== undefined ? { beta: Number(formData.beta) } : {}),
      ...(formData.rebalanceFrequency !== null && formData.rebalanceFrequency !== undefined
        ? { rebalanceFrequency: String(formData.rebalanceFrequency) }
        : {}),
      ...(formData.lastRebalanceDate ? { lastRebalanceDate: formData.lastRebalanceDate } : {}),
      ...(formData.nextRebalanceDate ? { nextRebalanceDate: formData.nextRebalanceDate } : {}),
    }

    return apiData
  }

  /**
   * 将API响应数据转换为表单格式
   * @param apiData API响应数据
   * @returns 转换后的表单数据
   */
  const transformApiDataToForm = (apiData: any): IndexFormData => {
    return {
      id: apiData?.id ?? null,
      indexName: apiData?.indexName ?? '',
      indexCode: apiData?.indexCode ?? '',
      // 将枚举型字段统一转换为 number，确保与 Select 选项匹配
      indexType: apiData?.indexType !== undefined && apiData?.indexType !== null ? Number(apiData.indexType) : null,
      market: apiData?.market !== undefined && apiData?.market !== null ? Number(apiData.market) : null,
      investmentStrategy: apiData?.investmentStrategy !== undefined && apiData?.investmentStrategy !== null ? Number(apiData.investmentStrategy) : null,
      currency: apiData?.currency !== undefined && apiData?.currency !== null ? Number(apiData.currency) : null,
      baseDate: apiData?.baseDate ?? null,
      basePoint: apiData?.basePoint !== undefined && apiData?.basePoint !== null ? Number(apiData.basePoint) : null,
      weightMethod: apiData?.weightMethod !== undefined && apiData?.weightMethod !== null ? Number(apiData.weightMethod) : null,
      calculationMethod: apiData?.calculationMethod !== undefined && apiData?.calculationMethod !== null ? Number(apiData.calculationMethod) : null,
      indexStatus: apiData?.indexStatus !== undefined && apiData?.indexStatus !== null ? Number(apiData.indexStatus) : null,
      publisher: apiData?.publisher ?? '',
      publishDate: apiData?.publishDate ?? null,
      description: apiData?.description ?? '',
      
      // 股票指数特有字段（与后端一致）
      constituentCount: apiData?.constituentCount !== undefined && apiData?.constituentCount !== null ? Number(apiData.constituentCount) : null,
      marketCap: apiData?.marketCap !== undefined && apiData?.marketCap !== null ? Number(apiData.marketCap) : null,
      freeFloatMarketCap: apiData?.freeFloatMarketCap !== undefined && apiData?.freeFloatMarketCap !== null ? Number(apiData.freeFloatMarketCap) : null,
      averagePe: apiData?.averagePe !== undefined && apiData?.averagePe !== null ? Number(apiData.averagePe) : null,
      averagePb: apiData?.averagePb !== undefined && apiData?.averagePb !== null ? Number(apiData.averagePb) : null,
      dividendYield: apiData?.dividendYield !== undefined && apiData?.dividendYield !== null ? Number(apiData.dividendYield) : null,
      turnoverRate: apiData?.turnoverRate !== undefined && apiData?.turnoverRate !== null ? Number(apiData.turnoverRate) : null,
      volatility: apiData?.volatility !== undefined && apiData?.volatility !== null ? Number(apiData.volatility) : null,
      beta: apiData?.beta !== undefined && apiData?.beta !== null ? Number(apiData.beta) : null,
      rebalanceFrequency: apiData?.rebalanceFrequency ?? null,
      lastRebalanceDate: apiData?.lastRebalanceDate ?? null,
      nextRebalanceDate: apiData?.nextRebalanceDate ?? null,
    }
  }

  /**
   * 提交表单数据
   * @param formData 表单数据
   * @param isEdit 是否为编辑模式
   * @returns Promise<boolean> 提交是否成功
   */
  const submitFormData = async (formData: IndexFormData, isEdit: boolean = false): Promise<boolean> => {
    if (isSubmitting.value) {
      return false
    }

    try {
      isSubmitting.value = true
      
      // 转换数据格式
      const payload = transformFormDataToApi(formData)

      let resp
      if (isEdit && formData.id) {
        // 编辑模式：调用更新接口，仅返回布尔结果
        resp = await updateIndex(Number(formData.id), payload as any)
      } else {
        // 新增模式
        resp = await createIndex(payload as any)
      }

      if (!resp.success) {
        ElMessage.error(resp.message || '操作失败')
        return false
      }

      return true
    } catch (error) {
      console.error('提交指数数据失败:', error)
      ElMessage.error('提交指数数据失败，请稍后重试')
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  /**
   * 加载指数详情数据
   * @param indexId 指数ID
   * @returns Promise<IndexFormData | null> 指数详情数据
   */
  const loadIndexDetail = async (indexId: number): Promise<IndexFormData | null> => {
    try {
      isLoading.value = true
      const resp = await getIndexDetail({ id: indexId })
      if (!resp.success || !resp.data) {
        ElMessage.error(resp.message || '获取指数详情失败')
        return null
      }

      const formData = transformApiDataToForm(resp.data)
      return formData
    } catch (error) {
      console.error('获取指数详情失败:', error)
      ElMessage.error('获取指数详情失败，请稍后重试')
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    isSubmitting,
    isLoading,
    submitFormData,
    loadIndexDetail,
  }
}