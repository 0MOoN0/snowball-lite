<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <div v-loading="loading">
      <Form ref="formRef" :is-col="false" :schema="gridRecordSchema" @register="register" />
    </div>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog" :loading="loading" :disabled="loading">提交</ElButton>
      <ElButton @click="closeDialog" :disabled="loading">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import * as recordApi from '@/api/snow/Record/index'
import { GridRecord } from '@/api/snow/Record/types'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { useForm } from '@/hooks/web/useForm'
import { webHelper } from '@/utils/webHelper'
import { ElMessage } from 'element-plus'
import { get, set, cloneDeep } from 'lodash-es'
import { computed, Ref, ref, toRef, unref, watch, onMounted } from 'vue'

const emit = defineEmits(['closeDialog', 'update:dialogVisible', 'update:record'])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false,
  },
  dialogTitle: {
    type: String,
    default: '网格记录操作',
  },
  gridRecordSchema: {
    type: Array<FormSchema>,
  },
  gridRecordId: {
    type: Number,
  },
})

let gridRecordSchema = toRef(props, 'gridRecordSchema') as Ref<Array<FormSchema>>
const { register, methods: formMethods } = useForm(gridRecordSchema)
const { setValues } = formMethods

const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val),
})

// hook ====
// 打印gridRecordId
onMounted(() => {
  console.log('gridRecordId', props.gridRecordId)
})

// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

const formRef = ref<FormExpose>()

// 加载状态
const loading = ref(false)

// 关闭弹窗
const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (valid) {
        loading.value = true
        try {
          const model = unref(formRef)?.formModel
          if (!model) {
            ElMessage({
              message: '数据为空，无法提交表单',
              type: 'error',
            })
            return
          }
          const gridTypeId = get(model, 'gridTypeId', null)
          const assetId = get(model, 'assetId', null)

          // 设置 assetId，如果 model 中没有，则尝试从 props 中获取
          if (!assetId) {
            // 如果没有 assetId，尝试从 gridTypeDetail 或其他地方获取，这里假设 gridRecordSchema 中有 assetId 字段或者可以通过 gridTypeId 获取 assetId
            // 暂时通过 schema 查找 assetId
            const assetIdSchema = gridRecordSchema.value.find((schema) => schema.field == 'assetId')
            if (assetIdSchema && assetIdSchema.value) {
              set(model, 'assetId', assetIdSchema.value)
            } else {
              // 如果 schema 中没有，则尝试从 gridTypeId 获取 (这需要额外的数据支持，暂时假设调用方会传入 assetId)
              // 为了兼容，我们这里可以报错提示或者尝试默认值
              // 实际上，创建记录时 assetId 是必须的
            }
          }

          // 克隆一份数据用于提交，避免直接修改表单数据导致污染
          const submitModel = cloneDeep(model)

          // 新增模式下设置关联关系
          if (!props.gridRecordId) {
            // 设置 groupType 和 groupId
            if (gridTypeId) {
              set(submitModel, 'groupType', 1) // 1 表示网格
              set(submitModel, 'groupId', gridTypeId)
            }

            // 获取gridTypeId的值 (虽然新接口不再直接依赖 gridTypeId 作为核心字段，但为了业务逻辑可能还需要保留或转换)
            if (!gridTypeId) {
              const schemas = gridRecordSchema.value.filter((schema) => schema.field == 'gridTypeId')
              if (schemas && schemas.length > 0) {
                schemas.forEach((schema) => {
                  set(submitModel, schema.field, schema.value)
                  // 如果找到了 gridTypeId，顺便设置 groupType 和 groupId
                  set(submitModel, 'groupType', 1)
                  set(submitModel, 'groupId', schema.value)
                })
              }
            }
          }

          if (props.gridRecordId) {
            set(submitModel, 'recordId', props.gridRecordId)
            set(submitModel, 'id', props.gridRecordId)
            // 编辑模式下移除关联关系字段，防止修改关联
            delete submitModel.groupType
            delete submitModel.groupId
            delete submitModel.tradeReferences
            delete submitModel.gridTypeId
          }
          submitModel.transactionsFee = Number(submitModel.transactionsFee) * 1000
          submitModel.transactionsPrice = Number(submitModel.transactionsPrice) * 1000
          // 去除逗号
          if (typeof submitModel.transactionsAmount === 'string') {
            submitModel.transactionsAmount = submitModel.transactionsAmount.replace(/,/g, '')
          }
          submitModel.transactionsAmount = Number(submitModel.transactionsAmount) * 1000
          const res = await recordApi.saveOrUpdateRecord(submitModel)
          ElMessage({
            message: res.message,
            type: res.data ? 'success' : 'error',
          })
          if (res.data) {
            emit('update:record')
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

watch(
  () => props.gridRecordId,
  async (recordId: number) => {
    loading.value = true
    try {
      gridRecordSchema = toRef(props, 'gridRecordSchema') as Ref<Array<FormSchema>>
      // 设置交易金额
      formMethods.setSchema([
        {
          field: 'groupType',
          path: 'value',
          value: 1, // 默认为网格
        },
        {
          field: 'transactionsPrice',
          path: 'componentProps.onChange',
          value: async (val) => {
            let model = await formMethods.getFormData<GridRecord>()
            const amount = webHelper.numFormat((val * 1000 * Number(model.transactionsShare)) / 1000, false)
            setValues({ transactionsAmount: amount })
          },
        },
        {
          field: 'transactionsShare',
          path: 'componentProps.onChange',
          value: async (val) => {
            let model = await formMethods.getFormData<GridRecord>()
            const amount = webHelper.numFormat((val * Number(model.transactionsPrice) * 1000) / 1000, false)
            setValues({ transactionsAmount: amount })
          },
        },
      ])
      if (recordId != null) {
        // ... do something
        const recordRes = await recordApi.getRecordById(recordId)
        if (recordRes && recordRes.data) {
          let record: GridRecord = Object.assign({}, recordRes.data)
          console.log('record before', record)
          record.transactionsAmount = Number(record.transactionsAmount) / 1000
          record.transactionsFee = Number(record.transactionsFee) / 1000
          record.transactionsPrice = Number(record.transactionsPrice) / 1000
          console.log('record after', record)
          await setValues(record)
        }
      }
    } finally {
      loading.value = false
    }
  }
)
</script>
<style></style>
