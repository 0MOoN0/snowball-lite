<template>
  <ContentWrap title="搜索条件">
    <Search :schema="searchSchema" @search="searchIndex" expand />
  </ContentWrap>
  <ContentWrap title="指数列表展示" class="mt-5">
    <el-space>
      <el-button @click="editIndex" plain type="primary" icon="Plus">新增指数</el-button>
      <el-popconfirm title="是否删除选中数据？" @confirm="deleteSelections">
        <template #reference>
          <el-button plain type="danger" icon="Delete"> 删除选中数据 </el-button>
        </template>
      </el-popconfirm>
    </el-space>
    <Table
      :columns="indexColumns"
      :data="tableObject.tableList"
      :loading="tableObject.loading"
      :pagination="paginationObj"
      @update:current-page="(val) => (tableObject.currentPage = val)"
      @update:page-size="(val) => (tableObject.pageSize = val)"
      @register="register"
      :expand="true"
      class="mt-5"
    >
      <template #expand="{ row }">
        <IndexExpandRow :index-id="row.id" />
      </template>
      <template #indexType="data">
        <el-tag>
          {{ getIndexTypeName(data.row.indexType) }}
        </el-tag>
      </template>
      <template #investmentStrategy="data">
        <el-tag type="info" size="small">
          {{ getInvestmentStrategyLabel(data.row.investmentStrategy) }}
        </el-tag>
      </template>
      <template #indexCode="data">
        <el-link :href="'https://xueqiu.com/S/' + data.row.indexCode" target="_blank" type="primary" :underline="false">
          {{ data.row.indexCode }}
        </el-link>
      </template>
      <template #market="data">
        <el-tag>
          {{ getMarketName(data.row.market) }}
        </el-tag>
      </template>
      <template #indexStatus="data">
        <el-tag :type="getStatusType(data.row.indexStatus)">
          {{ getStatusName(data.row.indexStatus) }}
        </el-tag>
      </template>
      <template #currency="data">
        <el-tag>
          {{ getCurrencyName(data.row.currency) }}
        </el-tag>
      </template>
      <template #weightMethod="data">
        <el-tag>
          {{ getWeightMethodName(data.row.weightMethod) }}
        </el-tag>
      </template>
      <template #calculationMethod="data">
        <el-tag>
          {{ getCalculationMethodName(data.row.calculationMethod) }}
        </el-tag>
      </template>
      <template #actions="data">
        <ElButton type="primary" @click="editIndex(data.row)" text icon="Edit">
          {{ '编辑' }}
        </ElButton>
        <el-popconfirm
          title="确认删除该指数？该操作不可恢复！"
          confirm-button-text="删除"
          cancel-button-text="取消"
          confirm-button-type="danger"
          @confirm="deleteIndex(data.row)"
        >
          <template #reference>
            <ElButton type="danger" text icon="Delete">
              {{ '删除' }}
            </ElButton>
          </template>
        </el-popconfirm>
      </template>
    </Table>
  </ContentWrap>
  <IndexManagerEditDialog
    :dialogVisible="editDialogVisible"
    :dialog-title="editDialogTitle"
    @update:dialog-visible="changeEditDialogVisible"
    @closeDialog="handleCloseDialog"
    @dataChanged="handleDataChanged"
    :curIndex="curIndex"
  />
</template>

<script lang="ts" setup>
import * as indexApi from '@/api/snow/index/IndexApi'
import type { IndexBase } from '@/api/snow/index/types'
import ContentWrap from '@/components/ContentWrap/src/ContentWrap.vue'
import { Search } from '@/components/Search'
import Table from '@/components/Table/src/Table.vue'
import { useTable } from '@/hooks/web/useTable'
import { ElMessage } from 'element-plus'
import _ from 'lodash'
import { reactive, ref, watch, onMounted } from 'vue'
import IndexManagerEditDialog from './IndexManagerEditDialog.vue'
import IndexExpandRow from './components/IndexExpandRow.vue'
import { useEnum } from '@/hooks/web/useEnum'

const editDialogVisible = ref(false)
const editDialogTitle = ref('')
const curIndex = ref()

// 使用表格展开行显示详情，无需对话框状态

// 创建适配器函数来转换 API 响应格式
const getIndexListAdapter = async (params: any): Promise<IResponse<{ list: IndexBase[], total: number, pageNumber: number, pageSize: number }>> => {
  const response = await indexApi.getIndexList(params)
  return {
    ...response,
    data: {
      list: response.data.items,
      total: response.data.total,
      pageNumber: response.data.page,
      pageSize: response.data.size
    }
  }
}

// useTable
const { register, tableObject, methods } = useTable<IndexBase>({
  getListApi: getIndexListAdapter,
  response: {
    list: 'list',
    total: 'total',
  },
})

// 默认的请求参数
tableObject.params = {
  indexStatus: 1, // 默认查询启用状态的指数
}

