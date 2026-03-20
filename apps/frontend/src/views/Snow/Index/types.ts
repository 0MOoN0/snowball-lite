/**
 * 指数表单数据类型（与后端字段保持一致）
 */
export interface IndexFormData {
  id?: number | null
  indexName: string
  indexCode: string
  indexType: number | null
  market: number | null
  investmentStrategy: number | null
  currency: number | null
  baseDate: string | null
  basePoint: number | null
  weightMethod: number | null
  calculationMethod: number | null
  indexStatus: number | null
  publisher: string
  publishDate: string | null
  description: string
  
  // 股票指数特有字段（与新增接口文档一致）
  constituentCount?: number | null
  marketCap?: number | null
  freeFloatMarketCap?: number | null
  averagePe?: number | null
  averagePb?: number | null
  dividendYield?: number | null
  turnoverRate?: number | null
  volatility?: number | null
  beta?: number | null
  rebalanceFrequency?: string | null
  lastRebalanceDate?: string | null
  nextRebalanceDate?: string | null
}

/**
 * 枚举选项类型
 */
export interface EnumOption {
  label: string
  value: any
}

/**
 * 枚举选项集合类型
 */
export interface EnumOptions {
  indexTypeEnum: EnumOption[]
  investmentStrategyEnum: EnumOption[]
  currencyEnum: EnumOption[]
  marketEnum: EnumOption[]
  indexStatusEnum: EnumOption[]
  weightMethodEnum: EnumOption[]
  calculationMethodEnum: EnumOption[]
  onIndexTypeChange?: (val: number) => void
}

/**
 * 表单字段配置类型
 */
export interface FormFieldConfig {
  field: string
  label: string
  component: string
  value?: any
  colProps?: {
    span: number
  }
  componentProps?: {
    placeholder?: string
    options?: EnumOption[]
    onChange?: (val: any) => void
    [key: string]: any
  }
  formItemProps?: {
    rules?: any[]
  }
}

/**
 * 缓存字段类型
 */
export interface CacheableFields {
  [key: string]: boolean
}