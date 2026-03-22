<script setup lang="ts">
import * as gridChartsApi from '@/api/snow/charts/gridRecord'
import { Echart } from '@/components/Echart'
import { EChartsOption } from 'echarts'
import { ElMessageBox, ElSkeleton, ElSkeletonItem } from 'element-plus'
import _ from 'lodash'
import { set } from 'lodash-es'
import { onMounted, reactive, ref, ref as vueRef, watch } from 'vue'
import {
  chartsLineSeries,
  chartsMainSeries,
  chartsVolumnSeries,
  lineOptions,
  tooltipFormatter
} from './echarts-data'

// === 类型定义 ===
type ChartType = 'line' | 'candlestick'
type DailyType = 'daily' | 'netvalue' | 'totvalue'
type EChartInstance = {
  getOption: () => any
  setOption: (option: any, opts?: any) => void
  on: (eventName: string, handler: (params: any) => void) => void
}

// 标记点数据类型
interface MarkPointData {
  date: string
  direction: number
  price: number
  // 添加更多可能的字段
  amount?: number
  reason?: string
}

// === 数据定义 ===
const loading = ref(true)
const chartRef = vueRef<{ getChart: () => EChartInstance } | null>(null)
const originalSeriesData = ref<any[]>([])
const currentDataZoom = ref<any>(null)
// 存储所有标记点数据，用于tooltip和点击事件
const allMarkPoints = ref<MarkPointData[]>([])

const props = defineProps({
  gridTypeId: {
    type: Object,
    default: null
  }
})

// 图表参数
const chartsParams = reactive<{ dailyType: DailyType }>({ dailyType: 'daily' })

// 日线数据类型
const dailyTypeArr: DailyType[] = ['close', 'netvalue', 'totvalue']
const dailyTypeRadio = ref<string>('收盘价（已复权）')

// 图表类型控制
const chartType = ref<ChartType>('candlestick')

// 图表控制开关
const showMA = ref(false)
const showMarkLabel = ref(true)
const showMarkPoint = ref(true)
const showMarkLine = ref(true)
const showUnitCost = ref(false)

// 图表配置
const lineOptionsData = reactive<EChartsOption>(lineOptions) as EChartsOption

// === 生命周期钩子 ===
watch(
  () => props.gridTypeId,
  async (gridTypeId) => {
    await initCharts(gridTypeId, true)
  }
)

onMounted(() => {
  initCharts(props.gridTypeId, true)
})

// === 工具函数 ===
/**
 * 获取图表实例
 * @returns 图表实例或null
 */
const getChartInstance = (): EChartInstance | null => {
  return chartRef.value?.getChart() || null
}

/**
 * 根据日线数据类型获取对应的参数
 */
const getDailyTypeParams = (dailyData: string): DailyType => {
  if (dailyData === '单位净值') {
    return dailyTypeArr[1]
  } else if (dailyData === '累计净值') {
    return dailyTypeArr[2]
  }
  // 默认返回收盘价
  return dailyTypeArr[0]
}

// === 数据处理函数 ===
/**
 * 解析并设置图表数据
 */
const parseAndSetSeriesData = (seriesData: any[], chartTypeObj: { value: ChartType }) => {
  const klineData = seriesData.find((item) => _.has(item, 'data'))

  if (chartTypeObj.value === 'line') {
    // 折线图模式：将 K 线数据转换为折线图
    return seriesData.map((data) => {
      if (_.has(data, 'data')) {
        return parseLineSeriesData(data)
      }
      if (_.has(data, 'volume')) {
        return parseVolumeData(data, klineData)
      }
      if (_.has(data, 'unitCost')) {
        return parseUnitCostSeriesData(data.unitCost)
      }
      return parseMASeriesData(data)
    })
  } else {
    // 蜡烛图模式
    return seriesData.map((data) => {
      if (_.has(data, 'data')) return parseCandlestickSeriesData(data)
      if (_.has(data, 'volume')) return parseVolumeData(data, klineData)
      if (_.has(data, 'unitCost')) return parseUnitCostSeriesData(data.unitCost)
      return parseMASeriesData(data)
    })
  }
}

/**
 * 解析折线图数据
 */
