<template>
  <Dialog
    v-model="dialogShow"
    :title="dialogTitle"
    @close="closeDialog"
    center
    :maxHeight="'80vh'"
    class="asset-alias-edit-dialog"
  >
    <div class="alias-form-container">
      <div v-if="isEditMode && isLoading" class="status-bar loading-status">
        <el-icon class="is-loading" size="16">
          <Loading />
        </el-icon>
        <span class="status-text">正在加载别名详情...</span>
      </div>
      <div v-else-if="isSubmitting" class="status-bar submitting-status">
        <el-icon class="is-loading" size="16">
          <Loading />
        </el-icon>
        <span class="status-text">正在提交数据，请稍候...</span>
      </div>
      <Form
        :schema="aliasFormSchema"
        ref="formRef"
        :is-col="true"
        :labelWidth="120"
        :disabled="isSubmitting || (isEditMode && isLoading)"
        class="alias-form"
        :class="{ 'form-with-status': (isEditMode && isLoading) || isSubmitting }"
      />
    </div>
    <template #footer>
      <div class="dialog-footer">
        <ElButton type="primary" @click="confirmDialog" size="default" :loading="isSubmitting" :disabled="isSubmitting || (isEditMode && isLoading)">
          {{ isSubmitting ? '提交中...' : '提交' }}
        </ElButton>
        <ElButton @click="closeDialog" size="default" :disabled="isSubmitting">关闭</ElButton>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { Form, FormExpose } from '@/components/Form'
import { ElMessage, ElButton } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { computed, nextTick, reactive, ref, unref, watch } from 'vue'
import * as aliasApi from '@/api/snow/asset/AssetAliasApi'
import * as assetApi from '@/api/snow/asset/AssetApi'
import { useEnum } from '@/hooks/web/useEnum'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

const formRef = ref<FormExpose>()

const dialogParams = defineProps({
  dialogVisible: { type: Boolean, default: false },
  dialogTitle: { type: String, default: '资产别名操作' },
  curAlias: { type: Object, default: null }
})

const isSubmitting = ref(false)
const hasDataChanged = ref(false)

const assetSelectLoading = ref(false)
const assetSelectOptions = ref<any[]>([])

const { enumData: providerEnum, loadEnum, getValue: getProviderValue } = useEnum('ProviderCodeEnum')

const dialogShow = computed({
  get: () => dialogParams.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})

const isEditMode = computed(() => {
  return !!dialogParams.dialogTitle && dialogParams.dialogTitle.includes('编辑')
})

const isLoading = computed(() => {
  return isEditMode.value && dialogParams.curAlias === null && dialogParams.dialogVisible
})

watch(
  () => dialogParams.dialogVisible,
  async (visible) => {
    if (visible) {
      await loadEnum()
      unref(formRef)?.setSchema([
        { field: 'providerName', path: 'component', value: 'Select' },
        { field: 'providerName', path: 'componentProps.options', value: unref(providerEnum) },
        { field: 'providerName', path: 'componentProps.optionsAlias', value: { labelField: 'label', valueField: 'label' } },
        { field: 'providerName', path: 'componentProps.placeholder', value: '请选择提供商名称' },
        {
          field: 'providerName',
          path: 'componentProps.onChange',
          value: (label: string) => {
            const code = getProviderValue(label)
            unref(formRef)?.setValues({ providerCode: code })
          }
        }
      ])
    }
  }
)

watch(
  () => dialogParams.curAlias,
  (val) => {
    nextTick(() => {
      if (val) {
        const normalized = {
          id: val.id,
          assetName: val.assetId,
          providerCode: val.providerCode,
          providerSymbol: val.providerSymbol,
          providerName: val.providerName,
          isPrimary: Number(val.isPrimary ? 1 : 0),
          status: val.status,
          description: val.description
        }
        unref(formRef)?.setValues(normalized)
        if (val.assetId) {
          assetSelectLoading.value = true
          assetApi
            .getById(val.assetId)
            .then((res) => {
              if (res && res.success && res.data) {
                const a = res.data
                assetSelectOptions.value = [
                  { label: `${a.assetName}`, value: a.id }
                ]
                unref(formRef)?.setSchema([
                  { field: 'assetName', path: 'componentProps.options', value: assetSelectOptions.value }
                ])
              }
            })
            .finally(() => {
              assetSelectLoading.value = false
              unref(formRef)?.setSchema([
                { field: 'assetName', path: 'componentProps.loading', value: assetSelectLoading.value }
              ])
            })
        }
      } else {
        unref(formRef)?.getElFormRef()?.resetFields()
      }
    })
  }
)

