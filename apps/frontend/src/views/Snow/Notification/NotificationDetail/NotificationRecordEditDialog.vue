<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" center @close="closeDialog">
    <ContentWrap title="可能发生交易的网格类型详情数据">
      <Table :columns="tradeListSchema.tableColumns" :data="gridTypeDetaillDataList" :fit="true" />
    </ContentWrap>
    <ContentWrap
      title="交易记录确认表单"
      class="mt-5"
      message="修改的数据会临时保存，但不会提交到服务端，数据会在刷新后丢失"
    >
      <Form ref="formRef" :is-col="false" :schema="gridRecordSchema" />
    </ContentWrap>
    <template #footer>
      <ElButton type="primary" @click="confirmDialog">保存</ElButton>
      <ElButton @click="closeDialog()">关闭</ElButton>
    </template>
  </Dialog>
</template>
<script lang="ts" setup>
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { FormExpose } from '@/components/Form'
import Form from '@/components/Form/src/Form.vue'
import { CrudSchema, useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { webHelper } from '@/utils/webHelper'
import { ElTag } from 'element-plus'
import { computed, h, nextTick, reactive, ref, unref, watch } from 'vue'
// 导入Table组件
import { Table } from '@/components/Table'
// 导入ContentWrap组件
import { ContentWrap } from '@/components/ContentWrap'
import Decimal from 'decimal.js'
import _ from 'lodash'
// 导入dayjs组件
import dayjs from 'dayjs'

const emit = defineEmits(['closeDialog', 'update:dialogVisible'])

// 表单引用
const formRef = ref<FormExpose>()

/**
 * 接收参数：dialogVisible、dialogTitle、网格类型详情、网格交易记录
 */
const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false,
  },
  dialogTitle: {
    type: String,
    default: '',
  },
  // 网格类型详情
  gridTypeDetail: {
    type: Object,
    default: {},
  },
  // 网格类型详情交易记录
  gridTradeRecord: {
    type: Object,
    default: {},
  },
  gridRecordSchema: {
    type: Array<FormSchema>,
    default: [],
  },
})

// 展示网格类型数据，类型为数组，但实际上只有一条数据
const gridTypeDetaillDataList = reactive<any[]>([])

// 使用toRefs复制网格类型交易记录表单Schema
const gridRecordSchema = ref(_.cloneDeep(props.gridRecordSchema))

const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val),
})
// 关闭对话框
const closeDialog = () => {
  const model = unref(formRef)?.formModel
  let record = {}
  // 如果model不为空，将model赋值给record
  if (!_.isEmpty(model) && model.has_transaction) {
    record[props?.gridTypeDetail?.id] = model
  } else {
    record[props?.gridTypeDetail?.id] = {}
  }
  // 删除schema数组的内容
  gridRecordSchema.value.length = 1
  emit('closeDialog', record)
}

// 确认表单并关闭弹窗
const confirmDialog = () => {
  unref(formRef)
    ?.getElFormRef()
    ?.validate((valid) => {
      if (valid) {
        // 获取表单数据
        closeDialog()
      }
    })
}

watch(
  () => props.gridTypeDetail,
  (val) => {
    gridTypeDetaillDataList.length = 0
    gridTypeDetaillDataList.push(val)
  }
)

// 监控窗口是否可见，当窗口可见时，向表单添加一个开关，表示是否有成交
watch(
  () => props.dialogVisible,
  (val) => {
    if (val) {
      nextTick(() => {
        // 给是否成交开关添加监听回调方法
        unref(formRef)?.setSchema([
          {
            field: 'has_transaction',
            path: 'componentProps.onChange',
            value: switchChange,
          },
        ])
        const recForId = props?.gridTypeDetail?.id ? props.gridTradeRecord?.[props.gridTypeDetail.id] : undefined
        if (recForId && recForId.has_transaction) {
          gridRecordSchema.value.push(...props.gridRecordSchema.slice(1))
          unref(formRef)?.setValues(recForId)
          return
        }
        // 删除schema数组的内容
        gridRecordSchema.value.length = 1
      })
    }
  }
)

