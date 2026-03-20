<template>
  <ContentWrap :title="title" class="mt-5">
    <Descriptions :schema="systemRunSummarySchema" :data="systemRunContentData" :column="3" size="small">
      <template #test_result="{ row }">
        <el-tag :type="row.test_result === 'success' ? 'success' : 'danger'">{{ row.test_result }}</el-tag>
      </template>
    </Descriptions>
    <ContentWrap v-if="systemRunContentData?.error_message" class="mt-5" title="错误信息">
      <pre
        style="
          white-space: pre-wrap;
          word-break: break-word;
          background: var(--el-bg-color-overlay);
          padding: 10px;
          border-radius: 6px;
        "
        >{{ systemRunContentData.error_message }}
      </pre>
    </ContentWrap>
  </ContentWrap>
</template>

<script setup lang="ts">
import Descriptions from '@/components/Descriptions/src/Descriptions.vue'
import { ContentWrap } from '@/components/ContentWrap'
import type { PropType } from 'vue'

const props = defineProps({
  title: { type: String, default: '系统运行检测' },
  systemRunSummarySchema: { type: Array as PropType<DescriptionsSchema[]>, required: true },
  systemRunContentData: { type: Object as PropType<Record<string, any>>, required: true },
})

const { title, systemRunSummarySchema, systemRunContentData } = props
</script>

<style scoped></style>
