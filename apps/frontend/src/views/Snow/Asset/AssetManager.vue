<template>
  <ContentWrap title="搜索条件">
    <Search :schema="searchSchema" @search="searchAsset" expand />
  </ContentWrap>
  <ContentWrap title="资产品种列表展示" class="mt-5">
    <el-space>
      <el-button @click="editAsset" plain type="primary" icon="Plus">新增资产</el-button>
      <el-popconfirm title="是否删除选中数据？" @confirm="deleteSelections">
        <template #reference>
          <el-button plain type="danger" icon="Delete"> 删除选中数据 </el-button>
        </template>
      </el-popconfirm>
    </el-space>
    <Table :columns="assetColumns" :data="tableObject.tableList" :loading="tableObject.loading"
      :pagination="paginationObj" @update:current-page="(val) => (tableObject.currentPage = val)"
      @update:page-size="(val) => (tableObject.pageSize = val)" @register="register" :expand="true" class="mt-5">
      <template #expand="{ row }">
        <AssetExpandRow :asset-id="row.id" />
      </template>
      <template #assetType="data">
        <el-tag>
          {{ getAssetTypeName(data.row.assetType) }}
        </el-tag>
      </template>
      <template #assetCode="data">
        <el-link :href="'https://xueqiu.com/S/' + data.row.assetCode" target="_blank" type="primary" :underline="false">
          {{ data.row.assetCode }}
        </el-link>
      </template>
      <template #market="data">
        <el-tag>
          {{ getMarketName(data.row.market) }}
        </el-tag>
      </template>
      <template #assetStatus="data">
        <el-tag :type="getAssetStatusType(data.row.assetStatus)">
          {{ getAssetStatusName(data.row.assetStatus) }}
        </el-tag>
      </template>
      <template #closePercent="data">
        <ElTag :type="getPercentTag(data.row.closePercent)"> {{ formatPercentage(data.row.closePercent) }} </ElTag>
      </template>

      <template #actions="data">
        <ElButton type="primary" @click="editAsset(data.row)" text icon="Edit">
          {{ '编辑' }}
        </ElButton>
        <ElButton type="danger" text icon="Delete" @click="deleteAsset(data.row)">
          {{ '删除' }}
        </ElButton>
      </template>
      <template #currency="data">
        <el-tag>
          {{ getCurrentName(data.row.currency) }}
        </el-tag>
      </template>
    </Table>
  </ContentWrap>
  <AssetManagerEditDialog :dialogVisible="editDialogVisible" :dialog-title="editDialogTitle"
    @update:dialog-visible="changeEditDialogVisible" @closeDialog="handleCloseDialog" :curAsset="curAsset" />
  <AssetManagerDeleteDialog :dialogVisible="deleteDialogVisible" :fullscreen="false" :dialog-title="deleteDialogTitle"
    :asset-id="deleteDialogParams.assetId" @update:dialog-visible="changeDeleteDialogVisible" />
</template>

<script lang="ts" setup>
import * as assetApi from '@/api/snow/asset/AssetApi'
import { TableData } from '@/api/table/types'
import ContentWrap from '@/components/ContentWrap/src/ContentWrap.vue'
import { Search } from '@/components/Search'
import Table from '@/components/Table/src/Table.vue'
import { useTable } from '@/hooks/web/useTable'
import { ElMessage, ElTag } from 'element-plus'
import _ from 'lodash'
import { reactive, ref, watch, h, onMounted } from 'vue'
import AssetManagerDeleteDialog from './AssetManagerDeleteDialog.vue'
import AssetManagerEditDialog from './AssetManagerEditDialog.vue'
import AssetExpandRow from './components/AssetExpandRow.vue'
import { formatPrice, formatPercentage } from '@/utils/gridDataFormatter'
import { useEnum } from '@/hooks/web/useEnum'

const editDialogVisible = ref(false)

const editDialogTitle = ref('')

const deleteDialogVisible = ref(false)

const deleteDialogTitle = ref('')

const deleteDialogParams = reactive({ assetId: 0 })

const curAsset = ref()

// useTable
const { register, tableObject, methods } = useTable<TableData>({
  getListApi: assetApi.getAssetList,
  response: {
    list: 'items',
    total: 'total',
  },
})

// 默认的请求参数是证券资产类型为基金
tableObject.params = {
  assetType: 1,
}

const { getList, getSelections } = methods
// 获取表格数据
getList()
// 显示分页
const paginationObj = ref<Pagination>()
paginationObj.value = {
  total: tableObject.total,
}
// 给分插件总条数赋值
watch(
  () => tableObject.total,
  (val: number) => {
    if (typeof paginationObj.value !== 'undefined') paginationObj.value.total = val
  }
)

