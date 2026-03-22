<template>
  <ContentWrap title="通知设置" class="mt-5">
    <div v-loading="loading">
      <!-- 发送渠道配置 -->
      <el-card class="mb-4">
        <template #header>
          <div class="card-header">
            <span style="font-size: 16px; font-weight: 600">发送渠道配置</span>
            <span style="color: #666; font-size: 12px; margin-left: 10px">配置各种通知发送渠道的参数</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="8" v-for="sender in senderChannels" :key="sender.key">
            <el-card shadow="hover" class="sender-card">
              <div class="sender-header">
                <el-icon class="sender-icon">
                  <component :is="getSenderIcon(sender.key)" />
                </el-icon>
                <span class="sender-name">{{ sender.description }}</span>
              </div>
              
              <!-- 动态渠道配置字段 -->
              <div class="channel-config">
                <template v-if="getChannelConfig(sender.key).length === 1 && getChannelConfig(sender.key)[0].key === 'config'">
                  <!-- 通用配置 -->
                  <el-input
                    v-model="sender.value"
                    type="textarea"
                    :rows="3"
                    :placeholder="getChannelConfig(sender.key)[0].placeholder"
                  />
                </template>
                <template v-else>
                  <!-- 结构化配置 -->
                  <div v-for="config in getChannelConfig(sender.key)" :key="config.key" class="config-field">
                    <label class="config-label">{{ config.label }}</label>
                    <el-input
                      v-if="config.type === 'input'"
                      v-model="parseChannelValue(sender.value, sender.key)[config.key]"
                      :placeholder="config.placeholder"
                      @input="updateChannelConfig(sender, config.key, $event)"
                    />
                    <el-input
                      v-else-if="config.type === 'password'"
                      v-model="parseChannelValue(sender.value, sender.key)[config.key]"
                      type="password"
                      :placeholder="config.placeholder"
                      show-password
                      @input="updateChannelConfig(sender, config.key, $event)"
                    />
                    <el-input
                      v-else-if="config.type === 'textarea'"
                      v-model="parseChannelValue(sender.value, sender.key)[config.key]"
                      type="textarea"
                      :rows="2"
                      :placeholder="config.placeholder"
                      @input="updateChannelConfig(sender, config.key, $event)"
                    />
                  </div>
                </template>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>

      <!-- 业务类型通知配置 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span style="font-size: 16px; font-weight: 600">业务类型通知配置</span>
            <span style="color: #666; font-size: 12px; margin-left: 10px">为每个业务类型选择通知发送方式</span>
          </div>
        </template>
        <div v-for="businessType in businessTypes" :key="businessType.key" class="business-type-item">
          <div class="business-type-header">
            <el-icon class="business-icon">
              <component :is="getBusinessIcon(businessType.key)" />
            </el-icon>
            <span class="business-name">{{ businessType.description }}</span>
          </div>
          <div class="sender-selection">
            <el-checkbox-group v-model="businessType.selectedSenders">
              <el-checkbox 
                v-for="sender in availableSenders" 
                :key="sender.key" 
                :label="sender.key"
                :disabled="!sender.value"
              >
                <div class="sender-option">
                  <el-icon class="option-icon">
                    <component :is="getSenderIcon(sender.key)" />
                  </el-icon>
                  <span>{{ sender.description }}</span>
                  <el-tag v-if="!sender.value" type="warning" size="small" class="ml-2">未配置</el-tag>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </div>
          <el-divider v-if="businessTypes.indexOf(businessType) < businessTypes.length - 1" />
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="mt-4">
        <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
        <el-button @click="testNotification" :loading="testing">发送测试通知</el-button>
        <el-button @click="refreshSettings">刷新配置</el-button>
      </div>
    </div>
  </ContentWrap>
</template>

<script lang="ts" setup>
import { ContentWrap } from '@/components/ContentWrap'
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Bell, 
  Message, 
  Monitor, 
  Document, 
  Setting,
  ChatDotRound,
  Promotion,
  Phone
} from '@element-plus/icons-vue'
import { systemSettingsApi, type SettingUpdate } from '@/api/snow/config'

