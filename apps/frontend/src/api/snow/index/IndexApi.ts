import request from '@/config/axios'
import type { IndexListParams, IndexListData, IndexCreateRequest, IndexCreateResponse, IndexBase, IndexUpdateRequest } from '@/api/snow/index/types'

/**
 * 获取指数列表
 * 根据指数名称、指数类型、市场和状态查询指数列表信息，支持分页查询
 */
export const getIndexList = (params: IndexListParams): Promise<IResponse<IndexListData>> => {
  return request.get({
    url: '/api/index/list/',
    params
  })
}

/**
 * 创建指数
 * 创建新的指数数据，支持基础指数和股票指数两种类型
 */
export const createIndex = (data: IndexCreateRequest): Promise<IndexCreateResponse> => {
  return request.post({
    url: '/api/index/',
    data
  })
}

/**
 * 更新指数详情（仅返回操作结果）
 * 根据 indexId 更新单个指数详情
 */
export const updateIndex = (indexId: number, data: IndexUpdateRequest): Promise<IResponse<boolean>> => {
  return request.put({
    url: `/api/index/${indexId}`,
    data
  })
}

/**
 * 获取指数详情
 * 支持通过 id 或 indexCode 查询单个指数详细信息
 */
export const getIndexDetail = (params: { id?: number; indexCode?: string }): Promise<IResponse<IndexBase>> => {
  return request.get({
    url: '/api/index/',
    params
  })
}

/**
 * 删除指数（ORM级联删除）
 * 根据 indexId 删除单个指数，返回布尔结果
 */
export const deleteIndexById = (indexId: number): Promise<IResponse<boolean>> => {
  return request.delete({
    url: `/api/index/${indexId}`
  })
}