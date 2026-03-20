<template>
  <div class="index-form-status">
    <!-- 枚举加载状态 -->
    <div v-if="showEnumStatus" class="status-section">
      <div class="status-header">
        <Icon icon="ep:loading" v-if="enumLoader.enumLoading.value" class="loading-icon" />
        <Icon icon="ep:check" v-else-if="enumLoader.isEnumsLoaded()" class="success-icon" />
        <Icon icon="ep:warning" v-else class="warning-icon" />
        <span class="status-text">枚举数据状态</span>
      </div>
      <div class="status-details">
        <el-tag
          v-for="(status, key) in enumStatusList"
          :key="key"
          :type="getTagType(status)"
          size="small"
          class="status-tag"
        >
          {{ getEnumDisplayName(key) }}: {{ getStatusText(status) }}
        </el-tag>
      </div>
    </div>

    <!-- 表单验证状态 -->
    <div v-if="showFormStatus" class="status-section">
      <div class="status-header">
        <Icon icon="ep:check" v-if="isFormValid" class="success-icon" />
        <Icon icon="ep:warning" v-else class="warning-icon" />
        <span class="status-text">表单验证状态</span>
      </div>
      <div v-if="!isFormValid && validationErrors.length > 0" class="status-details">
        <div v-for="(error, index) in validationErrors" :key="index" class="error-item">
          <Icon icon="ep:warning-filled" class="error-icon" />
          <span>{{ error }}</span>
        </div>
      </div>
    </div>

    <!-- 提交状态 -->
    <div v-if="showSubmitStatus" class="status-section">
      <div class="status-header">
        <Icon icon="ep:loading" v-if="isSubmitting" class="loading-icon" />
        <Icon icon="ep:check" v-else-if="submitSuccess" class="success-icon" />
        <Icon icon="ep:close" v-else-if="submitError" class="error-icon" />
        <Icon icon="ep:info" v-else class="info-icon" />
        <span class="status-text">提交状态</span>
      </div>
      <div v-if="submitMessage" class="status-message">
        {{ submitMessage }}
      </div>
    </div>

    <!-- 数据缓存状态 -->
    <div v-if="showCacheStatus && Object.keys(cacheStatus).length > 0" class="status-section">
      <div class="status-header">
        <Icon icon="ep:folder" class="info-icon" />
        <span class="status-text">数据缓存状态</span>
      </div>
      <div class="status-details">
        <el-tag
          v-for="(hasCachedData, indexType) in cacheStatus"
          :key="indexType"
          :type="hasCachedData ? 'success' : 'info'"
          size="small"
          class="status-tag"
        >
          类型{{ indexType }}: {{ hasCachedData ? '有缓存' : '无缓存' }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@/components/Icon'
import type { useIndexEnumLoader } from '@/views/Snow/Index/hooks/useIndexEnumLoader'

interface Props {
  // 枚举加载器实例
  enumLoader: ReturnType<typeof useIndexEnumLoader>

  // 表单验证状态
  isFormValid?: boolean
  validationErrors?: string[]

  // 提交状态
  isSubmitting?: boolean
  submitSuccess?: boolean
  submitError?: boolean
  submitMessage?: string

  // 缓存状态
  cacheStatus?: Record<string, boolean>

  // 显示控制
  showEnumStatus?: boolean
  showFormStatus?: boolean
  showSubmitStatus?: boolean
  showCacheStatus?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isFormValid: true,
  validationErrors: () => [],
  isSubmitting: false,
  submitSuccess: false,
  submitError: false,
  submitMessage: '',
  cacheStatus: () => ({}),
  showEnumStatus: true,
  showFormStatus: true,
  showSubmitStatus: true,
  showCacheStatus: true,
})

// 枚举状态列表
const enumStatusList = computed(() => {
  return {
    indexType: props.enumLoader.indexTypeEnumHook.isLoaded.value,
    investmentStrategy: props.enumLoader.investmentStrategyEnumHook.isLoaded.value,
    currency: props.enumLoader.currencyEnumHook.isLoaded.value,
    market: props.enumLoader.marketEnumHook.isLoaded.value,
    indexStatus: props.enumLoader.indexStatusEnumHook.isLoaded.value,
    weightMethod: props.enumLoader.weightMethodEnumHook.isLoaded.value,
    calculationMethod: props.enumLoader.calculationMethodEnumHook.isLoaded.value,
  }
})

// 计算属性
const enumStatusText = computed(() => {
  if (props.enumLoader.enumLoading.value) return '正在加载枚举数据...'
  if (props.enumLoader.isEnumsLoaded()) return '枚举数据加载完成'
  return '枚举数据加载失败或未完成'
})

// 获取枚举显示名称
const getEnumDisplayName = (key: string): string => {
  const nameMap: Record<string, string> = {
    indexType: '指数类型',
    investmentStrategy: '投资策略',
    currency: '货币',
    market: '市场',
    indexStatus: '状态',
    weightMethod: '权重方法',
    calculationMethod: '计算方法',
  }
  return nameMap[key] || key
}

// 获取状态文本
const getStatusText = (isLoaded: boolean): string => {
  return isLoaded ? '已加载' : '未加载'
}

// 获取标签类型
const getTagType = (isLoaded: boolean): 'success' | 'warning' => {
  return isLoaded ? 'success' : 'warning'
}
</script>

<style lang="less" scoped>
.index-form-status {
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);

  .status-section {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }

    .status-header {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      font-weight: 500;
      color: var(--el-text-color-primary);

      .status-text {
        margin-left: 6px;
      }

      .loading-icon {
        color: var(--el-color-primary);
        animation: rotate 1s linear infinite;
      }

      .success-icon {
        color: var(--el-color-success);
      }

      .warning-icon {
        color: var(--el-color-warning);
      }

      .error-icon {
        color: var(--el-color-danger);
      }

      .info-icon {
        color: var(--el-color-info);
      }
    }

    .status-details {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;

      .status-tag {
        margin: 0;
      }
    }

    .status-message {
      padding: 8px 12px;
      background-color: var(--el-fill-color-light);
      border-radius: 4px;
      font-size: 12px;
      color: var(--el-text-color-regular);
    }

    .error-item {
      display: flex;
      align-items: center;
      padding: 4px 0;
      font-size: 12px;
      color: var(--el-color-danger);

      .error-icon {
        margin-right: 4px;
        font-size: 14px;
      }
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>