// 是否交易开关变化时的监听回调方法
const switchChange = (val: boolean) => {
  // 判断是否有成交
  if (val) {
    // 有成交，向表单添加交易记录表单Schema
    gridRecordSchema.value.push(...props.gridRecordSchema.slice(1))
    // 添加值的监听方法
    unref(formRef)?.setSchema([
      // 更新交易单价时，自动计算交易金额
      {
        field: 'transactionsPrice',
        path: 'componentProps.onChange',
        value: async (val) => {
          let model = unref(formRef)?.formModel
          const amount = new Decimal(val).mul(model?.transactionsShare).toString()
          unref(formRef)?.setValues({ transactionsAmount: amount })
        },
      },
      // 更新交易份额时，自动计算交易金额
      {
        field: 'transactionsShare',
        path: 'componentProps.onChange',
        value: async (val) => {
          let model = unref(formRef)?.formModel
          const amount = new Decimal(val).mul(model?.transactionsPrice).toString()
          unref(formRef)?.setValues({ transactionsAmount: amount })
        },
      },
    ])
    // 判断网格类型详情所监听的交易类型
    if (props.gridTypeDetail.monitorType == 0) {
      // 买入
      unref(formRef)?.setValues({
        transactionsPrice: new Decimal(props.gridTypeDetail?.purchasePrice).div(10000),
        transactionsShare: props.gridTypeDetail?.purchaseShares,
        transactionsDirection: 1,
        transactionsAmount: new Decimal(props.gridTypeDetail?.purchasePrice)
          .mul(props.gridTypeDetail?.purchaseShares)
          .mul(-1)
          .div(10000)
          .toString(),
        transactionsDate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
      })
    } else {
      // 卖出
      unref(formRef)?.setValues({
        transactionsPrice: new Decimal(props.gridTypeDetail?.sellPrice).div(10000),
        transactionsShare: props.gridTypeDetail?.actualSellShares,
        transactionsDirection: 0,
        transactionsAmount: new Decimal(props.gridTypeDetail?.sellPrice)
          .mul(props.gridTypeDetail?.actualSellShares)
          .div(10000)
          .toString(),
        transactionsDate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
      })
    }
  } else {
    // 没有成交，删除表单中的交易记录表单Schema
    gridRecordSchema.value.length = 1
  }
}

// 网格类型详情数据表格Schema
const gridTypeDetailSchemas = reactive<CrudSchema[]>([
  {
    field: 'gear',
    label: '档位',
  },
  {
    field: 'purchasePrice',
    label: '买入价格',
    // 使用decimal格式化数字
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return webHelper.numFormatWithCurrency(cellValue, null, 10000, 3)
    },
  },
  {
    field: 'purchaseAmount',
    label: '买入金额',
    // 使用decimal格式化数字
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return webHelper.numFormatWithCurrency(cellValue, null, 10000, 3)
    },
  },
  {
    field: 'purchaseShares',
    label: '买入份额',
  },
  {
    field: 'sellPrice',
    label: '卖出价格',
    // 使用decimal格式化数字
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return webHelper.numFormatWithCurrency(cellValue, null, 10000, 3)
    },
  },
  {
    field: 'actualSellShares',
    label: '实际卖出份额',
  },
  {
    field: 'saveShareProfit',
    label: '留股盈利',
    // 使用decimal格式化数字
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return webHelper.numFormatWithCurrency(cellValue, null, 10000, 3)
    },
  },
  {
    field: 'saveShare',
    label: '留股份额',
  },
  {
    field: 'monitorType',
    label: '监控类型',
    formatter: (_: Recordable, __: TableColumn, cellValue: number) => {
      return h(ElTag, {}, () => (cellValue == 0 ? '买入' : cellValue == 1 ? '卖出' : '未知'))
    },
  },
])

let tradeListSchema = useCrudSchemas(gridTypeDetailSchemas).allSchemas
</script>
<style></style>
