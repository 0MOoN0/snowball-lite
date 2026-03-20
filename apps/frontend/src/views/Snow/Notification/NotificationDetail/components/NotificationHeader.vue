<template>
  <Descriptions :schema="schema" :title="notificationDetail?.title" :data="notificationDetail">
    <template #businessType="data">
      {{ getBusinessTypeName(data.row.businessType) }}
    </template>
    <template #noticeType="data">
      {{ getNoticeTypeName(data.row.noticeType) }}
    </template>
    <template #noticeStatus="data">
      <el-tag :type="getNoticeTagType(data.row)">
        {{ getNoticeStatusName(data.row.noticeStatus) }}
      </el-tag>
    </template>
  </Descriptions>
</template>

<script setup lang="ts">
import Descriptions from '@/components/Descriptions/src/Descriptions.vue'
import { useEnum } from '@/hooks/web/useEnum'
import type { SnowNotification } from '@/api/snow/Notification/types'
import { reactive, onMounted } from 'vue'

const props = defineProps<{ notificationDetail: SnowNotification | Record<string, any> }>()

const schema = reactive<DescriptionsSchema[]>([
  { label: '业务类型', field: 'businessType' },
  { label: '通知类型', field: 'noticeType' },
  { label: '通知状态', field: 'noticeStatus' },
  { label: '通知等级', field: 'noticeLevel' },
  { label: '通知日期', field: 'timestamp' },
])

// 枚举管理系统：通知业务类型 / 通知类型 / 通知状态
const { loadEnum: loadBusinessTypeEnum, getLabel: getBusinessTypeLabel } = useEnum('NotificationBusinessTypeEnum')
const { loadEnum: loadNoticeTypeEnum, getLabel: getNoticeTypeLabel } = useEnum('NotificationNoticeTypeEnum')
const { loadEnum: loadStatusEnum, getLabel: getStatusLabel } = useEnum('NotificationStatusEnum')

const getBusinessTypeName = (businessType: number) => getBusinessTypeLabel(businessType) || '未知'
const getNoticeTypeName = (noticeType: number) => getNoticeTypeLabel(noticeType) || '未知'
const getNoticeStatusName = (status: number) => getStatusLabel(status) || '未知'

// 状态标签类型与列表页保持一致：
// info: 已读且消息型；warning: 未读或已读且确认型；success: 已处理；默认：primary
const getNoticeTagType = (row: Record<string, any>) => {
  const status = row?.noticeStatus
  const type = row?.noticeType
  if (status === 2 && type === 0) {
    return 'info'
  } else if (status === 1 || (status === 2 && type === 1)) {
    return 'warning'
  } else if (status === 3) {
    return 'success'
  }
  return 'primary'
}

onMounted(async () => {
  try {
    await Promise.all([loadBusinessTypeEnum(), loadNoticeTypeEnum(), loadStatusEnum()])
  } catch (e) {
    // 忽略枚举加载错误，使用回退逻辑
  }
})
</script>