// 使用枚举管理系统
const { enumData: assetTypeEnum, loadEnum: loadAssetTypeEnum, getLabel: getAssetTypeLabel } = useEnum('AssetTypeEnum')
const { loadEnum: loadCurrencyEnum, getLabel: getCurrencyLabel } = useEnum('CurrencyEnum')
const { loadEnum: loadMarketEnum, getLabel: getMarketLabel } = useEnum('MarketEnum')
const {
  loadEnum: loadAssetStatusEnum,
  getLabel: getAssetStatusLabel,
} = useEnum('AssetStatusEnum')

// 组件挂载时加载枚举数据
onMounted(async () => {
  try {
    await Promise.all([loadAssetTypeEnum(), loadCurrencyEnum(), loadMarketEnum(), loadAssetStatusEnum()])
  } catch (error) {
    console.error('加载枚举数据失败:', error)
  }
})

// 获取资产类型描述
const getAssetTypeName = (assetType: number) => {
  return getAssetTypeLabel(assetType) || '未知'
}

const getCurrentName = (currencyType: number): string => {
  return getCurrencyLabel(currencyType) || '未知'
}

// 获取市场名称
const getMarketName = (market: number): string => {
  return getMarketLabel(market) || '未知'
}

// 获取资产状态名称
const getAssetStatusName = (status: number): string => {
  return getAssetStatusLabel(status) || '未知'
}

// 获取资产状态标签类型
const getAssetStatusType = (status: number): 'success' | 'warning' | 'danger' | 'info' => {
  switch (status) {
    case 0:
      return 'success' // 正常
    case 1:
      return 'warning' // 停牌
    case 2:
      return 'danger' // 退市
    case 3:
      return 'info' // 暂停
    default:
      return 'info'
  }
}

const editAsset = async (row) => {
  try {
    editDialogTitle.value = '编辑资产元数据'

    // 先弹出对话框，提升用户体验
    editDialogVisible.value = true

    // 如果传入了row参数，说明是编辑操作，需要异步查询完整的资产详情
    if (row && row.id) {
      // 先清空当前数据，显示加载状态
      curAsset.value = null

      try {
        const assetDetailRes = await assetApi.getById(row.id)
        if (assetDetailRes && assetDetailRes.success) {
          curAsset.value = assetDetailRes.data
        } else {
          ElMessage({
            message: '获取资产详情失败',
            type: 'error'
          })
          // 获取失败时关闭对话框
          editDialogVisible.value = false
        }
      } catch (error) {
        console.error('获取资产详情失败:', error)
        ElMessage({
          message: '获取资产详情失败，请重试',
          type: 'error'
        })
        // 获取失败时关闭对话框
        editDialogVisible.value = false
      }
    } else {
      // 新增操作，清空当前资产数据
      curAsset.value = null
    }
  } catch (error) {
    console.error('编辑资产失败:', error)
    ElMessage({
      message: '操作失败，请重试',
      type: 'error'
    })
  }
}

// 收盘涨百分比tag样式
const getPercentTag = (percent: number) => {
  // 将万倍数据转换为实际百分比进行判断
  const actualPercent = percent / 10000
  if (actualPercent > 0) {
    return 'danger' // 上涨显示红色
  } else if (actualPercent < 0) {
    return 'success' // 下跌显示绿色
  }
  return 'info' // 平盘显示灰色
}

// 表格列描述
const assetColumns = reactive<TableColumn[]>([
  {
    field: 'index',
    label: '序号',
    type: 'index',
  },
  {
    field: 'assetName',
    label: '资产名称',
  },
  {
    field: 'assetCode',
    label: '资产代码',
  },

  {
    field: 'assetType',
    label: '资产类型',
  },
  {
    field: 'currency',
    label: '货币类型',
  },
  {
    field: 'market',
    label: '市场',
  },
  {
    field: 'assetStatus',
    label: '资产状态',
  },
  {
    field: 'close',
    label: '收盘价',
    width: 120,
    formatter: (row: any) => {
      return '¥' + formatPrice(row.close)
    },
  },
  {
    field: 'closePercent',
    label: '涨跌幅',
    width: 120,
    slots: {
      default: (data: any) => {
        console.log('涨跌幅原始数据:', data.row.closePercent)
        const formattedPercent = formatPercentage(data.row.closePercent)
        console.log('涨跌幅格式化后:', formattedPercent)
        return h(ElTag, { type: getPercentTag(data.row.closePercent) }, () => formattedPercent)
      },
    },
  },
  {
    field: 'date',
    label: '最新交易日',
  },
  {
    field: 'actions',
    label: '操作',
    width: '200px',
  },
])

