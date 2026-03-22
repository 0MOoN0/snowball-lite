import request from '@/config/axios'

export const getGridTypeDetailList = (params: any): Promise<IResponse<any>> => {
  return request.get({ url: '/gridTypeDetail/1/list', params })
}

export const getGridList = (): Promise<IResponse<any>> => {
  return request.get({ url: '/grid_list' })
}

export const getGridRelationList = (): Promise<IResponse<any>> => {
  return request.get({ url: '/api/grid/relation' })
}

export const getById = (id: number): Promise<IResponse<any>> => {
  return request.get({ url: '/grid/' + id })
}

export const deleteById = (id: number): Promise<IResponse<any>> => {
  return request.delete({ url: '/grid/' + id })
}

export const saveOrUpdate = (data: any): Promise<IResponse<any>> => {
  if (data.id) {
    return request.put({ url: '/grid', data })
  }
  return request.post({ url: '/grid', data })
}
