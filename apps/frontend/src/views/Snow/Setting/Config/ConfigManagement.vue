<template>
  <div class="config-management">
    <ContentWrap>
      <!-- 页面标题和操作按钮 -->
      <div class="header-section">
        <div class="title-section">
          <h2>系统配置管理</h2>
          <p class="subtitle">管理系统设置项和配置分组</p>
        </div>
        <div class="action-buttons">
          <el-button type="primary" @click="handleAddConfig">
            <Icon icon="ep:plus" class="mr-5px" />
            新增配置项
          </el-button>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchForm.key"
              placeholder="搜索配置项名称或描述"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <Icon icon="ep:search" />
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="searchForm.group"
              placeholder="选择分组"
              clearable
              @change="handleSearch"
            >
              <el-option label="全部分组" value="" />
              <el-option label="通用设置" value="general" />
              <el-option label="系统设置" value="system" />
              <el-option label="邮件设置" value="email" />
              <el-option label="安全设置" value="security" />
              <el-option label="通知设置" value="notification" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="searchForm.settingType"
              placeholder="配置类型"
              clearable
              @change="handleSearch"
            >
              <el-option label="全部类型" value="" />
              <el-option label="字符串" value="string" />
              <el-option label="整数" value="int" />
              <el-option label="浮点数" value="float" />
              <el-option label="布尔值" value="bool" />
              <el-option label="密码" value="password" />
              <el-option label="JSON" value="json" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="handleSearch">
              <Icon icon="ep:search" class="mr-5px" />
              搜索
            </el-button>
          </el-col>
        </el-row>
      </div>



      <!-- 配置项列表 -->
      <div class="config-section">
        <h3>配置项列表</h3>
        <Table
          v-model:pageSize="tableObject.pageSize"
          v-model:currentPage="tableObject.currentPage"
          :columns="columns"
          :data="tableObject.tableList"
          :loading="tableObject.loading"
          :pagination="{
            total: tableObject.total
          }"
          @register="register"
        >
          <template #configType="{ row }">
            <el-tag :type="getConfigTypeTag(row.configType)" size="small">
              {{ getConfigTypeName(row.configType) }}
            </el-tag>
          </template>
          <template #status="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="handleStatusChange(row)"
            />
          </template>
          <template #action="{ row }">
            <el-button type="text" size="small" @click="handleEdit(row)">
              <Icon icon="ep:edit" class="mr-5px" />
              编辑
            </el-button>
            <el-button type="text" size="small" @click="handleDelete(row)">
              <Icon icon="ep:delete" class="mr-5px" />
              删除
            </el-button>
          </template>
        </Table>
      </div>
    </ContentWrap>



    <!-- 配置项对话框 -->
    <Dialog v-model="configDialogVisible" :title="configDialogTitle" width="600px">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px">
        <el-form-item label="配置项名称" prop="key">
          <el-input
            v-model="configForm.key"
            placeholder="请输入配置项名称"
            :disabled="isEditMode"
          />
        </el-form-item>
        <el-form-item label="配置项值" prop="value">
          <el-input
            v-if="configForm.settingType !== 'json'"
            v-model="configForm.value"
            :type="configForm.settingType === 'password' ? 'password' : 'text'"
            placeholder="请输入配置项值"
          />
          <div v-else class="json-config-container">
            <div class="json-toolbar">
              <el-button 
                size="small" 
                type="primary" 
                @click="formatJson"
                :disabled="!configForm.value"
              >
                格式化
              </el-button>
              <el-button 
                size="small" 
                @click="validateJson"
                :disabled="!configForm.value"
              >
                校验
              </el-button>
              <el-button 
                size="small" 
                @click="compressJson"
                :disabled="!configForm.value"
              >
                压缩
              </el-button>
            </div>
            <el-input
              v-model="configForm.value"
              type="textarea"
              :rows="8"
              placeholder="请输入JSON格式的配置值"
              class="json-textarea"
              :class="{ 'json-error': jsonValidationError }"
            />
            <div v-if="jsonValidationError" class="json-error-message">
              <el-icon><WarningFilled /></el-icon>
              {{ jsonValidationError }}
            </div>
            <div v-if="jsonValidationSuccess" class="json-success-message">
              <el-icon><SuccessFilled /></el-icon>
              JSON格式正确
            </div>
          </div>
        </el-form-item>
        <el-form-item label="配置类型" prop="settingType">
          <el-select v-model="configForm.settingType" placeholder="请选择配置类型">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="int" />
            <el-option label="浮点数" value="float" />
            <el-option label="布尔值" value="bool" />
            <el-option label="密码" value="password" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属分组" prop="group">
          <el-select v-model="configForm.group" placeholder="请选择分组" allow-create filterable>
            <el-option label="通用设置" value="general" />
            <el-option label="系统设置" value="system" />
            <el-option label="邮件设置" value="email" />
            <el-option label="安全设置" value="security" />
            <el-option label="通知设置" value="notification" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置描述" prop="description">
          <el-input
            v-model="configForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>
        <el-form-item label="默认值" prop="defaultValue">
          <el-input v-model="configForm.defaultValue" placeholder="请输入默认值（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfigSubmit">确定</el-button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, SuccessFilled } from '@element-plus/icons-vue'