const changeEditDialogVisible = (visible, hasDataChanged = false) => {
  editDialogVisible.value = visible
  // 只有在关闭对话框时才清空curAsset
  if (!visible) {
    curAsset.value = null
  }
  // 只有在数据发生变更时才重新加载列表
  if (hasDataChanged) {
    getList()
  }
}

// 专门处理closeDialog事件的方法
const handleCloseDialog = (hasDataChanged = false) => {
  // 关闭对话框
  changeEditDialogVisible(false, hasDataChanged)
}

/**
 * 删除当前行数据
 * @param row 当前行
 */
const deleteAsset = async (row) => {
  deleteDialogTitle.value = '删除证券数据确认对话框'
  deleteDialogVisible.value = true
  deleteDialogParams.assetId = row.id
}

// 根据选中列表批量删除资产数据
const deleteSelections = async () => {
  const selections = await getSelections()
  // 获取id列表
  const ids = selections.map((asset) => asset.id)
  const delRes = await assetApi.deleteByIds({ ids })
  if (delRes && delRes.data) {
    ElMessage({
      message: delRes.message,
      type: 'success',
    })
    // 刷新数据
    await getList()
    return
  }
}

// 搜索asset列表
const searchAsset = async (search) => {
  search = _.omitBy(search, (value) => {
    // 如果属性值是空或者null，就返回true，表示要移除该属性
    return _.isNil(value) || value === ''
  })
  tableObject.params = search
  await getList()
}

// 修改删除弹框可见
const changeDeleteDialogVisible = (visible) => {
  deleteDialogVisible.value = visible
  getList()
}

// 资产名称搜索选项
const remoteSearchAsset = _.debounce(async (query: string) => {
  if (query !== '') {
    const res = await assetApi.getAssetSelectList({
      assetName: query,
      pageSize: 999,
      page: 1,
    })
    if (res && res.data && res.data.items) {
      const assetNameSchema = searchSchema.find((item) => item.field === 'assetName')
      if (assetNameSchema && assetNameSchema.componentProps) {
        assetNameSchema.componentProps.options = res.data.items.map((item) => ({
          label: item.assetName,
          value: item.assetName,
        }))
      }
    }
  } else {
    const assetNameSchema = searchSchema.find((item) => item.field === 'assetName')
    if (assetNameSchema && assetNameSchema.componentProps) {
      assetNameSchema.componentProps.options = []
    }
  }
}, 300)

// 搜索表单Schema列表
const searchSchema = reactive<FormSchema[]>([
  {
    field: 'assetName',
    label: '证券资产名称',
    component: 'Select',
    componentProps: {
      filterable: true,
      remote: true,
      remoteShowSuffix: true,
      remoteMethod: (query: string) => {
        remoteSearchAsset(query)
      },
      options: [],
      placeholder: '请输入资产名称搜索',
    },
  },
  {
    field: 'assetType',
    label: '证券资产类型',
    component: 'Select',
    componentProps: {
      options: [],
    },
    value: 1,
  },
])

watch(
  () => assetTypeEnum.value,
  (data) => {
    if (data) {
      const assetTypeSchema = searchSchema.find((item) => item.field === 'assetType')
      if (assetTypeSchema && assetTypeSchema.componentProps) {
        assetTypeSchema.componentProps.options = [
          {
            label: '全部',
            value: '',
          },
          ...data,
        ]
      }
    }
  },
  {
    immediate: true,
  }
)
</script>

<style>
.red-percent {
  color: red;
  font-weight: bold;
}

.green-percent {
  color: green;
  font-weight: bold;
}

.gray-percent {
  color: #888;
  font-weight: bold;
}

.dark .el-table__expanded-cell {
  background-color: var(--el-bg-color) !important;
  border-color: var(--el-border-color) !important;
}

.dark .el-table__expanded-cell .asset-expand-row {
  background-color: var(--el-bg-color) !important;
}

.dark .el-descriptions--border .el-descriptions__table {
  background-color: var(--el-bg-color) !important;
}

.dark .el-descriptions--border .el-descriptions__cell {
  background-color: var(--el-bg-color) !important;
  border-color: var(--el-border-color) !important;
}

.dark .el-descriptions__title {
  color: var(--el-text-color-primary) !important;
}

.dark .el-descriptions__label {
  color: var(--el-text-color-secondary) !important;
}

.dark .el-descriptions__content {
  color: var(--el-text-color-primary) !important;
}
</style>
