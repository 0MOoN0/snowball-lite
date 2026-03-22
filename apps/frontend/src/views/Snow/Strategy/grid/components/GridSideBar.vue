<template>
  <div>
    <ContentWrap title="网格搜索">
      <Form :schema="searchSchema" :is-col="false" @register="registerForm" />
    </ContentWrap>

    <ContentWrap class="mt-20px" title="网格操作">
      <div class="grid grid-cols-2 col-auto row-auto gap-y-2">
        <ElButton
          plain
          type="primary"
          @click="$emit('add-grid', '新增新增网格数据')"
          icon="Plus"
          style="margin-left: 12px"
        >
          新增网格
        </ElButton>
        <ElButton
          plain
          type="primary"
          @click="$emit('edit-grid', '编辑网格数据')"
          icon="Edit"
          :disabled="!searchData.gridId"
        >
          编辑网格
        </ElButton>
        <el-popconfirm title="是否删除该网格，该网格下的网格类型数据也会被删除" @confirm="$emit('delete-grid')">
          <template #reference>
            <ElButton plain type="danger" icon="Delete" :disabled="!searchData.gridId">删除网格</ElButton>
          </template>
        </el-popconfirm>
        <ElButton
          plain
          type="primary"
          @click="$emit('update-analysis')"
          icon="Refresh"
          :loading="gridAnalysisData.loading"
        >
          更新网格类型数据
        </ElButton>
        <ElButton plain type="primary" icon="Upload" @click="$emit('sync-grid')"> 同步网格数据 </ElButton>
        <ElButton plain type="primary" icon="Upload" @click="$emit('sync-record')"> 同步交易数据 </ElButton>
        <ElButton plain type="primary" icon="Download" @click="$emit('export-grid')"> 导出网格数据 </ElButton>
        <ElButton plain type="primary" icon="Download" @click="$emit('export-record')"> 导出网格交易记录 </ElButton>
      </div>
    </ContentWrap>

    <ContentWrap class="mt-20px" title="网格类型操作">
      <div class="grid grid-cols-2 col-auto row-auto gap-y-2">
        <ElButton
          plain
          type="primary"
          icon="Plus"
          @click="$emit('add-grid-type', '新增网格类型数据')"
          style="margin-left: 12px"
        >
          新增网格类型数据
        </ElButton>
        <ElButton plain type="primary" icon="Upload" @click="$emit('upload-grid-type')"> 上传网格类型数据 </ElButton>
        <ElButton
          plain
          type="primary"
          icon="Edit"
          @click="$emit('edit-grid-type', '编辑网格类型数据')"
          :disabled="!searchData.gridTypeId"
        >
          编辑网格类型数据
        </ElButton>
        <ElButton
          plain
          type="danger"
          icon="Delete"
          @click="$emit('delete-grid-type')"
          :disabled="!searchData.gridTypeId"
        >
          删除网格类型数据
        </ElButton>
      </div>
    </ContentWrap>
  </div>
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
import Form from '@/components/Form/src/Form.vue'
import { ElButton, ElPopconfirm } from 'element-plus'
import { PropType } from 'vue'

defineProps({
  searchSchema: {
    type: Array as PropType<FormSchema[]>,
    default: () => [],
  },
  searchData: {
    type: Object,
    default: () => ({}),
  },
  gridAnalysisData: {
    type: Object,
    default: () => ({ loading: false }),
  },
})

const emit = defineEmits([
  'register-form',
  'add-grid',
  'edit-grid',
  'delete-grid',
  'update-analysis',
  'sync-grid',
  'sync-record',
  'export-grid',
  'export-record',
  'add-grid-type',
  'upload-grid-type',
  'edit-grid-type',
  'delete-grid-type',
])

const registerForm = (param) => {
  emit('register-form', param)
}
</script>
