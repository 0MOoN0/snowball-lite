import * as gridApi from '@/api/snow/grid/index'
import { useEnum } from '@/hooks/web/useEnum'
import { ref } from 'vue'

export const useRelationOptions = () => {
  // 分组类型选项
  const { enumData: groupTypeOptions, loadEnum: loadGroupTypeEnum } = useEnum('TradeReferenceGroupTypeEnum')

  // 缓存网格类型选项
  const gridTypeOptionsCache = ref<{ label: string; value: number }[]>([])

  // 获取关联选项
  const fetchRelationOptions = async (groupType: number, query?: string) => {
    // 1 代表网格类型
    if (groupType === 1) {
      // 网格
      if (gridTypeOptionsCache.value.length === 0) {
        try {
          const res = await gridApi.getGridRelationList()
          if (res.data) {
            const options: { label: string; value: number }[] = []
            for (const grid of res.data) {
              if (grid.gridTypes && grid.gridTypes.length > 0) {
                grid.gridTypes.forEach((type: any) => {
                  options.push({
                    label: `${grid.gridName} - ${type.typeName}`,
                    value: type.id,
                  })
                })
              }
            }
            gridTypeOptionsCache.value = options
          }
        } catch (e) {
          console.error(e)
        }
      }

      if (query) {
        return gridTypeOptionsCache.value.filter((item) => item.label.toLowerCase().includes(query.toLowerCase()))
      }
      return gridTypeOptionsCache.value
    }
    return []
  }

  return {
    groupTypeOptions,
    fetchRelationOptions,
    loadGroupTypeEnum,
  }
}
