<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElDialog, ElForm, ElFormItem, ElInputNumber, ElButton, ElRow, ElCol, ElSelect, ElOption } from 'element-plus'
import * as _ from 'lodash-es'
import { addThousandsSeparator } from '@/utils/gridDataFormatter'

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '编辑网格类型详情'
  },
  rowData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close-dialog', 'submit'])

const formRef = ref()
const formData = reactive({
  id: null,
  gear: 0,
  monitorType: 0,
  triggerPurchasePrice: 0,
  purchasePrice: 0,
  purchaseShares: 0,
  triggerSellPrice: 0,
  sellPrice: 0,
  sellShares: 0,
  saveShare: 0
})

// Initialize form data when rowData changes or dialog opens
watch(
  () => props.rowData,
  (newVal) => {
    if (newVal) {
      // Convert raw data (Hao) to UI data (Yuan)
      Object.assign(formData, {
        ...newVal,
        triggerPurchasePrice: newVal.triggerPurchasePrice ? newVal.triggerPurchasePrice / 10000 : 0,
        purchasePrice: newVal.purchasePrice ? newVal.purchasePrice / 10000 : 0,
        triggerSellPrice: newVal.triggerSellPrice ? newVal.triggerSellPrice / 10000 : 0,
        sellPrice: newVal.sellPrice ? newVal.sellPrice / 10000 : 0
      })
    } else {
      // Reset form if no data (add mode)
      Object.assign(formData, {
        id: null,
        gear: 0,
        monitorType: 0,
        triggerPurchasePrice: 0,
        purchasePrice: 0,
        purchaseShares: 0,
        triggerSellPrice: 0,
        sellPrice: 0,
        sellShares: 0,
        saveShare: 0
      })
    }
  },
  { immediate: true, deep: true }
)

// Computed fields (using Yuan directly)
const purchaseAmount = computed(() => {
  return formData.purchasePrice * formData.purchaseShares
})

const actualSellShares = computed(() => {
  return formData.sellShares - formData.saveShare
})

const sellAmount = computed(() => {
  return actualSellShares.value * formData.sellPrice
})

const profit = computed(() => {
  return formData.sellShares * formData.sellPrice - purchaseAmount.value
})

const saveShareProfit = computed(() => {
  return sellAmount.value - purchaseAmount.value
})

const formatNumber = (value: number | string, precision: number = 2) => {
  if (value === undefined || value === null) return '0'
  return addThousandsSeparator(Number(value).toFixed(precision))
}

const closeDialog = () => {
  emit('close-dialog')
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid, fields) => {
    if (valid) {
      // Convert UI data (Yuan) back to raw data (Hao)
      const dataToSubmit = {
        ...formData,
        triggerPurchasePrice: Math.round(formData.triggerPurchasePrice * 10000),
        purchasePrice: Math.round(formData.purchasePrice * 10000),
        triggerSellPrice: Math.round(formData.triggerSellPrice * 10000),
        sellPrice: Math.round(formData.sellPrice * 10000)
      }
      emit('submit', dataToSubmit)
      closeDialog()
    } else {
      console.log('error submit!', fields)
    }
  })
}
</script>

<template>
  <ElDialog
    :model-value="dialogVisible"
    :title="dialogTitle"
    width="800px"
    @close="closeDialog"
    :close-on-click-modal="false"
  >
    <ElForm :model="formData" ref="formRef" label-width="120px">
      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="档位" prop="gear">
            <ElInputNumber v-model="formData.gear" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="监控类型" prop="monitorType">
            <ElSelect v-model="formData.monitorType" placeholder="请选择">
              <ElOption label="买入" :value="0" />
              <ElOption label="卖出" :value="1" />
            </ElSelect>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="买入触发价" prop="triggerPurchasePrice">
            <ElInputNumber v-model="formData.triggerPurchasePrice" :precision="4" :step="0.0001" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="买入价" prop="purchasePrice">
            <ElInputNumber v-model="formData.purchasePrice" :precision="4" :step="0.0001" />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="入股数" prop="purchaseShares">
            <ElInputNumber v-model="formData.purchaseShares" :step="100" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="买入金额(元)">
            <span>{{ formatNumber(purchaseAmount) }}</span>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="卖出触发价" prop="triggerSellPrice">
            <ElInputNumber v-model="formData.triggerSellPrice" :precision="4" :step="0.0001" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="卖出价" prop="sellPrice">
            <ElInputNumber v-model="formData.sellPrice" :precision="4" :step="0.0001" />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="原出股数" prop="sellShares">
            <ElInputNumber v-model="formData.sellShares" :step="100" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="留存股数" prop="saveShare">
            <ElInputNumber v-model="formData.saveShare" :step="100" />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="实际出股数">
            <span>{{ formatNumber(actualSellShares, 0) }}</span>
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="实际卖出金额(元)">
            <span>{{ formatNumber(sellAmount) }}</span>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="收益(元)">
            <span>{{ formatNumber(profit) }}</span>
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="留股收益(元)">
            <span>{{ formatNumber(saveShareProfit) }}</span>
          </ElFormItem>
        </ElCol>
      </ElRow>
    </ElForm>
    <template #footer>
      <span class="dialog-footer">
        <ElButton @click="closeDialog">取消</ElButton>
        <ElButton type="primary" @click="submitForm">确认</ElButton>
      </span>
    </template>
  </ElDialog>
</template>
