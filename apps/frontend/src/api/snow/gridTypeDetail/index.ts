import request from '@/config/axios'

export const getGridTypeDetailList = (params: any): Promise<IResponse<any>> => {
  return request.get({ url: '/grid_type_detail_list', params: params })
}

export const saveOrUpdateGridTypeDetailList = (data: any): Promise<IResponse<any>> => {
  return request.post({ url: '/grid_type_detail_list', data: data })
}

export const deleteByIds = (data: any): Promise<IResponse<any>> => {
  return request.delete({ url: '/grid_type_detail_list', data: data })
}

export const setCurrent = (gridTypeDetail: number): Promise<IResponse<any>> => {
  return request.put({ url: '/grid_type_detail/is_current/' + gridTypeDetail })
}
