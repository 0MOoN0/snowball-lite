<template>
  <div>
<GridNotificationSection
  :current-grid-info="currentGridInfo"
  :current-grid-info-index="currentGridInfoIndex"
  :grid-info-count="gridInfoCount"
  :gird-info-schema="girdInfoSchema"
  :monitor-change-schema="monitorChangeSchema.tableColumns"
  :trade-list-schema="tradeListSchema.tableColumns"
  :table-row-class-name="tableRowClassName"
  :disable-confirm="isProcessed"
  @prev="changeCurrentGridInfo(-1)"
  @next="changeCurrentGridInfo(1)"
  @open-confirm-dialog="openConfirmDialogWrapper"
  @open-edit-dialog="openEditDialog"
/>

    <NotificationRecordEditDialog
      :dialog-visible="notificationRecordEditDialogData.visible"
      :dialog-title="notificationRecordEditDialogData.dialogTitle"
      :grid-type-detail="notificationRecordEditDialogData.gridTypeDetail"
      :grid-trade-record="notificationRecordEditDialogData.tradeRecord"
      @closeDialog="closeEditDialog"
      :grid-record-schema="allRecordSchemas.formSchema"
    />
    <NotificationRecordConfirmDialog
      :dialog-visible="notificationRecordConfirmDialogData.visible"
      :dialog-title="notificationRecordConfirmDialogData.dialogTitle"
      :confirm-notification-data="notificationRecordConfirmDialogData.confirmNotificationData"
      @closeDialog="closeConfirmDialog"
      @submitted="handleConfirmSubmitted"
      :grid-record-schema="allRecordSchemas.tableColumns"
      :grid-type-detail-schema="monitorChangeSchema.tableColumns"
      :grid-info-description-schema="girdInfoSchema"
      :notification-detail="notificationRecordConfirmDialogData.notificationDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onMounted, computed } from 'vue'
import { useEnum } from '@/hooks/web/useEnum'
import _ from 'lodash'
import GridNotificationSection from './GridNotificationSection.vue'
import NotificationRecordConfirmDialog from '@/views/Snow/Notification/NotificationDetail/NotificationRecordConfirmDialog.vue'
import NotificationRecordEditDialog from '@/views/Snow/Notification/NotificationDetail/NotificationRecordEditDialog.vue'
import { useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { useValidator } from '@/hooks/web/useValidator'
import { createGridCrudSchemas, createTradeListCrudSchema, gridRowClassName } from '../gridHelpers'
import { createRecordSchemas } from '../schemas/record'
import { useGridNotification } from '../useGridNotification'
import type { SnowNotification, GridInfo } from '@/api/snow/Notification/types'

const props = defineProps<{ notificationDetail: SnowNotification }>()
const emit = defineEmits(['updated'])

const { required } = useValidator()

// 组合式函数：编辑/确认弹窗与确认数据
const {
  confirmNotificationData,
  notificationRecordEditDialogData,
  notificationRecordConfirmDialogData,
  setGridContext,
  openEditDialog,
  closeEditDialog,
  openConfirmDialog,
  closeConfirmDialog,
  initConfirmDataFromGridInfoList,
} = useGridNotification()

// 网格详情上下文
const currentGridInfo = ref<GridInfo | any>({})
const currentGridInfoIndex = ref<number>(0)
const gridInfoCount = ref<number>(0)

// 网格详情描述项
const girdInfoSchema = reactive<DescriptionsSchema[]>([
  { label: '资产名称', field: 'asset_name' },
  { label: '网格类型名称', field: 'grid_type_name' },
])

// 表格列 schema
const crudSchemas = reactive(createGridCrudSchemas())
const monitorChangeSchema = useCrudSchemas(crudSchemas).allSchemas
const tradListCurdSchema = createTradeListCrudSchema(_.cloneDeep(crudSchemas), (row) => openEditDialog(row))
const tradeListSchema = useCrudSchemas(tradListCurdSchema).allSchemas

// 交易记录 schema（用于弹窗）
const recordSchemas = reactive(createRecordSchemas(required))
const allRecordSchemas = useCrudSchemas(recordSchemas).allSchemas

// 行样式
const tableRowClassName = (row) => gridRowClassName(row)

const { enumData: notificationStatusEnum, loadEnum: loadStatusEnum, getValue: getStatusValue } = useEnum('NotificationStatusEnum')
onMounted(async () => {
  try {
    await loadStatusEnum()
  } catch {}
})
const isProcessed = computed(() => {
  const _ = notificationStatusEnum.value
  const status = (props.notificationDetail as any)?.noticeStatus
  const num = typeof status === 'string' ? Number(status) : status
  const processedVal = getStatusValue('已处理') ?? notificationStatusEnum.value?.find((o: any) => o.label === '已处理')?.value ?? 3
  return num === processedVal
})

// 事件：上一条 / 下一条
const changeCurrentGridInfo = (num: number) => {
  currentGridInfoIndex.value += num
  currentGridInfo.value = (props.notificationDetail as any)?.content?.grid_info?.[currentGridInfoIndex.value]
}

// 打开确认弹窗（无参事件包装）
const openConfirmDialogWrapper = () => openConfirmDialog(props.notificationDetail)

const handleConfirmSubmitted = () => {
  emit('updated')
}

// 初始化
const initFromDetail = () => {
  const list = (props.notificationDetail as any)?.content?.grid_info || []
  gridInfoCount.value = list.length || 0
  currentGridInfoIndex.value = 0
  currentGridInfo.value = list[0] || {}
  // 初始化确认数据
  initConfirmDataFromGridInfoList(list)
  // 绑定上下文供编辑弹窗使用
  setGridContext(currentGridInfo, currentGridInfoIndex)
}

onMounted(initFromDetail)
watch(() => (props.notificationDetail as any)?.content?.grid_info, initFromDetail)
</script>

<style scoped></style>
