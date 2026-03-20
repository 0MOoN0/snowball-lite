import type { ComputedRef } from 'vue'

export interface EnumOption {
  value: number
  label: string
}

// 枚举版本信息
export interface EnumVersionInfo {
  enumKey: string
  version: string
  lastUpdated: number
}

// 枚举版本API响应
export interface EnumVersionResponse {
  code: number
  success: boolean
  message: string
  data: {
    global: number
  }
}

// 枚举数据包装器（包含版本信息）
export interface EnumDataWrapper {
  data: EnumOption[]
  version: string
  lastUpdated: number
  cacheExpiry?: number
}

// 可用枚举列表响应接口
export interface AvailableEnumsResponse {
  code: number
  success: boolean
  message: string
  data: Record<string, string> // 枚举键名 -> 枚举描述
}

// 枚举状态接口
export interface EnumState {
  enumData: Record<string, EnumDataWrapper>
  globalVersion: string | null
  loading: boolean
  lastGlobalCheck: number
  availableEnums: Record<string, string>
}

// 枚举缓存配置
export interface EnumCacheConfig {
  ttl: number // 缓存时间（毫秒）
  checkInterval: number // 版本检查间隔（毫秒）
}

// 枚举加载选项
export interface EnumLoadOptions {
  forceRefresh?: boolean
  skipVersionCheck?: boolean
}

// 批量获取枚举结果项
export interface BatchEnumResultItem {
  enumKey: string
  data: EnumOption[]
  success: boolean
  message: string
}

// 批量获取枚举响应数据
export interface BatchEnumResponseData {
  successCount: number
  failureCount: number
  results: BatchEnumResultItem[]
}

// 批量获取枚举API响应
export interface BatchEnumResponse {
  code: number
  success: boolean
  message: string
  data: BatchEnumResponseData
}

// 批量获取枚举请求参数
export interface BatchEnumRequest {
  enumKeys: string[]
}

// useEnum 返回类型
export interface UseEnumReturn {
  enumData: ComputedRef<EnumOption[]>
  isLoaded: ComputedRef<boolean>
  isExpired: ComputedRef<boolean>
  version: ComputedRef<string>
  loadEnum: (options?: EnumLoadOptions) => Promise<EnumOption[]>
  refreshEnum: () => Promise<EnumOption[]>
  getLabel: (value: number) => string
  getValue: (label: string) => number | undefined
}