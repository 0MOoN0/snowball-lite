import { reactive, h } from 'vue'
import { CrudSchema } from '@/hooks/web/useCrudSchemas'
import { useValidator } from '@/hooks/web/useValidator'
import { GridRecord } from '@/api/snow/Record/types'
import { ElTag } from 'element-plus'
import { getAssetSelectList } from '@/api/snow/asset/AssetApi'

const { required } = useValidator()

// 数字格式化工具函数
const formatNumCurrency = (num: number) => {
  const options = {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 3,
  } as const
  return num.toLocaleString('zh-CN', options)
}

const formatNumPlain = (num: number) => {
  const options = {
    style: 'decimal',
  } as const
  return num.toLocaleString('zh-CN', options)
}

export const useRecordSchemas = () => {
  const getAssetOptions = async (query: string) => {
    // Find schema item first to set loading
    const schemaItem = crudSchemas.find((item) => item.field === 'assetName')
    if (schemaItem?.search?.componentProps) {
      schemaItem.search.componentProps.loading = true
    }

    try {
      const res = await getAssetSelectList({
        assetName: query,
        page: 1,
        pageSize: 20,
      })
      if (res.data && res.data.items) {
        if (schemaItem && schemaItem.search && schemaItem.search.componentProps) {
          schemaItem.search.componentProps.options = res.data.items.map((item: any) => ({
            label: item.assetName,
            value: item.assetName,
          }))
        }
      }
    } finally {
      if (schemaItem?.search?.componentProps) {
        schemaItem.search.componentProps.loading = false
      }
    }
  }

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
      field: 'recordId',
      table: {
        show: false,
      },
      form: {
        hidden: true,
      },
    },
    {
      field: 'assetName',
      label: '资产名称',
      search: {
        show: true,
        component: 'Select',
        componentProps: {
          placeholder: '请输入资产名称搜索',
          filterable: true,
          remote: true,
          remoteMethod: getAssetOptions,
          loading: false,
          options: [],
        },
      },
      table: {
        show: true,
      },
      form: {
        show: true,
        colProps: {
          span: 12,
        },
      },
    },
    {
      field: 'primaryAliasCode',
      label: '主要别名代码',
      search: {
        show: false,
      },
      table: {
        show: true,
      },
      form: {
        show: false,
      },
    },
    {
      field: 'primaryProviderName',
      label: '主要提供商',
      search: {
        show: false,
      },
      table: {
        show: true,
      },
      form: {
        show: false,
      },
    },
    {
      field: 'assetAlias',
      label: '资产别名',
      search: {
        show: true,
        component: 'Input',
        componentProps: {
          placeholder: '请输入资产别名搜索',
        },
      },
      table: {
        show: false,
      },
      form: {
        show: false,
      },
    },
    {
      field: 'transactionsDate',
      label: '交易日期',
      search: {
        show: true,
        component: 'DatePicker',
        componentProps: {
          type: 'datetimerange',
          valueFormat: 'YYYY-MM-DD HH:mm:ss',
          startPlaceholder: '开始日期',
          endPlaceholder: '结束日期',
          shortcuts: [
            {
              text: '最近一周',
              value: () => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                return [start, end]
              },
            },
            {
              text: '最近一个月',
              value: () => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                return [start, end]
              },
            },
            {
              text: '最近三个月',
              value: () => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
                return [start, end]
              },
            },
          ],
        },
      },
      form: {
        component: 'DatePicker',
        componentProps: {
          type: 'datetime',
          valueFormat: 'YYYY-MM-DD HH:mm:ss',
        },
        formItemProps: {
          rules: [required()],
        },
        colProps: {
          span: 12,
        },
      },
    },
    {
      field: 'transactionsDirection',
      label: '交易方向',
      search: {
        show: true,
        component: 'Select',
        componentProps: {
          options: [
            { label: '卖出', value: 0 },
            { label: '买入', value: 1 },
          ],
        },
      },
      table: {
        show: false,
      },
      form: {
        component: 'Select',
        componentProps: {
          options: [
            { label: '卖出', value: 0 },
            { label: '买入', value: 1 },
          ],
        },
        formItemProps: {
          rules: [required()],
        },
        colProps: {
          span: 12,
        },
      },
    },
    {
      field: 'groupType',
      label: '分组类型',
      search: {
        show: true,
        component: 'Select',
        componentProps: {
          options: [
            { label: '其他', value: 0 },
            { label: '网格', value: 1 },
          ],
        },
      },
      table: {
        show: false,
      },
      form: {
        show: false,
      },
    },
    {
      field: 'groupTypes',
      label: '分组类型',
      search: {
        show: false,
      },
      table: {
        show: true,
      },
      formatter: (row: GridRecord) => {
        if (!row.groupTypes || row.groupTypes.length === 0) return '-'
        return h('div', { class: 'flex gap-1 justify-center' }, row.groupTypes.map((type) => {
          const label = type === 1 ? '网格' : '其他'
          const typeTag = type === 1 ? 'success' : 'info'
          return h(ElTag, { type: typeTag }, () => label)
        }))
      },
      form: {
        show: false,
      },
    },
    {
      field: 'assetId',
      table: {
        show: false,
      },
      form: {
        show: false,
        hidden: true,
      },
    },
    {
      field: 'transactionsPrice',
      label: '交易价格（元）',
      formatter: (row) => {
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
        colProps: {
          span: 12,
        },
        value: 0,
      },
    },
    {
      field: 'transactionsShare',
      label: '交易份额',
      formatter: (row) => {
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
        colProps: {
          span: 12,
        },
        value: 0,
      },
    },
    {
      field: 'transactionsFee',
      label: '交易费用（元）',
      formatter: (row) => {
        return formatNumCurrency(Number(row.transactionsFee) / 1000)
      },
      form: {
        component: 'InputNumber',
        componentProps: {
          precision: 1,
          step: 0.1,
        },
        formItemProps: {
          rules: [required()],
        },
        colProps: {
          span: 12,
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
        colProps: {
          span: 12,
        },
      },
    },
    {
      field: 'gridTypeId',
      table: {
        show: false,
      },
      form: {
        value: null, // 将在组件中动态设置
        hidden: true,
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
