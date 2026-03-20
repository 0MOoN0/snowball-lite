<template>
  <el-dialog
    v-model="dialogVisible"
    title="批量关联分组"
    width="600px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="flex flex-col gap-4">
      <div v-if="!isConsistent" class="mb-2">
        <el-alert
          title="当前选中记录包含不同的关联状态，操作将覆盖原有设置"
          type="warning"
          show-icon
          :closable="false"
        />
      </div>
      <div
        class="flex justify-between items-center bg-blue-50 p-2 rounded text-sm text-blue-600"
      >
        <span>设置将应用到: {{ targetDesc }}</span>
        <el-button type="primary" link @click="addRelationRow">
          <el-icon class="mr-1"><CirclePlus /></el-icon>添加关联
        </el-button>
      </div>

      <el-table :data="relationList" border style="width: 100%" size="small">
        <el-table-column label="分组类型" width="120">
          <template #default="{ row }">
            <el-select
              v-model="row.groupType"
              @change="handleRelationTypeChange(row)"
            >
              <el-option
                v-for="item in groupTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="业务对象">
          <template #default="{ row }">
            <el-select
              v-if="row.groupType === 1"
              v-model="row.groupId"
              filterable
              remote
              :remote-method="(query) => remoteRelationMethod(query, row)"
              :loading="row.loading"
              placeholder="请输入名称搜索"
              @change="handleRelationValueChange(row)"
              style="width: 100%"
            >
              <el-option
                v-for="item in row.options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-input
              v-else
              v-model.number="row.groupId"
              placeholder="请输入ID"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeRelationRow($index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyBatchRelation">应用</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  ElDialog,
  ElButton,
  ElTable,
  ElTableColumn,
  ElSelect,
  ElOption,
  ElInput,
  ElIcon,
  ElAlert
} from 'element-plus'
import { CirclePlus, Delete } from '@element-plus/icons-vue'
import { useRelationOptions } from '../hooks/useRelationOptions'

const emit = defineEmits(['apply'])

const dialogVisible = ref(false)
const targetDesc = ref('')
const isConsistent = ref(true)

interface RelationRow {
  groupType: number
  groupId: number | undefined
  groupName?: string
  loading: boolean
  options: any[]
}

const relationList = ref<RelationRow[]>([])

const { groupTypeOptions, fetchRelationOptions } = useRelationOptions()

// Exposed method to open dialog
const open = (targets: any[], desc: string) => {
  targetDesc.value = desc
  relationList.value = []

  // Check Consistency
  let commonRefs: any[] | null = null
  let consistent = true

  if (targets.length > 0) {
    // Helper to serialize for comparison
    const sortRefs = (refs: any[]) =>
      [...(refs || [])].sort(
        (a, b) => a.groupType - b.groupType || a.groupId - b.groupId
      )
    const serialize = (refs: any[]) =>
      sortRefs(refs)
        .map((r) => `${r.groupType}-${r.groupId}`)
        .join('|')

    const firstSig = serialize(targets[0].tradeReferences || [])

    for (let i = 1; i < targets.length; i++) {
      if (serialize(targets[i].tradeReferences || []) !== firstSig) {
        consistent = false
        break
      }
    }

    if (consistent) {
      commonRefs = targets[0].tradeReferences
    }
  }

  isConsistent.value = consistent

  if (consistent && commonRefs && commonRefs.length > 0) {
    // Pre-fill existing associations
    commonRefs.forEach((ref) => {
      const newRow: RelationRow = {
        groupType: ref.groupType,
        groupId: ref.groupId,
        groupName: ref.groupName,
        loading: false,
        options: []
      }
      // Pre-inject option using existing name to ensure Label display
      if (ref.groupId && ref.groupName) {
        newRow.options.push({ label: ref.groupName, value: ref.groupId })
      }

      relationList.value.push(newRow)

      // Load options asynchronously to allow changing
      initRelationRowOptions(newRow).then(() => {
        // Ensure our pre-filled value is still present or matched
        if (
          newRow.groupId &&
          !newRow.options.find((o) => o.value === newRow.groupId)
        ) {
          if (newRow.groupName) {
            newRow.options.unshift({
              label: newRow.groupName,
              value: newRow.groupId
            })
          }
        }
      })
    })
  } else {
    // Default empty row
    addRelationRow()
  }

  dialogVisible.value = true
}

const addRelationRow = () => {
  const newRow = {
    groupType: 1,
    groupId: undefined,
    groupName: '',
    loading: false,
    options: []
  }
  relationList.value.push(newRow)
  // Initialize options for the new row
  initRelationRowOptions(newRow)
}

const removeRelationRow = (index: number) => {
  relationList.value.splice(index, 1)
}

const initRelationRowOptions = async (row: RelationRow) => {
  row.loading = true
  try {
    row.options = await fetchRelationOptions(row.groupType)
  } finally {
    row.loading = false
  }
}

const handleRelationTypeChange = (row: RelationRow) => {
  row.groupId = undefined
  row.groupName = ''
  row.options = []
  initRelationRowOptions(row)
}

const remoteRelationMethod = async (query: string, row: RelationRow) => {
  row.loading = true
  try {
    row.options = await fetchRelationOptions(row.groupType, query)
  } finally {
    row.loading = false
  }
}

const handleRelationValueChange = (row: RelationRow) => {
  // Find name
  const opt = row.options.find((o: any) => o.value === row.groupId)
  row.groupName = opt ? opt.label : ''
}

const applyBatchRelation = () => {
  // Validate
  const validRelations = relationList.value.filter(
    (r) => r.groupId !== undefined
  )

  // Construct the References List
  const newRefs = validRelations.map((r) => ({
    groupType: r.groupType,
    groupId: r.groupId!,
    groupName: r.groupName
  }))

  emit('apply', newRefs)
  dialogVisible.value = false
}

defineExpose({ open })
</script>
