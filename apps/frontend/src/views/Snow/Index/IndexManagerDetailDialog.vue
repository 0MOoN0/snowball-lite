<template>
  <Dialog
    v-model="dialogShow"
    title="指数详情"
    width="800px"
    @close="closeDialog"
    class="index-detail-dialog"
  >
    <div class="detail-container">
      <div v-if="loading" class="loading-wrap">
        <el-skeleton :rows="8" animated />
      </div>
      <div v-else>
        <el-descriptions :column="2" border>
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
          <el-descriptions-item label="权重方法">{{ getWeightMethodLabel(detail.weightMethod) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="计算方法">{{ getCalculationMethodLabel(detail.calculationMethod) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getIndexStatusLabel(detail.indexStatus) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发布机构">{{ detail.publisher || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发布日期">{{ detail.publishDate || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detail.createTime || '-' }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ detail.updateTime || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="mt-4" v-if="detail.indexType === 0">
          <el-descriptions :column="2" border>
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
        </div>
        <div class="mt-4">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="指数描述">
              <div class="desc-text">{{ detail.description || '暂无描述' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeDialog">关闭</el-button>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { ElMessage } from 'element-plus'
import { computed, ref, watch } from 'vue'
import { getIndexDetail } from '@/api/snow/index/IndexApi'
import { useEnum } from '@/hooks/web/useEnum'

interface Props {
  dialogVisible: boolean
  indexId?: number | null
}

const emit = defineEmits(['update:dialogVisible', 'closeDialog'])

const props = withDefaults(defineProps<Props>(), {
  dialogVisible: false,
  indexId: null
})

const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (value: boolean) => emit('update:dialogVisible', value)
})

const loading = ref(false)
const detail = ref<Recordable>({})

// 枚举 hooks
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

const fetchDetail = async (id: number) => {
  try {
    loading.value = true
    const resp = await getIndexDetail({ id })
    if (!resp.success || !resp.data) {
      ElMessage.error(resp.message || '获取指数详情失败')
      return
    }
    detail.value = resp.data
  } catch (error) {
    console.error('获取指数详情失败:', error)
    ElMessage.error('获取指数详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

watch(
  () => props.dialogVisible,
  async (show) => {
    if (show && props.indexId) {
      await loadEnums()
      await fetchDetail(props.indexId)
    }
  }
)

const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}
</script>

<style scoped>
.index-detail-dialog {
  :deep(.el-dialog) {
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    background-color: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
  }

  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    background: linear-gradient(135deg, #5c6bc0 0%, #8e24aa 100%);
    color: white;
    border-radius: 12px 12px 0 0;

    .el-dialog__title {
      color: white;
      font-weight: 600;
      font-size: 16px;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
    background-color: var(--el-bg-color-page);
    min-height: 320px;
  }

  :deep(.el-dialog__footer) {
    padding: 16px 24px 20px;
    background-color: var(--el-bg-color);
    border-radius: 0 0 12px 12px;
    border-top: 1px solid var(--el-border-color-light);
  }
}

.detail-container {
  position: relative;
}

.loading-wrap {
  padding: 12px;
}

.desc-text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>