const { getList, getSelections } = methods
// 获取表格数据
getList()

// 显示分页
const paginationObj = ref<Pagination>()
paginationObj.value = {
  total: tableObject.total,
}

// 给分页插件总条数赋值
watch(
  () => tableObject.total,
  (val: number) => {
    if (typeof paginationObj.value !== 'undefined') paginationObj.value.total = val
  }
)

// 使用枚举管理系统
const { enumData: indexTypeEnum, loadEnum: loadIndexTypeEnum, getLabel: getIndexTypeLabel } = useEnum('IndexTypeEnum')
const { enumData: investmentStrategyEnum, loadEnum: loadInvestmentStrategyEnum, getLabel: getInvestmentStrategyLabel } = useEnum('InvestmentStrategyEnum')
const { enumData: currencyEnum, loadEnum: loadCurrencyEnum, getLabel: getCurrencyLabel } = useEnum('CurrencyEnum')
const { enumData: marketEnum, loadEnum: loadMarketEnum, getLabel: getMarketLabel } = useEnum('MarketEnum')
const { enumData: statusEnum, loadEnum: loadStatusEnum, getLabel: getStatusLabel } = useEnum('IndexStatusEnum')
const { enumData: weightMethodEnum, loadEnum: loadWeightMethodEnum, getLabel: getWeightMethodLabel } = useEnum('WeightMethodEnum')
const { enumData: calculationMethodEnum, loadEnum: loadCalculationMethodEnum, getLabel: getCalculationMethodLabel } = useEnum('CalculationMethodEnum')

// 组件挂载时加载枚举数据
onMounted(async () => {
  try {
    await Promise.all([
      loadIndexTypeEnum(),
      loadInvestmentStrategyEnum(),
      loadCurrencyEnum(),
      loadMarketEnum(),
      loadStatusEnum(),
      loadWeightMethodEnum(),
      loadCalculationMethodEnum()
    ])
    
    // 更新搜索表单选项
    updateSearchFormOptions()
  } catch (error) {
    console.error('加载枚举数据失败:', error)
  }
})

// 获取指数类型描述
const getIndexTypeName = (indexType: number) => {
  return getIndexTypeLabel(indexType) || '未知'
}

// 获取货币名称
const getCurrencyName = (currencyType: number): string => {
  return getCurrencyLabel(currencyType) || '未知'
}

// 获取市场名称
const getMarketName = (market: number): string => {
  return getMarketLabel(market) || '未知'
}

// 获取状态名称
const getStatusName = (status: number): string => {
  return getStatusLabel(status) || '未知'
}

// 获取权重方法名称
const getWeightMethodName = (weightMethod: number): string => {
  return getWeightMethodLabel(weightMethod) || '未知'
}

// 获取计算方法名称
const getCalculationMethodName = (calculationMethod: number): string => {
  return getCalculationMethodLabel(calculationMethod) || '未知'
}

// 获取状态标签类型
const getStatusType = (status: number): 'success' | 'warning' | 'danger' | 'info' => {
  switch (status) {
    case 1:
      return 'success' // 启用
    case 0:
      return 'danger' // 停用
    default:
      return 'info'
  }
}

const editIndex = async (row) => {
  try {
    editDialogTitle.value = row ? '编辑指数' : '新增指数'
    editDialogVisible.value = true
    
    if (row && row.id) {
      // 编辑操作，直接使用传入的行数据
      curIndex.value = row
    } else {
      // 新增操作，清空当前指数数据
      curIndex.value = null
    }
  } catch (error) {
    console.error('编辑指数失败:', error)
    ElMessage({
      message: '操作失败，请重试',
      type: 'error'
    })
  }
}

// 展开行展示详情，无需在此处理

// 表格列描述
const indexColumns = reactive<TableColumn[]>([
  {
    field: 'index',
    label: '序号',
    type: 'index',
  },
  {
    field: 'indexName',
    label: '指数名称',
    width: 200,
  },
  {
    field: 'indexCode',
    label: '指数代码',
    width: 120,
  },
  {
    field: 'indexType',
    label: '指数类型',
    width: 120,
  },
  {
    field: 'investmentStrategy',
    label: '投资策略',
    width: 120,
  },
  {
    field: 'market',
    label: '市场',
    width: 100,
  },
  {
    field: 'currency',
    label: '货币',
    width: 100,
  },
  {
    field: 'basePoint',
    label: '基准点数',
    width: 100,
  },
  {
    field: 'weightMethod',
    label: '权重方法',
    width: 120,
  },
  {
    field: 'calculationMethod',
    label: '计算方法',
    width: 120,
  },
  {
    field: 'indexStatus',
    label: '状态',
    width: 100,
  },
  {
    field: 'publisher',
    label: '发布机构',
    width: 150,
  },
  {
    field: 'publishDate',
    label: '发布日期',
    width: 120,
  },
  {
    field: 'actions',
    label: '操作',
    width: '200px',
  },
])

