<template>
  <Dialog
    v-model="dialogShow"
    :title="dialogTitle"
    @close="closeDialog"
    center
    :maxHeight="'80vh'"
    class="asset-edit-dialog"
  >
    <div class="asset-form-container">
      <!-- 顶部状态条 -->
      <div v-if="isEditMode && isLoading" class="status-bar loading-status">
        <el-icon class="is-loading" size="16">
          <Loading />
        </el-icon>
        <span class="status-text">正在加载资产详情...</span>
      </div>
      <div v-else-if="isSubmitting" class="status-bar submitting-status">
        <el-icon class="is-loading" size="16">
          <Loading />
        </el-icon>
        <span class="status-text">正在提交数据，请稍候...</span>
      </div>

      <!-- 表单内容 -->
      <Form
        :schema="assetFormSchema"
        ref="formRef"
        :is-col="true"
        :labelWidth="120"
        :disabled="isSubmitting"
        class="asset-form"
        :class="{ 'form-with-status': isEditMode && isLoading || isSubmitting }"
      >
      </Form>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <ElButton type="primary" @click="confirmDialog" size="default" :loading="isSubmitting" :disabled="isSubmitting">
          <Icon v-if="!isSubmitting" icon="ep:check" class="mr-5px" />
          {{ isSubmitting ? '提交中...' : '提交' }}
        </ElButton>
        <ElButton @click="closeDialog" size="default" :disabled="isSubmitting">
          <Icon icon="ep:close" class="mr-5px" />
          关闭
        </ElButton>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import * as assetApi from '@/api/snow/asset/AssetApi'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { Form, FormExpose } from '@/components/Form'
import { Icon } from '@/components/Icon'
import { useEnum } from '@/hooks/web/useEnum'
import { useValidator } from '@/hooks/web/useValidator'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, nextTick, onMounted, reactive, ref, unref, watch } from 'vue'
import { getFormSchema } from './assetFormSchemas'
import { useAssetForm } from './useAssetForm'
// FormSchema类型已在全局定义文件中声明

const emit = defineEmits(['closeDialog', 'update:dialogVisible', 'dataChanged'])

const { required } = useValidator()

const formRef = ref<FormExpose>()

 

// 使用枚举管理系统
const { enumData: assetTypeEnum, loadEnum: loadAssetTypeEnum } = useEnum('AssetTypeEnum')
const { enumData: currencyEnum, loadEnum: loadCurrencyEnum } = useEnum('CurrencyEnum')
const { enumData: marketEnum, loadEnum: loadMarketEnum } = useEnum('MarketEnum')
const { enumData: assetStatusEnum, loadEnum: loadAssetStatusEnum } = useEnum('AssetStatusEnum')
const { enumData: fundStatusEnum, loadEnum: loadFundStatusEnum } = useEnum('FundStatusEnum')
const { enumData: fundTradingModeEnum, loadEnum: loadFundTradingModeEnum } = useEnum('FundTradingModeEnum')
const { enumData: fundTypeEnum, loadEnum: loadFundTypeEnum } = useEnum('FundTypeEnum')

// 从父组件中接受的参数
const dialogParams = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false,
  },
  dialogTitle: {
    type: String,
    default: '证券元数据操作',
  },
  curAsset: {
    type: Object,
    default: null,
  },
})

// 计算属性：判断是否为编辑模式
const isEditMode = computed(() => {
  return dialogParams.dialogVisible && dialogParams.curAsset !== undefined
})

// 计算属性：判断是否正在加载
const isLoading = computed(() => {
  // 只有在编辑模式下，且curAsset为null，且对话框是可见的时候才显示加载状态
  return isEditMode.value && dialogParams.curAsset === null && dialogParams.dialogVisible
})

// 组件挂载时加载枚举数据
onMounted(async () => {
  try {
    await Promise.all([
      loadAssetTypeEnum(),
      loadCurrencyEnum(),
      loadMarketEnum(),
      loadAssetStatusEnum(),
      loadFundStatusEnum(),
      loadFundTradingModeEnum(),
      loadFundTypeEnum(),
    ])
    console.log('所有枚举数据加载完成')
  } catch (error) {
    console.error('加载枚举数据失败:', error)
  }
})

watch(
  () => dialogParams.curAsset,
  (val) => {
    nextTick(() => {
      console.log('val ', val)

      // 根据资产类型动态更新表单schema
      if (val && val.assetType !== undefined) {
        const newSchema = buildSchema(handleAssetTypeChange, val.assetType)
        assetFormSchema.splice(0, assetFormSchema.length, ...newSchema)
      }

      // 处理多态数据的字段映射
      const mappedValues = mapAssetData(val)

      unref(formRef)?.setValues(mappedValues)
    })
  }
)

