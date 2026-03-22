<template>
  <ContentWrap title="基础设置" class="mt-5">
    <Form :schema="basicSettingFormSchema" ref="formRef" :is-col="false">
      <template #system_section_header>
        <h3 style="font-size: 16px; margin-bottom: 10px; margin-top: 0px">系统基础配置</h3>
        <el-divider style="margin-top: 0px; margin-bottom: 20px" />
      </template>
      <template #appearance_section_header>
        <h3 style="font-size: 16px; margin-bottom: 10px; margin-top: 20px">外观设置</h3>
        <el-divider style="margin-top: 0px; margin-bottom: 20px" />
      </template>
      <template #language_section_header>
        <h3 style="font-size: 16px; margin-bottom: 10px; margin-top: 20px">语言设置</h3>
        <el-divider style="margin-top: 0px; margin-bottom: 20px" />
      </template>
    </Form>
    <el-button type="primary" @click="confirmForm">保存设置</el-button>
  </ContentWrap>
</template>

<script lang="ts" setup>
import { ContentWrap } from '@/components/ContentWrap'
import { Form, FormExpose } from '@/components/Form'
import { reactive, unref, ref, onMounted } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { ElMessage } from 'element-plus'

// == 数据定义
const { required } = useValidator()

const formRef = ref<FormExpose>()

const basicSettingFormSchema = reactive<FormSchema[]>([
  {
    field: 'system_section_header', // 系统基础配置头部插槽
    colProps: { span: 24 }
  },
  {
    field: 'system_name',
    label: '系统名称',
    component: 'Input',
    componentProps: {
      style: 'width: 400px',
      placeholder: '请输入系统名称'
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'system_version',
    label: '系统版本',
    component: 'Input',
    componentProps: {
      style: 'width: 400px',
      placeholder: '请输入系统版本'
    }
  },
  {
    field: 'system_description',
    label: '系统描述',
    component: 'Input',
    componentProps: {
      type: 'textarea',
      rows: 3,
      style: 'width: 400px',
      placeholder: '请输入系统描述'
    }
  },
  {
    field: 'appearance_section_header', // 外观设置头部插槽
    colProps: { span: 24 }
  },
  {
    field: 'theme_mode',
    label: '主题模式',
    component: 'Select',
    componentProps: {
      style: 'width: 400px',
      placeholder: '请选择主题模式',
      options: [
        { label: '浅色模式', value: 'light' },
        { label: '深色模式', value: 'dark' },
        { label: '跟随系统', value: 'auto' }
      ]
    }
  },
  {
    field: 'primary_color',
    label: '主题色',
    component: 'ColorPicker',
    componentProps: {
      showAlpha: false
    }
  },
  {
    field: 'layout_mode',
    label: '布局模式',
    component: 'Select',
    componentProps: {
      style: 'width: 400px',
      placeholder: '请选择布局模式',
      options: [
        { label: '经典布局', value: 'classic' },
        { label: '顶部菜单', value: 'topMenu' },
        { label: '混合布局', value: 'cutMenu' }
      ]
    }
  },
  {
    field: 'language_section_header', // 语言设置头部插槽
    colProps: { span: 24 }
  },
  {
    field: 'default_language',
    label: '默认语言',
    component: 'Select',
    componentProps: {
      style: 'width: 400px',
      placeholder: '请选择默认语言',
      options: [
        { label: '简体中文', value: 'zh-CN' },
        { label: 'English', value: 'en' }
      ]
    }
  },
  {
    field: 'timezone',
    label: '时区设置',
    component: 'Select',
    componentProps: {
      style: 'width: 400px',
      placeholder: '请选择时区',
      options: [
        { label: '北京时间 (UTC+8)', value: 'Asia/Shanghai' },
        { label: '东京时间 (UTC+9)', value: 'Asia/Tokyo' },
        { label: '纽约时间 (UTC-5)', value: 'America/New_York' },
        { label: '伦敦时间 (UTC+0)', value: 'Europe/London' }
      ]
    }
  }
])

// == hooks
onMounted(async () => {
  await getBasicSettings()
})

// == 方法交互

// 获取基础设置
const getBasicSettings = async () => {
  // TODO: 调用API获取基础设置数据
  // const res = await BasicSettingApi.getBasicSettings()
  // if (res && res.data) {
  //   unref(formRef)?.setValues(res.data)
  // }
  
  // 模拟数据
  const mockData = {
    system_name: 'Snow View Admin',
    system_version: '1.0.0',
    system_description: '基于 Vue3 + Element Plus 的现代化后台管理系统',
    theme_mode: 'light',
    primary_color: '#409EFF',
    layout_mode: 'classic',
    default_language: 'zh-CN',
    timezone: 'Asia/Shanghai'
  }
  unref(formRef)?.setValues(mockData)
}

// 提交表单
const confirmForm = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate(async (valid) => {
      if (valid) {
        const model = unref(formRef)?.formModel
        // TODO: 调用API保存基础设置
        // const optionRes = await BasicSettingApi.updateBasicSettings(model)
        // if (optionRes && optionRes.success) {
        //   ElMessage({
        //     message: '保存成功',
        //     type: 'success'
        //   })
        // }
        
        // 模拟保存成功
        ElMessage({
          message: '基础设置保存成功',
          type: 'success'
        })
        console.log('保存的基础设置:', model)
        await getBasicSettings()
      }
    })
}
</script>

<style scoped>
/* 自定义样式 */
</style>