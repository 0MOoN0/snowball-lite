
<template>
  <ContentDetailWrap :title="'导入交易记录'" @back="goBack">
    <div v-loading="loading" class="flex flex-col gap-4">

      <!-- 上传区域 -->
      <div v-if="!previewData.length">
        <div class="mb-4 flex items-center">
          <span class="text-sm text-[var(--el-text-color-regular)] mr-2">数据来源:</span>



          <el-select v-model="providerCode" placeholder="请选择数据来源" style="width: 200px" clearable>
              <el-option
                  v-for="item in providerOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
          </el-select>
        </div>

        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          :show-file-list="false"
          accept=".xlsx, .xls, .csv"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>

          <template #tip>
            <div class="el-upload__tip text-[var(--el-text-color-secondary)]">
              支持 .xlsx, .xls, .csv 格式文件
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 预览列表 -->
      <div v-else class="flex flex-col gap-2">
        <div class="flex justify-between items-center bg-[var(--el-fill-color-light)] p-2 rounded">
            <h3 class="text-lg font-bold m-0 text-[var(--el-text-color-primary)]">解析结果预览</h3>

            <div class="flex gap-2">

                <el-button @click="toggleExpandAll">
                  {{ isExpanded ? '全部收起' : '全部展开' }}
                </el-button>
                
                <el-button @click="openBatchRelationDialog">批量关联</el-button>
                
                <ImportBatchRelationDialog 
                    ref="batchRelationDialogRef" 
                    @apply="handleBatchApply" 
                />

                <el-button type="warning" @click="reUpload">重新上传</el-button>
                <el-button type="primary" @click="handleConfirmClick" :loading="loading" :disabled="previewData.length === 0">
                    确认导入
                </el-button>
            </div>
        </div>
        
        <!-- Filter Bar -->

        <div class="bg-[var(--el-fill-color-light)] p-2 rounded flex items-center overflow-x-auto">
            <el-radio-group v-model="currentAssetFilter">
                <el-radio-button v-for="group in assetGroups" :key="group.code" :label="group.code">
                   {{ group.name === 'ALL' ? '全部' : (group.code === group.name ? group.code : `${group.code} ${group.name}`) }}
                   <span v-if="group.count > 0">({{ group.count }})</span>
                   <span v-if="group.hasError" class="ml-1 text-red-500">●</span>
                </el-radio-button>
            </el-radio-group>
        </div>



        <Table
          ref="tableRef"
          :columns="tableColumns"
          :data="filteredData"
          align="center"
          header-align="center"
          height="calc(100vh - 280px)"
          :expand="true"
          :row-class-name="tableRowClassName"
        >


          <template #expand="{ row }">
            <div class="p-4 bg-[var(--el-fill-color-light)]">
              <!-- Message Alert -->
              <div v-if="row.message" class="mb-4">
                 <el-alert
                    :title="row.status === 'valid' ? '校验通过' : (row.status === 'error' ? '校验失败' : '警告')"
                    :type="row.status === 'valid' ? 'success' : (row.status === 'error' ? 'error' : 'warning')"
                    :description="row.message"
                    show-icon
                    :closable="false"
                 />
              </div>

              <h4 class="mb-2 mt-0 font-bold text-[var(--el-text-color-primary)]">原始数据</h4>
              <ElDescriptions v-if="row._rawData" border :column="3" size="small">
                <ElDescriptionsItem v-for="(value, key) in row._rawData" :key="key" :label="String(key)">
                  {{ value }}
                </ElDescriptionsItem>
              </ElDescriptions>
              <div v-else class="text-gray-400">无原始数据</div>
            </div>
          </template>
        </Table>

        <!-- Confirm Import Dialog -->
        <el-dialog
           v-model="confirmDialog.visible"
           title="确认导入"
           width="500px"
           append-to-body
        >
           <div class="flex flex-col gap-4">

               <el-alert 
                   :title="`即将导入 ${confirmDialog.validCount} 条记录`" 
                   :description="confirmDialog.scopeDesc"
                   type="info" 
                   show-icon
                   :closable="false"
               />
               
               <el-form label-position="top">
                   <el-form-item label="导入模式">
                       <el-radio-group v-model="confirmDialog.importForm.importMode" class="flex flex-col items-start w-full">
                           <el-radio 
                               v-for="item in importModeOptions" 
                               :key="item.value" 
                               :label="item.value" 
                               class="!h-auto !mr-0 mb-3 w-full" 
                               border
                           >
                               <div class="flex flex-col items-start py-1">
                                   <span class="font-bold">{{ formatModeLabel(item) }}</span>
                                   <span class="text-gray-400 text-xs mt-1">{{ getModeHint(item) }}</span>
                               </div>
                           </el-radio>
                       </el-radio-group>
                   </el-form-item>
                   
                   <el-form-item label="替换时间范围" v-if="confirmDialog.importForm.importMode === 3">
                       <el-date-picker
                          v-model="confirmDialog.importForm.range"
                          type="datetimerange"
                          range-separator="至"
                          start-placeholder="开始时间"
                          end-placeholder="结束时间"
                          value-format="YYYY-MM-DD HH:mm:ss"
                          style="width: 100%"
                       />
                   </el-form-item>
               </el-form>
           </div>
           <template #footer>
                <span class="dialog-footer">
                    <el-button @click="confirmDialog.visible = false">取消</el-button>
                    <el-button type="primary" @click="executeImport" :loading="loading">确认执行</el-button>
                </span>
           </template>
        </el-dialog>

      </div>
    
    </div>
  </ContentDetailWrap>
