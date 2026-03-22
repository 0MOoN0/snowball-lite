<template>
  <ContentWrap title="通知内容" class="mt-5">
    <pre style="white-space: pre-wrap">{{ genericContentRaw }}</pre>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
import type { PropType } from 'vue'

const props = defineProps({
  genericContentRaw: { type: String as PropType<string>, required: true },
})
</script>
