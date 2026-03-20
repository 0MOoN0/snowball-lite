import request from '@/config/axios'
export const getAssetList = (params: any): Promise<IResponse> => {
  return request.get({ url: '/api/asset/list/', params })
}

export const getAssetSelectList = (params: any): Promise<IResponse> => {
  return request.get({ url: '/api/asset/list/select', params })
}

export const saveAsset = (data: any): Promise<IResponse> => {
  return request.post({ url: 'asset', data })
}

export const updateAsset = (data: any): Promise<IResponse> => {
  return request.put({ url: 'asset', data })
}

export const saveOrUpdateAsset = (data: any): Promise<IResponse> => {
  if (data && data.id) {
    // 使用新的API接口：PUT /api/asset/{asset_id}
    return request.put({ url: `/api/asset/${data.id}`, data })
  }
  // 创建新资产的接口暂时保持原样，等待后续API定义
  return request.post({ url: 'asset', data })
}

export const queryLike = (params: any): Promise<IResponse<any>> => {
  return request.get({ url: 'asset', params })
}

/**
 * 根据ID列表删除资产数据
 * @param data ID列表
 * @returns 请求结果
 */
export const deleteByIds = (data: any): Promise<IResponse<any>> => {
  return request.delete({ url: '/api/asset/list/', data })
}

/**
 * 根据ID删除对应的资产数据
 * @param id 要删除的资产数据ID
 * @returns 请求结果
 */
export const deleteById = (id: any): Promise<IResponse<any>> => {
  return request.delete({ url: 'asset/' + id })
}

/**
 * 根据ID获取资产数据
 * @param id 资产数据ID
 */
export const getById = (id: any): Promise<IResponse<any>> => {
  return request.get({ url: '/api/asset/' + id })
}