<template>
  <ContentWrap title="数据设置" class="mt-5">
    <el-alert
      v-if="!runtimeCapabilityFlags.systemToken"
      title="当前运行口径已关闭系统 token 配置页"
      type="warning"
      :closable="false"
      show-icon
    />
    <template v-else>
      <Form :schema="dataSettingFormSchema" ref="formRef" :is-col="false">
        <template #xueqiu_section_header>
          <h3 style="font-size: 16px; margin-bottom: 10px; margin-top: 0px">雪球配置</h3>
          <el-divider style="margin-top: 0px; margin-bottom: 20px" />
        </template>
        <template #xq_a_token="data">
          <el-space>
            <el-input v-model="data.xq_a_token" required />
            <el-button @click="testCode">测试token</el-button>
            <span :style="{ color: tokenTestRes ? 'green' : 'red' }">{{
              tokenTestResC + (testTimestamp ? ' : ' + testTimestamp : '')
            }}</span>
          </el-space>
        </template>
        <template #serverchan_section_header>
          <h3 style="font-size: 16px; margin-bottom: 10px; margin-top: 20px">Server酱配置</h3>
          <el-divider style="margin-top: 0px; margin-bottom: 20px" />
        </template>
      </Form>
      <el-button type="primary" @click="confirmForm">确认</el-button>
    </template>
  </ContentWrap>
</template>
<script lang="ts" setup>
import { ContentWrap } from '@/components/ContentWrap'
import { Form, FormExpose } from '@/components/Form'
import { runtimeCapabilityFlags } from '@/config/runtimeProfile'
import { reactive, unref, ref, onMounted, computed } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { ElMessage } from 'element-plus'
import * as SettingDataApi from '@/api/snow/setting/SettingDataApi'
import * as systemApi from '@/api/snow/System/SystemApi'

// == 数据定义
const { required } = useValidator()

const formRef = ref<FormExpose>()
const testTimestamp = ref<string>('') // 新增：用于存储上次测试的时间戳

const dataSettingFormSchema = reactive<FormSchema[]>([
  {
    field: 'xueqiu_section_header', // 雪球配置头部插槽
    colProps: { span: 24 }
  },
  {
    field: 'xq_a_token',
    label: '雪球Token' // 标签名标准化
  },
  {
    field: 'u',
    label: '雪球UserID', // 标签名标准化
    component: 'Input',
    componentProps: {
      style: 'width: 500px'
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'serverchan_section_header', // Server酱配置头部插槽
    colProps: { span: 24 }
  },
  {
    field: 'serverchen_sendkey',
    label: 'Server酱SendKey', // 标签名标准化
    component: 'Input',
    componentProps: {
      style: 'width: 500px'
    },
    formItemProps: {
      rules: [required()]
    }
  }
])

// token测试结果 computed
const tokenTestRes = ref<any>(null)
const tokenTestResC = computed(() => {
  if (tokenTestRes.value == null) {
    return ''
  } else if (tokenTestRes.value == true) {
    return '测试成功'
  } else if (tokenTestRes.value == false) {
    return '测试失败'
  }
  return ''
})

// == hooks
onMounted(async () => {
  if (!runtimeCapabilityFlags.systemToken) {
    return
  }
  await getToken()
})

// == 方法交互

// 获取token
const getToken = async () => {
  if (!runtimeCapabilityFlags.systemToken) {
    return
  }
  const res = await SettingDataApi.getToken()
  if (res && res.data) {
    unref(formRef)?.setValues(res.data)
  }
}

// 提交表单
const confirmForm = () => {
  if (!runtimeCapabilityFlags.systemToken) {
    ElMessage.warning('当前运行口径已关闭系统 token 配置')
    return
  }
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (valid) {
        const model = unref(formRef)?.formModel
        const optionRes = await SettingDataApi.updateToken(model)
        if (optionRes && optionRes.success) {
          ElMessage({
            message: '操作成功',
            type: 'success'
          })
        }
        await getToken()
      }
    })
}

// 测试token
const testCode = async () => {
  if (!runtimeCapabilityFlags.systemToken) {
    ElMessage.warning('当前运行口径已关闭系统 token 测试')
    tokenTestRes.value = false
    testTimestamp.value = new Date().toLocaleString()
    return
  }
  const currentForm = unref(formRef)
  if (!currentForm || !currentForm.formModel) {
    ElMessage.error('表单数据不可用，请稍后重试。')
    tokenTestRes.value = false
    testTimestamp.value = new Date().toLocaleString() // 更新时间戳
    return
  }

  // 使用原始字段名从表单模型中提取 token 和 userid
  const { xq_a_token, u } = currentForm.formModel

  if (!xq_a_token || !u) {
    ElMessage.error('请填写雪球Token和UserID后再测试。')
    tokenTestRes.value = false
    testTimestamp.value = new Date().toLocaleString() // 更新时间戳
    return
  }

  try {
    // 将提取的 xq_a_token 作为 token，u 作为 userid 传递给 API
    // API `systemApi.tokenTestResult` 期望参数为 { xq_a_token: string; u: string }
    const res = await systemApi.tokenTestResult({ xq_a_token: xq_a_token, u: u })

    tokenTestRes.value = res && res.data // 直接使用 res.data 作为测试结果
    if (tokenTestRes.value === true) {
      ElMessage.success('Token 测试成功')
    } else if (tokenTestRes.value === false) {
      ElMessage.error('Token 测试失败')
    } else {
      // 如果 res.data 不是预期的布尔值，也视为失败
      tokenTestRes.value = false
      ElMessage.error('Token 测试结果异常')
    }
  } catch (error) {
    console.error('Token测试时发生错误:', error)
    tokenTestRes.value = false
    // ElMessage.error('Token测试失败，请检查网络或联系管理员。')
  } finally {
    testTimestamp.value = new Date().toLocaleString() // 确保在测试后（无论成功失败）都更新时间戳
  }
}
</script>
<style></style>
