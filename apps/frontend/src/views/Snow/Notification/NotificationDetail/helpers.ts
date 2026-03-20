import { webHelper } from '@/utils/webHelper'

// 友好标签映射（统一维护）
export const labelMap: Record<string, string> = {
  // 公共
  title: '标题',
  recordDate: '记录日期',
  date: '日期',
  assetName: '资产名称',
  presentValue: '现值',
  maximumOccupancy: '最大占用',
  purchaseAmount: '买入金额',
  holdingCost: '持有成本',
  dividend: '分红',
  profit: '盈利',
  unitCost: '单位成本',
  netValue: '净值',
  irr: 'IRR',
  investmentYield: '投资收益率',
  turnoverRate: '换手率',
  dividendYield: '股息率',
  close: '收盘价',
  closePercent: '涨跌幅',
  attributableShare: '归属份额',
  // 日常报告特有
  grid_info: '系统概览',
  asset_name: '模块/任务',
  grid_type_name: '状态/说明',
  buy_count: '买入次数',
  sell_count: '卖出次数',
  cb_subscribe_tomorrow: '明日可转债申购',
  databox_test_result: 'DataBox 测试结果',
  unprocessed_confirm_count: '未处理确认数',
  scheduler_status: '调度器状态',
  scheduler_errors_today: '今日调度器错误',
  // 系统运行特有（DataBox 测试）
  test_type: '测试类型',
  test_result: '测试结果',
  error_message: '错误信息',
  test_time: '测试时间',
  description: '说明',
}

// 百分比格式化
export const formatPercent = (val: number | string, denominator = 100, digits = 2): string => {
  const num = Number(val)
  if (isNaN(num)) return String(val)
  return (num / denominator).toFixed(digits) + '%'
}

// 针对常见字段的格式化规则
export const makeFormatter = (key: string) => {
  const lower = key.toLowerCase()
  // 价格类（毫→元），保留3位
  if (lower.includes('price') || lower.includes('unitcost') || lower.includes('netvalue') || lower === 'close') {
    return (_row: Recordable, _col: TableColumn, cellValue: number | string) =>
      webHelper.numFormatWithCurrency(cellValue as number, null, 10000, 3)
  }
  // 金额类（分→元），保留2位
  if (
    lower.includes('amount') ||
    lower.includes('value') ||
    lower.includes('profit') ||
    lower.includes('maximumoccupancy') ||
    lower.includes('purchaseamount') ||
    lower.includes('holdingcost') ||
    lower.includes('dividend')
  ) {
    return (_row: Recordable, _col: TableColumn, cellValue: number | string) =>
      webHelper.numFormatWithCurrency(cellValue as number, null, 100, 2)
  }
  // 份额（百倍）
  if (lower.includes('share')) {
    return (_row: Recordable, _col: TableColumn, cellValue: number | string) => {
      const num = Number(cellValue)
      return isNaN(num) ? String(cellValue) : (num / 100).toFixed(2)
    }
  }
  // 百分比：IRR 百倍，其它百分比万倍
  if (lower === 'irr') {
    return (_row: Recordable, _col: TableColumn, cellValue: number | string) => formatPercent(cellValue, 100, 2)
  }
  if (lower.includes('yield') || lower.includes('rate') || lower === 'closepercent') {
    return (_row: Recordable, _col: TableColumn, cellValue: number | string) => formatPercent(cellValue, 10000, 2)
  }
  // 默认不处理
  return undefined
}

// 构建日常报告渲染数据（摘要 + 动态表格）
export function buildDailyReportRender(content: Record<string, unknown>) {
  const raw = JSON.stringify(content, null, 2)

  // 摘要
  const summarySchemas: DescriptionsSchema[] = []
  const summaryData: Record<string, unknown> = {}
  Object.entries(content).forEach(([key, value]) => {
    const isPrimitive = typeof value === 'string' || typeof value === 'number'
    if (isPrimitive) {
      summarySchemas.push({ label: labelMap[key] || key, field: key })
      if (typeof value === 'number') {
        const fmt = makeFormatter(key)
        summaryData[key] = fmt ? fmt({}, {} as any, value) : value
      } else {
        summaryData[key] = value
      }
    }
  })

  // 动态表格
  const tables: Array<{ title: string; columns: TableColumn[]; data: Record<string, unknown>[] }> = []
  Object.entries(content).forEach(([key, value]) => {
    if (Array.isArray(value) && value.length > 0) {
      // 特例：grid_info 仅展示有意义的列
      if (key === 'grid_info' && typeof value[0] === 'object') {
        const cols: TableColumn[] = [
          { field: 'asset_name', label: labelMap['asset_name'] },
          { field: 'grid_type_name', label: labelMap['grid_type_name'] },
          { field: 'buy_count', label: labelMap['buy_count'] },
          { field: 'sell_count', label: labelMap['sell_count'] },
        ]
        tables.push({ title: labelMap[key] || key, columns: cols, data: value as Record<string, unknown>[] })
        return
      }

      // 对象数组：按首行键生成列，并附加格式化
      if (typeof value[0] === 'object') {
        const firstRow = value[0] as Record<string, unknown>
        const cols: TableColumn[] = Object.keys(firstRow).map((k) => {
          const col: TableColumn = {
            field: k,
            label: labelMap[k] || k,
          }
          const fmt = makeFormatter(k)
          if (fmt) (col as any).formatter = fmt
          return col
        })
        tables.push({ title: labelMap[key] || key, columns: cols, data: value as Record<string, unknown>[] })
        return
      }

      // 基本类型数组（字符串/数字）：构造成单列列表
      const rows = (value as Array<string | number>).map((v) => ({ value: v }))
      const cols: TableColumn[] = [{ field: 'value', label: '内容' }]
      tables.push({ title: labelMap[key] || key, columns: cols, data: rows as any })
    }
  })

  const showRaw = summarySchemas.length === 0 && tables.length === 0
  return { raw, summarySchemas, summaryData, tables, showRaw }
}

// 构建系统运行通知渲染数据（DataBox 功能测试）
export function buildSystemRunRender(content: Record<string, unknown>) {
  const summary: DescriptionsSchema[] = []
  if ('test_type' in content) summary.push({ label: labelMap['test_type'], field: 'test_type' })
  if ('test_result' in content) summary.push({ label: labelMap['test_result'], field: 'test_result' })
  if ('test_time' in content) summary.push({ label: labelMap['test_time'], field: 'test_time' })
  if ('description' in content) summary.push({ label: labelMap['description'], field: 'description', span: 3 })
  return { summarySchema: summary, contentData: content }
}
