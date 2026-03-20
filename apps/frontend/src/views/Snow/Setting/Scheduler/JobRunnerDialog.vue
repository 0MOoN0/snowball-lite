<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" center :max-height="200" @open="openDialog">
    <Form ref="formRef" :is-col="false" :schema="jobArgsForm" />
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">提交并执行任务</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import * as schedulerJobApi from '@/api/snow/Scheduler/job/index'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { ElMessage } from 'element-plus'
import _ from 'lodash'
import { computed, nextTick, reactive, ref, unref, watch } from 'vue'

// === 定义属性 ===
const emit = defineEmits(['closeDialog', 'runJob'])
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
  set: (val) => emit('closeDialog', val)
})

const formRef = ref<FormExpose>()

const jobArgsForm = reactive<FormSchema[]>([
  {
    field: 'jobId',
    hidden: true
  },
  {
    field: 'args',
    label: '参数',
    component: 'Input'
  },
  {
    field: 'kwargs',
    label: '关键字参数',
    component: 'Input',
    componentProps: {
      type: 'textarea'
    }
  }
])

// 表单模型副本, 用于表单回填
const jobInfoModel = ref()

// === hook ===

watch(
  () => props.jobInfo,
  (newJobInfo) => {
    jobInfoModel.value = _.pick(newJobInfo, ['jobId', 'args', 'kwargs'])
    // 将kwargs转换为json字符串
    jobInfoModel.value['kwargs'] = JSON.stringify(newJobInfo?.kwargs)
    nextTick(() => {
      unref(formRef)?.setValues(unref(jobInfoModel))
    })
  },
  { deep: true }
)

// === 定义方法 ===
// 关闭对话框
const closeDialog = () => {
  emit('closeDialog')
}

const openDialog = () => {
  unref(formRef)?.setValues(unref(jobInfoModel))
}

// 确认对话框
const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate((valid) => {
      if (valid) {
        const model = unref(formRef)?.formModel
        schedulerJobApi.runJob(model).then((res) => {
          if (res && res.success) {
            ElMessage.success('执行成功')
            // 发送运行任务事件
            emit('runJob', model?.jobId)
            closeDialog()
          } else {
            ElMessage.error('执行失败')
          }
        })
      }
    })
}
</script>
