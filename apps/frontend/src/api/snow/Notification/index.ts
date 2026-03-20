import request from '@/config/axios'

// 获取通知列表
export const getNotificationList = (params: any): Promise<IResponse<any>> => {
  return request.get({ url: '/api/notification_list', params: params })
}

// 根据通知状态获取通知数量
export const getNotificationCount = (params: any): Promise<IResponse<any>> => {
  return request.get({ url: '/api/notification_count', params: params })
}

// 根据ID获取通知详情
export const getNotificationDetail = (id: any): Promise<IResponse<any>> => {
  return request.get({ url: '/api/notification/' + id })
}

// 根据ID确认通知
export const confirmNotification = (id: any, data: any): Promise<IResponse<any>> => {
  return request.put({ url: '/api/notification/' + id, data: data })
}

// 按业务类型分组获取未读通知数量
export const getUnreadGroupCount = (params?: any): Promise<IResponse<any>> => {
  const query = { groupBy: 'businessType', ...(params || {}) }
  return request.get({ url: '/api/notification_count/unread_groups', params: query })
}

// 批量已读通知（支持 ids 或 businessType）
export const batchReadNotifications = (payload: any): Promise<IResponse<any>> => {
  return request.put({ url: '/api/notification/batch_read', data: payload })
}
