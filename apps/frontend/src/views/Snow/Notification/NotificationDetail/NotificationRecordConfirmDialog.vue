<template>
  <Dialog v-model="dialogShow" :title="props.dialogTitle" center @close="closeDialog">
    <div class="flex justify-center">
      <el-button type="primary" :disabled="currentGridInfoIndex <= 0" @click="changeCurrentGridInfo(-1)"
        >上一个</el-button
      >
      <el-button type="primary" :disabled="currentGridInfoIndex >= gridInfoCount - 1" @click="changeCurrentGridInfo(1)"
        >下一个</el-button
      >
    </div>
    <Descriptions
      :title="currentGridInfo.asset_name"
      :schema="gridInfoDescriptionSchema"
      :data="currentGridInfo"
      class="mt-5"
    />
    <ContentWrap title="网格交易记录" class="mt-5">
      <el-table :data="currentRecord" style="width: 100%">
        <el-table-column type="index" label="序号" width="50" />
        <el-table-column prop="transactionsDate" label="交易日期" width="180">
          <template #default="scope">
            {{ scope.row.transactionsDate }}
          </template>
        </el-table-column>
        <el-table-column prop="transactionsPrice" label="交易价格（元）" width="150" />
        <el-table-column prop="transactionsShare" label="交易份额" width="150" />
        <el-table-column prop="transactionsFee" label="交易费用（元）" width="150" />
        <el-table-column prop="transactionsAmount" label="交易金额（元）" width="150" />
        <el-table-column prop="transactionsDirection" label="交易方向" width="120">
          <template #default="scope">
            <el-tag type="success">{{ scope.row.transactionsDirection === 0 ? '卖出' : '买入' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </ContentWrap>
    <ContentWrap
      title="监控档位变化-亮色"
      class="mt-5"
      message="深色为历史数据，亮色为当前数据。会根据实际条件判断是否需要修改监控档位"
    >
      <Table
        :columns="gridTypeDetailSchema"
        :fit="true"
        :data="currentGridInfo.current_change"
        :default-sort="{ prop: 'gear', order: 'descending' }"
        :row-class-name="tableRowClassName"
      />
    </ContentWrap>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">提交</ElButton>
      <ElButton @click="closeDialog">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { computed, ref, watch } from 'vue'
// 导入Table组件
import { Table } from '@/components/Table'
// 导入ContentWrap组件
import { ContentWrap } from '@/components/ContentWrap'
// 导入描述组件和contentwarp组件
import * as notificationApi from '@/api/snow/Notification/index'
import { GridInfo } from '@/api/snow/Notification/types'
import Descriptions from '@/components/Descriptions/src/Descriptions.vue'
import { ElMessage } from 'element-plus'
import _ from 'lodash'
import { useRoute } from 'vue-router'

// 获取路由参数
const router = useRoute()
const notificationDetailId = router.query.id

const emit = defineEmits(['closeDialog', 'update:dialogVisible', 'submitted'])

// 当前的网格通知详情数据索引
const currentGridInfoIndex = ref<number>(0)

// 当前的网格通知详情数据
const currentGridInfo = ref<GridInfo | any>({})

// 总的网格通知内容条数
const gridInfoCount = ref<number | any>(0)

// 当前网格的交易记录数据
const currentRecord = ref<any[]>([])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false,
  },
  dialogTitle: {
    type: String,
    default: '确认窗口',
  },
  // 要提交的通知数据
  confirmNotificationData: {
    type: Object,
    default: {},
  },
  // 通知详情
  notificationDetail: {
    type: Object,
    default: {},
  },
  // 交易记录schema
  gridRecordSchema: {
    type: Array<TableColumn>,
    default: [],
  },
  // 网格类型详情shcema,监控记录变化表单schema
  gridTypeDetailSchema: {
    type: Array<TableColumn>,
    default: [],
  },
  // 网格数据描述schema
  gridInfoDescriptionSchema: {
    type: Array<DescriptionsSchema>,
    default: [],
  },
})
const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val),
})
// 关闭对话框a'a'a'a'a'aaaaaaaaaaaa
const closeDialog = () => {
  if (dialogShow.value) {
    emit('closeDialog')
  }
}

// 确认数据并关闭弹窗
const confirmDialog = async () => {
  const data_list = _.cloneDeep(props.confirmNotificationData)
  // 删除tradeRecord中的空数据
  data_list.forEach((data) => {
    const records = _.get(data, 'tradeRecord', [])
    records.forEach((record) => {
      for (var key in record) {
        if (_.isEmpty(record[key])) {
          delete record[key]
        }
      }
      if (_.isEmpty(record)) {
        _.remove(records, record)
      }
    })
  })
  // 删除tradeRecord中的空数据
  const res = await notificationApi.confirmNotification(notificationDetailId, {
    confirmData: data_list,
  })
  // 判断是否提交成功
  if (res && res.data) {
    // 打印响应信息
    ElMessage.success(res.message)
    emit('submitted')
    closeDialog()
  }
}

// 监听confirmNotificationData
watch(
  () => props.confirmNotificationData,
  (_confirmNotificationData) => {
    updateCurrentRecordTable()
  }
)

// 监听通知详情数据
watch(
  () => props.notificationDetail,
  (notificationDetail) => {
    gridInfoCount.value = notificationDetail?.content?.grid_info?.length || 0
    currentGridInfo.value = notificationDetail?.content?.grid_info?.[currentGridInfoIndex.value] || {}
  }
)

// 监听窗口是否被打开，如果被打开更新记录数据
watch(
  () => props.dialogVisible,
  (dialogVisible) => {
    if (dialogVisible) {
      gridInfoCount.value = props.notificationDetail?.content?.grid_info?.length || 0
      currentGridInfo.value = props.notificationDetail?.content?.grid_info?.[currentGridInfoIndex.value] || {}
      updateCurrentRecordTable()
    }
  }
)

// 改变当前通知网格内容
const changeCurrentGridInfo = (num) => {
  currentGridInfoIndex.value = currentGridInfoIndex.value + num
  const list = props.notificationDetail?.content?.grid_info || []
  currentGridInfo.value = list[currentGridInfoIndex.value] || {}
  updateCurrentRecordTable()
}

/**
 * 更新当前记录表格数据
 * 功能：从确认通知数据中提取当前网格的交易记录，过滤并处理后更新到当前记录数组
 * 参数：无
 * 返回值：void
 */
const updateCurrentRecordTable = () => {
  const bucket = props.confirmNotificationData?.[currentGridInfoIndex.value]
  const list = bucket?.tradeRecord || []
  const record = list
    .filter((item) => !_.isEmpty(_.values(item)[0]))
    .map((item) => _.values(item)[0])
  currentRecord.value.length = 0
  currentRecord.value.push(...record)
}

// 表格行样式，用于监控档位变化的数据显示，从历史浅色到当前深色
const tableRowClassName = (row) => {
  if (row.row?.isCurrent) {
    return 'history-row'
  }
  return 'cur-row'
}
</script>
<style scoped>
/* 适配浅色与深色主题并增强对比度 */
/* 浅色主题：历史行更浅，当前行更醒目 */
:deep(.history-row) {
  --el-table-tr-bg-color: var(--el-color-info-light-9);
  color: var(--el-text-color-primary);
  border-left: 3px solid var(--el-color-info);
}
:deep(.cur-row) {
  --el-table-tr-bg-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
  border-left: 3px solid var(--el-color-primary);
  font-weight: 600;
}
</style>
