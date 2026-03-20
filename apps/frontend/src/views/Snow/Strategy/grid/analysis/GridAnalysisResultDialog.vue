<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <el-space direction="vertical" :fill="true" style="width: 100%" alignment="center">
      <Descriptions title="交易分析数据概览" :data="analysisData" :schema="tradeAnalysisSchema" />
      <Descriptions
        title="网格分析数据概览"
        :data="analysisData"
        :schema="gridTradeAnalysisSchema"
      />
    </el-space>
    <template #footer>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { Descriptions } from '@/components/Descriptions'
import { computed, reactive } from 'vue'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: ''
  },
  analysisData: {
    type: Object
  }
})

const tradeAnalysisSchema = reactive<DescriptionsSchema[]>([
  {
    field: 'recordDate',
    label: '记录时间'
  },
  {
    field: 'netValue',
    label: '基金净值'
  },
  {
    field: 'irr',
    label: '内部收益率（%）'
  },
  {
    field: 'maximumOccupancy',
    label: '历史最大占用（元）'
  },
  {
    field: 'purchaseAmount',
    label: '基金总申购（元）'
  },
  {
    field: 'investmentYield',
    label: '投资收益率（%）'
  },
  {
    field: 'profit',
    label: '收益总额（元）'
  },
  {
    field: 'unitCost',
    label: '单位成本（元）'
  },
  {
    field: 'presentValue',
    label: '基金现值（元）'
  },
  {
    field: 'holdingCost',
    label: '持有成本（元）'
  },
  {
    field: 'attributableShare',
    label: '持有份额'
  },
  {
    field: 'dividend',
    label: '分红与赎回（元）'
  },
  {
    field: 'turnoverRate',
    label: '换手率（%）'
  },
  {
    field: 'dividendYield',
    label: '股息率（%）'
  }
])
const gridTradeAnalysisSchema = reactive<DescriptionsSchema[]>([
  {
    field: 'recordDate',
    label: '记录时间'
  },
  {
    field: 'holdingTimes',
    label: '待出网次数（次）'
  },
  {
    field: 'sellTimes',
    label: '出网次数（次）'
  },
  {
    field: 'estimateMaximumOccupancy',
    label: '预计最大占用（元）'
  },
  {
    field: 'upSoldPercent',
    label: '距离卖出需要上涨（%）'
  },
  {
    field: 'downBoughtPercent',
    label: '距离买入需要下跌（%）'
  }
])

const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})
// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}
</script>
<style></style>
