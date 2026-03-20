<template>
  <el-tabs v-model="activeTab" type="border-card">
    <el-tab-pane name="all">
      <template #label>
        <el-badge class="tab-badge" :value="totalUnread" :hidden="!(totalUnread > 0)">
          <span>全部通知</span>
        </el-badge>
      </template>
  <NotificationListPane
        :columns="allSchemas.tableColumns"
        :activated="activeTab === 'all'"
        @view="notificationDetail"
        @updated="refreshUnreadCounts"
      />
    </el-tab-pane>
    <el-tab-pane v-for="bt in businessTypeEnum" :key="bt.value" :name="`bt-${bt.value}`">
      <template #label>
        <el-badge class="tab-badge" :value="unreadFor(bt.value)" :hidden="!(unreadFor(bt.value) > 0)">
          <span>{{ bt.label }}</span>
        </el-badge>
      </template>
  <NotificationListPane
        :columns="allSchemas.tableColumns"
        :businessType="bt.value"
        :activated="activeTab === `bt-${bt.value}`"
        @view="notificationDetail"
        @updated="refreshUnreadCounts"
      />
    </el-tab-pane>
  </el-tabs>
</template>
<script setup lang="ts">
import NotificationListPane from './components/NotificationListPane.vue'
import { CrudSchema, useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { h, onMounted, onUnmounted, reactive, ref, computed, onActivated, watch } from 'vue'
// 导入通知接口
import * as notificationApi from '@/api/snow/Notification/index'
import { useRouter } from 'vue-router'
// 枚举管理
import { useEnum } from '@/hooks/web/useEnum'
// 导入路由
// import { useRouter } from 'vue-router'
const router = useRouter()

const activeTab = ref<string>('all')

// 使用枚举管理系统：通知业务类型 / 通知类型 / 通知状态
const {
  enumData: businessTypeEnum,
  loadEnum: loadBusinessTypeEnum,
  getLabel: getBusinessTypeLabel,
  getValue: getBusinessTypeValue,
} = useEnum('NotificationBusinessTypeEnum')
const { loadEnum: loadNoticeTypeEnum, getLabel: getNoticeTypeLabel } = useEnum('NotificationNoticeTypeEnum')
const { loadEnum: loadStatusEnum, getLabel: getStatusLabel } = useEnum('NotificationStatusEnum')

// 组件挂载时加载枚举数据
onMounted(async () => {
  try {
    await Promise.all([loadBusinessTypeEnum(), loadNoticeTypeEnum(), loadStatusEnum()])
  } catch (error) {
    console.error('加载通知枚举数据失败:', error)
  }
  await refreshUnreadCounts()
})
// 组件激活时刷新计数（在使用 keep-alive 或路由返回时）
onActivated(async () => {
  await refreshUnreadCounts()
})
watch(activeTab, async () => {
  await refreshUnreadCounts()
})

// 枚举标签获取封装
const getBusinessTypeName = (businessType: number) => getBusinessTypeLabel(businessType) || '未知'
const getNoticeTypeName = (noticeType: number) => getNoticeTypeLabel(noticeType) || '未知'
const getNoticeStatusName = (status: number) => getStatusLabel(status) || '未知'

// 判断状态tag样式的方法
const tagType = (row: any) => {
  if (row.noticeStatus == 2 && row.noticeType == 0) {
    return 'info'
  } else if (row.noticeStatus == 1 || (row.noticeStatus == 2 && row.noticeType == 1)) {
    return 'warning'
  } else if (row.noticeStatus == 3) {
    return 'success'
  }
}

import { createNotificationCrudSchemas } from './schemas'
const crudSchemas = reactive<CrudSchema[]>(
  createNotificationCrudSchemas({
    getBusinessTypeName,
    getNoticeTypeName,
    getNoticeStatusName,
    tagType,
  })
)

// 使用CurdSchema
let allSchemas = useCrudSchemas(crudSchemas).allSchemas

// 跳转通知详情方法
const notificationDetail = (row: any) => {
  router.push({
    path: '/dashboard/notification/detail',
    query: {
      id: row.id,
    },
  })
}

// 监听数据列表条数变化

// 未读计数与业务类型枚举值
const unreadCounts = ref<Record<number, number>>({})
const unreadFor = (bt: number) => unreadCounts.value[bt] ?? 0

// 总未读数量（全部通知）
const totalUnread = computed(() => {
  return Object.values(unreadCounts.value).reduce((sum, v) => sum + (typeof v === 'number' ? v : 0), 0)
})

// 刷新未读分组计数
const refreshUnreadCounts = async () => {
  try {
    const res = await notificationApi.getUnreadGroupCount()
    const data: any = res?.data
    const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
    const next: Record<number, number> = {}
    list.forEach((item: any) => {
      const rawBt = item.key ?? item.type ?? item.businessType
      const rawCnt = item.count ?? item.unreadCount
      const bt = typeof rawBt === 'string' ? Number(rawBt) : rawBt
      const cnt = typeof rawCnt === 'string' ? Number(rawCnt) : rawCnt
      if (typeof bt === 'number' && typeof cnt === 'number') {
        next[bt] = cnt
      }
    })
    unreadCounts.value = next
  } catch (e) {
    // 失败时保持现有计数
  }
}
onUnmounted(() => {
  // 输出销毁提示
  console.log('销毁:', '通知模块')
})
</script>
<style scoped>
:deep(.tab-badge) {
  padding-right: 18px;
}

:deep(.tab-badge .el-badge__content.is-fixed) {
  transform: translate(50%, 10%);
}

:deep(.tab-badge .el-badge__content) {
  z-index: 10;
}

:deep(.el-tabs__nav-wrap) {
  overflow: visible;
}
</style>
