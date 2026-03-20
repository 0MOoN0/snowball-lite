<template>
  <el-skeleton :loading="detailLoading" animated>
    <template #template>
      <el-skeleton-item variant="rect" style="height: 100px; margin-bottom: 16px" />
      <el-skeleton-item variant="p" style="width: 80%; margin-bottom: 8px" />
      <el-skeleton-item variant="p" style="width: 60%; margin-bottom: 8px" />
      <el-skeleton-item variant="rect" style="height: 200px; margin-bottom: 16px" />
    </template>
    <template #default>
      <NotificationHeader :notification-detail="notificationDetail" />
      <!-- 网格交易通知内容 -->
      <GridNotificationContainer v-if="isGridNotification" :notification-detail="notificationDetail" @updated="refreshDetail" />

      <!-- 日常报告通知内容 -->
      <DailyReportNotificationSection
        v-else-if="isDailyReportNotification"
        :daily-report-summary-schema="dailyReportSummarySchema"
        :daily-report-content="dailyReportContent"
        :daily-report-tables="dailyReportTables"
        :show-daily-report-raw="showDailyReportRaw"
        :daily-report-raw="dailyReportRaw"
      />

      <!-- 系统运行通知内容 -->
      <SystemRunNotificationSection
        v-else-if="isSystemRunNotification"
        :title="notificationDetail?.title || '系统运行检测'"
        :system-run-summary-schema="systemRunSummarySchema"
        :system-run-content-data="systemRunContentData"
      />

      <!-- 其他业务类型回退显示 -->
      <GenericNotificationSection v-else :generic-content-raw="genericContentRaw" />
    </template>
  </el-skeleton>
