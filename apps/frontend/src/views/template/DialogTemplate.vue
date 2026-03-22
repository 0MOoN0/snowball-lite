<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center>
    <Form ref="formRef" :is-col="false" />
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">提交</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import Form from '@/components/Form/src/Form.vue'
import { computed, ref, unref } from 'vue'
import * as assetApi from '@/api/snow/asset/AssetApi'
import { ElMessage } from 'element-plus'
import { FormExpose } from '@/components/Form'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '证券元数据操作'
  }
})
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})
// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

const formRef = ref<FormExpose>()

// 关闭弹窗
const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate((valid) => {
      if (valid) {
        const model = unref(formRef)?.formModel
        console.log('model : ', model)
        assetApi.saveOrUpdateAsset(model).then((res) => {
          if (res.success) {
            ElMessage({
              message: '操作成功',
              type: 'error'
            })
          }
        })
      }
    })
}
</script>
<style></style>
