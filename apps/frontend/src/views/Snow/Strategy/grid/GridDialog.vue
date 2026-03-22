<script lang="ts" setup>
import * as assetApi from '@/api/snow/asset/AssetApi'
import * as gridApi from '@/api/snow/grid/index'
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

interface GridInfo {
  gridId?: number
}

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '网格数据操作'
  },
  gridInfo: {
    type: Object as PropType<GridInfo>
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
    field: 'gridName',
    label: '网格名称',
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
    field: 'assetId',
    label: '关联证券数据',
    component: 'Select',
    componentProps: {
      filterable: true,
      placeholder: '请输入证券名称或相关代码',
      remote: true,
      remoteMethod: (query: string) => {
        queryAsset(query)
      }
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'gridStatus',
    label: '网格状态',
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
        }
      ]
    }
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
        const res = await gridApi.saveOrUpdate(model)
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
/**
 * 根据条件搜索证券数据
 * @param query
 */
const queryAsset = async (query: string) => {
  const res = await assetApi.queryLike({ query_like: query })
  if (res && res.data) {
    const options = res.data.map((x) => {
      return { value: x.id, label: x.assetName }
    })
    const { setSchema } = methods
    setSchema([
      {
        field: 'assetId',
        path: 'componentProps.options',
        value: options
      }
    ])
  }
}

watch(
  () => props.gridInfo,
  async () => {
    const gridId = _.get(props.gridInfo, 'gridId', null)
    if (gridId) {
      const gridRes = await gridApi.getById(gridId)
      if (gridRes && gridRes.data) {
        // 获取证券资产关联数据
        const assetRes = await assetApi.getById(gridRes.data.assetId)
        if (assetRes && assetRes.data) {
          const { setSchema } = methods
          setSchema([
            {
              field: 'assetId',
              path: 'componentProps.options',
              value: [{ value: assetRes.data.id, label: assetRes.data.assetName }]
            }
          ])
        }
        const { setValues } = methods
        setValues(gridRes.data)
      }
    }
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
