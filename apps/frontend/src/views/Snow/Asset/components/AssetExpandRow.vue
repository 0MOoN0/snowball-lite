<template>
  <div class="asset-expand-row">
    <el-skeleton v-if="loading" :rows="3" animated />
    <div v-else-if="assetDetail" class="asset-detail">
      <!-- 基本信息 -->
      <el-descriptions title="基本信息" :column="3" border>
        <el-descriptions-item label="资产名称">{{ assetDetail.assetName }}</el-descriptions-item>
        <el-descriptions-item label="资产代码">{{ assetDetail.assetCode }}</el-descriptions-item>
        <el-descriptions-item label="简称">{{ assetDetail.assetShortCode }}</el-descriptions-item>
        <el-descriptions-item label="资产类型">{{ getAssetTypeLabel(assetDetail.assetType) }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ getAssetStatusLabel(assetDetail.assetStatus) }}</el-descriptions-item>
        <el-descriptions-item label="货币">{{ getCurrencyLabel(assetDetail.currency) }}</el-descriptions-item>
        <el-descriptions-item label="市场">{{ getMarketLabel(assetDetail.market) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(assetDetail.createTime, 'YYYY-MM-DD HH:mm:ss')
          }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(assetDetail.updateTime, 'YYYY-MM-DD HH:mm:ss')
          }}</el-descriptions-item>
      </el-descriptions>

      <!-- 基金信息 (asset_type=1,4,5) -->
      <el-descriptions v-if="isFundType" title="基金信息" :column="3" border class="mt-4">
        <el-descriptions-item v-if="assetDetail.fundType" label="基金类型">{{ assetDetail.fundType }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.tradingMode" label="交易模式">{{ assetDetail.tradingMode
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.fundCompany" label="基金公司">{{ assetDetail.fundCompany
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.fundManager" label="基金经理">{{ assetDetail.fundManager
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.establishmentDate" label="成立日期">{{ assetDetail.establishmentDate
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.fundScale" label="基金规模">{{ assetDetail.fundScale
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.fundStatus !== undefined" label="基金状态">{{ assetDetail.fundStatus
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.investmentObjective" label="投资目标">{{ assetDetail.investmentObjective
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.investmentStrategy" label="投资策略">{{ assetDetail.investmentStrategy
          }}</el-descriptions-item>
      </el-descriptions>

      <!-- ETF特有信息 (asset_type=4) -->
      <el-descriptions v-if="isETFType" title="ETF信息" :column="3" border class="mt-4">
        <el-descriptions-item v-if="assetDetail.trackingIndexCode" label="跟踪指数代码">{{ assetDetail.trackingIndexCode
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.trackingIndexName" label="跟踪指数名称">{{ assetDetail.trackingIndexName
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.indexId" label="指数ID">{{ assetDetail.indexId }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.primaryExchange" label="主要交易所">{{ assetDetail.primaryExchange
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.dividendFrequency" label="分红频率">{{ assetDetail.dividendFrequency
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.trackingError" label="跟踪误差">{{ assetDetail.trackingError
          }}%</el-descriptions-item>
      </el-descriptions>

      <!-- LOF特有信息 (asset_type=5) -->
      <el-descriptions v-if="isLOFType" title="LOF信息" :column="3" border class="mt-4">
        <el-descriptions-item v-if="assetDetail.listingExchange" label="上市交易所">{{ assetDetail.listingExchange
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.subscriptionFeeRate" label="申购费率">{{ assetDetail.subscriptionFeeRate
          }}%</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.redemptionFeeRate" label="赎回费率">{{ assetDetail.redemptionFeeRate
          }}%</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.navCalculationTime" label="净值计算时间">{{ assetDetail.navCalculationTime
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.tradingSuspensionInfo" label="交易状态">{{ assetDetail.tradingSuspensionInfo
          }}</el-descriptions-item>
        <el-descriptions-item v-if="assetDetail.indexId" label="指数ID">{{ assetDetail.indexId }}</el-descriptions-item>
      </el-descriptions>
    </div>
    <div v-else class="error-message">
      <el-alert title="加载失败" type="error" description="无法获取资产详情" show-icon />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElDescriptions, ElDescriptionsItem, ElSkeleton, ElAlert } from 'element-plus'
