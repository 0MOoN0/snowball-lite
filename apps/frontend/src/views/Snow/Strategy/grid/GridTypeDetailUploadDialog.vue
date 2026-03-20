<!-- 网格类型详情上传弹窗 -->
<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" center @close="closeDialog">
    <Form ref="formRef" :is-col="false" :schema="uploadFormSchema">
      <template #file>
        <el-upload
          class="upload-demo"
          drag
          :action="uploadInfo.url"
          multiple
          :auto-upload="false"
          :data="uploadInfo.data"
          ref="uploadRef"
          :on-success="uploadSuccess"
          :on-error="uploadError"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text"> Drop file here or <em>click to upload</em> </div>
          <template #tip>
            <div class="el-upload__tip">请按照格式上传网格类型详情 xlsx 文件 </div>
          </template>
        </el-upload>
      </template>
    </Form>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">上传</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { ElMessage, UploadInstance } from 'element-plus'
import _ from 'lodash-es'
import { computed, reactive, ref, unref, watch } from 'vue'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '上传交易记录'
  },
  gridTypeId: {
    type: Number
  }
})
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})

const uploadInfo = reactive({
  // 上传的地址
  url: import.meta.env.VITE_API_BASEPATH + '/grid_type_detail_list/file',
  // 上传参数
  data: {
    gridTypeId: props.gridTypeId,
    sheetName: null
  }
})

const uploadRef = ref<UploadInstance>()

// 关闭对话框
const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

const formRef = ref<FormExpose>()
const uploadFormSchema = reactive<FormSchema[]>([
  {
    field: 'file',
    label: '交易记录文件',
    labelMessage: '上传记录将会覆盖原有网格类型详情记录'
  },
  {
    field: 'sheetName',
    label: '工作表名称',
    component: 'Input',
    labelMessage: "默认使用'网格名称_网格类型名称'作为读取的工作表名称"
  }
])

// 监听网格类型数据
watch(
  () => props.gridTypeId,
  (gridTypeId: number) => {
    // _.set(uploadInfo, 'data.gridId', gridInfo.gridId)
    // _.set(uploadInfo, 'data.gridTypeId', gridInfo.gridTypeId)
    uploadInfo.data.gridTypeId = gridTypeId
  }
)

// 提交表单
const confirmDialog = () => {
  if (uploadInfo.data.gridTypeId == null) {
    ElMessage({
      message: '无法获取网格类型数据，请刷新重试',
      type: 'error'
    })
    return
  }
  const sheetName = _.get(unref(formRef)?.formModel, 'sheetName', null)
  uploadInfo.data.sheetName = sheetName
  uploadRef.value!.submit()
}

/**
 * 上传成功
 * @param res
 */
const uploadSuccess = (res) => {
  if (res && res.data) {
    ElMessage({
      message: res.message,
      type: 'success'
    })
    dialogShow.value = false
    emit('closeDialog')
    return
  }
  ElMessage({
    message: res.message,
    type: 'error'
  })
  uploadRef.value!.clearFiles()
}

const uploadError = (error) => {
  ElMessage({
    message: '上传失败，文件未到达服务器，原因： ' + error,
    type: 'error'
  })
}
</script>
<style></style>
