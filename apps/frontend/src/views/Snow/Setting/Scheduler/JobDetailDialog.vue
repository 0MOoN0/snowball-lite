<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <Form ref="formRef" :is-col="false" :schema="jobForm" />
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">提交</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { useValidator } from '@/hooks/web/useValidator'
import { computed, nextTick, reactive, ref, unref, watch } from 'vue'

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
// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

const formRef = ref<FormExpose>()
const { required } = useValidator()

const jobForm = reactive<FormSchema[]>([
  {
    field: 'id',
    label: 'ID',
    component: 'Input',
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'name',
    label: '任务名称',
    component: 'Input'
  },
  {
    field: 'func',
    label: '调用方法',
    component: 'Input',
    componentProps: {
      type: 'textarea'
    }
  },
  {
    field: 'args',
    label: '参数列表',
    component: 'Input',
    componentProps: {
      placeholder: '请输入参数列表，如果有多个，请使用,隔开'
    }
  },
  {
    field: 'kwargs',
    label: '关键字参数字典',
    component: 'Input',
    componentProps: {
      type: 'textarea'
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
      onChange: (val) => {
        // 根据资产类型构建表单
        console.log('change select: ', val)
      }
    },
    formItemProps: {
      rules: [required()]
    }
  }
])

watch(
  () => props.jobInfo,
  (jobInfo) => {
    nextTick(() => {
      unref(formRef)?.setValues(jobInfo)
    })
  }
)

// 关闭弹窗
const confirmDialog = () => {
  // unref(formRef)
  //   ?.getElFormRef()
  //   ?.validate((valid) => {
  //     if (valid) {
  //       const model = unref(formRef)?.formModel
  //       console.log('model : ', model)
  //       assetApi.saveOrUpdateAsset(model).then((res) => {
  //         if (res.success) {
  //           ElMessage({
  //             message: '操作成功',
  //             type: 'error'
  //           })
  //         }
  //       })
  //     }
  //   })
  const model = unref(formRef)?.formModel
  console.log('model ===> ', model)
}
</script>
<style></style>
