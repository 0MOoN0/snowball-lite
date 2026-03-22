<template>
  <Dialog
    v-model="dialogShow"
    :title="isEditMode ? '编辑指数' : '新增指数'"
    width="900px"
    @close="closeDialog"
    class="index-edit-dialog"
  >
    <div class="index-form-container">
      <!-- 表单内容 -->
      <Form
        :ref="formManager.formRef"
        :schema="formManager.indexFormSchema.value"
        :rules="formManager.formRules.value"
        :disabled="dataProcessor.isSubmitting.value"
        label-width="120px"
      />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="dataProcessor.isSubmitting.value"
          :disabled="dataProcessor.isSubmitting.value"
          @click="confirmDialog"
        >
          {{ isEditMode ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { Form } from '@/components/Form'
import { ElMessage } from 'element-plus'
import { computed, ref, watch } from 'vue'

// 导入新的Hook和组件
import { useIndexEnumLoader } from '@/views/Snow/Index/hooks/useIndexEnumLoader'
import { useIndexFormManager } from '@/views/Snow/Index/hooks/useIndexFormManager'
import { useIndexDataProcessor } from '@/views/Snow/Index/hooks/useIndexDataProcessor'
import type { IndexBase } from '@/api/snow/index/types'

const emit = defineEmits(['closeDialog', 'update:dialogVisible', 'dataChanged'])

// 使用新的Hook系统
const enumLoader = useIndexEnumLoader()
const formManager = useIndexFormManager()
const dataProcessor = useIndexDataProcessor()

// Props 定义
interface Props {
  dialogVisible: boolean
  curIndex?: IndexBase | null
}

const props = withDefaults(defineProps<Props>(), {
  dialogVisible: false,
  curIndex: null,
})

// 计算属性：判断是否为编辑模式
const isEditMode = computed(() => {
  // 当存在有效的当前指数（含 id）时视为编辑模式
  return Boolean(props.curIndex && props.curIndex.id)
})

// 对话框显示状态
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (value: boolean) => {
    emit('update:dialogVisible', value)
  },
})

// 监听对话框显示状态变化
watch(
  () => props.dialogVisible,
  async (newVal) => {
    if (newVal) {
      // 保证枚举先加载，避免 Select 无法匹配值（如 0）
      await enumLoader.loadEnums()
      // 对话框打开时的逻辑
      if (isEditMode.value && props.curIndex) {
        // 编辑模式：加载指数详情并回显
        const indexData = await dataProcessor.loadIndexDetail(props.curIndex.id)
        if (indexData) {
          await formManager.setFormData(indexData)
        }
      } else {
        // 新增模式：重置表单
        formManager.resetForm()
      }
    }
  }
)

// 加载指数数据
const loadIndexData = async (indexId: number) => {
  try {
    const indexData = await dataProcessor.loadIndexDetail(indexId)
    if (indexData) {
      formManager.setFormData(indexData)
    }
  } catch (error) {
    console.error('加载指数详情失败:', error)
    ElMessage.error('加载指数详情失败')
  }
}

// 确认提交
const confirmDialog = async () => {
  try {
    // 验证表单
    const isValid = await formManager.validateForm()
    if (!isValid) {
      ElMessage.warning('请检查表单数据')
      return
    }

    // 获取表单数据
    const formData = await formManager.getFormData()
    if (!formData) {
      ElMessage.error('获取表单数据失败')
      return
    }

    // 提交数据
    const result = await dataProcessor.submitFormData(formData, isEditMode.value)

    if (result) {
      ElMessage.success(isEditMode.value ? '更新成功' : '创建成功')
      emit('dataChanged')
      closeDialog()
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  }
}

// 关闭对话框
const closeDialog = () => {
  // 关闭时重置表单，清空缓存与动态字段
  formManager.resetForm()
  dialogShow.value = false
  emit('closeDialog')
}
</script>

<style scoped>
.index-edit-dialog {
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
}

.index-form-container {
  position: relative;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
