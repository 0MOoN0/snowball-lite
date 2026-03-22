<script setup lang="ts">
import * as transactionApi from '@/api/snow/charts/transaction'
import { Echart } from '@/components/Echart'
import { useI18n } from '@/hooks/web/useI18n'
import { EChartsOption } from 'echarts'
import { ElCard, ElCol, ElRow, ElSkeleton, ElButton } from 'element-plus'
import _ from 'lodash'
import { set } from 'lodash-es'
import { reactive, ref } from 'vue'
import GridSoldDistance from './components/GridSoldDistance.vue'
import PanelGroup from './components/PanelGroup.vue'
import { barOptions, pieOptions, transacionOptions } from './echarts-data'

const { t } = useI18n()

const loading = ref(true)

const pieOptionsData = reactive<EChartsOption>(pieOptions) as EChartsOption

const getAmountTransaction = async () => {
  const res = await transactionApi.getAmountTransaction()
  if (res && res.success) {
    set(
      pieOptionsData,
      'legend.data',
      res.data.map((v) => t(v.assetName))
    )
    pieOptionsData!.series![0].data = res.data.map((v) => {
      return {
        name: t(v.assetName),
        value: v.presentValue
      }
    })
  }
}

const barOptionsData = reactive<EChartsOption>(barOptions) as EChartsOption

const getProfitRank = async () => {
  const res = await transactionApi.getTransactionProfitRank()
  if (res && res.success) {
    set(barOptionsData, 'title.text', '交易收益排名')
    set(barOptionsData, 'grid.containLabel', true) // Fix label cutoff
    set(barOptionsData, 'grid.top', 50) // Adjust top padding
    set(barOptionsData, 'grid.bottom', 10) // Adjust bottom padding to reduce whitespace
    set(barOptionsData, 'xAxis.data', res.data.xAxis)
    set(barOptionsData, 'xAxis.axisLabel', { interval: 0, rotate: 30 }) // Show all labels, rotate if needed
    set(barOptionsData, 'series', [
      {
        name: '收益',
        data: res.data.series[0].profit.map((val: string) => {
          const numVal = parseFloat(val)
          return {
            value: numVal,
            itemStyle: {
              color: numVal >= 0 ? '#f56c6c' : '#67c23a' // Red for positive, Green for negative
            }
          }
        }),
        type: 'bar'
      }
    ])
  }
}

const lineOptionsData = reactive<EChartsOption>(transacionOptions) as EChartsOption
const nameMap: Record<string, string> = {
  profit: '利润',
  presentValue: '现值',
  investmentYield: '投资收益率',
  irr: '内部收益率',
  annualizedReturn: '年化收益率'
}
const refreshingLine = ref(false)
const refreshLine = async () => {
  refreshingLine.value = true
  try {
    await getTransactionAnalysis()
  } finally {
    refreshingLine.value = false
  }
}

const getTransactionAnalysis = async () => {
  const res = await transactionApi.getAllTransaction()
  if (res.success) {
    // 获取xAxis
    const xAxis = _.get(res.data, 'xAxis', [])
    set(lineOptionsData, 'xAxis.data', xAxis)
    // 获取series数据
    const series = _.get(res.data, 'series', [])
    // 遍历series
    const series_data = series.map((seriesIn: any) => {
      // 获取marks
      const marksData = _.get(seriesIn, 'marks', []).map((mark) => {
        return {
          name: 'mark',
          coord: [mark.date, mark.netvalue],
          itemStyle: {
            color: mark.direction == 1 ? 'rgb(41,171,145)' : 'rgb(241,90,74)'
          }
        }
      })
      // 获取key
      const keys = Object.keys(seriesIn)
      let data = {}
      // 遍历keys
      keys.forEach((key) => {
        // 如果key不是data和marks，设置series
        if (key != 'marks') {
          const seriesData = _.get(seriesIn, `${key}`, [])
          data = {
            name: nameMap[key] || `${key}`,
            smooth: true,
            type: 'line',
            data: seriesData,
            animationDuration: 2800,
            animationEasing: 'cubicInOut',
            markPoint: {
              symbol: 'circle',
              symbolSize: 10,
              data: marksData
            },
            lineStyle: {
              width: 1
              // color: 'rgb(241,90,74)'
            },
            yAxisIndex:
              key === 'irr' || key === 'investmentYield' || key === 'annualizedReturn' ? 1 : 0
          }
        }
      })
      return data
    })
    set(lineOptionsData, 'series', series_data)
    loading.value = false
  }
}

const getAllApi = async () => {
  try {
    // await Promise.all([getAmountTransaction(), getWeeklyUserActivity(), getTransactionAnalysis()])
    await Promise.all([getAmountTransaction(), getTransactionAnalysis(), getProfitRank()])
    loading.value = false
  } catch (error) {
    console.error('[DashboardAnalysis] 数据加载失败:', error)
    loading.value = false
  }
}

getAllApi()

</script>

<template>
  <PanelGroup />
  <ElRow :gutter="20" justify="space-between">
    <ElCol :xl="10" :lg="10" :md="24" :sm="24" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated>
          <Echart :options="pieOptionsData" :height="400" />
        </ElSkeleton>
      </ElCard>
    </ElCol>
    <ElCol :xl="14" :lg="14" :md="24" :sm="24" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated>
          <GridSoldDistance />
        </ElSkeleton>
      </ElCard>
    </ElCol>

    <ElCol :span="24" :xl="10" :lg="10" :md="24" :sm="24" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated :rows="4">
          <Echart :options="barOptionsData" :height="450" />
        </ElSkeleton>
      </ElCard>
    </ElCol>

    <ElCol :span="24" :xl="14" :lg="14" :md="24" :sm="24" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated :rows="4">
          <div class="flex flex-nowarp order-bar h-50px">
            <div class="date-info">
              <div>收益图</div>
            </div>
            <div class="data-control">
              <div class="control-group">
                <ElButton
                  class="refresh-btn"
                  :icon="'Refresh'"
                  circle
                  size="small"
                  @click="refreshLine"
                  :loading="refreshingLine"
                />
              </div>
            </div>
          </div>
          <Echart :options="lineOptionsData" :height="400" />
        </ElSkeleton>
      </ElCard>
    </ElCol>
  </ElRow>
</template>
<style>
.order-type {
  align-items: center;
}
</style>