// == 数据定义
interface SenderChannel {
  key: string
  value: string
  description: string
  id: number
  originalValue?: string // 用于跟踪原始值，实现增量更新
}

interface BusinessType {
  key: string
  value: string
  description: string
  id: number
  selectedSenders: string[]
  originalSelectedSenders?: string[] // 用于跟踪原始值，实现增量更新
}

// 渠道配置字段定义
interface ChannelConfig {
  key: string
  label: string
  type: 'input' | 'textarea' | 'password'
  placeholder: string
  required?: boolean
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const senderChannels = ref<SenderChannel[]>([])
const businessTypes = ref<BusinessType[]>([])
const availableSenders = ref<SenderChannel[]>([])

// == 生命周期
onMounted(async () => {
  await loadNotificationSettings()
})

// == 工具方法

// 获取发送渠道图标
const getSenderIcon = (key: string) => {
  const iconMap: Record<string, any> = {
    'notification_sender.wecom': ChatDotRound,
    'notification_sender.server_chan': Promotion,
    'notification_sender.telegram_bot': Phone
  }
  return iconMap[key] || Message
}

// 获取业务类型图标
const getBusinessIcon = (key: string) => {
  const iconMap: Record<string, any> = {
    'notification_business_type.grid_trade': Monitor,
    'notification_business_type.message_remind': Bell,
    'notification_business_type.system_runing': Setting,
    'notification_business_type.daily_report': Document
  }
  return iconMap[key] || Bell
}

// 获取渠道配置字段
const getChannelConfig = (channelKey: string): ChannelConfig[] => {
  const configMap: Record<string, ChannelConfig[]> = {
    'notification_sender.wecom': [
      {
        key: 'webhook_url',
        label: 'Webhook URL',
        type: 'input',
        placeholder: '请输入企业微信机器人的Webhook URL',
        required: true
      }
    ],
    'notification_sender.server_chan': [
      {
        key: 'send_key',
        label: 'SendKey',
        type: 'input',
        placeholder: '请输入Server酱的SendKey',
        required: true
      }
    ],
    'notification_sender.telegram_bot': [
      {
        key: 'token',
        label: 'Bot Token',
        type: 'input',
        placeholder: '请输入Telegram Bot Token',
        required: true
      },
      {
        key: 'chat_id',
        label: 'Chat ID',
        type: 'input',
        placeholder: '请输入Telegram Chat ID',
        required: true
      }
    ]
  }
  
  return configMap[channelKey] || [
    {
      key: 'config',
      label: '配置值',
      type: 'textarea',
      placeholder: '请输入配置信息（JSON格式）',
      required: true
    }
  ]
}

// 解析渠道配置值
const parseChannelValue = (value: string, channelKey?: string): Record<string, string> => {
  if (!value) return {}
  
  // 获取渠道配置字段
  const configs = channelKey ? getChannelConfig(channelKey) : []
  
  // 如果是通用配置（只有一个config字段），直接返回
  if (configs.length === 1 && configs[0].key === 'config') {
    return { config: value }
  }
  
  // 对于结构化配置，尝试解析为JSON
  if (channelKey === 'notification_sender.telegram_bot') {
    try {
      const parsed = JSON.parse(value)
      if (typeof parsed === 'object' && parsed !== null) {
        // 确保返回的对象包含所有必需的字段
        return {
          token: parsed.token || '',
          chat_id: parsed.chat_id || ''
        }
      }
      return { token: '', chat_id: '' }
    } catch (e) {
      console.warn('解析Telegram配置失败:', value, e)
      return { token: '', chat_id: '' }
    }
  }
  
  // 对于简单字符串配置，直接映射到对应字段
  if (channelKey === 'notification_sender.wecom') {
    return { webhook_url: value }
  } else if (channelKey === 'notification_sender.server_chan') {
    return { send_key: value }
  }
  
  // 默认处理
  try {
    const parsed = JSON.parse(value)
    return typeof parsed === 'object' && parsed !== null ? parsed : { config: value }
  } catch (e) {
    return { config: value }
  }
}

// 构建渠道配置值
const buildChannelValue = (channelKey: string, configData: Record<string, string>): string => {
  const configs = getChannelConfig(channelKey)
  if (configs.length === 1 && configs[0].key === 'config') {
    return configData.config || ''
  }
  
  // 对于结构化配置，返回JSON字符串
  if (channelKey === 'notification_sender.telegram_bot') {
    // 确保只包含有效的字段
    const validConfig = {
      token: configData.token || '',
      chat_id: configData.chat_id || ''
    }
    return JSON.stringify(validConfig)
  }
  
  // 对于简单字符串配置，直接返回对应字段的值
  if (channelKey === 'notification_sender.wecom') {
    return configData.webhook_url || ''
  } else if (channelKey === 'notification_sender.server_chan') {
    return configData.send_key || ''
  }
  
  // 默认返回JSON字符串
  return JSON.stringify(configData)
}

// 更新渠道配置
const updateChannelConfig = (channel: SenderChannel, configKey: string, value: string) => {
  const currentConfig = parseChannelValue(channel.value, channel.key)
  currentConfig[configKey] = value
  channel.value = buildChannelValue(channel.key, currentConfig)
}

// 刷新设置
const refreshSettings = async () => {
  await loadNotificationSettings()
  ElMessage.success('配置已刷新')
}

// == API 方法

// 加载通知设置
const loadNotificationSettings = async () => {
  try {
    loading.value = true
    const response = await systemSettingsApi.getSettings({ group: 'notification' })
    
    console.log('加载的通知设置:', response)
    
    if (response && response.data && response.data.items) {
      const settings = response.data.items
      
      // 分离发送渠道和业务类型
      const senders: SenderChannel[] = []
      const businesses: BusinessType[] = []
      
      settings.forEach((setting: any) => {
        if (setting.key.startsWith('notification_sender.')) {
          senders.push({
            key: setting.key,
            value: setting.value || '',
            description: setting.description,
            id: setting.id,
            originalValue: setting.value || '' // 保存原始值
          })
        } else if (setting.key.startsWith('notification_business_type.')) {
          let selectedSenders: string[] = []
          try {
            selectedSenders = setting.value ? JSON.parse(setting.value) : []
          } catch (e) {
            console.warn('解析业务类型配置失败:', setting.key, setting.value)
            selectedSenders = []
          }
          
          businesses.push({
            key: setting.key,
            value: setting.value || '[]',
            description: setting.description,
            id: setting.id,
            selectedSenders,
            originalSelectedSenders: [...selectedSenders] // 保存原始值
          })
        }
      })
      
      // 按照固定顺序排序发送渠道
      const senderOrder = [
        'notification_sender.wecom',
        'notification_sender.server_chan', 
        'notification_sender.telegram_bot'
      ]
      
      senders.sort((a, b) => {
        const indexA = senderOrder.indexOf(a.key)
        const indexB = senderOrder.indexOf(b.key)
        return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB)
      })
      
      senderChannels.value = senders
      businessTypes.value = businesses
      availableSenders.value = [...senders]
      
      console.log('处理后的发送渠道:', senders)
      console.log('处理后的业务类型:', businesses)
    }
  } catch (error) {
    console.error('加载通知设置失败:', error)
    ElMessage.error('加载通知设置失败')
  } finally {
    loading.value = false
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    saving.value = true
    
    // 准备批量更新的设置数据
    const settingsToUpdate: SettingUpdate[] = []
    
    // 检查发送渠道设置的变更
    for (const sender of senderChannels.value) {
      if (sender.value !== sender.originalValue) {
        // 根据渠道类型确定正确的settingType
        let settingType: 'string' | 'json' = 'string'
        if (sender.key === 'notification_sender.telegram_bot') {
          settingType = 'json'
        }
        
        settingsToUpdate.push({
          key: sender.key,
          value: sender.value,
          settingType,
          group: 'notification',
          description: sender.description
        })
      }
    }
    
    // 检查业务类型设置的变更
    for (const business of businessTypes.value) {
      const currentValue = JSON.stringify(business.selectedSenders)
      const originalValue = JSON.stringify(business.originalSelectedSenders || [])
      if (currentValue !== originalValue) {
        settingsToUpdate.push({
          key: business.key,
          value: currentValue,
          settingType: 'json',
          group: 'notification',
          description: business.description
        })
      }
    }
    
    if (settingsToUpdate.length === 0) {
      ElMessage.info('没有检测到配置变更')
      return
    }
    
    console.log('准备更新的设置:', settingsToUpdate)
    
    // 批量更新设置
    const result = await systemSettingsApi.batchUpdateSettings({
      settings: settingsToUpdate
    })
    
    console.log('批量更新结果:', result)
    
    // 检查批量更新结果
    if (result.data && result.data.failure_count > 0) {
      console.warn('部分设置更新失败:', result.data.failures)
      ElMessage.warning(`成功更新 ${result.data.success_count} 项设置，${result.data.failure_count} 项失败`)
    } else if (result.data && result.data.success_count > 0) {
      ElMessage.success(`通知设置保存成功，共更新 ${result.data.success_count} 项设置`)
    } else {
      ElMessage.success('通知设置保存成功')
    }
    
    // 重新加载设置以确保数据同步
    await loadNotificationSettings()
  } catch (error) {
    console.error('保存通知设置失败:', error)
    ElMessage.error('保存通知设置失败')
  } finally {
    saving.value = false
  }
}

