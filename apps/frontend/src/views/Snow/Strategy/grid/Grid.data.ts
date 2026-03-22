// === 枚举与辅助函数 ===

// 资产类型枚举列表
export const assetTypeList = ['指数', '基金', '股票']

// 获取资产类型描述
export const getAssetTypeName = (assetType: number) => {
  if (assetTypeList.length <= 0 || assetType >= assetTypeList.length) {
    return '无'
  }
  return assetTypeList[assetType]
}

// 货币类型
export const currency = ['RMB', 'USD', 'EUR', 'HKD']

export const getCurrentName = (currencyType: number): string => {
  if (currencyType < 0 || currencyType >= currency.length) {
    return '未知'
  }
  return currency[currencyType]
}

export const getGridTypeStatus = (gridTypeStatus: number) => {
  switch (gridTypeStatus) {
    case 0:
      return '启用'
    case 1:
      return '停用'
    case 2:
      return '只卖出'
    case 3:
      return '只买入'
    default:
      return '未知'
  }
}

// === Schema 定义 ===

export const gridInfoSchema: DescriptionsSchema[] = [
  {
    field: 'gridStatus',
    label: '网格状态',
  },
  {
    field: 'gridTypeStatus',
    label: '网格类型状态',
  },
]

export const assetDataSchema: DescriptionsSchema[] = [
  {
    field: 'assetName',
    label: '资产名称',
  },
  {
    field: 'categoryName',
    label: '分类名称',
  },
  {
    field: 'currency',
    label: '货币类型',
  },
  {
    field: 'codeIndex',
    label: '指数代码',
  },
  {
    field: 'codeXQ',
    label: '雪球代码',
  },
  {
    field: 'codeTTJJ',
    label: '天天基金代码',
  },
]

export const gridTypeAnalysisSchema: DescriptionsSchema[] = [
  {
    field: 'recordDate',
    label: '记录时间',
  },
  {
    field: 'netValue',
    label: '基金净值',
  },
  {
    field: 'irr',
    label: '内部收益率',
  },
  {
    field: 'investmentYield',
    label: '投资收益率',
  },
  {
    field: 'profit',
    label: '收益总额（元）',
  },
  {
    field: 'unitCost',
    label: '单位成本（元）',
  },
  {
    field: 'presentValue',
    label: '基金现值（元）',
  },
  {
    field: 'holdingCost',
    label: '持有成本（元）',
  },
  {
    field: 'attributableShare',
    label: '持有份额',
  },
  {
    field: 'dividend',
    label: '分红与赎回（元）',
  },
  {
    field: 'dividendYield',
    label: '股息率',
  },
  {
    field: 'turnoverRate',
    label: '换手率',
  },
  {
    field: 'maximumOccupancy',
    label: '历史最大占用（元）',
  },
  {
    field: 'estimateMaximumOccupancy',
    label: '预计最大占用（元）',
  },
  {
    field: 'sellTimes',
    label: '出售次数（次）',
  },
  {
    field: 'holdingTimes',
    label: '待出网次数（次）',
  },
  {
    field: 'upSoldPercent',
    label: '距离卖出',
  },
  {
    field: 'downBoughtPercent',
    label: '距离买入',
  },
  {
    field: 'operation',
    label: '操作',
  },
]