const changeEditDialogVisible = (visible, hasDataChanged = false) => {
  editDialogVisible.value = visible
  // 只有在关闭对话框时才清空curIndex
  if (!visible) {
    curIndex.value = null
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

// 详情使用展开行，无需关闭逻辑

// 处理编辑/新增成功后的数据变更事件：刷新列表
const handleDataChanged = () => {
  try {
    getList()
  } catch (e) {
    console.warn('[IndexManager] 刷新列表失败', e)
  }
}

/**
 * 删除当前行数据
 * @param row 当前行
 */
const deleteIndex = async (row) => {
  if (!row || !row.id) return
  try {
    const resp = await indexApi.deleteIndexById(row.id)
    if (resp && resp.success && resp.data) {
      ElMessage({ message: resp.message || '删除成功', type: 'success' })
      await getList()
    } else {
      ElMessage({ message: resp?.message || '删除失败', type: 'error' })
    }
  } catch (e) {
    console.error('删除指数失败:', e)
    ElMessage({ message: '删除失败，请稍后重试', type: 'error' })
  }
}

// 根据选中列表批量删除指数数据
const deleteSelections = async () => {
  try {
    const selections = await getSelections()
    const ids = selections.map((i: any) => i.id).filter(Boolean)
    if (!ids.length) {
      ElMessage({ message: '请选择需要删除的指数', type: 'info' })
      return
    }
    // 后端未提供批量删除端点，这里按单条并发删除
    const results = await Promise.all(ids.map((id: number) => indexApi.deleteIndexById(id)))
    const successCount = results.filter(r => r && r.success && r.data).length
    const failCount = ids.length - successCount
    if (successCount) {
      ElMessage({ message: `删除成功 ${successCount} 条，失败 ${failCount} 条`, type: 'success' })
    } else {
      ElMessage({ message: '删除失败', type: 'error' })
    }
    await getList()
  } catch (e) {
    console.error('批量删除指数失败:', e)
    ElMessage({ message: '批量删除失败，请稍后重试', type: 'error' })
  }
}

// 搜索指数列表
const searchIndex = async (search) => {
  search = _.omitBy(search, (value) => {
    // 如果属性值是空或者null，就返回true，表示要移除该属性
    return _.isNil(value) || value === ''
  })
  tableObject.params = search
  await getList()
}

// 搜索表单Schema列表
const searchSchema = reactive<FormSchema[]>([
  {
    field: 'indexName',
    label: '指数名称',
    component: 'Input',
  },
  {
    field: 'indexType',
    label: '指数类型',
    component: 'Select',
    componentProps: {
      options: [
        {
          label: '全部',
          value: '',
        },
      ],
    },
  },
  {
    field: 'investmentStrategy',
    label: '投资策略',
    component: 'Select',
    componentProps: {
      options: [
        {
          label: '全部',
          value: '',
        },
      ],
    },
  },
  {
    field: 'market',
    label: '市场',
    component: 'Select',
    componentProps: {
      options: [
        {
          label: '全部',
          value: '',
        },
      ],
    },
  },
  {
    field: 'indexStatus',
    label: '状态',
    component: 'Select',
    componentProps: {
      options: [
        {
          label: '全部',
          value: '',
        },
      ],
    },
    value: 1,
  },
])

// 更新搜索表单选项
const updateSearchFormOptions = () => {
  // 更新指数类型选项
  const indexTypeField = searchSchema.find(item => item.field === 'indexType')
  if (indexTypeField && indexTypeEnum.value) {
    indexTypeField.componentProps = {
      options: [
        { label: '全部', value: '' },
        ...indexTypeEnum.value.map(item => ({
          label: item.label,
          value: item.value
        }))
      ]
    }
  }

  // 更新投资策略选项
  const investmentStrategyField = searchSchema.find(item => item.field === 'investmentStrategy')
  if (investmentStrategyField && investmentStrategyEnum.value) {
    investmentStrategyField.componentProps = {
      options: [
        { label: '全部', value: '' },
        ...investmentStrategyEnum.value.map(item => ({
          label: item.label,
          value: item.value
        }))
      ]
    }
  }

  // 更新市场选项
  const marketField = searchSchema.find(item => item.field === 'market')
  if (marketField && marketEnum.value) {
    marketField.componentProps = {
      options: [
        { label: '全部', value: '' },
        ...marketEnum.value.map(item => ({
          label: item.label,
          value: item.value
        }))
      ]
    }
  }

  // 更新状态选项
  const statusField = searchSchema.find(item => item.field === 'indexStatus')
  if (statusField && statusEnum.value) {
    statusField.componentProps = {
      options: [
        { label: '全部', value: '' },
        ...statusEnum.value.map(item => ({
          label: item.label,
          value: item.value
        }))
      ]
    }
  }
}
</script>

<style scoped>
</style>