import { ContentWrap } from '@/components/ContentWrap'
import { Dialog } from '@/components/Dialog'
import { Table } from '@/components/Table'
import { Icon } from '@/components/Icon'
import { useTable } from '@/hooks/web/useTable'
import { formatTime } from '@/utils'
import {
  systemSettingsApi,
  type Setting,
  type SettingCreate,
  type SettingUpdate,
  type SettingQueryParams,
  type DeleteResponse
} from '@/api/snow/config'

// 使用从API文件导入的类型

// 搜索表单
const searchForm = reactive<SettingQueryParams>({
  key: '',
  group: '',
  settingType: '',
  page: 1,
  size: 20
})



// 表格配置
const { register, tableObject, methods } = useTable({
  getListApi: (params: SettingQueryParams) => systemSettingsApi.getSettings(params),
  delListApi: (id: number) => systemSettingsApi.deleteSetting(id),
  response: {
    list: 'items',
    total: 'total'
  }
})

const { getList, delList } = methods

// 表格列配置
const columns = [
  {
    field: 'key',
    label: '配置项名称',
    minWidth: 180
  },
  {
    field: 'value',
    label: '配置值',
    minWidth: 200,
    formatter: (row: Setting) => {
      if (row.settingType === 'password') {
        return '******'
      }
      if (row.value && row.value.length > 50) {
        return row.value.substring(0, 50) + '...'
      }
      return row.value
    }
  },
  {
    field: 'settingType',
    label: '类型',
    width: 100
  },
  {
    field: 'group',
    label: '所属分组',
    width: 120
  },
  {
    field: 'description',
    label: '描述',
    minWidth: 150
  },
  {
    field: 'defaultValue',
    label: '默认值',
    minWidth: 50
  },
  {
    field: 'updatedTime',
    label: '更新时间',
    width: 200,
    formatter: (row: Setting) => {
      return row.updatedTime ? formatTime(row.updatedTime, 'yyyy-MM-dd HH:mm:ss') : '-'
    }
  },
  {
    field: 'action',
    label: '操作',
    width: 200,
    fixed: 'right'
  }
]

// 配置项对话框
const configDialogVisible = ref(false)
const configDialogTitle = ref('')
const configFormRef = ref()
const isEditMode = ref(false)
const configForm = reactive<Partial<Setting>>({
  key: '',
  value: '',
  settingType: 'string',
  group: 'general',
  description: '',
  defaultValue: ''
})

// JSON校验相关
const jsonValidationError = ref('')
const jsonValidationSuccess = ref(false)

const configRules = {
  key: [{ required: true, message: '请输入配置项名称', trigger: 'blur' }],
  value: [{ required: true, message: '请输入配置项值', trigger: 'blur' }],
  settingType: [{ required: true, message: '请选择配置类型', trigger: 'change' }]
}

// 分组管理（简化版，因为API不支持分组管理）
const groupDialogVisible = ref(false)
const groupDialogTitle = ref('')
const groupFormRef = ref()
const groupForm = reactive({
  name: '',
  description: ''
})

