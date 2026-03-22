import { reactive, ref } from 'vue'
import type { Ref } from 'vue'
import _ from 'lodash'
import type { SnowNotification } from '@/api/snow/Notification/types'
import { initConfirmNotificationData } from './gridHelpers'

export function useGridNotification() {
  // 确认数据（按网格项维度收集交易记录与当前变化ID）
  const confirmNotificationData = reactive<Array<any>>([])

  // 编辑弹窗数据
  const notificationRecordEditDialogData = reactive({
    visible: false,
    dialogTitle: '编辑交易记录',
    gridTypeDetail: {},
    tradeRecord: {},
  })

  // 确认弹窗数据
  const notificationRecordConfirmDialogData = reactive({
    visible: false,
    dialogTitle: '确认并提交交易记录',
    confirmNotificationData: {},
    notificationDetail: {} as SnowNotification | Record<string, any>,
  })

  // 由父组件注入的上下文（当前网格与索引）
  // 直接持有父组件的 ref 引用，确保索引变化实时生效
  let currentGridInfoRef: Ref<Record<string, any>> = ref({})
  let currentGridInfoIndexRef: Ref<number> = ref(0)

  const setGridContext = (currentGridInfo: Ref<Record<string, any>>, currentGridInfoIndex: Ref<number>) => {
    currentGridInfoRef = currentGridInfo
    currentGridInfoIndexRef = currentGridInfoIndex
  }

  const openEditDialog = (row: Record<string, any>) => {
    notificationRecordEditDialogData.visible = true
    notificationRecordEditDialogData.dialogTitle =
      '编辑 ' + (currentGridInfoRef.value?.asset_name || '') + ' - ' + (currentGridInfoRef.value?.grid_type_name || '') + ' 交易记录'
    notificationRecordEditDialogData.gridTypeDetail = row

    // 网格类型记录 id
    const gridTypeDetailId = row.id
    const idx = Number(currentGridInfoIndexRef.value)
    const bucket = confirmNotificationData[idx]
    const list = bucket?.tradeRecord || []
    let curRecord = list.find((item: Record<string, any>) => _.findKey(item) == gridTypeDetailId) || {}
    notificationRecordEditDialogData.tradeRecord = curRecord
  }

  const closeEditDialog = (record?: Record<string, any>) => {
    notificationRecordEditDialogData.visible = false
    if (!_.isEmpty(record)) {
      const gridTypeDetailId = _.findKey(record, _.constant(true))
      if (!gridTypeDetailId) return
      const oldRecord = confirmNotificationData[currentGridInfoIndexRef.value].tradeRecord.find(
        (item: Record<string, any>) => _.findKey(item) == gridTypeDetailId
      )
      if (!oldRecord) {
        confirmNotificationData[currentGridInfoIndexRef.value].tradeRecord.push(record)
      } else {
        oldRecord[gridTypeDetailId] = record[gridTypeDetailId]
      }
    }
  }

  const openConfirmDialog = (notificationDetail: SnowNotification | Record<string, any>) => {
    notificationRecordConfirmDialogData.visible = true
    notificationRecordConfirmDialogData.confirmNotificationData = confirmNotificationData
    notificationRecordConfirmDialogData.notificationDetail = notificationDetail
  }

  const closeConfirmDialog = () => {
    notificationRecordConfirmDialogData.visible = false
  }

  const initConfirmDataFromGridInfoList = (gridInfoList: Array<Record<string, any>>) => {
    confirmNotificationData.length = 0
    confirmNotificationData.push(...initConfirmNotificationData(gridInfoList || []))
  }

  return {
    confirmNotificationData,
    notificationRecordEditDialogData,
    notificationRecordConfirmDialogData,
    setGridContext,
    openEditDialog,
    closeEditDialog,
    openConfirmDialog,
    closeConfirmDialog,
    initConfirmDataFromGridInfoList,
  }
}
