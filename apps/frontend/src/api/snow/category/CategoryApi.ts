import request from '@/config/axios'
import { Category } from '@/api/snow/category/types'
export const getCategoryList = (): Promise<IResponse<any>> => {
  return request.get({ url: 'category/list' })
}

export const updateOrSave = (data: Category): Promise<IResponse<boolean>> => {
  if (typeof data.id === 'undefined') {
    return request.post({ url: 'category/', data })
  }
  return request.put({ url: 'category/', data })
}

export const deleteCategory = (id: number | any): Promise<IResponse<boolean>> => {
  return request.delete({ url: 'category/' + id })
}