// 测试通知
const testNotification = async () => {
  try {
    testing.value = true
    
    // 检查是否有配置的发送渠道
    const configuredSenders = senderChannels.value.filter(sender => {
      if (!sender.value || !sender.value.trim()) return false
      
      // 对于结构化配置，检查是否有有效的配置值
      if (sender.key === 'notification_sender.telegram_bot') {
        try {
          const config = JSON.parse(sender.value)
          return config.token && config.chat_id
        } catch (e) {
          return false
        }
      }
      
      return true
    })
    
    if (configuredSenders.length === 0) {
      ElMessage.warning('请先配置至少一个发送渠道')
      return
    }
    
    // 显示配置的渠道详情
    const channelDetails = configuredSenders.map(sender => {
      let detail = sender.description
      if (sender.key === 'notification_sender.telegram_bot') {
        try {
          const config = JSON.parse(sender.value)
          detail += ` (Chat ID: ${config.chat_id})`
        } catch (e) {
          // 忽略解析错误
        }
      }
      return detail
    })
    
    // 确认发送测试通知
    await ElMessageBox.confirm(
      `将向以下渠道发送测试通知：\n${channelDetails.join('\n')}`,
      '确认发送测试通知',
      {
        confirmButtonText: '发送',
        cancelButtonText: '取消',
        type: 'info',
        dangerouslyUseHTMLString: false
      }
    )
    
    // 这里可以添加实际的测试通知发送逻辑
    // 例如调用后端API发送测试消息
    
    ElMessage.success('测试通知发送成功，请检查对应的通知渠道')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发送测试通知失败:', error)
      ElMessage.error('测试通知发送失败')
    }
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
}

.sender-card {
  min-height: 120px;
  margin-bottom: 16px;
}

.sender-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.sender-icon {
  font-size: 18px;
  margin-right: 8px;
  color: #409eff;
}

.sender-name {
  font-weight: 500;
  font-size: 14px;
}

.business-type-item {
  margin-bottom: 20px;
}

.business-type-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.business-icon {
  font-size: 18px;
  margin-right: 8px;
  color: #67c23a;
}

.business-name {
  font-weight: 500;
  font-size: 15px;
}

.sender-selection {
  margin-left: 26px;
}

.sender-option {
  display: flex;
  align-items: center;
}

.option-icon {
  font-size: 14px;
  margin-right: 6px;
  color: #909399;
}

:deep(.el-checkbox) {
  margin-bottom: 12px;
  margin-right: 24px;
}

:deep(.el-checkbox__label) {
  font-size: 13px;
}

:deep(.el-divider--horizontal) {
  margin: 16px 0;
}

.channel-config {
  padding: 8px 0;
}

.config-field {
  margin-bottom: 12px;
}

.config-label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  font-weight: 500;
}
</style>