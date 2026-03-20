<template>
  <ContentWrap title="搜索条件">
    <Search :schema="searchSchema" @search="searchAlias" expand />
  </ContentWrap>
  <ContentWrap title="资产别名列表展示" class="mt-5">
    <el-space>
      <el-button @click="editAlias" plain type="primary" icon="Plus">新增别名</el-button>
    </el-space>
    <Table
      :columns="aliasColumns"
      :data="tableObject.tableList"
      :loading="tableObject.loading"
      :pagination="paginationObj"
      @update:current-page="(val) => (tableObject.currentPage = val)"
      @update:page-size="(val) => (tableObject.pageSize = val)"
      @register="register"
      class="mt-5"
    >
      <template #isPrimary="data">
        <el-tag :type="data.row.isPrimary ? 'success' : 'info'">
          {{ data.row.isPrimary ? '主别名' : '普通' }}
        </el-tag>
      </template>
      <template #status="data">
        <el-tag :type="data.row.status === 1 ? 'success' : 'warning'">
          {{ data.row.status === 1 ? '启用' : '禁用' }}
        </el-tag>
      </template>
      <template #actions="data">
        <ElButton type="primary" @click="editAlias(data.row)" text icon="Edit">编辑</ElButton>
        <ElPopconfirm title="是否删除该别名？" @confirm="deleteAlias(data.row)">
          <template #reference>
            <ElButton type="danger" text icon="Delete">删除</ElButton>
          </template>
        </ElPopconfirm>
      </template>
    </Table>
  </ContentWrap>
  <AssetAliasManagerEditDialog
    :dialogVisible="editDialogVisible"
    :dialog-title="editDialogTitle"
    @update:dialog-visible="changeEditDialogVisible"
    @closeDialog="handleCloseDialog"
    :curAlias="curAlias"
  />
</template>

<script lang="ts" setup>
import ContentWrap from '@/components/ContentWrap/src/ContentWrap.vue'
import { Search } from '@/components/Search'
import Table from '@/components/Table/src/Table.vue'
import { useTable } from '@/hooks/web/useTable'
import { ElMessage } from 'element-plus'
import { reactive, ref, watch } from 'vue'
import _ from 'lodash'
import { TableData } from '@/api/table/types'
import * as aliasApi from '@/api/snow/asset/AssetAliasApi'
import AssetAliasManagerEditDialog from './AssetAliasManagerEditDialog.vue'

const editDialogVisible = ref(false)
const editDialogTitle = ref('')
const curAlias = ref<any>()

const { register, tableObject, methods } = useTable<TableData>({
  getListApi: aliasApi.getAliasList,
  response: {
    list: 'items',
    total: 'total',
  },
})

const { getList } = methods
getList()

const paginationObj = ref<Pagination>()
paginationObj.value = { total: tableObject.total }
watch(
  () => tableObject.total,
  (val: number) => {
    if (typeof paginationObj.value !== 'undefined') paginationObj.value.total = val
  }
)

const editAlias = async (row?) => {
  editDialogTitle.value = row?.id ? '编辑资产别名' : '新增资产别名'
  editDialogVisible.value = true
  if (row?.id) {
    curAlias.value = null
    try {
      const res = await aliasApi.getAliasById(row.id)
      if (res && res.success) {
        curAlias.value = res.data
      } else {
        ElMessage({ message: '获取别名详情失败', type: 'error' })
        editDialogVisible.value = false
      }
    } catch (e) {
      ElMessage({ message: '获取别名详情失败，请重试', type: 'error' })
      editDialogVisible.value = false
    }
  } else {
    curAlias.value = null
  }
}

const deleteAlias = async (row) => {
  try {
    const delRes = await aliasApi.deleteAliasById(row.id)
    if (delRes && delRes.success) {
      ElMessage({ message: delRes.message || '删除成功', type: 'success' })
      await getList()
    }
  } catch (e) {
    ElMessage({ message: '删除失败，请重试', type: 'error' })
  }
}

const changeEditDialogVisible = (visible, hasDataChanged = false) => {
  editDialogVisible.value = visible
  if (!visible) {
    curAlias.value = null
  }
  if (hasDataChanged) {
    getList()
  }
}

const handleCloseDialog = (hasDataChanged = false) => {
  changeEditDialogVisible(false, hasDataChanged)
}

const aliasColumns = reactive<TableColumn[]>([
  { field: 'index', label: '序号', type: 'index' },
  { field: 'providerCode', label: '提供商代码' },
  { field: 'providerSymbol', label: '提供商符号' },
  { field: 'providerName', label: '提供商名称' },
  { field: 'assetId', label: '资产ID' },
  { field: 'assetName', label: '资产名称' },
  { field: 'isPrimary', label: '是否主别名' },
  { field: 'status', label: '状态' },
  { field: 'createTime', label: '创建时间' },
  { field: 'updateTime', label: '更新时间' },
  { field: 'actions', label: '操作', width: '200px' }
])

const searchAlias = async (search) => {
  search = _.omitBy(search, (value) => _.isNil(value) || value === '')
  tableObject.params = search
  await getList()
}

const searchSchema = reactive<FormSchema[]>([
  { field: 'providerCode', label: '提供商代码', component: 'Input' },
  { field: 'providerSymbol', label: '提供商符号', component: 'Input' },
  {
    field: 'status',
    label: '状态',
    component: 'Select',
    componentProps: {
      options: [
        { label: '全部', value: '' },
        { label: '启用', value: 1 },
        { label: '禁用', value: 0 }
      ]
    }
  },
  {
    field: 'isPrimary',
    label: '主别名',
    component: 'Select',
    componentProps: {
      options: [
        { label: '全部', value: '' },
        { label: '是', value: 1 },
        { label: '否', value: 0 }
      ]
    }
  }
])
</script>

<style>
</style>