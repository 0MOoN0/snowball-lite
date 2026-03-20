import { h } from 'vue'
import { ElTag, ElButton } from 'element-plus'
import { webHelper } from '@/utils/webHelper'
import type { CrudSchema } from '@/hooks/web/useCrudSchemas'

// 网格类型详情数据表格基础 CrudSchema
export const createGridCrudSchemas = (): CrudSchema[] => [
  { field: 'gear', label: '档位' },
  {
    field: 'triggerPurchasePrice',
    label: '触发买入价格',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  {
    field: 'purchasePrice',
    label: '买入价格',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  {
    field: 'purchaseAmount',
    label: '买入金额',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  { field: 'purchaseShares', label: '买入份额' },
  {
    field: 'triggerSellPrice',
    label: '触发卖出价格',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  {
    field: 'sellPrice',
    label: '卖出价格',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  { field: 'sellShares', label: '卖出份额' },
  { field: 'actualSellShares', label: '实际卖出份额' },
  {
    field: 'sellAmount',
    label: '卖出金额',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  {
    field: 'profit',
    label: '盈利',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  {
    field: 'saveShareProfit',
    label: '留股盈利',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      webHelper.numFormatWithCurrency(cellValue, null, 10000, 3),
  },
  { field: 'saveShare', label: '留股份额' },
  { field: 'isCurrent', label: '是否当前档位' },
  {
    field: 'monitorType',
    label: '监控类型',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) =>
      h(ElTag, {}, () => (cellValue == 0 ? '买入' : cellValue == 1 ? '卖出' : '未知')),
  },
]

// 交易列表 CrudSchema（附加操作列）
export const createTradeListCrudSchema = (base: CrudSchema[], onEdit: (row: Recordable) => void): CrudSchema[] => {
  const schemas = [...base]
  schemas.push({
    field: 'actions',
    label: '操作',
    formatter: (row: Recordable) =>
      h(ElButton, { type: 'warning', size: 'small', link: true, onClick: () => onEdit(row) }, () => '确认交易记录'),
  })
  return schemas
}

// 表格行样式：isCurrent 使用 info（history-row），否则 primary（cur-row）
export const gridRowClassName = (row: Recordable): string => {
  if (row.row?.isCurrent) return 'history-row'
  return 'cur-row'
}

// 初始化确认通知数据
export const initConfirmNotificationData = (gridInfoList: Array<Record<string, any>> = []) => {
  return Array.from({ length: gridInfoList.length }).map((_, index: number) => ({
    tradeRecord: [],
    currentChange: gridInfoList[index]?.current_change?.map((detail: any) => detail.id),
  }))
}
