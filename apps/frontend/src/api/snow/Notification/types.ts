// Notification类型定义文件
export interface SnowNotification {
  /** 通知id */
  id?: number
  /** 业务类型 */
  businessType?: number
  /** 创建时间 */
  createTime?: string
  /** 通知等级 */
  noticeLevel?: number
  /** 通知状态 */
  noticeStatus?: number
  /** 更新时间*/
  updateTime?: string
  /** 通知内容 */
  content?: GridContent
  /** 通知类型 */
  noticeType?: number
  /** 通知标题 */
  title?: string
}

export interface GridContent {
  /** 通知标题 */
  title: string
  /** 网格通知内容 */
  grid_info: GridInfo[]
}

export interface GridInfo {
  /** 资产名称 */
  asset_name?: string
  /**网格类型名称 */
  grid_type_name?: string
  /** 交易列表 */
  trade_list?: Array<any>
  /** 当前网格类型详情数据监控变化列表 */
  current_change?: Array<any>
}

export interface UnreadGroupCountItem {
  /** 业务类型（枚举值） */
  businessType: number
  /** 未读数量 */
  unreadCount: number
}
