<script lang="ts" setup>
import { ref } from 'vue'
import { ElTable, ElTableColumn, ElButton, ElPopconfirm, ElMessage, ElTag } from 'element-plus'
import * as gridTypeDetailApi from '@/api/snow/gridTypeDetail/index'
import GridTypeDetailEditDialog from '@/views/Snow/Strategy/grid/GridTypeDetail/GridTypeDetailEditDialog.vue'
import { addThousandsSeparator } from '@/utils/gridDataFormatter'

const props = defineProps({
  gridTypeDetailList: {
    type: Array,
    default: () => [],
  },
  gridInfos: {
    type: Object,
    default: () => ({}),
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submit', 'deleteRows', 'refreshData'])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentRowData = ref<any>({})
const selectedRows = ref<any[]>([])

const handleAdd = () => {
  dialogTitle.value = '新增网格类型详情'
  currentRowData.value = {}
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = '编辑网格类型详情'
  currentRowData.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  if (row.id) {
    await gridTypeDetailApi.deleteByIds({ ids: [row.id] })
    ElMessage.success('删除成功')
    emit('refreshData')
  }
}

const handleSelectionChange = (val: any[]) => {
  selectedRows.value = val
}

const handleSetCurrent = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择数据')
    return
  }
  if (selectedRows.value.length > 1) {
    ElMessage.warning('请选择一条数据')
    return
  }
  const selectedData = selectedRows.value[0]
  if (selectedData.id) {
    const res = await gridTypeDetailApi.setCurrent(selectedData.id)
    ElMessage.success(res.message || '设置成功')
    emit('refreshData')
  }
}

const tableRowClassName = ({ row }: { row: any }) => {
  if (row.isCurrent) {
    return 'current-row-highlight'
  }
  return ''
}

const handleDialogSubmit = async (formData: any) => {
  const dataToSave = { ...formData }
  // If adding new row, merge with gridInfos (gridId, gridTypeId)
  if (!dataToSave.id) {
    Object.assign(dataToSave, props.gridInfos)
  }

  try {
    await gridTypeDetailApi.saveOrUpdateGridTypeDetailList({
      gridTypeDetailList: [dataToSave],
    })
    ElMessage.success('保存成功')
    emit('refreshData')
  } catch (error) {
    console.error(error)
  }
}

// Helper to calculate display values
const calculatePurchaseAmount = (row: any) => {
  if (row.purchasePrice && row.purchaseShares) {
    // Price(Hao) * Shares = Amount(Hao). / 10000 = Amount(Yuan)
    return addThousandsSeparator(((row.purchasePrice * row.purchaseShares) / 10000).toFixed(2))
  }
  return '0'
}

const calculateActualSellShares = (row: any) => {
  if (row.sellShares && row.saveShare !== undefined) {
    return addThousandsSeparator((row.sellShares - row.saveShare).toString())
  }
  return '0'
}

const calculateSellAmount = (row: any) => {
  const actualSellShares = row.sellShares - row.saveShare
  if (actualSellShares && row.sellPrice) {
    // Price(Hao) * Shares = Amount(Hao). / 10000 = Amount(Yuan)
    return addThousandsSeparator(((Number(actualSellShares) * row.sellPrice) / 10000).toFixed(2))
  }
  return '0'
}

const calculateProfit = (row: any) => {
  const sellPrice = row.sellPrice
  const sellShares = row.sellShares
  const purchaseAmount = row.purchasePrice * row.purchaseShares
  if (sellShares > 0 && purchaseAmount > 0 && sellPrice > 0) {
    // (SellTotal(Hao) - BuyTotal(Hao)) / 10000 = Profit(Yuan)
    return addThousandsSeparator(((sellShares * sellPrice - purchaseAmount) / 10000).toFixed(2))
  }
  return '0'
}

const calculateSaveShareProfit = (row: any) => {
  const actualSellShares = row.sellShares - row.saveShare
  const sellAmount = Number(actualSellShares) * row.sellPrice
  const purchaseAmount = row.purchasePrice * row.purchaseShares
  if (sellAmount > 0 && purchaseAmount > 0) {
    // (SellAmount(Hao) - BuyAmount(Hao)) / 10000 = Profit(Yuan)
    return addThousandsSeparator(((sellAmount - purchaseAmount) / 10000).toFixed(2))
  }
  return '0'
}

const formatNumber = (value: number | string, precision: number = 0, scale: number = 1) => {
  if (value === undefined || value === null) return ''
  return addThousandsSeparator((Number(value) / scale).toFixed(precision))
}
</script>

<template>
  <div>
    <div class="mb-4">
      <ElButton type="primary" @click="handleAdd">新增</ElButton>
      <ElButton type="primary" plain @click="handleSetCurrent">设为当前</ElButton>
    </div>
    <ElTable
      :data="gridTypeDetailList"
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
      :row-class-name="tableRowClassName"
      v-loading="loading"
    >
      <ElTableColumn type="selection" width="55" />
      <ElTableColumn prop="gear" label="档位" width="80" />
      <ElTableColumn prop="monitorType" label="监控类型" width="100">
        <template #default="scope">
          <ElTag :type="scope.row.monitorType === 1 ? 'success' : 'danger'">
            {{ scope.row.monitorType === 1 ? '卖出' : '买入' }}
          </ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn label="买入触发价" width="120">
        <template #default="scope">
          {{ formatNumber(scope.row.triggerPurchasePrice, 4, 10000) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="买入价" width="120">
        <template #default="scope">
          {{ formatNumber(scope.row.purchasePrice, 4, 10000) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="入股数" width="100">
        <template #default="scope">
          {{ formatNumber(scope.row.purchaseShares) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="买入金额(元)" width="120">
        <template #default="scope">
          {{ calculatePurchaseAmount(scope.row) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="卖出触发价" width="120">
        <template #default="scope">
          {{ formatNumber(scope.row.triggerSellPrice, 4, 10000) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="卖出价" width="120">
        <template #default="scope">
          {{ formatNumber(scope.row.sellPrice, 4, 10000) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="原出股数" width="100">
        <template #default="scope">
          {{ formatNumber(scope.row.sellShares) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="实际出股数" width="100">
        <template #default="scope">
          {{ calculateActualSellShares(scope.row) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="实际卖出金额(元)" width="140">
        <template #default="scope">
          {{ calculateSellAmount(scope.row) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="收益(元)" width="120">
        <template #default="scope">
          {{ calculateProfit(scope.row) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="留股收益(元)" width="120">
        <template #default="scope">
          {{ calculateSaveShareProfit(scope.row) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="留存股数" width="100">
        <template #default="scope">
          {{ formatNumber(scope.row.saveShare) }}
        </template>
      </ElTableColumn>
      <ElTableColumn label="操作" fixed="right" width="150">
        <template #default="scope">
          <ElButton link type="primary" size="small" @click="handleEdit(scope.row)">编辑</ElButton>
          <ElPopconfirm title="确定删除吗？" @confirm="handleDelete(scope.row)">
            <template #reference>
              <ElButton link type="danger" size="small">删除</ElButton>
            </template>
          </ElPopconfirm>
        </template>
      </ElTableColumn>
    </ElTable>

    <GridTypeDetailEditDialog
      :dialog-visible="dialogVisible"
      :dialog-title="dialogTitle"
      :row-data="currentRowData"
      @close-dialog="dialogVisible = false"
      @submit="handleDialogSubmit"
    />
  </div>
</template>

<style scoped>
:deep(.current-row-highlight) {
  background-color: #fb7185 !important; /* bg-rose-400 */
}
</style>
