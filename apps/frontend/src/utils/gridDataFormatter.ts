/**
 * 网格分析数据格式化工具
 * 根据API文档，返回的数据是原始数值，需要前端进行格式化处理
 * 
 * 数据单位说明：
 * - 金额字段：单位为分（如123456表示¥1,234.56）
 * - 价格字段：单位为毫（如123450表示¥12.345）
 * - 百分比字段：单位为万倍（如1234表示12.34%）
 * - IRR字段：单位为百倍（如1234表示12.34%）
 * - 份额字段：单位为百倍（如12345表示123.45份）
 * - 净值字段：单位为毫（如123450表示¥12.345）
 */

/**
 * 添加千分位分隔符
 * @param value 数值字符串
 * @returns 带千分位分隔符的字符串
 */
export const addThousandsSeparator = (value: string): string => {
  const parts = value.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return parts.join('.')
}

/**
 * 格式化金额（分转元）
 * @param amount 金额（分）
 * @returns 格式化后的金额字符串（带千分位分隔符）
 */
export const formatAmount = (amount: number | null | undefined): string => {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '0.00'
  }
  const formatted = (amount / 100).toFixed(2)
  return addThousandsSeparator(formatted)
}

/**
 * 格式化价格（毫转元）
 * @param price 价格（毫）
 * @returns 格式化后的价格字符串（带千分位分隔符）
 */
export const formatPrice = (price: number | null | undefined): string => {
  if (price === null || price === undefined || isNaN(price)) {
    return '0.0000'
  }
  const formatted = (price / 10000).toFixed(4)
  return addThousandsSeparator(formatted)
}

/**
 * 格式化百分比（万倍转百分比）
 * @param percentage 百分比（万倍）
 * @returns 格式化后的百分比字符串
 */
export const formatPercentage = (percentage: number | null | undefined): string => {
  if (percentage === null || percentage === undefined || isNaN(percentage)) {
    return '0.00%'
  }
  return (percentage / 100).toFixed(2) + '%'
}

/**
 * 格式化百分比（百倍转百分比）
 * @param percentage 百分比（百倍）
 * @returns 格式化后的百分比字符串
 */
export const formatPercentageFromHundreds = (percentage: number | null | undefined): string => {
  if (percentage === null || percentage === undefined || isNaN(percentage)) {
    return '0.00%'
  }
  return (percentage / 100).toFixed(2) + '%'
}

/**
 * 格式化份额（百倍转份额）
 * @param share 份额（百倍）
 * @returns 格式化后的份额字符串（带千分位分隔符）
 */
export const formatShare = (share: number | null | undefined): string => {
  if (share === null || share === undefined || isNaN(share)) {
    return '0.00'
  }
  const formatted = (share / 100).toFixed(2)
  return addThousandsSeparator(formatted)
}

/**
 * 格式化净值（毫转元）
 * @param netValue 净值（毫）
 * @returns 格式化后的净值字符串（带千分位分隔符）
 */
export const formatNetValue = (netValue: number | null | undefined): string => {
  if (netValue === null || netValue === undefined || isNaN(netValue)) {
    return '0.0000'
  }
  const formatted = (netValue / 10000).toFixed(4)
  return addThousandsSeparator(formatted)
}

/**
 * 格式化网格分析数据
 * @param data 原始网格分析数据
 * @returns 格式化后的网格分析数据
 */
export const formatGridAnalysisData = (data: any) => {
  if (!data) return {}

  return {
    ...data,
    // 金额字段（分转元）
    maximumOccupancy: formatAmount(data.maximumOccupancy),
    purchaseAmount: formatAmount(data.purchaseAmount),
    presentValue: formatAmount(data.presentValue),
    profit: formatAmount(data.profit),
    holdingCost: formatAmount(data.holdingCost),
    dividend: formatAmount(data.dividend),
    estimateMaximumOccupancy: formatAmount(data.estimateMaximumOccupancy),

    // 价格字段（毫转元）
    unitCost: formatPrice(data.unitCost),

    // 百分比字段
    irr: formatPercentageFromHundreds(data.irr), // IRR字段为百倍转百分比
    investmentYield: formatPercentage(data.investmentYield),
    turnoverRate: formatPercentage(data.turnoverRate),
    dividendYield: formatPercentage(data.dividendYield),
    upSoldPercent: formatPercentage(data.upSoldPercent),
    downBoughtPercent: formatPercentage(data.downBoughtPercent),

    // 份额字段（百倍转份额）
    attributableShare: formatShare(data.attributableShare),

    // 净值字段（毫转元）
    netValue: formatNetValue(data.netValue),

    // 保持原始数值的字段
    sellTimes: data.sellTimes,
    holdingTimes: data.holdingTimes,
    businessType: data.businessType,
    recordDate: data.recordDate
  }
}

/**
 * 格式化网格类型分析数据
 * @param data 原始网格类型分析数据
 * @returns 格式化后的网格类型分析数据
 */
export const formatGridTypeAnalysisData = (data: any) => {
  if (!data) return {}

  return {
    ...data,
    // 金额字段（分转元）
    maximumOccupancy: formatAmount(data.maximumOccupancy),
    purchaseAmount: formatAmount(data.purchaseAmount),
    presentValue: formatAmount(data.presentValue),
    profit: formatAmount(data.profit),
    holdingCost: formatAmount(data.holdingCost),
    dividend: formatAmount(data.dividend),
    estimateMaximumOccupancy: formatAmount(data.estimateMaximumOccupancy),

    // 价格字段（毫转元）
    unitCost: formatPrice(data.unitCost),

    // 百分比字段
    irr: formatPercentageFromHundreds(data.irr), // IRR字段为百倍转百分比
    investmentYield: formatPercentage(data.investmentYield),
    turnoverRate: formatPercentage(data.turnoverRate),
    dividendYield: formatPercentage(data.dividendYield),
    upSoldPercent: formatPercentage(data.upSoldPercent),
    downBoughtPercent: formatPercentage(data.downBoughtPercent),

    // 份额字段（百倍转份额）
    attributableShare: formatShare(data.attributableShare),

    // 净值字段（毫转元）
    netValue: formatNetValue(data.netValue),

    // 保持原始数值的字段
    sellTimes: data.sellTimes,
    holdingTimes: data.holdingTimes,
    businessType: data.businessType,
    recordDate: data.recordDate
  }
}