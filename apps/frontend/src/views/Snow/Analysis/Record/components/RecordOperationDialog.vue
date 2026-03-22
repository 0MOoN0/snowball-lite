<template>
  <Dialog v-model="dialogVisible" :title="dialogTitle" @close="closeDialog" center width="60%">
    <div v-loading="loading">
      <Form ref="formRef" :is-col="true" :schema="formSchemas" @register="register" />

      <!-- 关联关系管理区域 -->
      <div class="mt-20px pt-20px border-t border-solid border-[var(--el-border-color)]">
        <div class="flex justify-between items-center mb-15px">
          <h3 class="text-16px font-bold text-[var(--el-text-color-primary)]">关联关系</h3>
          <ElButton type="primary" size="small" @click="addRelation" icon="Plus">添加关联</ElButton>
        </div>

        <el-table
          :data="tradeReferences"
          border
          style="width: 100%"
          class="custom-table"
          :header-cell-style="{ background: 'var(--el-fill-color-light)', color: 'var(--el-text-color-primary)' }"
        >
          <el-table-column prop="groupType" label="分组类型" width="150">
            <template #default="{ row }">
              <el-select
                v-model="row.groupType"
                style="width: 100%"
                class="table-select"
                @change="() => handleGroupTypeChange(row)"
              >
                <el-option v-for="item in groupTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </template>
          </el-table-column>

          <el-table-column prop="groupId" label="业务对象">
            <template #default="{ row }">
              <!-- 当分组类型为网格(1)时，显示下拉选择框 -->
              <el-select
                v-if="row.groupType === 1"
                v-model="row.groupId"
                style="width: 100%"
                class="table-select"
                placeholder="请选择"
                filterable
                remote
                :remote-method="(query) => remoteMethod(query, row)"
                :loading="row.loading"
                @focus="() => initOptions(row)"
              >
                <el-option v-for="item in row.options" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>

              <!-- 当分组类型为其他(0)或其他情况时，显示输入框 -->
              <!-- 注意：这里假设 groupType 不为 1 时，groupId 字段可能用于存储输入的文本值，或者需要一个新的字段来存储文本 -->
              <!-- 根据之前的接口定义，TradeReferenceUpdateItem 的 groupId 是 integer 类型 -->
              <!-- 如果 "其他" 类型需要输入文本 ID，请确保输入的是数字 -->
              <!-- 如果需要输入纯文本描述，可能需要后端接口支持或确认业务逻辑 -->
              <!-- 暂时假设 groupId 仍需为数字，使用 InputNumber 或 Input 限制输入 -->
              <el-input
                v-else
                v-model.number="row.groupId"
                style="width: 100%"
                class="table-input"
                placeholder="请输入ID"
              />
            </template>
          </el-table-column>

          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <ElButton type="danger" text bg size="default" icon="Delete" @click="removeRelation($index)" />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog" :loading="loading" :disabled="loading">提交</ElButton>
      <ElButton @click="closeDialog" :disabled="loading">关闭</ElButton>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import * as recordApi from '@/api/snow/Record/index'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { useForm } from '@/hooks/web/useForm'
import { webHelper } from '@/utils/webHelper'
import { ElMessage, ElButton, ElSelect, ElOption, ElTable, ElTableColumn } from 'element-plus'
import { cloneDeep } from 'lodash-es'
import { ref, unref, nextTick, PropType } from 'vue'
import { useRelationOptions } from '../hooks/useRelationOptions'

// 关联关系项类型
interface RelationItem {
  groupType: number
  groupId: number | null
  options: { label: string; value: number }[]
  loading: boolean
}

const emit = defineEmits(['success'])

const props = defineProps({
  formSchema: {
    type: Array as PropType<FormSchema[]>,
    default: () => [],
  },
})

// 使用 hooks
const { groupTypeOptions, fetchRelationOptions, loadGroupTypeEnum } = useRelationOptions()
const { register, methods: formMethods } = useForm()
const { setValues } = formMethods

// 状态定义
const dialogVisible = ref(false)
const dialogTitle = ref('')
const loading = ref(false)
const currentRecordId = ref<number | null>(null)
const tradeReferences = ref<RelationItem[]>([])
const formSchemas = ref<FormSchema[]>([])
const formRef = ref<FormExpose>()

// 过滤掉不需要的字段
const filterSchema = (schemas: FormSchema[]) => {
  const excludeFields = ['groupType', 'groupTypes', 'gridTypeId', 'recordId', 'index', 'actions']
  return schemas.filter((item) => !excludeFields.includes(item.field))
}

// 打开弹窗
const open = async (type: 'add' | 'edit', id?: number) => {
  dialogVisible.value = true
  dialogTitle.value = type === 'add' ? '新增交易记录' : '编辑交易记录'
  currentRecordId.value = id || null

  // 初始化 Schema
  formSchemas.value = filterSchema(props.formSchema)

  // 确保枚举数据已加载
  try {
    await loadGroupTypeEnum()
  } catch (e) {
    console.error('加载枚举失败', e)
  }

  await nextTick()

  // 确保表单组件已注册
  // Dialog 内容可能是懒加载的，需要等待 Form 组件挂载并执行 register
  let retries = 0
  while (!unref(formRef) && retries < 10) {
    await new Promise((resolve) => setTimeout(resolve, 50))
    retries++
  }

  // 设置自动计算逻辑
  setupAutoCalculate()

  if (type === 'edit' && id) {
    loadData(id)
  } else {
    resetData()
  }
}

