import { computed } from 'vue'
import { useEnumStore } from '@/store/modules/enum'
import type { EnumOption, EnumLoadOptions, UseEnumReturn } from '@/api/common/types'

/**
 * 枚举数据管理 Hook
 * @param enumKey 枚举键名
 */
export function useEnum(enumKey: string): UseEnumReturn {
  const enumStore = useEnumStore()

  const enumData = computed(() => {
    const data = enumStore.getEnumByKey(enumKey)
    if (data && data.length > 0) {
    }
    return data
  })
  const isLoaded = computed(() => {
    const loaded = enumStore.isLoaded(enumKey)
    return loaded
  })
  const isExpired = computed(() => {
    const expired = enumStore.isExpired(enumKey)
    if (expired) {
    }
    return expired
  })
  const version = computed(() => enumStore.getEnumVersion(enumKey))

  const loadEnum = async (options?: EnumLoadOptions) => {
    return await enumStore.loadEnum(enumKey, options)
  }

  const refreshEnum = async () => {
    return await enumStore.refreshEnum(enumKey)
  }

  const getLabel = (value: number) => {
    return enumStore.getEnumLabelByValue(enumKey, value)
  }

  const getValue = (label: string) => {
    return enumStore.getEnumValueByLabel(enumKey, label)
  }

  return {
    enumData,
    isLoaded,
    isExpired,
    version,
    loadEnum,
    refreshEnum,
    getLabel,
    getValue
  }
}

/**
 * 获取枚举选项列表
 * @param enumKey 枚举键名
 * @param options 加载选项
 */
export async function getEnumOptions(enumKey: string, options?: EnumLoadOptions): Promise<EnumOption[]> {
  const enumStore = useEnumStore()
  console.log(`[UseEnum] 获取枚举选项: ${enumKey}`, options)
  return await enumStore.loadEnum(enumKey, options)
}

/**
 * 根据值获取标签
 * @param enumKey 枚举键名
 * @param value 枚举值
 */
export function getEnumLabel(enumKey: string, value: number): string {
  const enumStore = useEnumStore()
  const label = enumStore.getEnumLabelByValue(enumKey, value)
  return label
}

/**
 * 根据标签获取值
 * @param enumKey 枚举键名
 * @param label 枚举标签
 */
export function getEnumValue(enumKey: string, label: string): number | undefined {
  const enumStore = useEnumStore()
  const value = enumStore.getEnumValueByLabel(enumKey, label)
  return value
}

/**
 * 刷新指定枚举数据
 * @param enumKey 枚举键名
 */
export async function refreshEnum(enumKey: string): Promise<EnumOption[]> {
  const enumStore = useEnumStore()
  return await enumStore.refreshEnum(enumKey)
}

/**
 * 刷新所有枚举数据
 */
export async function refreshAllEnums(): Promise<void> {
  const enumStore = useEnumStore()
  return await enumStore.refreshAllEnums()
}

/**
 * 清除枚举缓存
 * @param enumKey 枚举键名，不传则清除所有缓存
 */
export function clearEnumCache(enumKey?: string): void {
  const enumStore = useEnumStore()
  enumStore.clearEnumCache(enumKey)
}

/**
 * 检查并更新过期的枚举数据
 */
export async function checkAndUpdateExpiredEnums(): Promise<void> {
  const enumStore = useEnumStore()
  return await enumStore.checkAndUpdateExpiredEnums()
}

/**
 * 更新全局枚举版本
 */
export async function updateGlobalEnumVersion(): Promise<string> {
  const enumStore = useEnumStore()
  return await enumStore.updateGlobalVersion()
}

/**
 * 批量获取枚举选项列表
 * @param enumKeys 枚举键名数组
 * @param options 加载选项
 */
export async function batchGetEnumOptions(enumKeys: string[], options?: EnumLoadOptions): Promise<Record<string, EnumOption[]>> {
  const enumStore = useEnumStore()
  return await enumStore.batchLoadEnums(enumKeys, options)
}

/**
 * 批量刷新枚举数据
 * @param enumKeys 枚举键名数组
 */
export async function batchRefreshEnums(enumKeys: string[]): Promise<Record<string, EnumOption[]>> {
  const enumStore = useEnumStore()
  return await enumStore.batchLoadEnums(enumKeys, { forceRefresh: true })
}