const groupRules = {
  name: [{ required: true, message: '请输入分组名称', trigger: 'blur' }]
}

// API调用函数


async function saveSetting(data: Setting) {
  try {
    if (data.id) {
      // 更新设置项
      const updateData: SettingUpdate = {
        key: data.key,
        value: data.value,
        settingType: data.settingType,
        group: data.group,
        description: data.description,
        defaultValue: data.defaultValue
      }
      await systemSettingsApi.updateSetting(updateData)
    } else {
      // 创建设置项
      const createData: SettingCreate = {
        key: data.key,
        value: data.value,
        settingType: data.settingType,
        group: data.group,
        description: data.description,
        defaultValue: data.defaultValue
      }
      await systemSettingsApi.createSetting(createData)
    }
    return true
  } catch (error) {
    console.error('保存设置项失败:', error)
    ElMessage.error('保存设置项失败')
    return false
  }
}

// 工具函数
function getConfigTypeName(type: string) {
  const typeMap: Record<string, string> = {
    string: '字符串',
    number: '数字',
    boolean: '布尔值',
    password: '密码',
    json: 'JSON'
  }
  return typeMap[type] || type
}

function getConfigTypeTag(type: string) {
  const tagMap: Record<string, string> = {
    string: '',
    number: 'success',
    boolean: 'warning',
    password: 'danger',
    json: 'info'
  }
  return tagMap[type] || ''
}

// 事件处理函数
function handleSearch() {
  // 构建查询参数，包含所有搜索字段（后端支持空值模糊查询）
  const searchParams: SettingQueryParams = {
    key: searchForm.key?.trim() || '',
    group: searchForm.group?.trim() || '',
    settingType: searchForm.settingType?.trim() || '',
    page: searchForm.page,
    size: searchForm.size
  }
  
  methods.setSearchParams(searchParams)
}



function handleAddConfig() {
  configDialogTitle.value = '新增配置项'
  isEditMode.value = false
  // 清除JSON校验状态
  jsonValidationError.value = ''
  jsonValidationSuccess.value = false
  Object.assign(configForm, {
    key: '',
    value: '',
    settingType: 'string',
    group: 'general',
    description: '',
    defaultValue: ''
  })
  configDialogVisible.value = true
}

function handleEdit(row: Setting) {
  configDialogTitle.value = '编辑配置项'
  isEditMode.value = true
  // 清除JSON校验状态
  jsonValidationError.value = ''
  jsonValidationSuccess.value = false
  Object.assign(configForm, row)
  configDialogVisible.value = true
}

