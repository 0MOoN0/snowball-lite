<script setup lang="ts">
import { Echart } from '@/components/Echart'
import type { EChartsOption } from 'echarts'
// import echarts from '@/plugins/echarts'
import * as gridPercentApi from '@/api/snow/charts/gridPercent'
import { onUnmounted, reactive, ref } from 'vue'
import { gridPercentOptoins } from '../echarts-data'
import { set } from 'lodash-es'
import { useRouter } from 'vue-router'

const gridPercentOptoinsData = reactive<EChartsOption>(gridPercentOptoins) as EChartsOption

const router = useRouter()

const recordDate = ref()

// 排序类型
const gridOrderType = ref<String>('距离买入')

// 存储网格id和网格类型id列表
const gridIds = ref<[]>([])
const gridTypeIds = ref<[]>([])

// 加载状态
const loading = ref(false)

const getGridPercent = async (orderType?: String) => {
  loading.value = true
  try {
    const res = await gridPercentApi.getGridPercent({ order_type: orderType })
    recordDate.value = res.data.recordDate
    set(gridPercentOptoinsData, 'yAxis.data', res.data.yAxis)

    // 构建series
    const series_data = res.data.series.map((item) => {
      return {
        name: item.name,
        type: 'bar',
        stack: 'total',
        data: item.data,
        label: {
          show: true
        },
        emphasis: {
          focus: 'series'
        }
      }
    })
    set(gridPercentOptoinsData, 'series', series_data)
    gridIds.value = res.data.gridIdList
    gridTypeIds.value = res.data.gridTypeIdList
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}
getGridPercent()

const orderTypeChange = (orderType) => {
  orderType = '距离卖出' == orderType ? 'sold' : 'bought'
  getGridPercent(orderType)
}

// 刷新数据
const refreshData = () => {
  const orderType = gridOrderType.value === '距离卖出' ? 'sold' : 'bought'
  getGridPercent(orderType)
}

const jumpToDetail = (params) => {
  console.log('选中网格', gridTypeIds.value[params.dataIndex])
  console.log('选中网格类型ID', gridIds.value[params.dataIndex])
  router.push({
    path: '/strategy/grid',
    query: {
      grid_type_id: gridTypeIds.value[params.dataIndex],
      grid_id: gridIds.value[params.dataIndex]
    }
  })
}

// 销毁
onUnmounted(() => {
  // 输出销毁提示
  console.log('销毁:', '首页分析')
})
</script>
<template>
  <div>
    <div class="flex flex-nowarp order-bar h-50px">
      <div class="date-info">
        <div>数据日期：{{ recordDate }}</div>
      </div>
      <div class="data-control">
        <div class="data-type-label">数据类型：</div>
        <div class="control-group">
          <el-button
            class="refresh-btn"
            :icon="'Refresh'"
            circle
            size="small"
            @click="refreshData"
            :loading="loading"
          />
          <el-radio-group v-model="gridOrderType" @change="orderTypeChange">
            <el-radio-button label="距离买入" />
            <el-radio-button label="距离卖出" />
          </el-radio-group>
        </div>
      </div>
    </div>
    <Echart :options="gridPercentOptoinsData" :height="350" @click-echarts="jumpToDetail" />
  </div>
</template>
<style>
.order-bar {
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
}

.date-info {
  font-size: 14px;
  line-height: 50px;
}

.data-control {
  display: flex;
  align-items: center;
}

.data-type-label {
  margin-right: 10px;
  font-size: 14px;
}

.control-group {
  display: flex;
  align-items: center;
}

.refresh-btn {
  margin-right: 12px;
}
</style>