</template>
<script setup lang="ts">
import { useRoute } from 'vue-router'
// 导入通知接口
import * as notificationApi from '@/api/snow/Notification/index'
// 子组件
import NotificationHeader from './components/NotificationHeader.vue'
import GridNotificationContainer from './components/GridNotificationContainer.vue'
import DailyReportNotificationSection from './components/DailyReportNotificationSection.vue'
import GenericNotificationSection from './components/GenericNotificationSection.vue'
import SystemRunNotificationSection from './components/SystemRunNotificationSection.vue'
// 导入Table组件类型依赖等
import { GridInfo, SnowNotification } from '@/api/snow/Notification/types'
import { CrudSchema, useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { useValidator } from '@/hooks/web/useValidator'
import { webHelper } from '@/utils/webHelper'
import {
  labelMap,
  makeFormatter,
  formatPercent,
  buildSystemRunRender,
  buildDailyReportRender as buildDailyReportRenderHelper,
} from './helpers'
import { reactive, ref, computed, onMounted } from 'vue'
// 枚举管理
import { useEnum } from '@/hooks/web/useEnum'

const { required } = useValidator()

// 获取路由参数
const router = useRoute()
const notificationDetailId = router.query.id

// 页面加载骨架屏控制
const detailLoading = ref<boolean>(true)

// 通知详情数据
const notificationDetail = ref<SnowNotification>({})

/**
 * 确认通知的提交数据，数据为数组类型，数组内容为对象
 * 对象内部包含tradeRecord对象数组和currentChange对象数组
 * tradeRecord对象数组为对应的交易记录对象，结构为{gridTypeDetailId:recordObject}
 * currentChanage数组的对象为网格监控档位可能发生变化的id数组
 * 总体结构：[{'tradeRecord':[{1:{}}], 'currentChange':[{}]}]
 */

// 通知详情基础描述已抽取到 NotificationHeader 子组件

// 网格通知内容已在 GridNotificationContainer 中集中管理

// 使用枚举管理系统：通知业务类型 / 通知类型 / 通知状态
const {
  loadEnum: loadBusinessTypeEnum,
  getLabel: getBusinessTypeLabel,
  getValue: getBusinessTypeValue,
} = useEnum('NotificationBusinessTypeEnum')
const { loadEnum: loadNoticeTypeEnum, getLabel: getNoticeTypeLabel } = useEnum('NotificationNoticeTypeEnum')
const { loadEnum: loadStatusEnum, getLabel: getStatusLabel } = useEnum('NotificationStatusEnum')

// 枚举标签封装
const getBusinessTypeName = (businessType: number) => getBusinessTypeLabel(businessType) || '未知'
const getNoticeTypeName = (noticeType: number) => getNoticeTypeLabel(noticeType) || '未知'
const getNoticeStatusName = (status: number) => getStatusLabel(status) || '未知'

// 业务类型判定值（避免魔法值）
const dailyReportTypeValue = ref<number | undefined>(undefined)
const gridBusinessTypeValue = ref<number | undefined>(undefined)
const systemRunTypeValue = ref<number | undefined>(undefined)

// 日常报告渲染数据
type DailyReportContent = Record<string, unknown>
const dailyReportContent = ref<DailyReportContent>({})
const dailyReportSummarySchema = ref<DescriptionsSchema[]>([])
const dailyReportTables = ref<Array<{ title: string; columns: TableColumn[]; data: Record<string, unknown>[] }>>([])
const showDailyReportRaw = ref<boolean>(false)
const dailyReportRaw = ref<string>('')
const genericContentRaw = ref<string>('')

// 系统运行通知渲染数据（DataBox 功能测试等）
const systemRunSummarySchema = ref<DescriptionsSchema[]>([])
const systemRunContentData = ref<Record<string, unknown>>({})

// 业务类型判定（严格基于后端枚举，不做内容形态回退）
const isGridNotification = computed(() => {
  const rawBt = (notificationDetail.value as any)?.businessType
  const bt = typeof rawBt === 'string' ? Number(rawBt) : (rawBt as number | undefined)
  // 仅使用后端枚举值，不再在前端维护常量；保留 grid_info 结构兜底
  const candidates = [gridBusinessTypeValue.value].filter((v) => v !== undefined) as number[]
  const hasGridInfo = Array.isArray((notificationDetail.value as any)?.content?.grid_info)
  return (!!bt && candidates.includes(bt)) || hasGridInfo
})
const isDailyReportNotification = computed(() => {
  const rawBt = (notificationDetail.value as any)?.businessType
  const bt = typeof rawBt === 'string' ? Number(rawBt) : (rawBt as number | undefined)
  const candidates = [dailyReportTypeValue.value].filter((v) => v !== undefined) as number[]
  return !!bt && candidates.includes(bt)
})
const isSystemRunNotification = computed(() => {
  const rawBt = (notificationDetail.value as any)?.businessType
  const bt = typeof rawBt === 'string' ? Number(rawBt) : (rawBt as number | undefined)
  const candidates = [systemRunTypeValue.value].filter((v) => v !== undefined) as number[]
  return !!bt && candidates.includes(bt)
})

// 获取通知详情ID获取通知详情
const getNotificationDetail = async (notificationDetailId) => {
  detailLoading.value = true
  try {
    const res = await notificationApi.getNotificationDetail(notificationDetailId)
    // 如果响应数据不为空，则将响应数据赋值给notificationDetail
    if (res.data) {
      notificationDetail.value = res.data
      try {
        notificationDetail.value.content = JSON.parse(res.data.content)
      } catch (e) {
        // 非 JSON 字符串或解析失败，保留原始内容
        notificationDetail.value.content = res.data.content as any
      }
      // 根据业务类型分别处理内容
      if (isGridNotification.value) {
        // 网格通知内容由 GridNotificationContainer 负责管理
      } else if (isDailyReportNotification.value) {
        // 日常报告：尝试构造描述和动态表格
        buildDailyReportRender(notificationDetail.value.content as DailyReportContent)
      } else if (isSystemRunNotification.value) {
        // 系统运行通知：解析 DataBox 测试与运行信息
        const contentObj = notificationDetail.value.content as Record<string, unknown>
        const { summarySchema, contentData } = buildSystemRunRender(contentObj)
        systemRunContentData.value = contentData
        systemRunSummarySchema.value = summarySchema
      } else {
        // 其他业务类型：回退显示原始内容
        genericContentRaw.value = JSON.stringify(notificationDetail.value.content, null, 2)
      }
    }
  } finally {
    detailLoading.value = false
  }
}

const refreshDetail = () => {
  getNotificationDetail(notificationDetailId)
}

// 构建日常报告渲染数据（动态）
const buildDailyReportRender = (content: DailyReportContent) => {
  try {
    const { raw, summarySchemas, summaryData, tables, showRaw } = buildDailyReportRenderHelper(content)
    dailyReportRaw.value = raw
    dailyReportSummarySchema.value = summarySchemas
    dailyReportContent.value = summaryData
    dailyReportTables.value = tables
    showDailyReportRaw.value = showRaw
  } catch (e) {
    // 构建失败直接展示原始数据
    showDailyReportRaw.value = true
  }
}
// 加载枚举并初始化业务类型判定后再拉取详情
onMounted(async () => {
  try {
    // 加载枚举，使用后端真实标签进行精确匹配
    await loadBusinessTypeEnum()
    await Promise.all([loadNoticeTypeEnum(), loadStatusEnum()])

    // 精确标签：网格交易=0，系统运行=2，日常报告=3
    dailyReportTypeValue.value = getBusinessTypeValue('日常报告')
    gridBusinessTypeValue.value = getBusinessTypeValue('网格交易')
    systemRunTypeValue.value = getBusinessTypeValue('系统运行')
  } catch (e) {
    // 忽略枚举加载错误，使用回退逻辑
  } finally {
    getNotificationDetail(notificationDetailId)
  }
})

// 已由枚举标签替换显示逻辑

// 网格相关交互、样式与表格列已在 GridNotificationContainer 中集中管理
</script>

<style>
/* 行样式已迁移至 GridNotificationSection.vue 并做了暗/亮主题适配 */
</style>
