<template>
  <ContentWrap title="通知内容" class="mt-5">
    <div>
      <el-button type="primary" :disabled="currentGridInfoIndex == 0" @click="emit('prev')">上一个</el-button>
      <el-button type="primary" :disabled="currentGridInfoIndex == gridInfoCount - 1" @click="emit('next')"
        >下一个</el-button
      >
    </div>
    <Descriptions :title="currentGridInfo?.asset_name" :schema="girdInfoSchema" :data="currentGridInfo" class="mt-5" />
    <ContentWrap title="可能发生交易的数据" class="mt-5">
      <Table :columns="tradeListSchema" :data="currentGridInfo?.trade_list" />
    </ContentWrap>
    <ContentWrap
      title="监控挡位变化的网格数据"
      class="mt-5"
      message="深色为历史数据，亮色为当前数据。会根据实际条件判断是否需要修改监控档位"
    >
      <Table
        :columns="monitorChangeSchema"
        :data="currentGridInfo?.current_change"
        :default-sort="{ prop: 'gear', order: 'descending' }"
        :row-class-name="tableRowClassName"
      />
    </ContentWrap>

    <!-- 操作通知 -->
    <ContentWrap class="mt-5" title="通知操作">
      <div class="flex justify-center" style="width: 100%">
        <el-button type="primary" :disabled="disableConfirm" @click="emit('openConfirmDialog')">确认通知内容</el-button>
      </div>
    </ContentWrap>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
import Descriptions from '@/components/Descriptions/src/Descriptions.vue'
import { Table } from '@/components/Table'
import type { PropType } from 'vue'

const props = defineProps({
  currentGridInfo: { type: Object as PropType<Record<string, any>>, required: true },
  currentGridInfoIndex: { type: Number, required: true },
  gridInfoCount: { type: Number, required: true },
  girdInfoSchema: { type: Array as PropType<DescriptionsSchema[]>, required: true },
  monitorChangeSchema: { type: Array as PropType<TableColumn[]>, required: true },
  tradeListSchema: { type: Array as PropType<TableColumn[]>, required: true },
  tableRowClassName: { type: Function as PropType<(row: Record<string, any>) => string>, required: true },
  disableConfirm: { type: Boolean, default: false },
})

const emit = defineEmits<{
  (e: 'prev'): void
  (e: 'next'): void
  (e: 'openConfirmDialog'): void
  (e: 'openEditDialog', row: Record<string, any>): void
}>()
</script>

<style scoped>
/* 与确认通知弹窗颜色保持一致：非当前（历史）较浅、当前更醒目 */
:deep(.history-row) {
  --el-table-tr-bg-color: var(--el-color-info-light-9);
  color: var(--el-text-color-primary);
  border-left: 3px solid var(--el-color-info);
}

:deep(.cur-row) {
  --el-table-tr-bg-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
  border-left: 3px solid var(--el-color-primary);
  font-weight: 600;
}
</style>
