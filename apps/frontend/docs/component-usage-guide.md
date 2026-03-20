# Snow View 项目组件使用指南

本文档详细介绍了 Snow View 项目中核心封装组件的使用方法，以配置管理模块为例，展示各组件的实际应用场景和最佳实践。

## 目录

- [ContentWrap 内容包装组件](#contentwrap-内容包装组件)
- [Dialog 对话框组件](#dialog-对话框组件)
- [Table 表格组件](#table-表格组件)
- [Icon 图标组件](#icon-图标组件)
- [useTable Hook](#usetable-hook)
- [完整示例](#完整示例)
- [最佳实践](#最佳实践)

## ContentWrap 内容包装组件

### 组件概述

`ContentWrap` 是基于 Element Plus 的 `ElCard` 封装的内容包装组件，提供统一的页面内容容器样式。

### 基本用法

```vue
<template>
  <ContentWrap>
    <!-- 页面内容 -->
    <div class="your-content">
      <!-- 内容区域 -->
    </div>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ContentWrap } from '@/components/ContentWrap'
</script>
```

### 带标题和提示的用法

```vue
<template>
  <ContentWrap 
    title="系统配置管理" 
    message="管理系统设置项和配置分组的详细说明"
  >
    <!-- 页面内容 -->
  </ContentWrap>
</template>
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | '' | 卡片标题 |
| message | string | '' | 标题旁的提示信息，显示为问号图标 |

### 特性

- 自动应用项目统一的设计风格
- 支持标题和提示信息显示
- 基于 `ElCard` 实现，无阴影效果
- 支持插槽内容

## Dialog 对话框组件

### 组件概述

`Dialog` 是基于 Element Plus 的 `ElDialog` 增强封装，提供全屏切换、自适应高度等功能。

### 基本用法

```vue
<template>
  <Dialog 
    v-model="dialogVisible" 
    title="配置项管理" 
    width="600px"
  >
    <!-- 对话框内容 -->
    <el-form :model="form">
      <!-- 表单内容 -->
    </el-form>
    
    <!-- 底部按钮 -->
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Dialog } from '@/components/Dialog'

const dialogVisible = ref(false)
const form = ref({})

const handleSubmit = () => {
  // 提交逻辑
}
</script>
```

### 配置管理中的实际应用

```vue
<template>
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
        <el-input
          v-else
          v-model="configForm.value"
          type="textarea"
          :rows="6"
          placeholder="请输入JSON格式的配置值"
        />
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
    </el-form>
    
    <template #footer>
      <el-button @click="configDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleConfigSubmit">确定</el-button>
    </template>
  </Dialog>
</template>
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | boolean | false | 对话框显示状态 |
| title | string | 'Dialog' | 对话框标题 |
| fullscreen | boolean | true | 是否显示全屏按钮 |
| maxHeight | string/number | '500px' | 最大高度 |

### 特性

- 支持全屏切换功能
- 自适应高度计算
- 可拖拽
- 点击遮罩层不关闭
- 销毁时清理DOM

## Table 表格组件

### 组件概述

`Table` 是基于 Element Plus 的 `ElTable` 增强封装，集成分页、加载状态、插槽等功能。

### 基本用法

```vue
<template>
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
    <!-- 自定义列插槽 -->
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
</template>

<script setup lang="ts">
import { Table } from '@/components/Table'
import { useTable } from '@/hooks/web/useTable'

// 表格列配置
const columns = [
  {
    field: 'key',
    label: '配置项名称',
    width: 200
  },
  {
    field: 'value',
    label: '配置值',
    showOverflowTooltip: true
  },
  {
    field: 'configType',
    label: '配置类型',
    width: 120,
    slots: {
      default: 'configType'
    }
  },
  {
    field: 'status',
    label: '状态',
    width: 80,
    slots: {
      default: 'status'
    }
  },
  {
    field: 'action',
    label: '操作',
    width: 150,
    slots: {
      default: 'action'
    }
  }
]

// 使用 useTable hook
const { tableObject, tableMethods } = useTable({
  getListApi: systemSettingsApi.getSystemSettings,
  response: {
    list: 'list',
    total: 'total'
  }
})

const { register } = tableMethods
</script>
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| columns | Array | [] | 表格列配置 |
| data | Array | [] | 表格数据 |
| loading | boolean | false | 加载状态 |
| pagination | Object | undefined | 分页配置 |
| selection | boolean | true | 是否显示多选 |
| pageSize | number | 10 | 每页条数 |
| currentPage | number | 1 | 当前页 |

### 列配置说明

```typescript
interface TableColumn {
  field: string          // 字段名
  label: string          // 列标题
  width?: number         // 列宽度
  minWidth?: number      // 最小宽度
  fixed?: string         // 固定列
  sortable?: boolean     // 是否可排序
  showOverflowTooltip?: boolean  // 是否显示溢出提示
  slots?: {
    default?: string     // 自定义插槽名
  }
}
```

## Icon 图标组件

### 组件概述

`Icon` 是基于 Iconify 的图标组件，支持丰富的图标库和自定义样式。

### 基本用法

```vue
<template>
  <!-- 基本图标 -->
  <Icon icon="ep:plus" />
  
  <!-- 带样式的图标 -->
  <Icon icon="ep:edit" :size="16" color="#409eff" />
  
  <!-- 在按钮中使用 -->
  <el-button type="primary">
    <Icon icon="ep:plus" class="mr-5px" />
    新增配置项
  </el-button>
  
  <!-- 在表格操作中使用 -->
  <el-button type="text" size="small">
    <Icon icon="ep:edit" class="mr-5px" />
    编辑
  </el-button>
</template>

<script setup lang="ts">
import { Icon } from '@/components/Icon'
</script>
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| icon | string | - | 图标名称 |
| size | number | 16 | 图标大小 |
| color | string | - | 图标颜色 |

### 常用图标

```vue
<!-- Element Plus 图标集 -->
<Icon icon="ep:plus" />        <!-- 加号 -->
<Icon icon="ep:edit" />        <!-- 编辑 -->
<Icon icon="ep:delete" />      <!-- 删除 -->
<Icon icon="ep:search" />      <!-- 搜索 -->
<Icon icon="ep:refresh" />     <!-- 刷新 -->
<Icon icon="ep:setting" />     <!-- 设置 -->
<Icon icon="ep:view" />        <!-- 查看 -->
<Icon icon="ep:download" />    <!-- 下载 -->
<Icon icon="ep:upload" />      <!-- 上传 -->

<!-- 全屏相关 -->
<Icon icon="zmdi:fullscreen" />      <!-- 全屏 -->
<Icon icon="zmdi:fullscreen-exit" /> <!-- 退出全屏 -->
```

## useTable Hook

### Hook 概述

`useTable` 是表格数据管理的组合式函数，提供数据获取、分页、加载状态等功能。

### 基本用法

```typescript
import { useTable } from '@/hooks/web/useTable'
import { systemSettingsApi } from '@/api/snow/config'

// 配置 useTable
const { tableObject, tableMethods } = useTable({
  getListApi: systemSettingsApi.getSystemSettings,
  delListApi: systemSettingsApi.deleteSystemSetting,
  response: {
    list: 'list',
    total: 'total'
  }
})

const { register, getList, setSearchParams } = tableMethods
```

### 配置参数

```typescript
interface UseTableConfig<T = any> {
  getListApi: (option: any) => Promise<IResponse<TableResponse<T>>>  // 获取列表API
  delListApi?: (option: any) => Promise<IResponse>                   // 删除API（可选）
  response: {
    list: string      // 数据列表字段名
    total?: string    // 总数字段名
  }
  props?: TableProps  // 表格属性
}
```

### 返回值说明

```typescript
// tableObject - 响应式表格状态
const tableObject = {
  pageSize: number      // 每页条数
  currentPage: number   // 当前页
  total: number         // 总条数
  tableList: T[]        // 表格数据
  params: any           // 查询参数
  loading: boolean      // 加载状态
  currentRow: T | null  // 当前选中行
}

// tableMethods - 表格操作方法
const tableMethods = {
  register: Function           // 注册表格实例
  getList: Function           // 获取数据
  setSearchParams: Function   // 设置搜索参数
  delList: Function           // 删除数据
  // ... 其他方法
}
```

### 实际应用示例

```vue
<script setup lang="ts">
import { useTable } from '@/hooks/web/useTable'
import { systemSettingsApi, type SettingQueryParams } from '@/api/snow/config'

// 搜索表单
const searchForm = reactive<SettingQueryParams>({
  key: '',
  group: '',
  settingType: '',
  page: 1,
  size: 20
})

// 配置表格
const { tableObject, tableMethods } = useTable({
  getListApi: systemSettingsApi.getSystemSettings,
  response: {
    list: 'list',
    total: 'total'
  }
})

const { register, getList, setSearchParams } = tableMethods

// 搜索处理
function handleSearch() {
  const searchParams: SettingQueryParams = {
    key: searchForm.key?.trim() || '',
    group: searchForm.group?.trim() || '',
    settingType: searchForm.settingType?.trim() || '',
    page: searchForm.page,
    size: searchForm.size
  }
  
  setSearchParams(searchParams)
}

// 删除处理
const handleDelete = async (row: Setting) => {
  try {
    await ElMessageBox.confirm('确定要删除这个配置项吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await systemSettingsApi.deleteSystemSetting(row.id)
    ElMessage.success('删除成功')
    getList() // 刷新列表
  } catch (error) {
    // 处理错误
  }
}
</script>
```

## 组件协作原理

### 工作流程概述

配置管理模块展示了各组件的协作模式：

1. **页面结构**：`ContentWrap` 作为页面容器，提供统一布局
2. **数据管理**：`useTable` Hook 管理表格数据、分页和加载状态
3. **数据展示**：`Table` 组件展示配置列表，支持自定义插槽
4. **交互操作**：`Dialog` 组件处理新增/编辑表单
5. **图标系统**：`Icon` 组件提供统一的图标显示

### 核心实现

```vue
<template>
  <ContentWrap>
    <!-- 搜索区域 -->
    <el-input v-model="searchForm.key" @input="handleSearch">
      <template #prefix><Icon icon="ep:search" /></template>
    </el-input>
    
    <!-- 数据表格 -->
    <Table
      v-model:pageSize="tableObject.pageSize"
      v-model:currentPage="tableObject.currentPage"
      :columns="columns"
      :data="tableObject.tableList"
      :loading="tableObject.loading"
      @register="register"
    >
      <template #action="{ row }">
        <el-button @click="handleEdit(row)">
          <Icon icon="ep:edit" />编辑
        </el-button>
      </template>
    </Table>
    
    <!-- 编辑对话框 -->
    <Dialog v-model="dialogVisible" title="配置管理">
      <el-form :model="form">
        <!-- 表单内容 -->
      </el-form>
    </Dialog>
  </ContentWrap>
</template>

<script setup lang="ts">
// 1. 数据管理
const { tableObject, tableMethods } = useTable({
  getListApi: systemSettingsApi.getSystemSettings,
  response: { list: 'list', total: 'total' }
})

// 2. 表格列配置
const columns = [
  { field: 'key', label: '配置名称' },
  { field: 'value', label: '配置值' },
  { field: 'action', label: '操作', slots: { default: 'action' } }
]

// 3. 事件处理
function handleSearch() {
  setSearchParams({ key: searchForm.key })
}

function handleEdit(row) {
  Object.assign(form, row)
  dialogVisible.value = true
}
</script>
```

### 数据流转

```
用户操作 → useTable Hook → API 调用 → 数据更新 → Table 组件渲染
    ↓
搜索/分页 → setSearchParams → 重新获取数据 → 更新 tableObject
    ↓
编辑操作 → Dialog 显示 → 表单提交 → API 更新 → 刷新列表
```

## 最佳实践

### 1. 组件导入规范

```typescript
// 推荐：从统一入口导入
import { ContentWrap } from '@/components/ContentWrap'
import { Dialog } from '@/components/Dialog'
import { Table } from '@/components/Table'
import { Icon } from '@/components/Icon'

// 避免：直接导入具体文件
// import ContentWrap from '@/components/ContentWrap/src/ContentWrap.vue'
```

### 2. 类型定义

```typescript
// 定义清晰的接口类型
interface SettingQueryParams {
  key?: string
  group?: string
  settingType?: string
  page: number
  size: number
}

interface Setting {
  id: number
  key: string
  value: string
  settingType: string
  group: string
  description?: string
  status: number
  createdAt: string
  updatedAt: string
}
```

### 3. 响应式数据管理

```typescript
// 使用 reactive 管理表单数据
const searchForm = reactive<SettingQueryParams>({
  key: '',
  group: '',
  settingType: '',
  page: 1,
  size: 20
})

// 使用 ref 管理简单状态
const dialogVisible = ref(false)
const loading = ref(false)
```

### 4. 错误处理

```typescript
// 统一的错误处理模式
const handleDelete = async (row: Setting) => {
  try {
    await ElMessageBox.confirm('确定要删除这个配置项吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await systemSettingsApi.deleteSystemSetting(row.id)
    ElMessage.success('删除成功')
    getList() // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('Delete error:', error)
    }
  }
}
```

### 5. 性能优化

- 使用 `computed` 缓存计算结果
- 防抖搜索：`debounce(handleSearch, 300)`
- 大数据虚拟滚动：`:virtual-scroll="list.length > 100"`
- 条件渲染优化：频繁切换用 `v-show`

### 6. 可访问性

- 按钮添加 `aria-label` 属性
- 表单项使用 `aria-describedby` 关联帮助文本
- 合理的标签层次结构

### 7. 国际化支持

```typescript
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
// 使用：{{ t('config.title') }}
```

---

本文档涵盖了 Snow View 项目中主要封装组件的使用方法和最佳实践。通过这些组件的合理使用，可以快速构建功能完整、用户体验良好的管理界面。建议在实际开发中参考本文档的示例代码，并根据具体需求进行调整。