import { getById } from '@/api/snow/asset/AssetApi'
import { useEnum } from '@/hooks/web/useEnum'
import { formatTime } from '@/utils'

interface Props {
  assetId: number
}

const props = defineProps<Props>()

const loading = ref(false)
const assetDetail = ref<any>(null)

// 枚举相关
const { getLabel: getAssetTypeLabel, enumData: assetTypeEnum, loadEnum: loadAssetTypeEnum } = useEnum('AssetTypeEnum')
const { getLabel: getCurrencyLabel } = useEnum('CurrencyEnum')
const { getLabel: getMarketLabel } = useEnum('MarketEnum')
const { getLabel: getAssetStatusLabel } = useEnum('AssetStatusEnum')

// 计算属性 - 根据资产类型判断显示哪些信息区块
const isFundType = computed(() => {
  if (!assetDetail.value || !assetTypeEnum.value) return false
  // 基金类型：普通基金、ETF基金、LOF基金
  const fundTypes = assetTypeEnum.value
    .filter(item => ['基金', 'ETF基金', 'LOF基金'].includes(item.label))
    .map(item => item.value)
  return fundTypes.includes(assetDetail.value.assetType)
})

const isETFType = computed(() => {
  if (!assetDetail.value || !assetTypeEnum.value) return false
  // ETF基金特有字段
  const etfType = assetTypeEnum.value.find(item => item.label === 'ETF基金')
  return etfType && assetDetail.value.assetType === etfType.value
})

const isLOFType = computed(() => {
  if (!assetDetail.value || !assetTypeEnum.value) return false
  // LOF基金特有字段
  const lofType = assetTypeEnum.value.find(item => item.label === 'LOF基金')
  return lofType && assetDetail.value.assetType === lofType.value
})

// 获取资产状态标签类型
const getAssetStatusTagType = (status: number) => {
  switch (status) {
    case 0:
      return 'success' // 活跃
    case 1:
      return 'danger' // 退市
    default:
      return 'info'
  }
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return formatTime(new Date(dateTime), 'YYYY-MM-DD HH:mm:ss')
}

// 懒加载获取资产详情
const loadAssetDetail = async () => {
  if (!props.assetId) return

  loading.value = true
  try {
    const response = await getById(props.assetId)
    if (response && response.success) {
      assetDetail.value = response.data
    }
  } catch (error) {
    console.error('获取资产详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  try {
    // 先加载枚举数据
    await loadAssetTypeEnum()
    // 再加载资产详情
    await loadAssetDetail()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
})
</script>

<style scoped lang="less">
.asset-expand-row {
  padding: 20px;
  background-color: #fafafa;
  border-radius: 4px;

  .asset-detail {
    .mt-4 {
      margin-top: 16px;
    }
  }

  .no-data {
    text-align: center;
    padding: 40px 0;
  }
}

:deep(.el-descriptions__title) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-descriptions__body) {
  .el-descriptions__table {
    .el-descriptions__cell {
      padding: 12px 15px;
    }
  }
}

:deep(.dark .asset-expand-row) {
  background-color: #1e1e1e;
  border-color: #333;
}

:deep(.dark .asset-expand-row .el-descriptions__title) {
  color: #f3f4f6;
}

:deep(.dark .asset-expand-row .el-descriptions--border .el-descriptions__cell) {
  border-color: #404040;
}

:deep(.dark .asset-expand-row .el-descriptions__label) {
  color: #9ca3af;
}

:deep(.dark .asset-expand-row .el-descriptions__content) {
  color: #e5e7eb;
}
</style>
