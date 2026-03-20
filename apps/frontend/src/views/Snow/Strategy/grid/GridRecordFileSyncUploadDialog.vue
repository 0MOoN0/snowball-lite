<!-- 网格类型详情上传弹窗 -->
<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" center @close="closeDialog" :fullscreen="false">
    <ContentWrap title="网格交易文件上传表单" class="w-full">
      <Form ref="formRef" :is-col="false" :schema="uploadFormSchema" class="m-auto w-4/5">
        <template #file>
          <el-upload class="upload-demo" drag :action="uploadInfo.url" multiple :auto-upload="false" ref="uploadRef"
            :on-success="uploadSuccess" :on-error="uploadError">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text"> Drop file here or <em>click to upload</em> </div>
            <template #tip>
              <div class="el-upload__tip">请按照格式上传网格交易详情 xlsx 文件，上传后会根据文件内容同步所有网格交易数据 </div>
            </template>
          </el-upload>
        </template>
      </Form>
    </ContentWrap>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">上传</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import { Form } from '@/components/Form'
import { ElMessage, UploadInstance } from 'element-plus'
import { computed, reactive, ref } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])
// const { register, methods: formMethods } = useForm(uploadFormSchema)

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '上传网格交易同步文件'
  }
})
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})

const uploadInfo = reactive({
  // 上传的地址
  url: import.meta.env.VITE_API_BASEPATH + '/grid_record_all_sync/file'
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
    label: '网格交易记录文件',
    labelMessage: '上传记录将会根据"网格名称_网格类型名称"覆盖原有网格类型详情记录'
  }
])


// 提交表单
const confirmDialog = () => {
  uploadRef.value!.submit()
}

/**
 * 上传成功
 * @param res
 */
const uploadSuccess = (res) => {
  if (res && res.data) {
    let message = (res.data && res.data.length > 0) ? (res.message + ' 未更新的工作簿列表：' + res.data) : res.message
    ElMessage({
      message: message,
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
