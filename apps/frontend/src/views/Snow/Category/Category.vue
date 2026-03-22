<template>
  <ContentWrap title="分类列表">
    <el-tree
      :data="categoryList"
      show-checkbox
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      v-loading="dataLoading"
      draggable
      @node-drop="nodeDrop"
    >
      <template #default="{ data }">
        <span class="custom-tree-node">
          <span>{{ data.categoryName }}</span>
          <span>
            <ElButton link @click="addOrAppend(data, true)"> 添加同级分类 </ElButton>
            <ElButton link @click="addOrAppend(data)"> 添加子分类 </ElButton>
            <ElButton link style="margin-left: 8px" @click="edit(data)"> 编辑分类 </ElButton>
            <ElButton link style="margin-left: 8px" @click="remove(data)"> 删除分类 </ElButton>
          </span>
        </span>
      </template>
    </el-tree>
    <Dialog v-model="dialogVisible" :title="dialogTitle" max-height="300px" center>
      <Form ref="formRef" :schema="schema" :is-col="false" :model="editCategory" />
      <template #footer>
        <ElButton type="primary" @click="submitCategory">确定</ElButton>
        <ElButton @click="dialogVisible = false">取消</ElButton>
      </template>
    </Dialog>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
import * as categoryApi from '@/api/snow/category/CategoryApi'
import { nextTick, reactive, ref, unref } from 'vue'
import { Dialog } from '@/components/Dialog'
import { useValidator } from '@/hooks/web/useValidator'
import { Form, FormExpose } from '@/components/Form'
import { ElMessage, ElMessageBox } from 'element-plus'
import type Node from 'element-plus/es/components/tree/src/model/node'
import { Category } from '@/api/snow/category/types'

const { required } = useValidator()

//---table dialog
const dialogVisible = ref(false)

const dialogTitle = ref('分类表单')

const formRef = ref<FormExpose>()

const editCategory = ref<Category>({})

const schema = reactive<FormSchema[]>([
  {
    field: 'categoryName',
    label: '分类名称',
    component: 'Input',
    formItemProps: {
      rules: [required()]
    }
  }
])
//---talbe dialog end ---
const dataLoading = ref(false)
const categoryList = ref<Array<Category | any>>([])

const fetchCategoryList = () => {
  dataLoading.value = true
  categoryApi.getCategoryList().then((res) => {
    if (res.success) {
      categoryList.value = res.data
      dataLoading.value = false
    }
  })
}
fetchCategoryList()

const addOrAppend = (data: Category, isAdd = false) => {
  dialogVisible.value = true
  nextTick(() => {
    dialogTitle.value = isAdd ? '添加同级分类' : '添加子分类'
    editCategory.value = isAdd ? { pid: data.pid } : { pid: data.id }
    unref(formRef)?.setValues({
      categoryName: editCategory.value.categoryName
    })
  })
}

const remove = (data: Category) => {
  if (data.id) {
    ElMessageBox.confirm('是否删除选中数据？', '删除分类提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      categoryApi.deleteCategory(data.id).then((res) => {
        if (res.data) {
          fetchCategoryList()
          ElMessage.success(res.message)
        }
      })
    })
  }
}

const edit = (data: Category) => {
  dialogVisible.value = true
  nextTick(() => {
    editCategory.value = data
    unref(formRef)?.setValues({
      categoryName: editCategory.value.categoryName
    })
  })
}
const submitCategory = () => {
  Object.assign(editCategory.value, formRef.value?.formModel)
  categoryApi.updateOrSave(editCategory.value).then((res) => {
    if (res.data) {
      fetchCategoryList()
      dialogVisible.value = false
      ElMessage.success(res.message)
    }
  })
}
const nodeDrop = (droppedNode: Node, inNode: Node, loc: string) => {
  const dropNodeData = Object.assign({}, droppedNode.data)
  if (loc === 'before' || loc === 'after') {
    dropNodeData.pid = inNode.data.pid
  } else {
    dropNodeData.pid = inNode.data.id
  }
  categoryApi.updateOrSave(dropNodeData).then((res) => {
    if (res.data) {
      fetchCategoryList()
      ElMessage.success(res.message)
    }
  })
}
</script>

<style scoped>
.custom-tree-node {
  display: flex;
  padding-right: 8px;
  font-size: 14px;
  flex: 1;
  align-items: center;
  justify-content: space-between;
}
</style>
