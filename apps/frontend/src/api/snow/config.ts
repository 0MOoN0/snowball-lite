import request from '@/config/axios'

// 系统设置项接口（基于swagger定义）
export interface Setting {
  id?: number
  key: string
  value: string
  settingType: 'string' | 'int' | 'float' | 'bool' | 'json' | 'password'
  group?: string
  description?: string
  defaultValue?: string
  createdTime?: string
  updatedTime?: string
}

// 创建设置项接口
export interface SettingCreate {
  key: string
  value: string
  settingType: 'string' | 'int' | 'float' | 'bool' | 'json' | 'password'
  group?: string
  description?: string
  defaultValue?: string
}

// 更新设置项接口
export interface SettingUpdate {
  id?: number
  key: string
  value: string
  settingType?: 'string' | 'int' | 'float' | 'bool' | 'json' | 'password'
  group?: string
  description?: string
  defaultValue?: string
}

// 分页响应接口
export interface PaginationData<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface PaginationResponse<T> {
  code: number
  message: string
  data: PaginationData<T>
  success: boolean
}

// 单个设置项响应接口
export interface SingleSettingResponse {
  code: number
  message: string
  data: Setting
  success: boolean
}

// 查询参数接口
export interface SettingQueryParams {
  key?: string
  group?: string
  settingType?: string
  page?: number
  size?: number
}

// 删除响应接口
export interface DeleteResponse {
  code: number
  message: string
  data: boolean
  success: boolean
}

// 批量更新响应接口
export interface BatchUpdateResponse {
  code: number
  message: string
  data: {
    success_count: number
    failure_count: number
    successful_keys: string[]
    failures: Array<{
      key: string
      error: string
    }>
  }
  success: boolean
}

// 批量更新请求接口
export interface BatchUpdateRequest {
  settings: SettingUpdate[]
}

// 系统设置API（基于swagger定义）
export const systemSettingsApi = {
  // 查询系统设置
  getSettings: (params?: SettingQueryParams): Promise<PaginationResponse<Setting>> => {
    return request.get({ url: '/system/settings/', params })
  },

  // 创建系统设置
  createSetting: (data: SettingCreate): Promise<SingleSettingResponse> => {
    return request.post({ url: '/system/settings/', data })
  },

  // 更新系统设置
  updateSetting: (data: SettingUpdate): Promise<SingleSettingResponse> => {
    return request.put({ url: '/system/settings/', data })
  },

  // 根据ID删除系统设置
  deleteSetting: (settingId: number): Promise<DeleteResponse> => {
    return request.delete({ url: `/system/settings/${settingId}` })
  },

  // 批量更新系统设置
  batchUpdateSettings: (data: BatchUpdateRequest): Promise<BatchUpdateResponse> => {
    return request.put({
      url: '/system/settings/batch',
      data
    })
  }
}

// 兼容性API别名（为了保持向后兼容）
export const configGroupApi = systemSettingsApi
export const configItemApi = systemSettingsApi
export const configApi = systemSettingsApi

// 导出主要API
export default {
  systemSettings: systemSettingsApi,
  // 保持向后兼容的别名
  configGroup: systemSettingsApi,
  configItem: systemSettingsApi,
  config: systemSettingsApi
}