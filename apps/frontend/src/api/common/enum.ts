import type { AvailableEnumsResponse, BatchEnumResponse, EnumDataWrapper, EnumVersionResponse } from '@/api/common/types'
import request from '@/config/axios'

// 获取指定枚举数据
export const getEnumByKeyApi = (enumKey: string) => {
  return request.get<EnumDataWrapper>({ url: `/api/enums/${enumKey}` })
}

// 获取枚举版本信息（使用实际存在的接口）
export const getEnumVersionsApi = (): Promise<EnumVersionResponse> => {
  return request.get({ url: '/api/enums/versions' })
}

// 获取所有可用的枚举列表
export const getAvailableEnumsApi = (): Promise<AvailableEnumsResponse> => {
  return request.get({ url: '/api/enums/' })
}

// 批量获取枚举数据
export const batchGetEnumsApi = (enumKeys: string[]): Promise<BatchEnumResponse> => {
  return request.post({
    url: '/api/enums/batch',
    data: { enumKeys }
  })
}