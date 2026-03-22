import request from '@/config/axios'
export const getByGridTypeId = (id: number | any, params: {}): Promise<IResponse<boolean>> => {
  return request.get({ url: 'charts/grid_record/' + id, params })
}