async function handleDelete(row: Setting) {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置项 "${row.key}" 吗？此操作不可逆！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    if (!row.id) {
      ElMessage.error('配置项ID不存在，无法删除')
      return
    }
    
    const response = await systemSettingsApi.deleteSetting(row.id)
    if (response.success) {
      ElMessage.success('删除成功')
      // 刷新列表
      await getList()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除配置项失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

// JSON数据校验函数
function validateJsonValue(value: string): boolean {
  if (!value || value.trim() === '') {
    return true // 空值认为是有效的
  }
  
  try {
    JSON.parse(value)
    return true
  } catch (error) {
    console.error('JSON格式验证失败:', error)
    return false
  }
}

// JSON格式化
function formatJson() {
  if (!configForm.value) {
    ElMessage.warning('请先输入JSON内容')
    return
  }
  
  try {
    const parsed = JSON.parse(configForm.value)
    configForm.value = JSON.stringify(parsed, null, 2)
    jsonValidationError.value = ''
    jsonValidationSuccess.value = true
    ElMessage.success('JSON格式化成功')
    
    // 3秒后清除成功提示
    setTimeout(() => {
      jsonValidationSuccess.value = false
    }, 3000)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    jsonValidationError.value = `JSON格式错误: ${errorMessage}`
    jsonValidationSuccess.value = false
    ElMessage.error('JSON格式化失败，请检查格式')
  }
}

// JSON校验
function validateJson() {
  if (!configForm.value) {
    ElMessage.warning('请先输入JSON内容')
    return
  }
  
  try {
    JSON.parse(configForm.value)
    jsonValidationError.value = ''
    jsonValidationSuccess.value = true
    ElMessage.success('JSON格式正确')
    
    // 3秒后清除成功提示
    setTimeout(() => {
      jsonValidationSuccess.value = false
    }, 3000)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    jsonValidationError.value = `JSON格式错误: ${errorMessage}`
    jsonValidationSuccess.value = false
    ElMessage.error('JSON格式校验失败')
  }
}

// JSON压缩
function compressJson() {
  if (!configForm.value) {
    ElMessage.warning('请先输入JSON内容')
    return
  }
  
  try {
    const parsed = JSON.parse(configForm.value)
    configForm.value = JSON.stringify(parsed)
    jsonValidationError.value = ''
    jsonValidationSuccess.value = true
    ElMessage.success('JSON压缩成功')
    
    // 3秒后清除成功提示
    setTimeout(() => {
      jsonValidationSuccess.value = false
    }, 3000)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    jsonValidationError.value = `JSON格式错误: ${errorMessage}`
    jsonValidationSuccess.value = false
    ElMessage.error('JSON压缩失败，请检查格式')
  }
}

function handleConfigSubmit() {
  configFormRef.value?.validate(async (valid: boolean) => {
    if (valid) {
      // 如果设置类型是JSON，需要单独校验数据格式
      if (configForm.settingType === 'json' && configForm.value) {
        if (!validateJsonValue(configForm.value)) {
          jsonValidationError.value = 'JSON格式不正确，请检查数据格式'
          jsonValidationSuccess.value = false
          ElMessage.error('JSON格式不正确，请检查数据格式')
          return
        }
      }
      
      const success = await saveSetting(configForm as Setting)
      if (success) {
        ElMessage.success('保存成功')
        configDialogVisible.value = false
        // 清除JSON校验状态
        jsonValidationError.value = ''
        jsonValidationSuccess.value = false
        getList()
      } else {
        // 保存失败时不关闭对话框，让用户可以重新尝试
        ElMessage.error('保存失败，请检查输入内容后重试')
      }
    } else {
      ElMessage.warning('请检查表单输入是否正确')
    }
  })
}

async function handleStatusChange(row: Setting) {
  ElMessage.warning('状态切换功能暂不支持，请通过编辑功能修改设置项')
}

// 初始化
onMounted(() => {
  getList()
})
</script>

<style lang="less" scoped>
.config-management {
  .header-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;

    .title-section {
      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .subtitle {
        margin: 0;
        color: var(--el-text-color-regular);
        font-size: 14px;
      }
    }

    .action-buttons {
      display: flex;
      gap: 12px;
    }
  }

  .filter-section {
    margin-bottom: 16px;
    padding: 16px;
    background: var(--el-bg-color-page);
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    
    .el-row {
      align-items: center;
    }
    
    .el-col {
      display: flex;
      align-items: center;
    }
    
    .el-input,
    .el-select {
      width: 100%;
    }
  }





  .config-section {
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }
  
  .json-config-container {
    .json-toolbar {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
      padding: 8px;
      background: var(--el-bg-color-page);
      border: 1px solid var(--el-border-color-light);
      border-radius: 4px;
    }
    
    .json-config-container {
      width: 100%;
    }
    
    .json-textarea {
      width: 100%;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 13px;
      line-height: 1.4;
      
      &.json-error {
        border-color: var(--el-color-danger);
      }
      
      :deep(.el-textarea__inner) {
        width: 100%;
      }
    }
    
    .json-error-message {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 8px;
      padding: 8px 12px;
      background: var(--el-color-danger-light-9);
      border: 1px solid var(--el-color-danger-light-7);
      border-radius: 4px;
      color: var(--el-color-danger);
      font-size: 12px;
    }
    
    .json-success-message {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 8px;
      padding: 8px 12px;
      background: var(--el-color-success-light-9);
      border: 1px solid var(--el-color-success-light-7);
      border-radius: 4px;
      color: var(--el-color-success);
      font-size: 12px;
    }
  }
}
</style>
