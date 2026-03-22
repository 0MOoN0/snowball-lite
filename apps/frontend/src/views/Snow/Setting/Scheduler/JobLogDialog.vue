<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <Descriptions title="日志数据" :data="jobInfo" :schema="jobLogSchema" :column="4">
      <template #traceback="{ row }">
        <span v-html="row.traceback" class="text-wrap"></span>
      </template>
    </Descriptions>
    <template #footer>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import { Descriptions } from '@/components/Descriptions'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { computed, reactive } from 'vue'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: ''
  },
  jobInfo: {
    type: Object,
    default: null
  }
})

const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})

const jobLogSchema = reactive<DescriptionsSchema[]>([
  {
    field: 'exception',
    label: '异常信息',
    span: 24
  },
  {
    field: 'traceback',
    label: '堆栈信息',
    span: 24
  }
])

// == 数据定义

// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

</script>
<style>
.text-wrap {
  white-space: pre-line;
  /* 保留换行符并换行 */
}
</style>
