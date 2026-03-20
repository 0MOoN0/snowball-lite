
export interface TradeReference {
  id?: number
  recordId?: number
  groupType?: number
  groupId?: number
}

export interface TradeReferenceUpdateItem {
  groupType?: number
  groupId: number
}

export interface GridRecord {
  transactionsFee: number | string
  transactionsShare: number | string
  transactionsDate: string
  transactionsPrice: number | string
  transactionsDirection: number
  transactionsAmount: number | string
  strategyType?: number
  strategyKey?: number
  id?: number
  recordId?: number
  gridTypeId?: number
  assetId?: number
  assetName?: string
  primaryAliasCode?: string
  primaryProviderName?: string
  groupTypes?: number[]
  tradeReferences?: TradeReference[]
}

export interface RecordCreate {
  assetId: number
  transactionsShare: number
  transactionsPrice: number
  transactionsFee: number
  transactionsDirection?: number
  transactionsDate?: string
  transactionsAmount?: number
  /** 分组类型: 0-其他, 1-网格 */
  groupType?: number
  /** 业务对象ID */
  groupId?: number
}

export interface RecordUpdate {
  id: number
  transactionsShare?: number
  transactionsPrice?: number
  transactionsFee?: number
  transactionsDirection?: number
  transactionsDate?: string
  transactionsAmount?: number
  tradeReferences?: TradeReferenceUpdateItem[]
  [key: string]: any
}

export interface RecordListParams {
  page: number
  pageSize: number
  /** 分组类型: 0-其他, 1-网格 */
  groupType?: number
  /** 业务对象ID */
  groupId?: number
  assetName?: string
  assetAlias?: string
  startDate?: string
  endDate?: string
  transactionsDirection?: number
}

export interface RecordListData {
  items: GridRecord[]
  total: number
  page: number
  size: number
}


export interface ImportPreviewParsedData {
  assetId?: number
  assetName?: string
  transactionsDate?: string
  transactionsPrice?: number
  transactionsShare?: number
  transactionsAmount?: number

  transactionsFee?: number
  transactionsDirection?: number
  matchSource?: string
}

export interface ImportPreviewItem {
  rowIndex: number
  status: 'valid' | 'error' | 'warning'
  message?: string
  rawData?: Record<string, any>
  parsedData?: ImportPreviewParsedData
  // Frontend extended properties for Table display
  transactionsDate?: string
  transactionsPrice?: number
  transactionsShare?: number
  transactionsAmount?: number
  transactionsFee?: number

  transactionsDirection?: number
  assetName?: string
  matchSource?: string


  // Association (Frontend)
  tradeReferences?: { groupType: number, groupId: number, groupName?: string }[]

  // Deprecated single fields (keep for compatibility if needed, or remove)
  // groupType?: number
  // groupId?: number
  // groupName?: string 

  _rawData?: Record<string, any>
}


export interface ImportConfirmItem {
  assetId: number
  transactionsDate: string
  transactionsPrice: number // 厘
  transactionsShare: number
  transactionsAmount: number // 厘
  transactionsFee: number // 厘
  transactionsDirection: number


  // New backend spec uses 'groups'
  groups?: { groupType: number, groupId: number }[]
}

export interface ImportConfirmRequest {
  importMode?: number // 0-增量, 1-全量覆盖, 2-部分替换, 3-范围替换
  rangeStart?: string
  rangeEnd?: string
  items: ImportConfirmItem[]
}
