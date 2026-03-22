<template>
  <div class="index-expand-row">
    <el-skeleton v-if="loading" :rows="6" animated />
    <div v-else-if="detail" class="index-detail">
      <!-- 基本信息 -->
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="指数名称">{{ detail.indexName }}</el-descriptions-item>
        <el-descriptions-item label="指数代码">
          <el-link :href="'https://xueqiu.com/S/' + detail.indexCode" target="_blank" type="primary" :underline="false">
            {{ detail.indexCode }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="指数类型">{{ getIndexTypeLabel(Number(detail.indexType)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="投资策略">{{ getInvestmentStrategyLabel(Number(detail.investmentStrategy)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="市场">{{ getMarketLabel(Number(detail.market)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="货币">{{ getCurrencyLabel(Number(detail.currency)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="权重方法">{{ getWeightMethodLabel(Number(detail.weightMethod)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="计算方法">{{ getCalculationMethodLabel(Number(detail.calculationMethod)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ getIndexStatusLabel(Number(detail.indexStatus)) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="基准日期">{{ detail.baseDate || '-' }}</el-descriptions-item>
        <el-descriptions-item label="基准点数">{{ detail.basePoint ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="发布机构">{{ detail.publisher || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发布日期">{{ detail.publishDate || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.createTime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detail.updateTime || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 仅基础指数显示的统计信息 -->
      <el-descriptions class="mt-4" v-if="detail.indexType === 0" title="统计信息" :column="2" border>
        <el-descriptions-item label="成分股数量">{{ detail.constituentCount ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="总市值（万元）">{{ detail.marketCap ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="自由流通市值（万元）">{{ detail.freeFloatMarketCap ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="平均市盈率">{{ detail.averagePe ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="平均市净率">{{ detail.averagePb ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="股息率（%）">{{ detail.dividendYield ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="换手率（%）">{{ detail.turnoverRate ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="波动率（%）">{{ detail.volatility ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="贝塔系数">{{ detail.beta ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="调仓频率">{{ detail.rebalanceFrequency ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="最后调仓日期">{{ detail.lastRebalanceDate ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="下次调仓日期">{{ detail.nextRebalanceDate ?? '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 指数描述 -->
      <el-descriptions class="mt-4" :column="1" border>
        <el-descriptions-item label="指数描述">
          <div class="desc-text">{{ detail.description || '暂无描述' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </div>
    <div v-else class="error-message">
      <el-alert title="加载失败" type="error" description="无法获取指数详情" show-icon />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElSkeleton, ElAlert, ElDescriptions, ElDescriptionsItem, ElLink } from 'element-plus'
import { getIndexDetail } from '@/api/snow/index/IndexApi'
import { useEnum } from '@/hooks/web/useEnum'

interface Props {
  indexId: number
}

const props = defineProps<Props>()

const loading = ref(false)
const detail = ref<Recordable | null>(null)

// 枚举 hooks，用于显示中文标签
const { loadEnum: loadIndexTypeEnum, getLabel: getIndexTypeLabel } = useEnum('IndexTypeEnum')
const { loadEnum: loadInvestmentStrategyEnum, getLabel: getInvestmentStrategyLabel } = useEnum('InvestmentStrategyEnum')
const { loadEnum: loadCurrencyEnum, getLabel: getCurrencyLabel } = useEnum('CurrencyEnum')
const { loadEnum: loadMarketEnum, getLabel: getMarketLabel } = useEnum('MarketEnum')
const { loadEnum: loadIndexStatusEnum, getLabel: getIndexStatusLabel } = useEnum('IndexStatusEnum')
const { loadEnum: loadWeightMethodEnum, getLabel: getWeightMethodLabel } = useEnum('WeightMethodEnum')
const { loadEnum: loadCalculationMethodEnum, getLabel: getCalculationMethodLabel } = useEnum('CalculationMethodEnum')

const loadEnums = async () => {
  try {
    await Promise.all([
      loadIndexTypeEnum(),
      loadInvestmentStrategyEnum(),
      loadCurrencyEnum(),
      loadMarketEnum(),
      loadIndexStatusEnum(),
      loadWeightMethodEnum(),
      loadCalculationMethodEnum()
    ])
  } catch (e) {
    // 枚举加载失败不阻塞详情显示
    console.warn('枚举加载失败', e)
  }
}

const fetchDetail = async () => {
  if (!props.indexId) return
  loading.value = true
  try {
    const resp = await getIndexDetail({ id: props.indexId })
    if (resp.success && resp.data) {
      detail.value = resp.data
    } else {
      detail.value = null
    }
  } catch (e) {
    console.error('获取指数详情失败:', e)
    detail.value = null
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadEnums()
  await fetchDetail()
})
</script>

<style scoped lang="less">
.index-expand-row {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
  border: 1px solid var(--el-border-color-light);

  .index-detail {
    .mt-4 {
      margin-top: 16px;
    }
  }
}

.desc-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

:deep(.el-descriptions__title) {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

:deep(.el-descriptions__body) {
  .el-descriptions__table {
    .el-descriptions__cell {
      padding: 12px 15px;
      background-color: var(--el-bg-color);
      color: var(--el-text-color-regular);
      border-color: var(--el-border-color-light);
    }
  }
}
</style>