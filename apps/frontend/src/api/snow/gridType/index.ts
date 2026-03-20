import request from '@/config/axios'
import _ from 'lodash-es'
export const getGridType = (params = {}): Promise<IResponse<any>> => {
  const id = _.get(params, 'id', null)
  if (id) {
    return request.get({ url: '/grid_type/' + id, params: params })
  }
  return request.get({ url: '/grid_type', params: params })
}

export const saveOrUpdateGridType = (data: any): Promise<IResponse<any>> => {
  const gridId = _.get(data, 'id', null)
  if (gridId) {
    return request.put({ url: '/grid_type', data: data })
  }
  return request.post({ url: '/grid_type', data: data })
}

export const deleteGridTypeById = (gridTypeId: any): Promise<IResponse<any>> => {
  return request.delete({ url: '/grid_type/' + gridTypeId })
}
