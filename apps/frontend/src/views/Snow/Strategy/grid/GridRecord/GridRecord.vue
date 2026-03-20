<template>
  <div class="mb-3">
    <el-space>
      <el-button icon="Upload" @click="uploadData">上传数据</el-button>
      <el-button icon="Download" @click="downloadData" :loading="exportLoading" :disabled="exportLoading"
        >下载数据</el-button
      >
      <el-button icon="Plus" type="primary" @click="allRecord">新增数据</el-button>
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
  <GridRecordUploadDialog
    title="上传交易记录"
    :dialog-visible="uploadDialogVisible"
    @close-dialog="closeUploadDialog"
    :grid-type-id="gridRecordProps.gridTypeId"
  />
  <!--  编辑交易记录-->
  <GridRecordEditDialog
    :dialog-title="gridRecordDialogInfo.dialogTitle"
    :grid-record-schema="gridRecordDialogInfo.formSchema"
    :dialog-visible="gridRecordDialogInfo.editDialogVisible"
    @close-dialog="closeEditDialog"
    @update:record="updateRecorded"
    :grid-record-id="gridRecordDialogInfo.editRecordId"
  />
</template>

<script setup lang="ts">
import * as recordApi from '@/api/snow/Record/index'
import { GridRecord } from '@/api/snow/Record/types'
import Table from '@/components/Table/src/Table.vue'
import { useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { useTable } from '@/hooks/web/useTable'
import GridRecordEditDialog from './components/GridRecordEditDialog.vue'
import GridRecordUploadDialog from './components/GridRecordUploadDialog.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { set, pickBy } from 'lodash-es'
import { reactive, ref, watch, onMounted } from 'vue'
import { useGridRecordSchemas } from './GridRecord.data'

interface GridRecordDialogInfo {
  editDialogVisible?: boolean
  formSchema?: Array<FormSchema>
  dialogTitle?: string
  editRecordId?: number | any
}

const uploadDialogVisible = ref(false)

const gridRecordDialogInfo = reactive<GridRecordDialogInfo>({})

// 分页组件
const paginationObj = ref<Pagination>()

const gridRecordProps = defineProps({
  gridId: {
    type: Number,
    default: null,
  },
  gridTypeId: {
    type: Number,
    default: null,
  },
  assetId: {
    type: Number,
    default: null,
  },
})

const { tableObject, methods } = useTable<GridRecord>({
  getListApi: recordApi.getRecordList as any,
  response: {
    list: 'items',
    total: 'total',
  },
})
const { getList } = methods

const { crudSchemas } = useGridRecordSchemas(gridRecordProps.gridTypeId || 0, gridRecordProps.assetId)
let allSchemas = useCrudSchemas(crudSchemas).allSchemas

const setFormSchemaValue = (field: string, value: number | null) => {
  const schema = allSchemas.formSchema.find((item) => item.field === field)
  if (schema) {
    schema.value = value
  }
}

watch(
  () => gridRecordProps.gridTypeId,
  async (newGridTypeId) => {
    setFormSchemaValue('gridTypeId', newGridTypeId)
    initGridRecord(newGridTypeId)
  },
  {
    immediate: true,
  }
)

watch(
  () => gridRecordProps.assetId,
  (newAssetId) => {
    setFormSchemaValue('assetId', newAssetId)
  },
  {
    immediate: true,
  }
)

onMounted(() => {
  initGridRecord(gridRecordProps.gridTypeId)
})

// 监听数据列表条数变化
watch(
  () => tableObject.total,
  (total: number) => {
    if (paginationObj.value?.total) {
      set(paginationObj.value, 'total', total)
    }
  }
)

const uploadData = () => {
  if (gridRecordProps.gridId == null || gridRecordProps.gridTypeId == null) {
    ElMessage({
      message: '请选择网格和网格类型',
      type: 'error',
    })
    return
  }
  uploadDialogVisible.value = true
}

const exportLoading = ref(false)

const downloadData = async () => {
  if (gridRecordProps.gridId == null || gridRecordProps.gridTypeId == null) {
    ElMessage({
      message: '请选择网格和网格类型',
      type: 'error',
    })
    return
  }
  exportLoading.value = true
  const currentParams = { ...tableObject.params }

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

  const cleanParams = pickBy(currentParams, (value) => {
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
  if (gridRecordProps.gridId == null || gridRecordProps.gridTypeId == null) {
    ElMessage({
      message: '请选择网格和网格类型',
      type: 'error',
    })
    return
  }
  if (gridRecordProps.assetId == null) {
    ElMessage({
      message: '当前网格未关联资产，无法新增交易记录',
      type: 'error',
    })
    return
  }
  gridRecordDialogInfo.editDialogVisible = true
  gridRecordDialogInfo.formSchema = allSchemas.formSchema
  gridRecordDialogInfo.dialogTitle = '新增网格交易记录'
  gridRecordDialogInfo.editRecordId = null
}

const editRecord = (row: any) => {
  gridRecordDialogInfo.editDialogVisible = true
  gridRecordDialogInfo.formSchema = allSchemas.formSchema
  gridRecordDialogInfo.dialogTitle = '编辑网格交易记录'
  gridRecordDialogInfo.editRecordId = row.recordId
}

const deleteRecord = async (row: any) => {
  console.log('tableObject before ==> ', tableObject.total)
  console.log('pagObject before ==> ', paginationObj.value)
  const res = await recordApi.deleteById(row.recordId)
  if (res && res.data) {
    ElMessage({
      message: res.message,
      type: 'success',
    })
  }
  await getList()
  console.log('tableObject ==> ', tableObject.total)
  console.log('pagObject before ==> ', paginationObj.value)
}

const closeUploadDialog = async () => {
  uploadDialogVisible.value = false
  const { getList } = methods
  await getList()
  console.log('close dialog')
}

const closeEditDialog = () => {
  gridRecordDialogInfo.editDialogVisible = false
  gridRecordDialogInfo.editRecordId = null
}
const updateRecorded = async () => {
  gridRecordDialogInfo.editDialogVisible = false
  gridRecordDialogInfo.editRecordId = null
  const { getList } = methods
  await getList()
}

const initGridRecord = async (gridTypeId) => {
  if (gridTypeId !== null && gridTypeId !== undefined && gridTypeId !== 0) {
    // 获取网格类型详情交易记录
    tableObject.params = {
      groupType: 1,
      groupId: gridTypeId,
    }
    if (tableObject.pageSize === 30) {
      await getList()
    } else {
      tableObject.pageSize = 30
    }
    paginationObj.value = { total: tableObject.total, defaultPageSize: 30 }
    setFormSchemaValue('gridTypeId', gridRecordProps.gridTypeId)
    setFormSchemaValue('assetId', gridRecordProps.assetId)
  } else {
    tableObject.loading = false
    tableObject.tableList = []
    tableObject.total = 0
  }
}

// initGridRecord(gridRecordProps.gridTypeId)
</script>

<style scoped></style>
