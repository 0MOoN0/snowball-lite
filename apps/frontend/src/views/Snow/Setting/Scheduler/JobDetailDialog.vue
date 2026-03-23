<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <Form ref="formRef" :is-col="false" :schema="jobForm" />
    <template #footer>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import type { JobInfo } from '@/api/snow/Scheduler/job/types'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { computed, nextTick, reactive, ref, unref, watch, type PropType } from 'vue'

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
    type: Object as PropType<JobInfo | null>,
    default: null
  }
})
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})
// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

const formRef = ref<FormExpose>()

const jobForm = reactive<FormSchema[]>([
  {
    field: 'jobId',
    label: 'ID',
    component: 'Input',
    componentProps: {
      readonly: true
    }
  },
  {
    field: 'name',
    label: '任务名称',
    component: 'Input',
    componentProps: {
      readonly: true
    }
  },
  {
    field: 'func',
    label: '调用方法',
    component: 'Input',
    componentProps: {
      type: 'textarea',
      readonly: true
    }
  },
  {
    field: 'args',
    label: '参数列表',
    component: 'Input',
    componentProps: {
      readonly: true
    }
  },
  {
    field: 'kwargs',
    label: '关键字参数字典',
    component: 'Input',
    componentProps: {
      type: 'textarea',
      readonly: true
    }
  },
  {
    field: 'trigger',
    label: '触发器',
    component: 'Select',
    labelMessage: `date：一次性指定固定时间，只执行一次。
                   interval：间隔调度，隔多长时间执行一次。
                   cron：指定相对时间执行，比如每天几点几分。`,
    componentProps: {
      options: [
        {
          label: 'date',
          value: 'date'
        },
        {
          label: 'interval',
          value: 'interval'
        },
        {
          label: 'cron',
          value: 'cron'
        }
      ],
      disabled: true
    }
  }
])

watch(
  () => props.jobInfo,
  (jobInfo) => {
    nextTick(() => {
      if (jobInfo) {
        unref(formRef)?.setValues(jobInfo)
      }
    })
  }
)
</script>
<style></style>