const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog', hasDataChanged.value)
  hasDataChanged.value = false
  isSubmitting.value = false
}

const confirmDialog = () => {
  if ((isEditMode.value && isLoading.value)) {
    ElMessage({ message: '数据加载中，请稍后再提交', type: 'warning' })
    return
  }
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (!valid) return
      const model = unref(formRef)?.formModel
      if (!model) return
      isSubmitting.value = true
      try {
        const payload = {
          ...model,
          assetId: model.assetName,
          isPrimary: Number(model.isPrimary)
        }
        delete (payload as any).assetName
        const res = await aliasApi.saveOrUpdateAlias(payload)
        if (res && res.success) {
          ElMessage({ message: res.message || '操作成功', type: 'success' })
          hasDataChanged.value = true
          closeDialog()
        } else {
          ElMessage({ message: res?.message || '操作失败，请重试', type: 'error' })
        }
      } catch (e) {
        ElMessage({ message: '网络错误，请重试', type: 'error' })
      } finally {
        isSubmitting.value = false
      }
    })
}

const aliasFormSchema = reactive<FormSchema[]>([
  {
    field: 'assetName',
    label: '资产名称',
    component: 'Select',
    componentProps: {
      filterable: true,
      remote: true,
      placeholder: '请输入资产名称搜索',
      remoteMethod: async (query: string) => {
        assetSelectLoading.value = true
        unref(formRef)?.setSchema([
          { field: 'assetName', path: 'componentProps.loading', value: assetSelectLoading.value }
        ])
        try {
          const res = await assetApi.getAssetSelectList({ page: 1, pageSize: 20, assetName: query })
          if (res && res.success && res.data?.items) {
            assetSelectOptions.value = res.data.items.map((a: any) => ({ label: a.assetName, value: a.id }))
            unref(formRef)?.setSchema([
              { field: 'assetName', path: 'componentProps.options', value: assetSelectOptions.value }
            ])
          }
        } finally {
          assetSelectLoading.value = false
          unref(formRef)?.setSchema([
            { field: 'assetName', path: 'componentProps.loading', value: assetSelectLoading.value }
          ])
        }
      },
      loading: assetSelectLoading.value,
      options: assetSelectOptions.value,
      optionsAlias: { labelField: 'label', valueField: 'value' }
    },
    value: undefined
  },
  {
    field: 'providerName',
    label: '提供商名称',
    labelMessage: '提供商的资产名称',
    component: 'Select',
    componentProps: {
      placeholder: '请选择提供商名称',
      options: [],
      optionsAlias: { labelField: 'label', valueField: 'label' }
    },
    value: ''
  },
  { field: 'providerCode', label: '数据提供商代码', component: 'Input', componentProps: { disabled: true }, value: '' },
  { field: 'providerSymbol', label: '提供商的资产代码', component: 'Input', value: '' },
  {
    field: 'isPrimary',
    label: '主要代码',
    labelMessage: '是否为主要代码',
    component: 'Switch',
    componentProps: { activeValue: 1, inactiveValue: 0 },
    value: 0
  },
  {
    field: 'status',
    label: '状态',
    component: 'Select',
    componentProps: {
      options: [
        { label: '启用', value: 1 },
        { label: '禁用', value: 0 }
      ]
    },
    value: 1
  },
  {
    field: 'description',
    label: '描述',
    component: 'Input',
    componentProps: { type: 'textarea', rows: 3, placeholder: '可填写备注信息' },
    colProps: { span: 24 },
    value: ''
  }
])
</script>

<style scoped>
.alias-form-container {
  padding: 24px;
  background-color: var(--el-bg-color);
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 12px;
}

.loading-status {
  background-color: var(--el-fill-color-light);
}

.submitting-status {
  background-color: var(--el-fill-color);
}

.alias-form.form-with-status {
  opacity: 0.85;
  transition: opacity 0.2s ease;
}

:deep(.el-dialog) {
  background-color: var(--el-bg-color);
}

:deep(.el-dialog__body) {
  background-color: var(--el-bg-color-page);
}

:deep(.el-form) {
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
}
</style>