const parseLineSeriesData = (seriesData: any) => {
  const markLines = parseMarkLineData(seriesData)
  const markPoint = parseMarkPointData(seriesData)

  // 使用收盘价或净值作为折线图数据
  const netValue = _.get(seriesData, 'data.close', [])

  const mainSeries = _.cloneDeep(chartsLineSeries)
  return {
    ...mainSeries,
    name: '价格',
    data: netValue,
    markPoint,
    markLine: markLines,
    lineStyle: {
      width: 2,
      color: '#5470C6'
    },
    itemStyle: {
      color: '#5470C6'
    }
  }
}

/**
 * 解析K线数据
 */
const parseCandlestickSeriesData = (seriesData: any) => {
  const markLines = parseMarkLineData(seriesData)
  const markPoint = parseMarkPointData(seriesData)
  const { open, close, low, high } = seriesData.data

  const minLength = Math.min(open.length, close.length, low.length, high.length)
  const data = Array.from({ length: minLength }, (_, index) => [
    open[index],
    close[index],
    low[index],
    high[index]
  ])

  const mainSeries = _.cloneDeep(chartsMainSeries)
  return {
    ...mainSeries,
    name: '日K',
    type: 'candlestick',
    data,
    markPoint,
    markLine: markLines
  }
}

/**
 * 解析成交量数据
 */
const parseVolumeData = (seriesData: any, klineData: any) => {
  const volume = _.get(seriesData, 'volume', [])
  const close = _.get(klineData, 'data.close', [])
  const open = _.get(klineData, 'data.open', [])

  const volumeData = volume.map((vol: number, index: number) => ({
    value: vol,
    isUp: close[index] >= open[index]
  }))

  return { ..._.cloneDeep(chartsVolumnSeries), data: volumeData }
}

/**
 * 解析均线数据
 */
const parseMASeriesData = (seriesData: any) => {
  const key = Object.keys(seriesData)[0]
  return {
    ..._.cloneDeep(chartsLineSeries),
    name: key,
    data: _.get(seriesData, key, [])
  }
}

/**
 * 解析单位成本数据
 */
const parseUnitCostSeriesData = (seriesData: any) => {
  return {
    ..._.cloneDeep(chartsLineSeries),
    name: 'unitCost',
    data: seriesData
  }
}

/**
 * 解析标记线数据
 */
const parseMarkLineData = (seriesData: any) => {
  if (!showMarkLine.value) return []

  // 获取原始 markLine 配置
  const markLineConfig = _.cloneDeep(chartsMainSeries.markLine)

  // 只修改数据部分
  markLineConfig.data = _.get(seriesData, 'markLines', []).map((yAxis: number) => ({
    name: '',
    yAxis
  }))

  return markLineConfig
}

/**
 * 解析标记点数据
 */
const parseMarkPointData = (seriesData: any) => {
  if (!showMarkPoint.value) return []

  // 获取原始 markPoint 配置
  const markPointConfig = _.cloneDeep(chartsMainSeries.markPoint)

  // 获取标记点数据
  const markPoints = _.get(seriesData, 'markPoint', [])

  // 修改数据部分
  markPointConfig.data = markPoints.map((mark: any) => {
    // 只设置需要动态修改的属性
    return {
      name: 'mark',
      coord: [mark.date, mark.price],
      itemStyle: {
        color: mark.direction == 1 ? '#FFD700' : '#00FFFF'
      },
      label: {
        show: showMarkLabel.value,
        formatter: mark.direction == 1 ? '买' : '卖'
      }
    }
  })

  return markPointConfig
}

// === 图表初始化与更新 ===
/**
 * 初始化图表
 */
