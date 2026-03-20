export type SelectOption = { label: string; value: any }

export interface AssetFormOptions {
  assetTypeOptions: SelectOption[]
  currencyOptions: SelectOption[]
  marketOptions: SelectOption[]
  assetStatusOptions: SelectOption[]
  fundTypeOptions: SelectOption[]
  fundTradingModeOptions: SelectOption[]
  fundStatusOptions: SelectOption[]
  required: () => any
  onAssetTypeChange: (val: number) => void
}

export const BASE_FIELD_NAMES = [
  'assetName',
  'assetType',
  'assetCode',
  'assetShortCode',
  'currency',
  'market',
  'assetStatus',
]

export const FUND_FIELD_NAMES = [
  'fundType',
  'tradingMode',
  'fundCompany',
  'fundManager',
  'establishmentDate',
  'fundScale',
  'fundStatus',
  'investmentObjective',
  'investmentStrategy',
]

export const ETF_FIELD_NAMES = [
  'trackingIndexCode',
  'trackingIndexName',
  'indexId',
  'primaryExchange',
  'dividendFrequency',
  'trackingError',
]

export const LOF_FIELD_NAMES = [
  'listingExchange',
  'subscriptionFeeRate',
  'redemptionFeeRate',
  'navCalculationTime',
  'tradingSuspensionInfo',
]

const createDivider = (label: string): FormSchema => ({
  field: `divider_${label.replace(/\s+/g, '_').toLowerCase()}`,
  component: 'Divider',
  label,
  colProps: {
    span: 24,
  },
  componentProps: {
    contentPosition: 'left',
    style: {
      margin: '24px 0 20px 0',
      fontSize: '15px',
      fontWeight: '600',
      color: '#409eff',
      borderColor: '#e4e7ed',
    },
  },
})

export const getFormSchema = (assetType: number, opts: AssetFormOptions): FormSchema[] => {
  const schema: FormSchema[] = []

  const baseFields: FormSchema[] = [
    {
      field: 'assetName',
      label: '资产名称',
      component: 'Input',
      value: null,
      colProps: { span: 24 },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'assetType',
      label: '资产类型',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        options: opts.assetTypeOptions || [],
        onChange: (val: number) => opts.onAssetTypeChange(val),
      },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'assetCode',
      label: '资产代码',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'assetShortCode',
      label: '资产简码',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'currency',
      label: '货币类型',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        options: opts.currencyOptions || [],
      },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'market',
      label: '市场',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        options: opts.marketOptions || [],
      },
    },
    {
      field: 'assetStatus',
      label: '资产状态',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: {
        options: opts.assetStatusOptions || [],
      },
      formItemProps: { rules: [opts.required()] },
    },
  ]

  const fundFields: FormSchema[] = [
    {
      field: 'fundType',
      label: '基金类型',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: { options: opts.fundTypeOptions || [] },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'tradingMode',
      label: '交易模式',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: { options: opts.fundTradingModeOptions || [] },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'fundCompany',
      label: '基金公司',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'fundManager',
      label: '基金经理',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'establishmentDate',
      label: '成立日期',
      component: 'DatePicker',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'fundScale',
      label: '基金规模',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'fundStatus',
      label: '基金状态',
      component: 'Select',
      value: null,
      colProps: { span: 12 },
      componentProps: { options: opts.fundStatusOptions || [] },
      formItemProps: { rules: [opts.required()] },
    },
    {
      field: 'investmentObjective',
      label: '投资目标',
      component: 'Input',
      value: null,
      colProps: { span: 24 },
      componentProps: { type: 'textarea', rows: 3 },
    },
    {
      field: 'investmentStrategy',
      label: '投资策略',
      component: 'Input',
      value: null,
      colProps: { span: 24 },
      componentProps: { type: 'textarea', rows: 3 },
    },
  ]

  const etfFields: FormSchema[] = [
    {
      field: 'trackingIndexCode',
      label: '跟踪指数代码',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'trackingIndexName',
      label: '跟踪指数名称',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'indexId',
      label: '指数ID',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'primaryExchange',
      label: '主要交易所',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'dividendFrequency',
      label: '分红频率',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'trackingError',
      label: '跟踪误差',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: { step: 0.01, precision: 4 },
    },
  ]

  const lofFields: FormSchema[] = [
    {
      field: 'listingExchange',
      label: '上市交易所',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'subscriptionFeeRate',
      label: '申购费率',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: { step: 0.1, precision: 2 },
    },
    {
      field: 'redemptionFeeRate',
      label: '赎回费率',
      component: 'InputNumber',
      value: null,
      colProps: { span: 12 },
      componentProps: { step: 0.1, precision: 2 },
    },
    {
      field: 'navCalculationTime',
      label: '净值计算时间',
      component: 'Input',
      value: null,
      colProps: { span: 12 },
    },
    {
      field: 'tradingSuspensionInfo',
      label: '交易暂停信息',
      component: 'Input',
      value: null,
      colProps: { span: 24 },
    },
  ]

  schema.push(createDivider('📋 基础信息'))
  schema.push(...baseFields)

  if ([1, 4, 5].includes(assetType)) {
    schema.push(createDivider('💰 基金信息'))
    schema.push(...fundFields)

    if (assetType === 4) {
      schema.push(createDivider('📈 ETF特有信息'))
      schema.push(...etfFields)
    } else if (assetType === 5) {
      schema.push(createDivider('🏦 LOF特有信息'))
      schema.push(...lofFields)
    }
  }

  return schema
}