</template>

<script setup lang="ts">

import { ref, h, computed, onMounted, unref } from 'vue'
import ContentDetailWrap from '@/components/ContentDetailWrap/src/ContentDetailWrap.vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElUpload, ElDescriptions, ElDescriptionsItem, ElTag, ElAlert, ElSelect, ElOption, ElRadioGroup, ElRadioButton, ElDialog, ElButton, ElRadio, ElDatePicker, ElForm, ElFormItem } from 'element-plus'
import * as recordApi from '@/api/snow/Record/index'
import Table from '@/components/Table/src/Table.vue'
import { useRouter } from 'vue-router'
import { useRecordSchemas } from './data'
import { useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { useRelationOptions } from './hooks/useRelationOptions'
import { useEnum } from '@/hooks/web/useEnum'

import ImportBatchRelationDialog from './components/ImportBatchRelationDialog.vue'

const { crudSchemas } = useRecordSchemas()
const { allSchemas } = useCrudSchemas(crudSchemas)
const tableColumns = ref([...allSchemas.tableColumns])
const { groupTypeOptions: _ignore, loadGroupTypeEnum } = useRelationOptions()


// Provider Code Enum
const { enumData: providerOptions, loadEnum: loadProviderEnum } = useEnum('ProviderCodeEnum')
// Import Mode Enum
const { enumData: importModeOptions, loadEnum: loadImportModeEnum } = useEnum('RecordImportModeEnum')

// Load Enums
onMounted(() => {
    loadGroupTypeEnum()
    loadProviderEnum()
    loadImportModeEnum()
})

const formatModeLabel = (item: any) => {
    let label = item.label || ''
    if (item.value === 0) {
        label += ' (默认)'
    }
    return label
}

const getModeHint = (item: any) => {
    const label = item.label || ''
    if (label.includes('增量')) {
        return '仅添加新记录，不影响旧数据'
    } else if (label.includes('全量')) {
        return '清空该资产的所有历史记录'
    } else if (label.includes('部分')) {
        return '覆盖所导入时间段内的旧数据'
    } else if (label.includes('范围')) {
        return '覆盖指定时间范围内的旧数据'
    }
    return ''
}


// Inject 'message' and 'matchSource' columns
// 1. Match Source
tableColumns.value.splice(tableColumns.value.length - 1, 0, {
  field: 'matchSource',
  label: '匹配来源',
  width: 120,
  formatter: (row: any) => {
    const map: Record<string, string> = {
      'provider_symbol': '代码匹配',
      'global_symbol': '全局代码匹配',
      'asset_name': '名称匹配',
      'similarity': '相似度匹配'
    }
    return map[row.matchSource] || row.matchSource || '-'
  }
})


// 2. Verification Result (Status/Message)
tableColumns.value.splice(1, 0, {
  field: 'status',
  label: '校验结果',
  width: 150,
  formatter: (row: recordApi.ImportPreviewItem) => {
    const type = row.status === 'valid' ? 'success' : (row.status === 'error' ? 'danger' : 'warning')
    const label = row.status === 'valid' ? '通过' : (row.status === 'error' ? '失败' : '警告')

    return h('div', { class: 'flex flex-col items-start gap-1' }, [
        h(ElTag, { type }, () => label),
        row.message ? h('span', { class: 'text-xs truncate w-full', title: row.message }, row.message) : null
    ])
  }
})

// 3. Association
tableColumns.value.splice(2, 0, {
  field: 'groupName',
  label: '关联分组',
  width: 250,
  formatter: (row: recordApi.ImportPreviewItem) => {
      if (row.tradeReferences && row.tradeReferences.length > 0) {
          return row.tradeReferences.map(r => r.groupName || '未知').join('; ')
      }
      return '-'
  }
})

const router = useRouter()

const loading = ref(false)
const providerCode = ref('')
const previewData = ref<recordApi.ImportPreviewItem[]>([])

const currentAssetFilter = ref('ALL')

const assetGroups = computed(() => {
    const groups: Record<string, { code: string, name: string, count: number, hasError: boolean }> = {}
    
    previewData.value.forEach(item => {
        // Try to find security code in rawData
        let code = '未知'
        // Using _rawData mapped in handleFileChange or fallback to checking parsed items?
        // Note: item.rawData is the right place as per types.ts update. 
        // But in handleFileChange we assign `_rawData: item.rawData`.
        // Let's use item.rawData directly since type defines it.
        const rData = item.rawData || item._rawData
        if (rData) {
             // Common headers for Chinese securities
             code = rData['证券代码'] || rData['代码'] || rData['Symbol'] || rData['Code'] || '未知'
        }
        
        // Use parsed name if available, else fallback to code or default
        let name = item.assetName || code

        if (!groups[code]) {
            groups[code] = { code, name, count: 0, hasError: false }
        }
        groups[code].count++
        if (item.status === 'error') {
            groups[code].hasError = true
        }
        
        // If name was unknown but now we have it (e.g. from valid row), update it
        // Only update if current name is the code (fallback) and we found a real name
        if (groups[code].name === code && item.assetName) {
            groups[code].name = item.assetName
        }
    })
    
    return [
        { code: 'ALL', name: 'ALL', count: previewData.value.length, hasError: previewData.value.some(i => i.status === 'error') },
        ...Object.values(groups)
    ]
})

const filteredData = computed(() => {
    if (currentAssetFilter.value === 'ALL') {
        return previewData.value
    }
    // Filter by the same code logic
    return previewData.value.filter(item => {
        let code = '未知'
        const rData = item.rawData || item._rawData
        if (rData) {
             code = rData['证券代码'] || rData['代码'] || rData['Symbol'] || rData['Code'] || '未知'
        }
        return code === currentAssetFilter.value
    })
})

const goBack = () => {
    router.push('/analysis/record')
}

// Expand All / Collapse All
const tableRef = ref()
const isExpanded = ref(false)
const toggleExpandAll = () => {
  isExpanded.value = !isExpanded.value
  const elTable = tableRef.value?.elTableRef
  if (elTable) {
    // previewData or filteredData? If we only see filtered, expanding hidden ones is fine but maybe confusing. 
    // Usually expanding filtered view is better. 
    // But toggleAll usually implies visible rows.
    filteredData.value.forEach(row => {
      elTable.toggleRowExpansion(row, isExpanded.value)
    })
  }
}

// Row style for error/warning
const tableRowClassName = ({ row }: { row: recordApi.ImportPreviewItem }) => {
  if (row.status === 'error') {
    return 'error-row'
  }
  if (row.status === 'warning') {
    return 'warning-row'
  }
  return ''
}



// Access selections from Table component safely
const selectedRows = computed(() => {
    return unref(tableRef)?.selections || []
})

// Batch Relation State (Dialog Mode)
const batchRelationDialogRef = ref<InstanceType<typeof ImportBatchRelationDialog>>()

const openBatchRelationDialog = () => {
    // Determine Target
    const currentSelection = unref(selectedRows)
    const targets = currentSelection.length > 0 ? currentSelection : filteredData.value
    
    // Description
    const desc = currentSelection.length > 0 ? `选中记录 (${currentSelection.length}条)` : `所有记录 (${filteredData.value.length}条)`
    
    batchRelationDialogRef.value?.open(targets, desc)
}

const handleBatchApply = (newRefs: any[]) => {
    const groupNamesStr = newRefs.map(r => r.groupName).join('; ')

    // Determine Target (Re-evaluate)
    const currentSelection = unref(selectedRows)
    const hasSelection = currentSelection.length > 0
    const targetItems = hasSelection ? currentSelection : filteredData.value

    targetItems.forEach(item => {
        // Deep copy
        item.tradeReferences = newRefs.map(r => ({ ...r }))
    })
    
    ElMessage.success(`已关联 ${targetItems.length} 条记录到: ${groupNamesStr || '无关联'}`)
}


const handleFileChange = async (uploadFile: any) => {
  if (!uploadFile.raw) return
  
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.raw)
    if (providerCode.value) {
        formData.append('providerCode', providerCode.value)
    }
    
    const res = await recordApi.importRecordPreview(formData)
    if (res.data) {
       // API returns List<ImportPreviewItem>
       const items = Array.isArray(res.data) ? res.data : ((res.data as any).items || [])
       
       previewData.value = items.map((item: recordApi.ImportPreviewItem) => {
           const data = item.parsedData || {}
           return {
               ...item, // keep status/message
               
               transactionsDate: data.transactionsDate,
               transactionsPrice: data.transactionsPrice, 
               transactionsShare: data.transactionsShare,
               transactionsAmount: data.transactionsAmount,
               transactionsFee: data.transactionsFee,

               transactionsDirection: data.transactionsDirection,
               
               assetName: data.assetName,
               matchSource: data.matchSource,
               
               tradeReferences: [], // Initialize empty
               
               _rawData: item.rawData
           }
       })

       if (previewData.value.length === 0) {
           ElMessage.warning('未能解析出有效数据')
       } else {
           const validCount = previewData.value.filter(i => i.status === 'valid').length
           const errorCount = previewData.value.length - validCount
           if (errorCount > 0) {
               ElMessage.warning(`解析完成：${validCount} 条有效，${errorCount} 条异常`)
           } else {
               ElMessage.success(`成功解析 ${validCount} 条数据`)
           }
       }
    }
  } catch (error) {
    console.error('预览失败', error)
    ElMessage.error('解析文件失败，请检查文件格式')
  } finally {
    loading.value = false
  }
}


