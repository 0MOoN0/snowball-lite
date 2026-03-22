<template>
  <ContentWrap title="搜索条件">
    <Search :schema="allSchemas.searchSchema" :key="searchKey" @search="setSearchParams" @reset="setSearchParams" />
  </ContentWrap>

  <ContentWrap title="交易记录列表" class="mt-20px">
    <div class="mb-10px">
      <el-space>
        <el-button icon="Download" @click="downloadData" :loading="exportLoading" :disabled="exportLoading"
          >下载数据</el-button
        >

        <el-button icon="Plus" type="primary" @click="allRecord">新增数据</el-button>
        <el-button icon="Upload" type="warning" @click="importRecord">导入数据</el-button>
      </el-space>
    </div>

    <Table
      :columns="allSchemas.tableColumns"
      :pagination="paginationObj"
      :data="tableObject.tableList"
      :loading="tableObject.loading"
      v-model:pageSize="tableObject.pageSize"
      v-model:currentPage="tableObject.currentPage"
      align="center"
      header-align="center"
    >
      <template #actions="data">
        <el-button icon="Edit" link type="primary" @click="editRecord(data.row)"> 修改 </el-button>
        <el-popconfirm title="是否确定删除交易ID记录" @confirm="deleteRecord(data.row)">
          <template #reference>
            <el-button icon="Delete" link type="danger"> 删除 </el-button>
          </template>
        </el-popconfirm>
      </template>
    </Table>
  </ContentWrap>



  <RecordOperationDialog
    ref="recordOperationDialogRef"
    :form-schema="allSchemas.formSchema"
    @success="updateRecorded"
  />
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
import * as recordApi from '@/api/snow/Record/index'
import { GridRecord } from '@/api/snow/Record/types'
import Table from '@/components/Table/src/Table.vue'
import Search from '@/components/Search/src/Search.vue'
import { useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { useTable } from '@/hooks/web/useTable'



import RecordOperationDialog from './components/RecordOperationDialog.vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import _ from 'lodash-es'
import { ref, watch } from 'vue'
import { useRecordSchemas } from './data'



// 引用 RecordOperationDialog 组件实例
const recordOperationDialogRef = ref<InstanceType<typeof RecordOperationDialog>>()

// === 数据定义 ===

// 分页组件
const paginationObj = ref<Pagination>()

const { tableObject, methods } = useTable<GridRecord>({
  getListApi: (params) => {
    // 1. 处理 pageIndex 问题：useTable 会自动带上 pageIndex，但后端文档仅要求 page。为保持请求整洁，移除 pageIndex。
    // 用户反馈看到 pageIndex，可能是因为 useTable 默认行为。此处显式清理。
    if (params.pageIndex) {
      delete params.pageIndex
    }

    // 2. 处理时间范围查询：后端需要 startDate 和 endDate，而前端 Search 组件返回的是 transactionsDate 数组
    if (params.transactionsDate && Array.isArray(params.transactionsDate) && params.transactionsDate.length === 2) {
      params.startDate = params.transactionsDate[0]
      params.endDate = params.transactionsDate[1]
      delete params.transactionsDate
    }

    // 3. 处理空参数问题：后端无法处理空字符串等无效值（如 transactionsDirection='' 会报错 Not a valid integer）
    // 因此需要遍历参数，移除空字符串、null 或 undefined 的字段
    const cleanParams = _.pickBy(params, (value) => {
      return value !== '' && value !== null && value !== undefined
    })

    return recordApi.getRecordList(cleanParams as any) as unknown as Promise<IResponse<any>>
  },
  response: {
    list: 'items',
    total: 'total',
  },
})
const { getList, setSearchParams } = methods

const { crudSchemas } = useRecordSchemas()
let allSchemas = useCrudSchemas(crudSchemas).allSchemas
const searchKey = ref(0)

// === hook ===

// 监听交易总数变化，更新分页器
watch(
  () => tableObject.total,
  (total: number) => {
    if (paginationObj.value?.total) {
      _.set(paginationObj.value, 'total', total)
    }
  }
)

const exportLoading = ref(false)

const downloadData = async () => {
  exportLoading.value = true
  // 处理搜索参数，与getListApi逻辑保持一致
  // ... 其他参数处理逻辑如果 getListApi 中有特殊处理也应在这里复用，但目前 getListApi 是直接传递 cleanParams

  // 复用 getListApi 中的参数清理逻辑
  // 注意：tableObject.params 包含了当前的搜索条件
  // 我们需要构建一个包含所有必要参数的对象

  const currentParams: any = { ...tableObject.params }
  if (currentParams.page) delete currentParams.page
  if (currentParams.pageSize) delete currentParams.pageSize

  // 处理时间范围查询 (如果 tableObject.params 中直接存的是 transactionsDate 数组)
  if (
    currentParams.transactionsDate &&
    Array.isArray(currentParams.transactionsDate) &&
    currentParams.transactionsDate.length === 2
  ) {
    currentParams.startDate = currentParams.transactionsDate[0]
    currentParams.endDate = currentParams.transactionsDate[1]
    delete currentParams.transactionsDate
  }

  const cleanParams = _.pickBy(currentParams, (value) => {
    return value !== '' && value !== null && value !== undefined
  })

  try {
    // 1. 检查导出数量
    const checkRes = await recordApi.exportRecordCheck(cleanParams as any)
    if (checkRes.code === 20000) {
      const count = checkRes.data.count
      if (count === 0) {
        ElMessage.warning('当前条件下没有可导出的数据')
        return
      }

      // 2. 弹窗确认
      await ElMessageBox.confirm(`当前条件下共查询到 ${count} 条记录，是否确认导出？`, '导出确认', {
        confirmButtonText: '确认导出',
        cancelButtonText: '取消',
        type: 'info',
      })

      // 3. 执行导出
      const res = await recordApi.exportRecordList(cleanParams as any)
      const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = `交易记录_${new Date().getTime()}.xlsx`
      link.click()
      window.URL.revokeObjectURL(link.href)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('导出失败', error)
      // 如果是取消操作，不提示错误
      if (error?.message) {
        ElMessage.error(error.message || '导出失败')
      }
    }
  } finally {
    exportLoading.value = false
  }
}


const allRecord = () => {
  // 使用 open 方法打开弹窗
  recordOperationDialogRef.value?.open('add')
}



const { push } = useRouter()

const importRecord = () => {
  push('/analysis/record/import')
}

const editRecord = (row: GridRecord) => {
  // 使用 open 方法打开弹窗并传递 ID
  recordOperationDialogRef.value?.open('edit', row.recordId || row.id)
}

const deleteRecord = async (row: GridRecord) => {
  const res = await recordApi.deleteById(row.id)
  if (res && res.data) {
    ElMessage({
      message: res.message,
      type: 'success',
    })
  }
  await getList()
}

const updateRecorded = async () => {
  const { getList } = methods
  await getList()
}

const initRecordList = async () => {
  tableObject.pageSize = 30
  // await getList()
  paginationObj.value = { total: tableObject.total, defaultPageSize: 30 }
}


const { currentRoute } = useRouter()

// Auto-filter by query param (e.g. from Import)
const checkQueryParams = async () => {
    const assetName = currentRoute.value.query.assetName as string
    if (assetName) {
        // Set search params directly
        tableObject.params.assetName = assetName
        
        // Update UI by modifying the allSchemas and forcing re-render
        const schemaItem = allSchemas.searchSchema.find(item => item.field === 'assetName')
        if (schemaItem) {
             schemaItem.value = assetName
             if (schemaItem.componentProps) {
                  schemaItem.componentProps.options = [{ label: assetName, value: assetName }]
             }
             // Force re-render of Search component to pick up the new value
             searchKey.value += 1
        }
        
        // Initialize paging defaults
        tableObject.pageSize = 30
        paginationObj.value = { total: tableObject.total, defaultPageSize: 30 }

        await getList()
    } else {
        await initRecordList()
    }
}

// Ensure search triggers on mount or activation (if cached)
import { onActivated, onMounted } from 'vue'

onMounted(() => {
    checkQueryParams()
})

onActivated(() => {
    checkQueryParams()
})
</script>

<style scoped></style>
