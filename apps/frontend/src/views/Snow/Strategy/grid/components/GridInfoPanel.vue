<template>
  <el-space direction="vertical" :fill="true" style="width: 100%" alignment="center">
    <Descriptions
      title="网格信息"
      :schema="gridInfoSchema"
      :data="{
        gridStatus: currentGridInfo?.gridInfo?.gridStatus,
        gridTypeStatus: currentGridInfo?.gridTypeInfo?.gridTypeStatus,
      }"
    >
      <template #gridStatus="scope">
        <ElTag>
          {{ scope.row.gridStatus === 0 ? '已启用' : '未启用' }}
        </ElTag>
      </template>
      <template #gridTypeStatus="scope">
        <ElTag>
          {{ getGridTypeStatus(scope.row.gridTypeStatus) }}
        </ElTag>
      </template>
    </Descriptions>
    <Descriptions title="资产信息" :schema="assetDataSchema" :data="currentAssetData" :column="3">
      <template #assetType="data">
        <el-tag>
          {{ getAssetTypeName(data.row.assetType) }}
        </el-tag>
      </template>
      <template #categoryName="data">
        <el-space>
          <ElTag v-for="categoryName in data.row.categoryName">
            {{ categoryName }}
          </ElTag>
        </el-space>
      </template>
      <template #currency="data">
        <el-tag>
          {{ getCurrentName(data.row.currency) }}
        </el-tag>
      </template>
    </Descriptions>
    <Descriptions title="网格数据概览" :data="gridAnalysisData" :schema="gridTypeAnalysisSchema" :column="4">
      <template #operation>
        <ElButton @click="$emit('show-grid-analysis-detail')">查看详情</ElButton>
      </template>
    </Descriptions>
    <Descriptions
      title="网格类型数据概览"
      :data="gridTypeAnalysisData.data"
      :loading="gridTypeAnalysisData.loading"
      :schema="gridTypeAnalysisSchema"
      :column="4"
    >
      <template #operation>
        <ElButton @click="$emit('show-grid-type-analysis-detail')" :disabled="!searchData.gridTypeId" icon="View"
          >查看详情
        </ElButton>
        <ElButton
          plain
          @click="$emit('update-grid-type-analysis-result')"
          :disabled="!searchData.gridTypeId"
          type="primary"
          icon="Refresh"
          >更新网格类型分析数据</ElButton
        >
      </template>
    </Descriptions>
  </el-space>
</template>

<script setup lang="ts">
import { Descriptions } from '@/components/Descriptions'
import { ElButton, ElSpace, ElTag } from 'element-plus'
import { PropType } from 'vue'
import { getAssetTypeName, getCurrentName, getGridTypeStatus } from '@/views/Snow/Strategy/grid/Grid.data'

defineProps({
  gridInfoSchema: {
    type: Array as PropType<DescriptionsSchema[]>,
    default: () => [],
  },
  currentGridInfo: {
    type: Object,
    default: () => ({}),
  },
  assetDataSchema: {
    type: Array as PropType<DescriptionsSchema[]>,
    default: () => [],
  },
  currentAssetData: {
    type: Object,
    default: () => ({}),
  },
  gridAnalysisData: {
    type: Object,
    default: () => ({}),
  },
  gridTypeAnalysisSchema: {
    type: Array as PropType<DescriptionsSchema[]>,
    default: () => [],
  },
  gridTypeAnalysisData: {
    type: Object,
    default: () => ({ data: {}, loading: false }),
  },
  searchData: {
    type: Object,
    default: () => ({}),
  },
})

defineEmits(['show-grid-analysis-detail', 'show-grid-type-analysis-detail', 'update-grid-type-analysis-result'])
</script>