const reUpload = () => {
    previewData.value = []
    isExpanded.value = false
    providerCode.value = ''
    currentAssetFilter.value = 'ALL'
}




// Confirm Dialog State
const confirmDialog = ref({
    visible: false,
    validCount: 0,
    importForm: {
        importMode: 0,
        range: [] as any // Flexible type for DatePicker v-model
    },
    scopeDesc: '',
    pendingItems: [] as recordApi.ImportPreviewItem[]
})

// Open Confirm Dialog
const handleConfirmClick = () => {
    // Smart Selection Logic: Prioritize Selection > Filtered View
    const currentSelection = unref(selectedRows)
    const hasSelection = currentSelection.length > 0
    
    // Determine candidate items
    let candidates = hasSelection ? currentSelection : filteredData.value
    
    const validItems = candidates.filter(item => item.status === 'valid')
    
    if (validItems.length === 0) {
        ElMessage.warning('当前范围内没有有效的数据可导入')
        return
    }
    
    // Store pending items for execution
    confirmDialog.value.pendingItems = validItems
    confirmDialog.value.validCount = validItems.length
    
    // Set Description
    if (hasSelection) {
        confirmDialog.value.scopeDesc = `来源: 已选记录 (${validItems.length}条)`
    } else {
        const filterName = currentAssetFilter.value === 'ALL' ? '全部' : currentAssetFilter.value
        confirmDialog.value.scopeDesc = `来源: 当前列表 [${filterName}]`
    }
    
    // Calculate Range from valid items
    let minDate = ''
    let maxDate = ''
    
    validItems.forEach(item => {
        const d = item.parsedData?.transactionsDate
        if (d) {
            if (!minDate || d < minDate) minDate = d
            if (!maxDate || d > maxDate) maxDate = d
        }
    })
    
    confirmDialog.value.importForm.importMode = 0
    // Default range: min and max of current batch
    if (minDate && maxDate) {
        confirmDialog.value.importForm.range = [minDate, maxDate]
    } else {
        confirmDialog.value.importForm.range = []
    }
    
    confirmDialog.value.visible = true
}