// 设置自动计算逻辑
const setupAutoCalculate = async () => {
  await formMethods.setSchema([
    {
      field: 'transactionsPrice',
      path: 'componentProps.onChange',
      value: async (val: number) => {
        const model = await formMethods.getFormData()
        if (model && model.transactionsShare) {
          const amount = webHelper.numFormat(val * Number(model.transactionsShare), false)
          setValues({ transactionsAmount: amount })
        }
      },
    },
    {
      field: 'transactionsShare',
      path: 'componentProps.onChange',
      value: async (val: number) => {
        const model = await formMethods.getFormData()
        if (model && model.transactionsPrice) {
          const amount = webHelper.numFormat(val * Number(model.transactionsPrice), false)
          setValues({ transactionsAmount: amount })
        }
      },
    },
  ])
}

// 加载数据
const loadData = async (id: number) => {
  loading.value = true
  try {
    const res = await recordApi.getRecordById(id)
    if (res.data) {
      const record = res.data
      // 金额单位转换 (厘 -> 元)
      record.transactionsAmount = Number(record.transactionsAmount) / 1000
      record.transactionsFee = Number(record.transactionsFee) / 1000
      record.transactionsPrice = Number(record.transactionsPrice) / 1000
      // 确保份额是数字类型，避免 InputNumber 报错
      record.transactionsShare = Number(record.transactionsShare)

      await setValues(record)

      // 回显关联关系
      if (record.tradeReferences && record.tradeReferences.length > 0) {
        tradeReferences.value = record.tradeReferences.map((ref: any) => ({
          groupType: ref.groupType,
          groupId: ref.groupId,
          options: [],
          loading: false,
        }))

        // 触发选项加载以显示Label
        tradeReferences.value.forEach((row) => initOptions(row))
      } else {
        tradeReferences.value = []
      }
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 重置数据
const resetData = async () => {
  tradeReferences.value = []
  const form = unref(formRef)
  if (form) {
    await form.getElFormRef()?.resetFields()
  }
}

// 关闭弹窗
const closeDialog = () => {
  dialogVisible.value = false
}

// 添加关联
const addRelation = () => {
  tradeReferences.value.push({
    groupType: 1, // 默认网格
    groupId: null,
    options: [],
    loading: false,
  })
}

// 删除关联
const removeRelation = (index: number) => {
  tradeReferences.value.splice(index, 1)
}

// 处理分组类型变更
const handleGroupTypeChange = (row: RelationItem) => {
  row.groupId = null
  row.options = []
  initOptions(row)
}

// 初始化选项
const initOptions = async (row: RelationItem) => {
  row.loading = true
  try {
    const options = await fetchRelationOptions(row.groupType)
    row.options = options
  } catch (e) {
    console.error(e)
  } finally {
    row.loading = false
  }
}

// 远程搜索
const remoteMethod = async (query: string, row: RelationItem) => {
  row.loading = true
  try {
    const options = await fetchRelationOptions(row.groupType, query)
    row.options = options
  } catch (e) {
    console.error(e)
  } finally {
    row.loading = false
  }
}

// 提交表单
const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (valid) {
        loading.value = true
        try {
          const model = unref(formRef)?.formModel
          if (!model) return

          const submitModel = cloneDeep(model)

          // 处理金额单位 (元 -> 厘)
          submitModel.transactionsFee = Number(submitModel.transactionsFee) * 1000
          submitModel.transactionsPrice = Number(submitModel.transactionsPrice) * 1000

          // 确保 transactionsShare 是数字
          submitModel.transactionsShare = Number(submitModel.transactionsShare)

          if (typeof submitModel.transactionsAmount === 'string') {
            submitModel.transactionsAmount = submitModel.transactionsAmount.replace(/,/g, '')
          }
          submitModel.transactionsAmount = Number(submitModel.transactionsAmount) * 1000

          // 构建 tradeReferences
          const mappedTradeReferences = tradeReferences.value
            .filter((item) => item.groupId !== null)
            .map((item) => ({
              groupType: item.groupType,
              groupId: item.groupId,
            }))

          // 构造最终提交的数据对象，确保是一个纯净的对象
          const finalSubmitData: any = {
            ...submitModel,
            tradeReferences: mappedTradeReferences,
          }

          if (currentRecordId.value) {
            finalSubmitData.id = currentRecordId.value
          }

          const res = await recordApi.saveOrUpdateRecord(finalSubmitData)
          ElMessage({
            message: res.message,
            type: res.success ? 'success' : 'error',
          })

          if (res.success) {
            emit('success')
            closeDialog()
          }
        } catch (error) {
          console.error(error)
        } finally {
          loading.value = false
        }
      }
    })
}

defineExpose({
  open,
})
</script>

<style scoped>
:deep(.el-form-item__content) {
  width: 100%;
}

/* 表格内 Select 样式优化 */
:deep(.table-select .el-input__wrapper),
:deep(.table-input .el-input__wrapper) {
  box-shadow: none !important;
  background-color: transparent;
  padding-left: 0;
}

:deep(.table-select .el-input__wrapper:hover),
:deep(.table-input .el-input__wrapper:hover) {
  background-color: var(--el-fill-color-light);
}

:deep(.table-select.is-focus .el-input__wrapper),
:deep(.table-input.is-focus .el-input__wrapper) {
  box-shadow: none !important;
  background-color: var(--el-fill-color-light);
}

/* 去除表格单元格的默认内边距，让Select填满 */
:deep(.custom-table .el-table__cell .cell) {
  padding: 0 10px;
}
</style>
