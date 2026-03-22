import { CrudSchema } from '@/hooks/web/useCrudSchemas'
import { h } from 'vue'
import { ElTag } from 'element-plus'
import dayjs from 'dayjs'

export const createNotificationCrudSchemas = (p: {
  getBusinessTypeName: (n: number) => string
  getNoticeTypeName: (n: number) => string
  getNoticeStatusName: (n: number) => string
  tagType: (row: any) => string | undefined
}): CrudSchema[] => [
  {
    field: 'index',
    label: '序号',
    type: 'index',
    form: { show: false },
  },
  {
    field: 'timestamp',
    label: '发送时间',
    formatter: (row: Recordable, __: TableColumn, cellValue: number) => {
      return h(
        'div',
        { style: { color: row.noticeStatus == 2 && row.noticeType == 0 ? '#606266' : '' } },
        dayjs(cellValue).format('YYYY-MM-DD HH:mm:ss')
      )
    },
  },
  {
    field: 'title',
    label: '标题',
    formatter: (row: Recordable, __: TableColumn, cellValue: number) => {
      return h(
        'div',
        { style: { color: row.noticeStatus == 2 && row.noticeType == 0 ? '#606266' : '' } },
        cellValue as any
      )
    },
  },
  {
    field: 'businessType',
    label: '业务类型',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return h(ElTag, {}, () => p.getBusinessTypeName(cellValue))
    },
  },
  {
    field: 'noticeType',
    label: '通知类型',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return h(ElTag, {}, () => p.getNoticeTypeName(cellValue))
    },
  },
  {
    field: 'noticeStatus',
    label: '通知状态',
    formatter: (row: Recordable, __: TableColumn, cellValue: number) => {
      return h(ElTag, { type: p.tagType(row) as any }, () => p.getNoticeStatusName(cellValue))
    },
  },
  {
    field: 'actions',
    label: '操作',
    form: { show: false },
  },
]