const initCharts = async (gridTypeId: any, showSkeleton = false) => {
  if (!gridTypeId) {
    loading.value = false
    return
  }

  loading.value = showSkeleton
  try {
    const res = await gridChartsApi.getByGridTypeId(gridTypeId, {
      daily_type: chartsParams.dailyType
    })

    if (res.success) {
      const xAxis = _.get(res.data, 'xAxis', [])
      _.forEach(lineOptionsData.xAxis, (axis) => {
        _.set(axis, 'data', xAxis)
      })

      // 保存原始数据
      originalSeriesData.value = _.get(res.data, 'series', [])

      // 提取并保存所有标记点数据
      const klineData = originalSeriesData.value.find((s) => _.has(s, 'data'))
      if (klineData && klineData.markPoint) {
        allMarkPoints.value = klineData.markPoint
      }

      const seriesData = parseAndSetSeriesData(originalSeriesData.value, { value: chartType.value })
      set(lineOptionsData, 'series', seriesData)

      // 设置自定义tooltip
      setupCustomTooltip()

      // 应用当前的开关状态到图表
      applyControlSettings()

      // 设置 dataZoom 监听器
      setTimeout(setupDataZoomListener, 200)

      // 设置点击事件监听器
      setTimeout(setupClickEventListener, 200)
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 设置自定义tooltip
 */
const setupCustomTooltip = () => {
  // 修改tooltip配置，添加formatter函数
  if (lineOptionsData.tooltip) {
    lineOptionsData.tooltip = {
      ...lineOptionsData.tooltip,
      formatter: (params: any) => {
        return tooltipFormatter.format(params, allMarkPoints.value)
      }
    }
  }
}

/**
 * 设置点击事件监听器
 */
const setupClickEventListener = () => {
  const chart = getChartInstance()
  if (!chart) return

  chart.on('click', (params: any) => {
    // 检查是否点击了标记点
    if (params.componentType === 'markPoint') {
      console.log(params)
      const pointData = params.data
      const coord = pointData.coord

      if (coord && coord.length === 2) {
        const date = coord[0]
        const value = coord[1]

        // 查找对应的标记点详细数据
        const markPoint = allMarkPoints.value.find(
          (mp) => mp.date === date && Math.abs(mp.price - value) < 0.0001
        )

        if (markPoint) {
          // 显示详细信息
          showMarkPointDetails(markPoint)
        }
      }
    }
  })
}

/**
 * 显示标记点详细信息
 */
const showMarkPointDetails = (markPoint: MarkPointData) => {
  // 使用Element Plus的MessageBox显示详细信息
  const direction = markPoint.direction === 1 ? '买入' : '卖出'
  const title = `${direction}信号详情 (${markPoint.date})`

  let content = `
    <div style="margin-bottom:10px;">
      <div><strong>日期:</strong> ${markPoint.date}</div>
      <div><strong>净值:</strong> ${markPoint.netValue}</div>
      <div><strong>方向:</strong> ${direction}</div>
  `

  // 添加其他可能的字段
  if (markPoint.price) {
    content += `<div><strong>价格:</strong> ${markPoint.price}</div>`
  }
  if (markPoint.amount) {
    content += `<div><strong>数量:</strong> ${markPoint.amount}</div>`
  }
  if (markPoint.reason) {
    content += `<div><strong>原因:</strong> ${markPoint.reason}</div>`
  }

  content += `</div>`

  // 使用Element Plus的MessageBox显示
  ElMessageBox.alert(content, title, {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '确定'
  })
}

/**
 * 设置dataZoom监听器
 */
const setupDataZoomListener = () => {
  const chart = getChartInstance()
  if (!chart) return

  chart.on('datazoom', () => {
    // 当用户进行缩放操作时，保存当前的 dataZoom 状态
    const option = chart.getOption()
    currentDataZoom.value = option.dataZoom
  })
}

/**
 * 应用控制设置到图表
 */
const applyControlSettings = () => {
  const chart = getChartInstance()
  if (!chart) return

  // 获取当前 dataZoom 状态
  const option = chart.getOption()
  const currentDataZoom = option.dataZoom

  // 应用均线显示状态
  const maSelected = {
    MA20: showMA.value,
    MA51: showMA.value,
    MA120: showMA.value,
    MA250: showMA.value
  }

  // 只更新 legend.selected，不影响其他配置
  chart.setOption(
    {
      legend: [
        {
          ...option.legend[0], // 保留原始 legend 的所有配置
          selected: {
            ...option.legend[0].selected, // 保留原始 selected 状态
            ...maSelected, // 更新均线的 selected 状态
            unitCost: showUnitCost.value // 更新成本线的 selected 状态
          }
        }
      ]
    },
    { replaceMerge: ['legend'] }
  )

  // 恢复 dataZoom 状态
  chart.setOption(
    {
      dataZoom: currentDataZoom
    },
    { replaceMerge: ['dataZoom'] }
  )
}

// === 事件处理函数 ===
/**
 * 日线数据类型改变时的回调
 */
const dailyDataRadioChange = (dailyData: string) => {
  chartsParams.dailyType = getDailyTypeParams(dailyData)
  initCharts(props.gridTypeId, true)
}

/**
 * 图表类型改变处理
 */
const handleChartTypeChange = (type: ChartType) => {
  const chart = getChartInstance()
  if (!chart) {
    // 如果图表实例不存在，直接更新类型并初始化
    chartType.value = type
    initCharts(props.gridTypeId)
    return
  }

  // 获取当前配置
  const option = chart.getOption()

  // 保存当前的 dataZoom 状态
  const savedDataZoom = option.dataZoom

  // 更新图表类型
  chartType.value = type

  // 获取新的系列数据
  const newSeriesData = parseAndSetSeriesData(originalSeriesData.value, { value: type })

  // 直接更新图表的 series 数据，而不是重新初始化整个图表
  chart.setOption(
    {
      series: newSeriesData,
      dataZoom: savedDataZoom // 保持 dataZoom 状态不变
    },
    { replaceMerge: ['series'] } // 只替换 series 部分
  )
}

/**
 * 均线显示控制
 */
const handleShowMAChange = (value: boolean) => {
  showMA.value = value

  const chart = getChartInstance()
  if (!chart) return

  // 获取当前 dataZoom 状态
  const option = chart.getOption()
  const currentDataZoom = option.dataZoom

  // 修改 legend 的 selected 属性
  const maSelected = {
    MA20: value,
    MA51: value,
    MA120: value,
    MA250: value
  }

  // 只更新 legend.selected，不影响其他配置
  chart.setOption(
    {
      legend: [
        {
          ...option.legend[0], // 保留原始 legend 的所有配置
          selected: {
            ...option.legend[0].selected, // 保留原始 selected 状态
            ...maSelected // 更新均线的 selected 状态
          }
        }
      ]
    },
    { replaceMerge: ['legend'] }
  )

  // 恢复 dataZoom 状态
  chart.setOption(
    {
      dataZoom: currentDataZoom
    },
    { replaceMerge: ['dataZoom'] }
  )
}

/**
 * 标记点标签显示控制
 */
const handleShowMarkLabelChange = (value: boolean) => {
  showMarkLabel.value = value

  const chart = getChartInstance()
  if (!chart) return

  // 获取当前配置
  const option = chart.getOption()

  // 找到主系列（包含标记点的系列）
  const mainSeries = option.series.find((s: any) => s.name === '日K' || s.name === '价格')
  if (!mainSeries) return

  // 更新标记点的标签显示状态
  if (mainSeries.markPoint && mainSeries.markPoint.data) {
    mainSeries.markPoint.data.forEach((point: any) => {
      if (point.label) {
        point.label.show = value
      }
    })
  }

  // 应用更新
  chart.setOption(
    {
      series: option.series
    },
    { replaceMerge: ['series'] }
  )
}

/**
 * 标记点显示控制
 */
const handleShowMarkPointChange = (value: boolean) => {
  showMarkPoint.value = value

  const chart = getChartInstance()
  if (!chart) return

  // 获取当前配置
  const option = chart.getOption()

  // 找到主系列（包含标记点的系列）
  const mainSeries = option.series.find((s: any) => s.name === '日K' || s.name === '价格')
  if (!mainSeries) return

  // 更新标记点显示状态
  if (value) {
    // 如果要显示标记点，重新获取数据并设置
    const klineData = originalSeriesData.value.find((s) => _.has(s, 'data'))
    const markPoint = parseMarkPointData(klineData)
    mainSeries.markPoint = markPoint
  } else {
    // 如果要隐藏标记点，设置空数据
    mainSeries.markPoint = { data: [] }
  }

  // 应用更新
  chart.setOption(
    {
      series: option.series
    },
    { replaceMerge: ['series'] }
  )
}

/**
 * 标记线显示控制
 */
const handleShowMarkLineChange = (value: boolean) => {
  showMarkLine.value = value

  const chart = getChartInstance()
  if (!chart) return

  // 获取当前配置
  const option = chart.getOption()

  // 找到主系列（包含标记线的系列）
  const mainSeries = option.series.find((s: any) => s.name === '日K' || s.name === '价格')
  if (!mainSeries) return

  // 更新标记线显示状态
  if (value) {
    // 如果要显示标记线，重新获取数据并设置
    const klineData = originalSeriesData.value.find((s) => _.has(s, 'data'))
    const markLine = parseMarkLineData(klineData)
    mainSeries.markLine = markLine
  } else {
    // 如果要隐藏标记线，设置空数据
    mainSeries.markLine = {
      ..._.cloneDeep(chartsMainSeries.markLine),
      data: []
    }
  }

  // 应用更新
  chart.setOption(
    {
      series: option.series
    },
    { replaceMerge: ['series'] }
  )
}

/**
 * 单位成本线显示控制
 */
const handleShowUnitCostChange = (value: boolean) => {
  showUnitCost.value = value

  const chart = getChartInstance()
  if (!chart) return

  // 获取当前 dataZoom 状态
  const option = chart.getOption()
  const currentDataZoom = option.dataZoom

  // 只更新 legend.selected，不影响其他配置
  chart.setOption(
    {
      legend: [
        {
          ...option.legend[0], // 保留原始 legend 的所有配置
          selected: {
            ...option.legend[0].selected, // 保留原始 selected 状态
            unitCost: value // 更新成本线的 selected 状态
          }
        }
      ]
    },
    { replaceMerge: ['legend'] }
  )

  // 恢复 dataZoom 状态
  chart.setOption(
    {
      dataZoom: currentDataZoom
    },
    { replaceMerge: ['dataZoom'] }
  )
}
</script>

<template>
  <ElSkeleton :loading="loading" animated>
    <template #template>
      <!-- 骨架屏模板 -->
      <div class="flex justify-between mb-4">
        <div class="flex items-center">
          <ElSkeletonItem variant="text" style="width: 200px; height: 32px" />
        </div>
        <div class="flex items-center">
          <ElSkeletonItem variant="text" style="width: 300px; height: 32px" class="mx-4" />
        </div>
        <div class="flex items-center">
          <ElSkeletonItem variant="text" style="width: 250px; height: 32px" />
        </div>
      </div>
      <ElSkeletonItem variant="p" style="height: 800px" />
    </template>

    <!-- 实际内容 -->
    <div class="flex justify-between">
      <div class="flex items-center">
        <!-- 左侧内容 -->
        <div class="flex flex-nowarp chart-type">
          <div>图表类型：</div>
          <el-radio-group v-model="chartType" @change="handleChartTypeChange">
            <el-radio-button label="line" value="line">折线图</el-radio-button>
            <el-radio-button label="candlestick" value="candlestick">蜡烛图</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <div class="flex items-center">
        <!-- 中间内容 -->
        <div class="flex flex-nowarp show-ma">
          <div>显示均线：</div>
          <el-switch v-model="showMA" @change="handleShowMAChange" />
        </div>
        <div class="flex flex-nowarp show-mark ml-4">
          <div>显示标签：</div>
          <el-switch v-model="showMarkLabel" @change="handleShowMarkLabelChange" />
        </div>
        <div class="flex flex-nowarp show-mark ml-4">
          <div>显示买卖点：</div>
          <el-switch v-model="showMarkPoint" @change="handleShowMarkPointChange" />
        </div>
        <div class="flex flex-nowarp show-mark ml-4">
          <div>显示标记线：</div>
          <el-switch v-model="showMarkLine" @change="handleShowMarkLineChange" />
        </div>
        <div class="flex flex-nowarp show-mark ml-4">
          <div>显示成本线：</div>
          <el-switch v-model="showUnitCost" @change="handleShowUnitCostChange" />
        </div>
      </div>
      <div class="flex items-center">
        <!-- 右侧内容 -->
        <div class="flex flex-nowarp daily-data-type">
          <div>数据类型：</div>
          <el-radio-group v-model="dailyTypeRadio" @change="dailyDataRadioChange">
            <el-radio-button label="收盘价（已复权）" />
            <el-radio-button label="单位净值" />
            <el-radio-button label="累计净值" />
          </el-radio-group>
        </div>
      </div>
    </div>
    <div class="mt-5">
      <Echart ref="chartRef" :options="lineOptionsData" :height="800" />
    </div>
  </ElSkeleton>
</template>

<style scoped>
.daily-data-type {
  align-items: center;
}
.chart-type {
  align-items: center;
}
.show-ma {
  align-items: center;
}
.show-mark {
  align-items: center;
}

:deep(.el-skeleton__item) {
  background: rgba(190, 190, 190, 0.2);
}

:deep(.el-skeleton) {
  width: 100%;
}
</style>