// 数据是否发生变更的标识
const hasDataChanged = ref(false)

// 提交状态管理
const isSubmitting = ref(false)

// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog', hasDataChanged.value)
  // 重置所有状态
  hasDataChanged.value = false
  isSubmitting.value = false
  // 清空数据缓存
  formDataCache.value = {}
  console.log('Dialog closed, cache cleared')
}

const dialogShow = computed({
  get: () => dialogParams.dialogVisible,
  set: (val) => emit('update:dialogVisible', val),
})

const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (valid) {
        const model = unref(formRef)?.formModel
        if (!model) return

        // 开始提交，设置loading状态
        isSubmitting.value = true

        try {
          const optionRes = await assetApi.saveOrUpdateAsset(model)
          if (optionRes && optionRes.success) {
            ElMessage({
              message: '操作成功',
              type: 'success',
            })
            // 标记数据已变更
            hasDataChanged.value = true
            // 调用closeDialog方法正确关闭对话框
            closeDialog()
          } else {
            // 处理API返回的错误
            ElMessage({
              message: optionRes?.message || '操作失败，请重试',
              type: 'error',
            })
          }
        } catch (error) {
          // 处理网络错误或其他异常
          console.error('提交失败:', error)
          ElMessage({
            message: '网络错误，请检查网络连接后重试',
            type: 'error',
          })
        } finally {
          // 无论成功失败都要重置提交状态
          isSubmitting.value = false
        }
      }
    })
}

const assetFormSchema = reactive<FormSchema[]>([])
const buildSchema = (onChange: (val: number) => void, assetType: number) =>
  getFormSchema(assetType, {
    assetTypeOptions: assetTypeEnum.value || [],
    currencyOptions: currencyEnum.value || [],
    marketOptions: marketEnum.value || [],
    assetStatusOptions: assetStatusEnum.value || [],
    fundTypeOptions: fundTypeEnum.value || [],
    fundTradingModeOptions: fundTradingModeEnum.value || [],
    fundStatusOptions: fundStatusEnum.value || [],
    required,
    onAssetTypeChange: onChange,
  })
const { handleAssetTypeChange, mapAssetData, formDataCache } = useAssetForm(
  formRef,
  (schema) => assetFormSchema.splice(0, assetFormSchema.length, ...schema),
  buildSchema
)
assetFormSchema.splice(0, assetFormSchema.length, ...buildSchema(handleAssetTypeChange, 1))
</script>

<style scoped>
.asset-edit-dialog {
  :deep(.el-dialog) {
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    background-color: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
  }

  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px 12px 0 0;

    .el-dialog__title {
      color: white;
      font-weight: 600;
      font-size: 16px;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
    background-color: var(--el-bg-color-page);
    min-height: 400px;
  }

  :deep(.el-dialog__footer) {
    padding: 16px 24px 20px;
    background-color: var(--el-bg-color);
    border-radius: 0 0 12px 12px;
    border-top: 1px solid var(--el-border-color-light);
  }

  /* 表单内容区域样式 */
  :deep(.el-form) {
    background-color: var(--el-bg-color);
    border-radius: 8px;
    padding: 20px;
    border: 1px solid var(--el-border-color-lighter);
    
    .el-form-item {
      margin-bottom: 20px;
      
      .el-form-item__label {
        color: var(--el-text-color-regular);
        font-weight: 500;
        margin-bottom: 8px;
      }
      
      .el-input__inner,
      .el-textarea__inner,
      .el-select .el-input__inner {
        background-color: var(--el-fill-color-blank);
        border: 1px solid var(--el-border-color);
        color: var(--el-text-color-primary);
        border-radius: 6px;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: var(--el-color-primary-light-7);
        }
        
        &:focus {
          border-color: var(--el-color-primary);
          box-shadow: 0 0 0 2px var(--el-color-primary-light-9);
        }
      }
      
      .el-select__wrapper {
        background-color: var(--el-fill-color-blank);
        border: 1px solid var(--el-border-color);
        border-radius: 6px;
        
        &:hover {
          border-color: var(--el-color-primary-light-7);
        }
        
        &.is-focused {
          border-color: var(--el-color-primary);
          box-shadow: 0 0 0 2px var(--el-color-primary-light-9);
        }
      }
    }
  }

  /* 分隔符样式优化 */
  :deep(.el-divider) {
    margin: 24px 0;
    border-color: var(--el-border-color);
    
    .el-divider__text {
      background-color: var(--el-bg-color);
      color: var(--el-text-color-primary);
      font-weight: 600;
      font-size: 14px;
      padding: 0 16px;
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 16px;
        background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
        border-radius: 2px;
      }
    }
  }

  /* 状态条样式 */
  :deep(.el-alert) {
    background-color: var(--el-fill-color-light);
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    
    .el-alert__title {
      color: var(--el-text-color-primary);
    }
    
    .el-alert__description {
      color: var(--el-text-color-regular);
    }
  }
}

