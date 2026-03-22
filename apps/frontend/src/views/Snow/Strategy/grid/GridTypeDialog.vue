<script lang="ts" setup>
import * as gridTypeApi from '@/api/snow/gridType/index'
import { ContentWrap } from '@/components/ContentWrap'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { useForm } from '@/hooks/web/useForm'
import { useValidator } from '@/hooks/web/useValidator'
import { ElMessage } from 'element-plus'
import _ from 'lodash-es'
import { computed, PropType, reactive, ref, unref, watch } from 'vue'

const emit = defineEmits(['close-dialog', 'update:dialog-visible'])

interface GridTypeInfo {
  gridId?: number
  gridTypeId?: number
}

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '网格类型数据操作'
  },
  gridTypeInfo: {
    type: Object as PropType<GridTypeInfo>
  }
})
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialog-visible', val)
})
// 关闭对话框
const closeDialog = () => {
  emit('close-dialog')
}

// 表单校验
const { required } = useValidator()
// 表单引用
const formRef = ref<FormExpose>()

const gridFormSchema = reactive<FormSchema[]>([
  {
    field: 'typeName',
    label: '网格类型名称',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: 'width:200px'
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'gridTypeStatus',
    label: '网格类型状态',
    component: 'Select',
    componentProps: {
      options: [
        {
          value: 0,
          label: '启用'
        },
        {
          value: 1,
          label: '停用'
        },
        {
          value: 2,
          label: '只卖出'
        },
        {
          value: 3,
          label: '只买入'
        }
      ]
    },
    formItemProps: {
      rules: [required()]
    },
    value: 0 // 默认启用
  }
])

const { register, methods } = useForm({
  gridFormSchema
})

// 提交表单数据，关闭弹窗
const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (valid) {
        const model = unref(formRef)?.formModel
        const res = await gridTypeApi.saveOrUpdateGridType(model)
        if (res && res.data) {
          ElMessage({
            message: res.message,
            type: 'success'
          })
          closeDialog()
        }
      }
    })
}

watch(
  () => props.gridTypeInfo?.gridTypeId,
  async (gridTypeId) => {
    
    if (!gridTypeId) return
    const gridTypeRes = await gridTypeApi.getGridType({ id: gridTypeId })
    if (gridTypeRes && gridTypeRes.data) {
      const { setValues } = methods
      const data = Object.assign({}, gridTypeRes.data, props.gridTypeInfo)
      setValues(data)
    }
  }
)

// 监听gridId
watch(
  () => props.gridTypeInfo?.gridId,
  async (gridId) => {
    const { setValues } = methods
    // 合并模型
    const model = unref(formRef)?.formModel
    const data = Object.assign({},model, { gridId })
    setValues(data)
  }
)
</script>
<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <ContentWrap title="网格表单">
      <Form ref="formRef" class="text-center" :is-col="false" :schema="gridFormSchema" @register="register" />
    </ContentWrap>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">提交</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<style></style>
