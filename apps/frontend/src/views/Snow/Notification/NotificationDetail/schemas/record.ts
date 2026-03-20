import type { CrudSchema } from '@/hooks/web/useCrudSchemas'

export const createRecordSchemas = (required: () => any): CrudSchema[] => [
  {
    field: 'index',
    label: '序号',
    type: 'index',
    form: { show: false },
  },
  {
    field: 'has_transaction',
    label: '是否成交',
    table: { show: false },
    form: { component: 'Switch', value: false },
  },
  {
    field: 'transactionsDate',
    label: '交易日期',
    form: {
      component: 'DatePicker',
      componentProps: { type: 'datetime', valueFormat: 'YYYY-MM-DD HH:mm:ss' },
      formItemProps: { rules: [required()] },
    },
  },
  {
    field: 'transactionsPrice',
    label: '交易价格（元）',
    form: {
      component: 'Input',
      componentProps: { style: 'width:150px' },
      formItemProps: { rules: [required()] },
    },
  },
  {
    field: 'transactionsShare',
    label: '交易份额',
    form: {
      component: 'Input',
      componentProps: { style: 'width:150px' },
      formItemProps: { rules: [required()] },
    },
  },
  {
    field: 'transactionsFee',
    label: '交易费用（元）',
    form: {
      component: 'Input',
      componentProps: { style: 'width:150px' },
      formItemProps: { rules: [required()] },
      value: 0.2,
    },
  },
  {
    field: 'transactionsAmount',
    label: '交易金额（元）',
    form: {
      component: 'Input',
      componentProps: { disabled: true, style: 'width:150px' },
    },
  },
  {
    field: 'transactionsDirection',
    label: '交易方向',
    form: {
      component: 'Select',
      componentProps: {
        options: [
          { label: '卖出', value: 0 },
          { label: '买入', value: 1 },
        ],
      },
      formItemProps: { rules: [required()] },
    },
  },
]
