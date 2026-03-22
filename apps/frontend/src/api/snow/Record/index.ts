
import request from '@/config/axios'
import { get } from 'lodash-es'


export * from './types'
import type { RecordListParams, RecordListData, ImportPreviewItem, ImportConfirmRequest } from './types'

export const getRecordList = (params: RecordListParams): Promise<IResponse<RecordListData>> => {
  return request.get({ url: '/api/record_list', params: params })
}

export const getRecordById = (id: any): Promise<IResponse<any>> => {
  return request.get({ url: '/api/record/' + id })
}

export const saveOrUpdateRecord = (data: any): Promise<IResponse<any>> => {
  if (get(data, 'recordId', null) == null && get(data, 'id', null) == null) {
    // 增加
    return request.post({ url: '/api/record', data })
  }
  // 更新
  // 确保id存在
  if (!data.id && data.recordId) {
    data.id = data.recordId
  }
  return request.put({ url: '/api/record', data })
}

export const deleteById = (id: any): Promise<IResponse<any>> => {
  return request.delete({ url: '/api/record/' + id })
}

export const exportRecordList = (params: RecordListParams): Promise<any> => {
  return request.get({ url: '/api/record_file/export', params: params, responseType: 'blob' })
}


export const exportRecordCheck = (params: RecordListParams): Promise<IResponse<{ count: number }>> => {
  return request.get({ url: '/api/record_file/export/check', params: params })
}


export const importRecordPreview = (data: FormData): Promise<IResponse<ImportPreviewItem[]>> => {
  return request.post({ url: '/api/record_file/import/preview', data })
}


export const importRecordConfirm = (data: ImportConfirmRequest): Promise<IResponse<{ count: number }>> => {
  return request.post({ url: '/api/record_file/import/confirm', data })
}
