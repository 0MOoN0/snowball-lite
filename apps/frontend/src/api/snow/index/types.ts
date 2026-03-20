// 指数列表查询参数
export interface IndexListParams {
  page: number
  pageSize: number
  indexName?: string
  indexType?: number
  investmentStrategy?: number
  market?: number
  indexStatus?: number
}

// 指数基础信息
export interface IndexBase {
  id: number
  indexCode: string
  indexName: string
  indexType: number
  investmentStrategy?: number
  market: number
  baseDate?: string
  basePoint?: number
  currency?: number
  weightMethod?: number
  calculationMethod?: number
  indexStatus: number
  description?: string
  publisher?: string
  publishDate?: string
  createTime: string
  updateTime: string
}

// 股票指数特有字段
export interface IndexStock extends IndexBase {
  constituentCount?: number
  marketCap?: number
  freeFloatMarketCap?: number
  averagePe?: number
  averagePb?: number
  dividendYield?: number
  turnoverRate?: number
  volatility?: number
  beta?: number
  rebalanceFrequency?: string
  lastRebalanceDate?: string
  nextRebalanceDate?: string
}

// 指数列表数据
export interface IndexListData {
  items: IndexBase[]
  total: number
  page: number
  size: number
}

// 指数列表响应
export interface IndexListResponse {
  code: number
  data: IndexListData
  message: string
  success: boolean
}

// 指数创建请求
export interface IndexCreateRequest {
  indexCode: string
  indexName: string
  indexType: number
  investmentStrategy?: number
  market: number
  baseDate?: string
  basePoint?: number
  currency?: number
  weightMethod?: number
  calculationMethod?: number
  indexStatus?: number
  description?: string
  publisher?: string
  publishDate?: string
  // 股票指数特有字段
  constituentCount?: number
  marketCap?: number
  freeFloatMarketCap?: number
  averagePe?: number
  averagePb?: number
  dividendYield?: number
  turnoverRate?: number
  volatility?: number
  beta?: number
  rebalanceFrequency?: string
  lastRebalanceDate?: string
  nextRebalanceDate?: string
}

// 指数更新请求（允许部分字段）
export type IndexUpdateRequest = Partial<IndexCreateRequest>

// 指数创建响应
export interface IndexCreateResponse {
  code: number
  data: IndexBase
  message: string
  success: boolean
}