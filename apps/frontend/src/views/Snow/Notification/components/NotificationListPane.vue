<template>
  <el-skeleton :loading="tableObject.loading" animated>
    <template #template>
      <el-skeleton-item variant="h1" style="width: 40%; margin-bottom: 12px" />
      <el-skeleton-item v-for="i in 6" :key="i" variant="p" style="margin-bottom: 8px" />
    </template>
    <template #default>
      <el-space style="margin-bottom: 8px">
        <el-popconfirm title="是否批量标记为已读？" @confirm="batchReadSelected">
          <template #reference>
            <span>
              <el-tooltip :content="tipText" placement="top">
                <el-button type="primary" plain icon="Finished"> 批量标记已读 </el-button>
              </el-tooltip>
            </span>
          </template>
        </el-popconfirm>
      </el-space>
      <Table
        :columns="columns"
        :pagination="paginationObj"
        :data="tableObject.tableList"
        v-model:pageSize="tableObject.pageSize"
        v-model:currentPage="tableObject.currentPage"
        align="center"
        header-align="center"
        row-key="id"
        @register="register"
      >
        <template #actions="data">
          <el-button icon="View" link type="primary" @click="emit('view', data.row)"> 查看详情 </el-button>
        </template>
      </Table>
    </template>
  </el-skeleton>
</template>
<script setup lang="ts">
import { Table } from '@/components/Table'
import { useTable } from '@/hooks/web/useTable'
import * as notificationApi from '@/api/snow/Notification/index'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, watch, onMounted, computed } from 'vue'
import { TableData } from '@/api/table/types'

const props = defineProps<{ columns: TableColumn[]; businessType?: number; activated?: boolean }>()
const emit = defineEmits(['view', 'updated'])

const { register, elTableRef, tableObject, methods } = useTable<TableData>({
  getListApi: notificationApi.getNotificationList,
  response: { list: 'items', total: 'total' },
})
const { getList, getSelections, setSearchParams } = methods

const paginationObj = ref<Pagination>({ total: tableObject.total, defaultPageSize: 20 })
watch(
  () => tableObject.total,
  (total: number) => {
    if (paginationObj.value?.total) paginationObj.value.total = total
  }
)

onMounted(() => {
  if (typeof props.businessType === 'number') {
    setSearchParams({ businessType: props.businessType })
    getList()
  } else {
    getList()
  }
})

watch(
  () => props.businessType,
  (bt) => {
    if (typeof bt === 'number') {
      setSearchParams({ businessType: bt })
      getList()
    }
  }
)

watch(
  () => props.activated,
  (val) => {
    if (val) getList()
  }
)

const batchReadSelected = async () => {
  try {
    const selections = await getSelections()
    const ids = selections.map((v: any) => v?.id).filter((v: any) => typeof v === 'number')

    let payload: any
    if (ids.length > 0) {
      payload = { ids }
    } else if (typeof props.businessType === 'number') {
      await ElMessageBox.confirm('将该业务类型的所有未读通知标记为已读，是否确认？', '批量标记已读', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      })
      payload = { businessType: props.businessType }
    } else {
      ElMessage({ type: 'warning', message: '请勾选通知后再进行批量标记已读' })
      return
    }

    const res = await notificationApi.batchReadNotifications(payload)
    if (res && res.success) {
      const updated = (res.data && (res.data.updated ?? res.data)) as number | undefined
      ElMessage({ message: updated ? `批量更新成功：标记已读 ${updated} 条` : '批量更新成功', type: 'success' })
      await getList()
      emit('updated')
      try {
        elTableRef?.value?.clearSelection?.()
      } catch {}
    } else {
      ElMessage({ type: 'error', message: (res && (res.message as string)) || '批量更新失败，请重试' })
    }
  } catch (e) {
    // 用户取消确认或请求失败
  }
}
const tipText = computed(() =>
  typeof props.businessType === 'number' ? '未选择时将按该类型全部未读标记已读' : '请先勾选通知再批量标记已读'
)
</script>
