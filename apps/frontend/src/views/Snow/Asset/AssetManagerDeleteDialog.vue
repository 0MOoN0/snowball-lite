<template>
  <el-dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center align-center width="30%"
    @open="loadAssetReference">
    <el-space direction="vertical" style="width: 100%;">
      <div v-if="!confirmDisabled" class="flex flex-col">
        <span class="text-lg text-red-500"><el-icon>
            <Warning />
          </el-icon> 如果继续操作，以下关联数据将会被删除：</span>
        <span>日线数据：<span>{{ assetRelations.dailyData }}</span></span>
        <span>分类数据：<span>{{ assetRelations.category }}</span></span>
        <span>费用数据：<span>{{ assetRelations.feeRule }}</span></span>
        <span>持仓数据：<span>{{ assetRelations.holdingData }}</span></span>
        <span>交易记录数据：<span>{{ assetRelations.recordData }}</span></span>
      </div>
      <div v-if="confirmDisabled" class="flex flex-col">
        <span class="text-lg text-red-500"><el-icon>
            <Warning />
          </el-icon> 该证券数据已经被其他数据依赖，请解除关联后再尝试删除：</span>
        <span>网格关联数据：<span class="text-red-500">{{ assetRelations.gridData }}</span></span>
        <span>被其他资产持有数据：<span class="text-red-500">{{ assetRelations.heldData }}</span></span>
        <span>交易记录分析数据：<span class="text-red-500">{{ assetRelations.transactionAnalysisData }}</span></span>
      </div>
    </el-space>
    <template #footer>
      <ElButton type="danger" @click="confirmDialog" :loading="loadingRelation" :disabled="confirmDisabled">确认删除
      </ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import * as assetRelationApi from '@/api/snow/asset/AssetRelationApi'
import * as assetApi from '@/api/snow/asset/AssetApi'
import { ElMessage } from 'element-plus'
import { reactive } from 'vue'
import { computed, ref } from 'vue'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

const loadingRelation = ref(true)

const confirmDisabled = ref(true)


// 从父组件中接受的参数
const dialogParams = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '删除证券数据确认对话框'
  },
  assetId: {
    type: Number
  }
})

// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

// 打开弹窗时，检索数据关联情况
const loadAssetReference = async () => {
  const res = await assetRelationApi.getAssetList(dialogParams.assetId)
  console.log(res)
  if (!res.success || !res.data) {
    ElMessage.error('获取数据关联情况失败')
    return
  }
  Object.assign(assetRelations, res.data)
  console.log(assetRelations)
  loadingRelation.value = false
  // 如果该证券数据被其他数据依赖，则不允许删除
  if (assetRelations.gridData > 0 || assetRelations.heldData > 0 || assetRelations.transactionAnalysisData > 0) {
    confirmDisabled.value = true
  } else {
    confirmDisabled.value = false
  }
}
const dialogShow = computed({
  get: () => dialogParams.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})

// 调用api删除对应的证券数据
const confirmDialog = async () => {
  if (!dialogParams.assetId || dialogParams.assetId < 0) {
    ElMessage.error('请选择证券数据')
    return
  }
  loadingRelation.value=true
  const res = await assetApi.deleteById(dialogParams.assetId)
  if (!res.success || !res.data) {
    ElMessage.error(res.message)
    loadingRelation.value=false
    return
  }
  ElMessage.success('删除成功')
  loadingRelation.value=false
  dialogShow.value = false
}

const assetRelations = reactive({
  category: 0,
  dailyData: 0,
  heldData: 0,
  recordData: 0,
  transactionAnalysisData: 0,
  id: 0,
  feeRule: 0,
  gridData: 0,
  holdingData: 0
})

</script>

<style scoped></style>
