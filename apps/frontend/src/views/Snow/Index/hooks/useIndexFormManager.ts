import { ref, computed, watch, nextTick } from 'vue'
import { cloneDeep } from 'lodash-es'
import type { FormExpose } from '@/components/Form'
import { getFormSchema, getDefaultValues, getCacheableFields, getBaseFieldNames, getTypeFieldNames } from '@/views/Snow/Index/config/formSchema'
import { getFormRules } from '@/views/Snow/Index/config/formRules'
import { useIndexEnumLoader } from '@/views/Snow/Index/hooks/useIndexEnumLoader'
import type { IndexFormData } from '@/views/Snow/Index/types'

/**
 * 指数表单管理Hook
 * 整合表单状态管理、数据缓存、验证等逻辑
 */
export const useIndexFormManager = () => {
  // 表单引用
  const formRef = ref<FormExpose>()

  // 表单数据缓存，用于保存不同指数类型的表单数据
  const formDataCache = ref<Record<number, Recordable>>({})

  // 当前表单数据
  const formData = ref<Recordable>({})

  // 表单提交状态
  const submitting = ref(false)

  // 使用枚举加载器
  const enumLoader = useIndexEnumLoader()

  /**
   * 生成表单Schema
   */
  const indexFormSchema = computed(() => {
    const enumOptions = enumLoader.getAllEnums()
    return getFormSchema(formData.value.indexType ?? null, {
      ...enumOptions,
      onIndexTypeChange: handleIndexTypeChange
    })
  })

  /**
   * 判断是否为股票指数
   */
  const isStockIndex = (indexType: number): boolean => {
    // 股票指数的类型值为0
    return indexType === 0
  }

  /**
   * 处理指数类型变更
   */
  const handleIndexTypeChange = async (newIndexType: number) => {
    if (!formRef.value) {
      console.warn('⚠️ formRef.value 不存在')
      return
    }

    try {
      const uiModel = cloneDeep(formRef.value.formModel || {})
      const oldIndexType = formData.value.indexType
      if (oldIndexType === newIndexType) return

      if (oldIndexType !== undefined && oldIndexType !== null) {
        const cacheableFields = getCacheableFields()
        const cacheData: Recordable = {}
        cacheableFields.forEach((field) => {
          if (uiModel[field] !== undefined) {
            cacheData[field] = uiModel[field]
          }
        })
        formDataCache.value[oldIndexType] = cacheData
      }

      // 保留基础字段（排除 indexType 防止覆盖新类型）
      const preservedBaseData: Recordable = {}
      getBaseFieldNames().forEach((field) => {
        if (field !== 'indexType' && uiModel[field] !== undefined) {
          preservedBaseData[field] = uiModel[field]
        }
      })

      // 初始或设置数据时，保留当前类型的专属字段值，避免丢失
      const preservedTypeData: Recordable = {}
      getTypeFieldNames(newIndexType).forEach((field) => {
        if (uiModel[field] !== undefined) {
          preservedTypeData[field] = uiModel[field]
        }
      })

      let newFormData = getDefaultValues()
      newFormData.indexType = newIndexType
      const cachedData = formDataCache.value[newIndexType] || {}
      newFormData = { ...newFormData, ...cachedData, ...preservedBaseData, ...preservedTypeData, indexType: newIndexType }

      formData.value = newFormData
      await nextTick()
      await formRef.value.setValues(newFormData)
    } catch (error) {
      console.error('处理指数类型变更失败:', error)
    }
  }

  /**
   * 初始化表单数据
   */
  const initFormData = (indexData?: any) => {
    if (indexData) {
      // 编辑模式：使用传入的数据
      formData.value = cloneDeep(indexData)
    } else {
      // 新建模式：使用默认数据
      formData.value = getDefaultValues()
    }
  }

  /**
   * 重置表单
   */
  const resetForm = async () => {
    if (!formRef.value) return

    try {
      // 清空表单数据缓存
      formDataCache.value = {}

      // 重置为默认数据
      const defaultData = getDefaultValues()
      formData.value = defaultData

      // 重置表单
      await formRef.value.setValues(defaultData)

      console.log('表单已重置')
    } catch (error) {
      console.error('重置表单失败:', error)
    }
  }

  /**
   * 验证表单
   */
  const validateForm = async (): Promise<boolean> => {
    if (!formRef.value) return false

    try {
      const valid = await formRef.value.getElFormRef()?.validate()
      return !!valid
    } catch (error) {
      console.error('表单验证失败:', error)
      return false
    }
  }

  /**
   * 获取表单数据
   */
  const getFormData = async (): Promise<IndexFormData | null> => {
    if (!formRef.value) return null

    try {
      // 始终以 Form 内部的实时值为准
      const current = cloneDeep(formRef.value.formModel || {})
      return current as IndexFormData
    } catch (error) {
      console.error('获取表单数据失败:', error)
      return null
    }
  }

  /**
   * 设置表单数据
   */
  const setFormData = async (data: Recordable) => {
    if (!formRef.value) return

    try {
      formData.value = cloneDeep(data)
      await formRef.value.setValues(data)
    } catch (error) {
      console.error('设置表单数据失败:', error)
    }
  }

  /**
   * 监听指数类型变化
   */
  watch(
    () => formData.value.indexType,
    (newType, oldType) => {
      if (newType !== oldType && newType !== undefined && newType !== null) {
        nextTick(() => {
          handleIndexTypeChange(newType)
        })
      }
    },
    { immediate: false }
  )

  return {
    // 表单引用
    formRef,

    // 表单数据
    formData,
    formDataCache,

    // 表单Schema
    indexFormSchema,

    // 表单验证规则
    formRules: computed(() => getFormRules()),

    // 状态
    submitting,

    // 枚举相关
    ...enumLoader,

    // 方法
    isStockIndex,
    handleIndexTypeChange,
    initFormData,
    resetForm,
    validateForm,
    getFormData,
    setFormData,
  }
}