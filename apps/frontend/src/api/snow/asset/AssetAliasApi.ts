import request from '@/config/axios'

export const getAliasList = (params: any): Promise<IResponse> => {
  return request.get({ url: '/api/asset/alias/list', params })
}

export const createAlias = (data: any): Promise<IResponse> => {
  return request.post({ url: '/api/asset/alias/', data })
}

export const updateAliasById = (id: number, data: any): Promise<IResponse> => {
  return request.put({ url: `/api/asset/alias/${id}`, data })
}

export const saveOrUpdateAlias = (data: any): Promise<IResponse> => {
  if (data && data.id) {
    return updateAliasById(data.id, data)
  }
  return createAlias(data)
}

export const getAliasById = (id: number): Promise<IResponse> => {
  return request.get({ url: `/api/asset/alias/${id}` })
}

export const deleteAliasById = (id: number): Promise<IResponse> => {
  return request.delete({ url: `/api/asset/alias/${id}` })
}

export const batchAssociate = (data: { assetId: number; aliasIds: number[] }): Promise<IResponse> => {
  return request.put({ url: '/api/asset/alias/batch-associate', data })
}