:deep(.dark .el-dialog) {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
  background-color: var(--el-bg-color) !important;
  border-color: var(--el-border-color) !important;
}

:deep(.dark .el-dialog__body) {
  background-color: var(--el-bg-color-page) !important;
}

:deep(.dark .el-dialog__footer) {
  background-color: var(--el-bg-color) !important;
  border-top-color: var(--el-border-color) !important;
}

:deep(.dark .el-form) {
  background-color: var(--el-bg-color) !important;
  border-color: var(--el-border-color) !important;
}

:deep(.dark .el-form-item__label) {
  color: var(--el-text-color-primary) !important;
}

:deep(.dark .el-input__inner),
:deep(.dark .el-textarea__inner) {
  background-color: var(--el-fill-color-blank) !important;
  border-color: var(--el-border-color) !important;
  color: var(--el-text-color-primary) !important;
}

:deep(.dark .el-input__inner:hover),
:deep(.dark .el-textarea__inner:hover) {
  border-color: var(--el-color-primary-light-5) !important;
}

:deep(.dark .el-input__inner:focus),
:deep(.dark .el-textarea__inner:focus) {
  border-color: var(--el-color-primary) !important;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
}

:deep(.dark .el-input__inner::placeholder),
:deep(.dark .el-textarea__inner::placeholder) {
  color: var(--el-text-color-secondary) !important;
}

:deep(.dark .el-select__wrapper) {
  background-color: var(--el-fill-color-blank) !important;
  border-color: var(--el-border-color) !important;
}

:deep(.dark .el-select__wrapper:hover) {
  border-color: var(--el-color-primary-light-5) !important;
}

:deep(.dark .el-select__wrapper.is-focused) {
  border-color: var(--el-color-primary) !important;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
}

:deep(.dark .el-select__selected-item) {
  color: var(--el-text-color-primary) !important;
}

:deep(.dark .el-select__placeholder) {
  color: var(--el-text-color-secondary) !important;
}

:deep(.dark .el-divider) {
  border-color: var(--el-border-color) !important;
}

:deep(.dark .el-divider__text) {
  background-color: var(--el-bg-color) !important;
  color: var(--el-text-color-primary) !important;
}

:deep(.dark .el-alert) {
  background-color: var(--el-fill-color-blank) !important;
  border-color: var(--el-border-color) !important;
}

:deep(.dark .el-alert__title) {
  color: var(--el-text-color-primary) !important;
}

:deep(.dark .el-alert__description) {
  color: var(--el-text-color-secondary) !important;
}

.asset-form-container {
  position: relative;
  padding: 24px;
  background-color: var(--el-bg-color);
  min-height: 400px;
  max-height: none;

  /* 让内容自适应高度，避免不必要的滚动条 */
  overflow: visible;
}

.asset-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;

    .el-form-item__label {
      font-weight: 500;
      color: #303133;
      line-height: 1.4;
    }

    .el-form-item__content {
      .el-input,
      .el-select,
      .el-input-number,
      .el-date-editor {
        width: 100%;
      }

      .el-textarea {
        .el-textarea__inner {
          border-radius: 6px;
          border: 1px solid #dcdfe6;
          transition: border-color 0.2s;

          &:focus {
            border-color: #409eff;
            box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
          }
        }
      }
    }
  }

  :deep(.el-row) {
    margin-left: -8px;
    margin-right: -8px;

    .el-col {
      padding-left: 8px;
      padding-right: 8px;
    }
  }
}

/* 顶部状态条样式 */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  margin: -24px -24px 16px -24px;
  border-radius: 8px 8px 0 0;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;

  .el-icon {
    margin-right: 8px;
    flex-shrink: 0;
  }

  .status-text {
    line-height: 1.4;
  }

  &.loading-status {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    color: #1976d2;
    border: 1px solid #90caf9;

    .el-icon {
      color: #1976d2;
    }
  }

  &.submitting-status {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    color: #f57c00;
    border: 1px solid #ffcc02;

    .el-icon {
      color: #f57c00;
    }
  }
}

/* 表单在有状态条时的样式调整 */
.asset-form {
  &.form-with-status {
    opacity: 0.8;
    transition: opacity 0.3s ease;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .el-button {
    min-width: 88px;
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s;

    &.el-button--primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      }
    }

    &:not(.el-button--primary) {
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
    }
  }
}

/* Dialog组件的ElScrollbar会处理滚动，这里不需要额外的滚动条样式 */
</style>
