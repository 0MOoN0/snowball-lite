import { createBaseFields } from '@/views/Snow/Index/config/formFields/baseFields'
import { createStockFields } from '@/views/Snow/Index/config/formFields/stockFields'

/**
 * 创建分隔符字段
 */
export const createDivider = (label: string): FormSchema => ({
  field: `divider-${Date.now()}`,
  component: 'Divider',
  label,
  colProps: {
    span: 24,
  },
  componentProps: {
    style: {
      fontWeight: 600,
      color: '#409eff',
      fontSize: '16px',
    },
  },
})

/**
 * 判断是否为股票指数
 */
export const isStockIndex = (indexType: number): boolean => {
  // 假设 1 代表股票指数，根据实际枚举值调整
  return indexType === 0
}

/**
 * 生成动态表单Schema
 */
export const getFormSchema = (
  indexType: number | null,
  enumOptions: {
    indexTypeEnum: any[]
    investmentStrategyEnum: any[]
    currencyEnum: any[]
    marketEnum: any[]
    indexStatusEnum: any[]
    weightMethodEnum: any[]
    calculationMethodEnum: any[]
    rebalanceFrequencyEnum: any[]
    onIndexTypeChange: (val: number) => void
  }
): FormSchema[] => {
  // 基础字段
  const baseFields = createBaseFields(enumOptions)
  
  // 如果是股票指数，添加股票指数特有字段
  if (indexType !== null && indexType !== undefined && isStockIndex(indexType)) {
    const stockFields = createStockFields({ rebalanceFrequencyEnum: enumOptions.rebalanceFrequencyEnum })
    return [...baseFields, ...stockFields]
  }
  
  return baseFields
}

/**
 * 获取表单字段的默认值映射
 */
export const getDefaultValues = (): Record<string, any> => ({
  indexName: null,
  indexCode: null,
  indexShortCode: null,
  indexType: null,
  investmentStrategy: null,
  market: null,
  currency: null,
  baseDate: null,
  basePoint: null,
  weightMethod: null,
  calculationMethod: null,
  indexStatus: null,
  publisher: null,
  publishDate: null,
  description: null,
  // 股票指数特有字段（与后端一致）
  constituentCount: null,
  marketCap: null,
  freeFloatMarketCap: null,
  averagePe: null,
  averagePb: null,
  dividendYield: null,
  turnoverRate: null,
  volatility: null,
  beta: null,
  rebalanceFrequency: null,
  lastRebalanceDate: null,
  nextRebalanceDate: null,
})

/**
 * 获取需要缓存的字段列表
 */
// 字段目录统一维护：基础字段与按类型的专属字段
export const FIELD_CATALOG = {
  base: [
    'indexName',
    'indexCode',
    'indexShortCode',
    'investmentStrategy',
    'market',
    'currency',
    'baseDate',
    'basePoint',
    'weightMethod',
    'calculationMethod',
    'indexStatus',
    'publisher',
    'publishDate',
    'description',
  ],
  byType: {
    // 股票指数（indexType = 0）
    0: [
      'constituentCount',
      'marketCap',
      'freeFloatMarketCap',
      'averagePe',
      'averagePb',
      'dividendYield',
      'turnoverRate',
      'volatility',
      'beta',
      'rebalanceFrequency',
      'lastRebalanceDate',
      'nextRebalanceDate',
    ],
  } as Record<number, string[]>,
}

// 获取基础字段名列表
export const getBaseFieldNames = (): string[] => FIELD_CATALOG.base

// 获取指定类型的字段名列表
export const getTypeFieldNames = (indexType: number): string[] => FIELD_CATALOG.byType[indexType] || []

// 获取需要缓存的字段列表（基础 + 所有类型专属）
export const getCacheableFields = (): string[] => [
  ...FIELD_CATALOG.base,
  ...Object.values(FIELD_CATALOG.byType).flat(),
]