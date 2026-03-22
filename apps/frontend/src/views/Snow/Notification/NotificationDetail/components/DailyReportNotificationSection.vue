<template>
  <ContentWrap title="日常报告内容" class="mt-5">
    <Descriptions :schema="dailyReportSummarySchema" :data="dailyReportContent">
      <!-- DataBox 测试结果：成功/失败 彩色标签显示 -->
      <template #databox_test_result="{ row }">
        <ElTag :type="row.databox_test_result?.includes('成功') ? 'success' : 'danger'">
          {{ row.databox_test_result }}
        </ElTag>
      </template>
      <!-- 调度器状态：运行正常 success，否则 warning -->
      <template #scheduler_status="{ row }">
        <ElTag :type="row.scheduler_status === '运行正常' ? 'success' : 'warning'">
          {{ row.scheduler_status }}
        </ElTag>
      </template>
      <!-- 未处理确认数：>0 warning，否则 success -->
      <template #unprocessed_confirm_count="{ row }">
        <ElTag :type="Number(row.unprocessed_confirm_count) > 0 ? 'warning' : 'success'">
          {{ row.unprocessed_confirm_count }}
        </ElTag>
      </template>
    </Descriptions>
    <template v-for="tbl in dailyReportTables" :key="tbl.title">
      <ContentWrap class="mt-5" :title="tbl.title">
        <Table :columns="tbl.columns" :data="tbl.data" />
      </ContentWrap>
    </template>
    <ContentWrap v-if="showDailyReportRaw" class="mt-5" title="原始数据">
      <pre style="white-space: pre-wrap">{{ dailyReportRaw }}</pre>
    </ContentWrap>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
import Descriptions from '@/components/Descriptions/src/Descriptions.vue'
import { Table } from '@/components/Table'
import { ElTag } from 'element-plus'
import type { PropType } from 'vue'

const props = defineProps({
  dailyReportSummarySchema: { type: Array as PropType<DescriptionsSchema[]>, required: true },
  dailyReportContent: { type: Object as PropType<Record<string, unknown>>, required: true },
  dailyReportTables: {
    type: Array as PropType<Array<{ title: string; columns: TableColumn[]; data: Record<string, unknown>[] }>>,
    required: true,
  },
  showDailyReportRaw: { type: Boolean, required: true },
  dailyReportRaw: { type: String, required: true },
})
</script>
