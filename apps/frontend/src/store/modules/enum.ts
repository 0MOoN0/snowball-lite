import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { store } from '../index'
import type { EnumOption, EnumState, EnumDataWrapper, EnumLoadOptions, EnumCacheConfig, EnumVersionResponse } from '@/api/common/types'
import {
  getEnumByKeyApi,
  getEnumVersionsApi,
  batchGetEnumsApi,
  getAvailableEnumsApi
} from '@/api/common/enum'

// 默认缓存配置
const DEFAULT_CACHE_CONFIG: EnumCacheConfig = {
  ttl: 30 * 60 * 1000, // 30分钟
  checkInterval: 5 * 60 * 1000 // 5分钟检查一次版本
}

export const useEnumStore = defineStore('enum', () => {
  // 响应式状态
  const enumData = ref<Record<string, EnumDataWrapper>>({})
  const availableEnums = ref<Record<string, string>>({})
  const globalVersion = ref<string | null>(null)
  const loading = ref(false)
  const lastGlobalCheck = ref(0)

  // 计算属性
  const getEnumByKey = computed(() => (key: string) => {
    return enumData.value[key]?.data || []
  })

  const getEnumLabelByValue = computed(() => (key: string, value: number | string) => {
    const enumOptions = enumData.value[key]?.data || []
    const option = enumOptions.find(item => {
      const itemVal = (item as any).value
      // 优先数值比较，其次字符串比较，兼容 '0' 与 0
      const bothNumeric = !isNaN(Number(itemVal)) && !isNaN(Number(value))
      if (bothNumeric) return Number(itemVal) === Number(value)
      return String(itemVal) === String(value)
    })
    return option?.label || ''
  })

  const getEnumValueByLabel = computed(() => (key: string, label: string) => {
    const enumOptions = enumData.value[key]?.data || []
    const option = enumOptions.find(item => item.label === label)
    return option?.value
  })

  const isLoaded = computed(() => (key: string) => {
    return !!enumData.value[key]?.data
  })

  const isExpired = computed(() => (key: string) => {
    const enumWrapper = enumData.value[key]
    if (!enumWrapper) return true

    const now = Date.now()
    const expiry = enumWrapper.cacheExpiry || (enumWrapper.lastUpdated + DEFAULT_CACHE_CONFIG.ttl)
    return now > expiry
  })

  const getEnumVersion = computed(() => (key: string) => {
    return enumData.value[key]?.version || ''
  })

  const shouldCheckGlobalVersion = computed(() => {
    const now = Date.now()
    return now - lastGlobalCheck.value > DEFAULT_CACHE_CONFIG.checkInterval
  })

  // 获取可用枚举列表
  const getAvailableEnums = computed(() => {
    return availableEnums.value
  })

  // 检查是否需要更新可用枚举列表（基于版本变化）
  const shouldUpdateAvailableEnums = computed(() => {
    // 如果没有可用枚举列表，需要获取
    if (!availableEnums.value || Object.keys(availableEnums.value).length === 0) return true
    // 如果应该检查全局版本，则需要更新
    const now = Date.now()
    if (now - lastGlobalCheck.value > DEFAULT_CACHE_CONFIG.checkInterval) return true
    // 其他情况不需要更新
    return false
  })

  // Actions
  const loadEnum = async (key: string, options: EnumLoadOptions = {}) => {
    const { forceRefresh = false, skipVersionCheck = false } = options

    // 检查缓存是否有效
    if (!forceRefresh && enumData.value[key] && !isExpired.value(key)) {
      return enumData.value[key].data
    }

    // 版本检查（如果不跳过且不强制刷新）
    if (!skipVersionCheck && enumData.value[key] && !forceRefresh) {
      const hasUpdate = await checkEnumUpdate(key)
      if (!hasUpdate) {
        return enumData.value[key].data
      }
    }

    loading.value = true
    try {
      const response = await getEnumByKeyApi(key)
      const enumWrapper: EnumDataWrapper = {
        data: response.data || [],
        version: response.version || '1.0.0',
        lastUpdated: Date.now(),
        cacheExpiry: Date.now() + DEFAULT_CACHE_CONFIG.ttl
      }

      enumData.value[key] = enumWrapper
      return enumWrapper.data
    } catch (error) {
      return []
    } finally {
      loading.value = false
    }
  }

  const checkEnumUpdate = async (key: string): Promise<boolean> => {
    const currentWrapper = enumData.value[key]
    if (!currentWrapper) return true

    try {
      const currentVersion = currentWrapper.version
      const versions = await getEnumVersionsApi()
      const latestVersion = versions[key]?.version || '1.0.0'

      const hasUpdate = currentWrapper.version !== latestVersion
      return hasUpdate
    } catch (error) {
      return false
    }
  }

  const updateGlobalVersion = async (): Promise<string> => {
    try {
      const response: EnumVersionResponse = await getEnumVersionsApi()

      // 解析API响应，获取data字段中的版本信息
      const versionData = response.data || {}

      // 使用global字段的值作为全局版本标识
      const globalVersionValue = versionData.global?.toString() || Date.now().toString()
      globalVersion.value = globalVersionValue
      lastGlobalCheck.value = Date.now()
      return globalVersionValue
    } catch (error) {
      // 确保返回字符串类型，如果globalVersion为null则返回默认值
      return globalVersion.value || '0'
    }
  }

  const refreshEnum = async (key: string): Promise<EnumOption[]> => {
    return loadEnum(key, { forceRefresh: true })
  }

  const refreshAllEnums = async (): Promise<void> => {
    const keys = Object.keys(enumData.value)
    await Promise.all(keys.map(key => refreshEnum(key)))
  }

  const clearEnumCache = (key?: string): void => {
    if (key) {
      delete enumData.value[key]
    } else {
      enumData.value = {}
    }
  }

  const checkAndUpdateExpiredEnums = async (): Promise<void> => {
    const expiredKeys = Object.keys(enumData.value).filter(key => isExpired.value(key))

    if (expiredKeys.length > 0) {
      // 如果过期的枚举数量大于1，使用批量加载
      if (expiredKeys.length > 1) {
        await batchLoadEnums(expiredKeys)
      } else {
        await loadEnum(expiredKeys[0])
      }
    }
  }

  const batchLoadEnums = async (keys: string[], options: EnumLoadOptions = {}): Promise<Record<string, EnumOption[]>> => {
    const { forceRefresh = false } = options

    // 过滤出需要加载的枚举
    const keysToLoad = forceRefresh
      ? keys
      : keys.filter(key => !enumData.value[key] || isExpired.value(key))

    if (keysToLoad.length === 0) {
      const result: Record<string, EnumOption[]> = {}
      keys.forEach(key => {
        result[key] = enumData.value[key]?.data || []
      })
      return result
    }

    loading.value = true

    try {
      const response = await batchGetEnumsApi(keysToLoad)

      const result: Record<string, EnumOption[]> = {}
      const now = Date.now()

      // 处理成功的结果
      response.data.results.forEach(item => {
        if (item.success) {
          const enumWrapper: EnumDataWrapper = {
            data: item.data,
            version: '1.0.0', // 批量接口暂时使用默认版本
            lastUpdated: now,
            cacheExpiry: now + DEFAULT_CACHE_CONFIG.ttl
          }
          enumData.value[item.enumKey] = enumWrapper
          result[item.enumKey] = item.data
        } else {
          result[item.enumKey] = []
        }
      })

      // 对于未在批量结果中的枚举，返回缓存数据或空数组
      keys.forEach(key => {
        if (!(key in result)) {
          result[key] = enumData.value[key]?.data || []
        }
      })

      return result
    } catch (error) {
      // 降级到单个加载
      const result: Record<string, EnumOption[]> = {}
      for (const key of keysToLoad) {
        try {
          result[key] = await loadEnum(key, { forceRefresh })
        } catch (err) {
          result[key] = []
        }
      }
      return result
    } finally {
      loading.value = false
    }
  }

  // 加载可用枚举列表（版本驱动）
  const loadAvailableEnums = async (forceRefresh = false): Promise<Record<string, string>> => {
    // 如果不强制刷新且版本一致，直接返回
    if (!forceRefresh && !shouldUpdateAvailableEnums.value) {
      return availableEnums.value
    }

    loading.value = true
    try {
      const response = await getAvailableEnumsApi()
      if (response.success && response.data) {
        availableEnums.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取可用枚举列表失败')
      }
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 基于可用枚举列表批量预加载枚举数据（版本驱动）
  const preloadEnumsFromAvailableList = async (options: EnumLoadOptions = {}): Promise<void> => {
    try {
      // 首先确保可用枚举列表是最新的
      const availableEnumsData = await loadAvailableEnums(options.forceRefresh)
      const enumKeys = Object.keys(availableEnumsData)

      if (enumKeys.length === 0) {
        return
      }

      // 过滤出需要加载的枚举（未加载或版本不一致）
      const enumsToLoad = enumKeys.filter(key => {
        if (options.forceRefresh) return true
        const cached = enumData.value[key]
        if (!cached) return true
        // 基于版本检查是否需要更新
        return cached.version !== globalVersion.value
      })

      if (enumsToLoad.length === 0) {
        return
      }

      // 批量加载枚举数据
      await batchLoadEnums(enumsToLoad, {
        ...options,
        skipVersionCheck: true // 预加载时跳过版本检查以提高性能
      })
    } catch (error) {
      throw error
    }
  }

  // 清除可用枚举列表缓存
  const clearAvailableEnumsCache = (): void => {
    availableEnums.value = {}
  }

  // 版本驱动的枚举管理：基于版本变化更新可用枚举列表和枚举数据
  const versionDrivenEnumManagement = async (options: EnumLoadOptions = {}): Promise<void> => {
    try {
      // 1. 检查并更新全局版本
      await updateGlobalVersion()

      // 2. 基于版本变化更新可用枚举列表
      await loadAvailableEnums(options.forceRefresh)

      // 3. 基于可用枚举列表和版本预加载数据
      await preloadEnumsFromAvailableList(options)
    } catch (error) {
      throw error
    }
  }

  return {
    // 状态
    enumData,
    availableEnums,
    globalVersion,
    loading,
    lastGlobalCheck,

    // 计算属性
    getEnumByKey,
    getEnumLabelByValue,
    getEnumValueByLabel,
    isLoaded,
    isExpired,
    getEnumVersion,
    shouldCheckGlobalVersion,
    getAvailableEnums,
    shouldUpdateAvailableEnums,

    // 方法
    loadEnum,
    checkEnumUpdate,
    updateGlobalVersion,
    refreshEnum,
    refreshAllEnums,
    clearEnumCache,
    checkAndUpdateExpiredEnums,
    batchLoadEnums,
    loadAvailableEnums,
    preloadEnumsFromAvailableList,
    clearAvailableEnumsCache,
    versionDrivenEnumManagement
  }
}, {
  persist: {
    key: 'enum-store',
    storage: localStorage,
    paths: ['enumData', 'availableEnums', 'globalVersion', 'lastGlobalCheck']
  }
})

export const useEnumStoreWithOut = () => {
  return useEnumStore(store)
}