import type { EnumOption } from '@/views/Snow/Index/types'
// FormSchema 类型已在全局类型定义中声明

/**
 * 股票指数特有字段配置（与后端新增接口字段对齐）
 */
export const createStockFields = (enumOptions?: { rebalanceFrequencyEnum?: EnumOption[] }): FormSchema[] => {
  return [
    {
      field: 'divider-stock',
      component: 'Divider',
      label: '股票指数特有信息',
      colProps: { span: 24 },
      componentProps: {
        style: { fontWeight: 600, color: '#409eff', fontSize: '16px' },
      },
    },
    {
      field: 'constituentCount',
      label: '成分股数量',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入成分股数量',
        min: 0,
      },
    },
    {
      field: 'marketCap',
      label: '总市值（万元）',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入总市值（万元）',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'freeFloatMarketCap',
      label: '自由流通市值（万元）',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入自由流通市值（万元）',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'averagePe',
      label: '平均市盈率',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入平均市盈率',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'averagePb',
      label: '平均市净率',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入平均市净率',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'dividendYield',
      label: '股息率（%）',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入股息率（%）',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'turnoverRate',
      label: '换手率（%）',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入换手率（%）',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'volatility',
      label: '波动率（%）',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入波动率（%）',
        min: 0,
        precision: 2,
      },
    },
    {
      field: 'beta',
      label: '贝塔系数',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请输入贝塔系数',
        precision: 3,
      },
    },
    {
      field: 'rebalanceFrequency',
      label: '调仓频率',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请选择调仓频率',
        options: enumOptions?.rebalanceFrequencyEnum || [],
      },
    },
    {
      field: 'lastRebalanceDate',
      label: '最后调仓日期',
      component: 'DatePicker',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请选择最后调仓日期',
        type: 'date',
        format: 'YYYY-MM-DD',
        valueFormat: 'YYYY-MM-DD',
      },
    },
    {
      field: 'nextRebalanceDate',
      label: '下次调仓日期',
      component: 'DatePicker',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        placeholder: '请选择下次调仓日期',
        type: 'date',
        format: 'YYYY-MM-DD',
        valueFormat: 'YYYY-MM-DD',
      },
    },
  ]
}