// Execute Import (Real API Call)
const executeImport = async () => {
    // Use stored pending items
    const validItems = confirmDialog.value.pendingItems
    const form = confirmDialog.value.importForm
    
    // Helper formats
    const payload: recordApi.ImportConfirmRequest = {
        importMode: form.importMode,
        rangeStart: undefined,
        rangeEnd: undefined,
        items: []
    }
    
    // Check Range for Mode 3
    if (form.importMode === 3) {
        if (!form.range || form.range.length < 2) {
             ElMessage.warning('请选择替换的时间范围')
             return
        }
        payload.rangeStart = form.range[0]
        payload.rangeEnd = form.range[1]
    }
    
    loading.value = true
    confirmDialog.value.visible = false 

    try {
        const items: recordApi.ImportConfirmItem[] = validItems.map(item => {
             const d = item.parsedData!
             const groups = item.tradeReferences?.map(r => ({
                 groupType: r.groupType,
                 groupId: r.groupId!
             })) || []

             return {
                 assetId: d.assetId!,
                 transactionsDate: d.transactionsDate!,
                 transactionsPrice: d.transactionsPrice!,
                 transactionsShare: d.transactionsShare!,
                 transactionsAmount: d.transactionsAmount!,
                 transactionsFee: d.transactionsFee || 0,
                 transactionsDirection: d.transactionsDirection!,
                 groups: groups
             }
        })
        payload.items = items
        
        const res = await recordApi.importRecordConfirm(payload)
        
        if (res) {
             const count = (res.data as any)?.count ?? (typeof res.data === 'number' ? res.data : 0)
             
             // Extract unique asset names for smart navigation
             const uniqueAssets = Array.from(new Set(validItems.map(i => i.assetName || '')))
             const targetAssetName = uniqueAssets.length === 1 ? uniqueAssets[0] : undefined

             ElMessageBox.confirm(
                `成功导入 ${count} 条记录。是否前往查看记录列表？`,
                '导入成功',
                {
                    confirmButtonText: '查看记录',
                    cancelButtonText: '继续导入',
                    type: 'success',
                    distinguishCancelAndClose: true
                }
             )
             .then(() => {
                 // View Records
                 if (targetAssetName) {
                     router.push({ path: '/analysis/record', query: { assetName: targetAssetName } })
                 } else {
                     router.push('/analysis/record')
                 }
             })
             .catch((action) => {
                 // Cancel (= Continue Import) or Close
                 if (action === 'cancel') {
                     reUpload()
                 }
                 // If close (x), do nothing (stay on current state) or reUpload? 
                 // Usually user expects stay. But state is "previewing imported stuff". 
                 // Let's call reUpload to clear for next batch if they explicitly clicked "Continue".
                 // If they just closed dialog, maybe they want to see preview again? 
                 // Let's stick to "Cancel button" triggers reUpload.
             })
        }
    } catch (error) {
        console.error('导入失败', error)
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.upload-demo {
  display: block;
}

.upload-demo :deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.content-detail-wrap-body) {
  margin-bottom: 0 !important;
}

/* Row Highlighting */
:deep(.el-table .error-row) {
  --el-table-tr-bg-color: var(--el-color-error-light-9);
}
:deep(.el-table .warning-row) {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
</style>
