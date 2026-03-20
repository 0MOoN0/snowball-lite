<script setup lang="ts">
import { CountTo } from '@/components/CountTo'
import { useDesign } from '@/hooks/web/useDesign'
import { useI18n } from '@/hooks/web/useI18n'
import { ElCard, ElCol, ElRow, ElSkeleton } from 'element-plus'
import { reactive, ref } from 'vue'
import { getGridStrategySummaryApi, getOverallTradeAnalysisApi } from '@/api/dashboard/analysis'
import type { AnalysisTotalTypes } from '@/api/dashboard/analysis/types'

const { t } = useI18n()

const { getPrefixCls } = useDesign()

const prefixCls = getPrefixCls('panel')

const loading = ref(false)

let totalState = reactive<AnalysisTotalTypes>({
  users: 0,
  messages: 0,
  moneys: 0,
  shoppings: 0,
  recordDate: '',
  gridRecordDate: ''
})

const formatDate = (date: string) => {
  if (!date) return ''
  return date.split(' ')[0]
}

const getCount = async () => {
  const res = await getGridStrategySummaryApi()
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
  if (res && res.data) {
    totalState.users = res.data.estimateMaximumOccupancy / 10000
    totalState.gridRecordDate = formatDate(res.data.recordDate)
  }

  const overallRes = await getOverallTradeAnalysisApi()
    .catch(() => {})
  if (overallRes && overallRes.data) {
    totalState.messages = overallRes.data.presentValue / 100
    totalState.moneys = overallRes.data.profit / 100
    totalState.shoppings = overallRes.data.investmentYield / 10000
    totalState.recordDate = formatDate(overallRes.data.recordDate)
  }
}

getCount()
</script>

<template>
  <ElRow :gutter="20" justify="space-between" :class="prefixCls">
    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div :class="`${prefixCls}__item flex justify-between`">
              <div>
                <div
                  :class="`${prefixCls}__item--icon ${prefixCls}__item--peoples p-16px inline-block rounded-6px`"
                >
                  <Icon icon="svg-icon:money" :size="40" />
                </div>
              </div>
              <div class="flex flex-col justify-between">
                <div :class="`${prefixCls}__item--text text-16px text-gray-500 text-right`">{{
                  t('analysis.estimateMaximumOccupancy')
                }}</div>
                <CountTo
                  class="text-20px font-700 text-right"
                  :start-val="0"
                  :end-val="totalState.users"
                  :duration="2600"
                />
                <div class="text-12px text-gray-400 text-right mt-1">{{
                  totalState.gridRecordDate
                }}</div>
              </div>
            </div>
          </template>
        </ElSkeleton>
      </ElCard>
    </ElCol>

    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div :class="`${prefixCls}__item flex justify-between`">
              <div>
                <div
                  :class="`${prefixCls}__item--icon ${prefixCls}__item--message p-16px inline-block rounded-6px`"
                >
                  <Icon icon="svg-icon:money" :size="40" />
                </div>
              </div>
              <div class="flex flex-col justify-between">
                <div :class="`${prefixCls}__item--text text-16px text-gray-500 text-right`">{{
                  t('analysis.fundPresentValue')
                }}</div>
                <CountTo
                  class="text-20px font-700 text-right"
                  :start-val="0"
                  :end-val="totalState.messages"
                  :duration="2600"
                  :decimals="2"
                />
                <div class="text-12px text-gray-400 text-right mt-1">{{ totalState.recordDate }}</div>
              </div>
            </div>
          </template>
        </ElSkeleton>
      </ElCard>
    </ElCol>

    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div :class="`${prefixCls}__item flex justify-between`">
              <div>
                <div
                  :class="`${prefixCls}__item--icon ${prefixCls}__item--money p-16px inline-block rounded-6px`"
                >
                  <Icon icon="svg-icon:chart" :size="40" />
                </div>
              </div>
              <div class="flex flex-col justify-between">
                <div :class="`${prefixCls}__item--text text-16px text-gray-500 text-right`">{{
                  t('analysis.totalProfit')
                }}</div>
                <CountTo
                  class="text-20px font-700 text-right"
                  :start-val="0"
                  :end-val="totalState.moneys"
                  :duration="2600"
                  :decimals="2"
                />
                <div class="text-12px text-gray-400 text-right mt-1">{{ totalState.recordDate }}</div>
              </div>
            </div>
          </template>
        </ElSkeleton>
      </ElCard>
    </ElCol>

    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
      <ElCard shadow="hover" class="mb-20px">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div :class="`${prefixCls}__item flex justify-between`">
              <div>
                <div
                  :class="`${prefixCls}__item--icon ${prefixCls}__item--shopping p-16px inline-block rounded-6px`"
                >
                  <Icon icon="svg-icon:trend" :size="40" />
                </div>
              </div>
              <div class="flex flex-col justify-between">
                <div :class="`${prefixCls}__item--text text-16px text-gray-500 text-right`">{{
                  t('analysis.investmentYield')
                }}</div>
                <CountTo
                  class="text-20px font-700 text-right"
                  :start-val="0"
                  :end-val="totalState.shoppings"
                  :duration="2600"
                  :decimals="2"
                  suffix="%"
                />
                <div class="text-12px text-gray-400 text-right mt-1">{{ totalState.recordDate }}</div>
              </div>
            </div>
          </template>
        </ElSkeleton>
      </ElCard>
    </ElCol>
  </ElRow>
</template>

<style lang="less" scoped>
@prefix-cls: ~'@{namespace}-panel';

.@{prefix-cls} {
  &__item {
    &--peoples {
      color: #40c9c6;
    }

    &--message {
      color: #36a3f7;
    }

    &--money {
      color: #f4516c;
    }

    &--shopping {
      color: #34bfa3;
    }

    &:hover {
      :deep(.@{namespace}-icon) {
        color: #fff !important;
      }
      .@{prefix-cls}__item--icon {
        transition: all 0.38s ease-out;
      }
      .@{prefix-cls}__item--peoples {
        background: #40c9c6;
      }
      .@{prefix-cls}__item--message {
        background: #36a3f7;
      }
      .@{prefix-cls}__item--money {
        background: #f4516c;
      }
      .@{prefix-cls}__item--shopping {
        background: #34bfa3;
      }
    }
  }
}
</style>
