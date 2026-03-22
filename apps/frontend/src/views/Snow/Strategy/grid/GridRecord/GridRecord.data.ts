import { reactive } from 'vue'
import { CrudSchema } from '@/hooks/web/useCrudSchemas'
import { useValidator } from '@/hooks/web/useValidator'
import { GridRecord } from '@/api/snow/Record/types'

const { required } = useValidator()

const formatNumCurrency = (num: number) => {
  const options: Intl.NumberFormatOptions = {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 3,
  }
  return num.toLocaleString('zh-CN', options)
}

const formatNumPlain = (num: number) => {
  const options: Intl.NumberFormatOptions = {
    style: 'decimal',
  }
  return num.toLocaleString('zh-CN', options)
}

export const useGridRecordSchemas = (gridTypeId: number, assetId?: number | null) => {
  const crudSchemas = reactive<CrudSchema[]>([
    {
      field: 'index',
      label: '序号',
      type: 'index',
      form: {
        show: false,
      },
    },
    {
      field: 'groupType',
      label: '分组类型',
      table: {
        show: false,
      },
      form: {
        component: 'Select',
        componentProps: {
          disabled: true,
          options: [
            {
              label: '其他',
              value: 0,
            },
            {
              label: '网格',
              value: 1,
            },
          ],
        },
      },
    },
    {
      field: 'transactionsDate',
      label: '交易日期',
      form: {
        component: 'DatePicker',
        componentProps: {
          type: 'datetime',
          valueFormat: 'YYYY-MM-DD HH:mm:ss',
        },
        formItemProps: {
          rules: [required()],
        },
      },
    },
    {
      field: 'transactionsPrice',
      label: '交易价格（元）',
      formatter: (row: GridRecord) => {
        return formatNumCurrency(Number(row.transactionsPrice) / 1000)
      },
      form: {
        component: 'InputNumber',
        componentProps: {
          precision: 3,
          step: 0.001,
        },
        formItemProps: {
          rules: [required()],
        },
      },
    },
    {
      field: 'transactionsShare',
      label: '交易份额',
      formatter: (row: GridRecord) => {
        const direction = row.transactionsDirection == 0 ? -1 : row.transactionsDirection
        return formatNumPlain(Number(row.transactionsShare) * direction)
      },
      form: {
        component: 'InputNumber',
        componentProps: {
          step: 100,
        },
        formItemProps: {
          rules: [required()],
        },
      },
    },
    {
      field: 'transactionsFee',
      label: '交易费用（元）',
      formatter: (row: GridRecord) => {
        return formatNumCurrency(Number(row.transactionsFee) / 1000)
      },
      form: {
        component: 'InputNumber',
        componentProps: {
          precision: 3,
          step: 0.001,
        },
        formItemProps: {
          rules: [required()],
        },
        value: 0.2,
      },
    },
    {
      field: 'transactionsAmount',
      label: '交易金额（元）',
      formatter: (row: GridRecord) => {
        const direction = row.transactionsDirection == 0 ? -1 : row.transactionsDirection
        return formatNumCurrency((Number(row.transactionsAmount) / 1000) * -direction)
      },
      form: {
        component: 'Input',
        componentProps: {
          disabled: true,
        },
      },
    },
    {
      field: 'gridTypeId',
      table: {
        show: false,
      },
      form: {
        value: gridTypeId,
        hidden: true,
      },
    },
    {
      field: 'assetId',
      table: {
        show: false,
      },
      form: {
        value: assetId,
        hidden: true,
      },
    },
    {
      field: 'transactionsDirection',
      label: '交易方向',
      table: {
        show: false,
      },
      form: {
        component: 'Select',
        componentProps: {
          options: [
            {
              label: '卖出',
              value: 0,
            },
            {
              label: '买入',
              value: 1,
            },
          ],
        },
        formItemProps: {
          rules: [required()],
        },
      },
    },
    {
      field: 'actions',
      label: '操作',
      form: {
        show: false,
      },
    },
  ])

  return { crudSchemas }
}
