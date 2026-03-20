<template>
  <div>
    <el-space class="mb-5">
      <el-button @click="resetData">
        <Icon icon="ep:refresh-right" />
        重置数据
      </el-button>
      <el-button type="primary" @click="addRow" plain icon="Plus">新增数据</el-button>
      <el-button type="primary" @click="setCurrent" plain icon="Aim">设为当前</el-button>
      <el-popconfirm title="是否删除选中数据" @confirm="deleteData">
        <template #reference>
          <el-button type="danger" plain icon="Delete">删除选中</el-button>
        </template>
      </el-popconfirm>
      <el-button type="primary" @click="submit" plain>确认数据</el-button>
      <el-button link :disabled="!careTaker.undoAble()" @click="undoEdit" icon="Back" />
      <el-button link :disabled="!careTaker.redoAble()" @click="redoEdit" icon="Right" />
    </el-space>
  </div>
  <div style="height: 400px">
    <el-auto-resizer>
      <template #default="{ height, width }">
        <el-table-v2
          :columns="columns"
          :data="data"
          :width="width"
          :height="height"
          fixed
          :row-class="rowClass"
        />
      </template>
    </el-auto-resizer>
  </div>
</template>

<script lang="tsx" setup>
import type { FunctionalComponent } from 'vue'
import { reactive, Ref, ref, resolveDynamicComponent, toRef, unref, watch } from 'vue'
import {
  Column,
  ElInput,
  ElCheckbox,
  RowClassNameGetter,
  CheckboxValueType,
  ElMessage
} from 'element-plus'
import _ from 'lodash-es'
import { any } from 'vue-types'
import * as gridTypeDetailApi from '@/api/snow/gridTypeDetail/index'
import { numFormat } from '@/utils/formatHelper'

interface CellContent {
  rowKey: any
  colKey: any
  cellContent: any
}

const Input = resolveDynamicComponent('ElInput') as typeof ElInput
// get props
const props = defineProps({
  columns: {
    type: Array<Column>
  },
  columnFields: {
    type: Array<ColumnField>
  },
  dataList: {
    type: Array<any>
  },
  dataListCache: {
    type: Array<any>
  },
  newRow: {
    type: any
  },
  editingArr: {
    type: Array<Array<Boolean>>
  }
})

const emit = defineEmits(['submit', 'addRow', 'deleteRows', 'refreshData'])
// 获取列信息
const columns = toRef(props, 'columns') as Ref<Array<Column>>
const dataList = toRef(props, 'dataList') as Ref<Array<Array<any>>>
const dataListCache = toRef(props, 'dataListCache') as Ref<Array<any>>
const editingArr = toRef(props, 'editingArr') as Ref<Array<Array<Boolean>>>

type SelectionCellProps = {
  value: boolean
  intermediate?: boolean
  onChange?: (value: string) => void
}

type InputCellProps = {
  value: string
  intermediate?: boolean
  onChange?: (value: string) => void
  forwardRef?: (el: InstanceType<typeof ElInput>) => void
  onBlur?: () => void
}

/**
 * 自定义Input组件
 * @param value 值
 * @param onChange  值改变时的回调
 * @param forwardRef
 * @param onBlur    组件失去焦点时的回调
 * @constructor
 */
const InputCell: FunctionalComponent<InputCellProps> = ({
  value,
  onChange,
  forwardRef,
  onBlur
}) => {
  return <Input ref={forwardRef as any} onInput={onChange} modelValue={value} onBlur={onBlur} />
}

/**
 * 选项框组件
 * @param value 选项框的值
 * @param intermediate
 * @param onChange  选择框的值改变时的回调
 * @constructor
 */
const SelectionCell: FunctionalComponent<SelectionCellProps> = ({
  value,
  intermediate = false,
  onChange
}) => {
  return <ElCheckbox onChange={onChange} modelValue={value} indeterminate={intermediate} />
}

// 缓存行数据，并设置

const data = ref<Array<any>>(dataList.value)

// 监听数据变化
watch(
  () => props.dataList,
  () => {
    data.value = dataList.value
    editingArr.value.length = 0
    editingArr.value.push(
      ...new Array(data.value.length)
        .fill(null)
        .map(() => Array.from({ length: columns.value.length }).map(() => false))
    )
    // 重新渲染
    columns.value = renderColumn(columns.value)
    addRowSelection()
  }
)

// 监听新增数据
watch(
  () => props.newRow,
  (val: any) => {
    if (val) {
      data.value.push(val)
    }
  }
)

// 记录修改的位置，用于应用不同的样式
const changeLocations = reactive<Array<Array<number>>>([[]])

const addRow = () => {
  emit('addRow', columns)
}

/**
 * 重置数据，使用缓存数据转换成表格格式数据
 */
const resetData = () => {
  data.value = dataListCache.value
  careTaker.clear()
}
const submit = () => {
  emit('submit', data, columns)
}

/**
 * 自定义table单元格字体样式样式，主动修改的字体颜色为蓝色，红色为修改后的受影响的数据
 */
const gridTypeFontStyle = (colDataKey: number, rowIndex: number) => {
  const isDataChange = dataListCache.value[rowIndex][colDataKey] != data.value[rowIndex][colDataKey]
  const changesLocs = changeLocations.filter((loc) => loc[0] == rowIndex && loc[1] == colDataKey)
  if (!isDataChange) {
    return ''
  }
  if (changesLocs.length > 0) {
    return 'text-blue-500'
  }
  return 'text-red-500'
}

/**
 * 鼠标悬停在单元格上时，根据单元格是否可以编辑给定单元边框样式
 * @param editAble
 */
const editGridHoverCss = (editAble: boolean): string => {
  return editAble ? 'table-v2-inline-editing-trigger' : ''
}

/**
 * 高亮行
 * @param rowIndex
 */
const rowClass = ({ rowIndex }: Parameters<RowClassNameGetter<any>>[0]) => {
  if (data.value[rowIndex].isCurrent) {
    return 'bg-rose-400'
  }
  return ''
}

/**
 * 撤回
 */
const undoEdit = () => {
  if (careTaker.undoAble()) {
    const cellContent: Memento = careTaker.undo()
    data.value[cellContent.getContent().rowKey][cellContent.getContent().colKey] =
      cellContent.getContent().cellContent
  }
}

/**
 * 重做
 */
const redoEdit = () => {
  if (careTaker.redoAble()) {
    const memento: Memento = careTaker.redo()
    data.value[memento.getContent().rowKey][memento.getContent().colKey] =
      memento.getContent().cellContent
  }
}

const deleteData = () => {
  if (data.value.length > 0) {
    const noneIdList = data.value.filter((row) => row.checked && !row.id).map((row) => row.index)
    // 删除选中但未提交的数据
    _.remove(data.value, (row) => _.findIndex(noneIdList, (id) => row.index === id) >= 0)
    _.remove(dataListCache.value, (row) => _.findIndex(noneIdList, (id) => row.index === id) >= 0)
    const ids = data.value.filter((row) => row.checked && row.id).map((row) => row.id)
    emit('deleteRows', ids)
  }
}

// 状态存储
// 备忘类
class Memento {
  content: CellContent
  constructor(content) {
    this.content = content
  }
  getContent() {
    return this.content
  }
}

// 备忘列表
class CareTaker {
  // 旧数据列表
  oldValues: Array<Memento>
  // 新数据列表
  newValues: Array<Memento>
  // 游标，默认为0
  cursor = -1
  constructor() {
    this.oldValues = []
    this.newValues = []
  }
  // 保存
  add(memento: Memento, refresh = false) {
    if (!refresh) {
      this.oldValues.push(memento)
      return
    }
    this.cursor++
    this.oldValues[this.cursor] = this.oldValues[this.oldValues.length - 1]
    this.newValues[this.cursor] = memento
    this.oldValues.length = this.cursor + 1
    this.newValues.length = this.cursor + 1
  }
  get(index: number) {
    return this.oldValues[index]
  }
  undo(): Memento {
    return this.oldValues[this.cursor--]
  }
  redo() {
    return this.newValues[++this.cursor]
  }
  // 是否可以撤回
  undoAble(): boolean {
    return this.cursor >= 0
  }
  //  是否可以重做
  redoAble(): boolean {
    return this.oldValues.length > 0 && this.cursor < this.oldValues.length - 1
  }

  /**
   * 返回最新的旧记录元素，注：虽然数组中可能存在元素，但因为并不是一个完整的记录，所以可能会忽视该元素，这种情况下，会返回Null
   * 直到调用add方法并传入refresh刷新数组。
   */
  getLast() {
    if (this.cursor < 0) {
      return null
    }
    return this.oldValues[this.cursor]
  }
  // 返回旧记录的最后一个元素
  getTail() {
    return _.nth(this.oldValues, -1)
  }
  pop() {
    if (this.cursor < 0) {
      return null
    }
    // this.cursor--
    return this.oldValues.pop()
  }

  /**
   * 清除所有备忘记录
   */
  clear() {
    this.newValues.length = 0
    this.oldValues.length = 0
    this.cursor = -1
  }
}

// 记录器
class Recoder {
  content: any
  constructor() {
    this.content = null
  }
  setContent(content) {
    this.content = content
  }
  getContent() {
    return this.content
  }
  saveContentToMemento() {
    return new Memento(this.content)
  }
  getContentFromMemento(memento) {
    this.content = memento.getContent()
    return this.content
  }
}

let recorder = new Recoder()
let careTaker = reactive(new CareTaker())

const numFormatList = []
const shareFormatList = ['purchaseShares', 'actualSellShares', 'saveShare']
const priceFormatList = [
  'triggerPurchasePrice',
  'purchasePrice',
  'triggerSellPrice',
  'sellPrice'
]

const amountFormatList = ['purchaseAmount', 'sellAmount', 'profit', 'saveShareProfit']

const formatGridData = (num: number, rowFields: string) => {
  if (_.indexOf(priceFormatList, rowFields) >= 0) {
    const options = {
      style: 'currency',
      currency: 'CNY',
      maximumFractionDigits: 4,
      minimumFractionDigits: 4
    } as Intl.NumberFormatOptions
    const numStr = Number(num / 10000).toLocaleString('zh-CN', options)
    return numStr
  }
  if (_.indexOf(amountFormatList, rowFields) >= 0) {
    const options = {
      style: 'currency',
      currency: 'CNY',
      maximumFractionDigits: 2,
      minimumFractionDigits: 2
    } as Intl.NumberFormatOptions
    const numStr = Number(num / 100).toLocaleString('zh-CN', options)
    return numStr
  }
  if (_.indexOf(shareFormatList, rowFields) >= 0) {
    const options = {
      style: 'decimal',
      maximumFractionDigits: 2,
      minimumFractionDigits: 2
    } as Intl.NumberFormatOptions
    const numStr = Number(num / 100).toLocaleString('zh-CN', options)
    return numStr
  }
  if (_.indexOf(numFormatList, rowFields) >= 0) {
    return numFormat(num)
  }
  return num
}

/**
 * 为数据表添加选择框列，需要在数据表列数据赋值后调用
 */
const addRowSelection = () => {
  columns.value.unshift({
    key: 'selection',
    width: 50,
    cellRenderer: ({ rowData }) => {
      const onChange = (value: CheckboxValueType) => (rowData.checked = value)
      return <SelectionCell value={rowData.checked} onChange={onChange} />
    },

    headerCellRenderer: () => {
      const _data = unref(data)
      const onChange = (value: CheckboxValueType) =>
        (data.value = _data.map((row) => {
          row.checked = value
          return row
        }))
      const allSelected = _data.every((row) => row.checked)
      const containsChecked = _data.some((row) => row.checked)

      return (
        <SelectionCell
          value={allSelected}
          intermediate={containsChecked && !allSelected}
          onChange={onChange}
        />
      )
    }
  })
}

/**
 * 设置网格当前所在位置
 */
const setCurrent = async () => {
  const selectedArr = data.value.filter((row) => row.checked)
  if (selectedArr.length == 0) {
    ElMessage({
      message: '请选择数据',
      type: 'error'
    })
    return
  }
  if (selectedArr.length > 1) {
    ElMessage({
      message: '请选择一条数据',
      type: 'error'
    })
    return
  }
  const selectedData = selectedArr.pop()
  // 如果所设置的数据是新增的数据，直接修改该行数据的isCurrent值
  if (selectedData.id) {
    // 提交数据
    const res = await gridTypeDetailApi.setCurrent(selectedData.id)
    ElMessage({
      message: res.message,
      type: 'success'
    })
    emit('refreshData')
    return
  }
  // 遍历数据
  data.value.forEach((row) => {
    row.isCurrent = row.index === selectedData.index
  })
}

/**
 * 根据列数据自定义单元格渲染方式
 * @param columns
 */
const renderColumn = (columns: Array<Column>) => {
  // 处理列渲染方式
  return columns.map((column) => ({
    ...column,
    // 自定义表格渲染，rowData.id为行坐标,column.dataKey为列坐标
    cellRenderer: ({ rowData, column }) => {
      /**
       * 单元格改变时调用
       * @param value
       */
      const onChange = (value: string) => {
        rowData[column.dataKey!] = value
      }
      /**
       * 进入编辑模式
       */
      const onEnterEditMode = () => {
        if (!column.editable) {
          return
        }
        editingArr.value[rowData.index][column.key] = true
        const cellContent: CellContent = {
          rowKey: rowData.index,
          colKey: column.dataKey!,
          cellContent: rowData[column.dataKey!]
        }
        // 设置当前内容
        recorder.setContent(cellContent)
        // 保存当前内容
        careTaker.add(recorder.saveContentToMemento())
      }
      /**
       * 退出编辑模式
       */
      const onExitEditMode = () => {
        if (dataListCache.value[rowData.index][column.dataKey!] != rowData[column.dataKey!]) {
          const changesLocs = changeLocations.filter(
            (loc) => loc[0] == rowData.index && loc[1] == column.dataKey!
          )
          if (changesLocs.length == 0) {
            changeLocations.push([rowData.index, column.dataKey!])
          }
        }
        editingArr.value[rowData.index][column.dataKey] = false
        let lastData: CellContent = recorder.getContentFromMemento(careTaker.getTail())
        if (rowData[lastData.colKey!] === lastData.cellContent) {
          // 如果数据没有改变，删除备忘记录上一条记录
          careTaker.pop()
          return
        }
        // 记录当前值
        const cellContent: CellContent = {
          rowKey: rowData.index,
          colKey: column.dataKey!,
          cellContent: rowData[column.dataKey!]
        }
        // 设置当前内容
        recorder.setContent(cellContent)
        // 保存当前内容
        careTaker.add(recorder.saveContentToMemento(), true)
      }
      const input = ref()
      const setRef = (el) => {
        input.value = el
        if (el) {
          el.focus?.()
        }
      }
      return column.editable && editingArr.value[rowData.index][column.dataKey] ? (
        <InputCell
          forwardRef={setRef}
          value={rowData[column.dataKey!]}
          onChange={onChange}
          onBlur={onExitEditMode}
        />
      ) : (
        <div
          // 设置css样式
          class={[
            editGridHoverCss(column.editable),
            gridTypeFontStyle(column.dataKey, rowData.index)
          ]}
          onClick={onEnterEditMode}
        >
          {formatGridData(rowData[column.dataKey!], column.field)}
        </div>
      )
    }
  }))
}
addRowSelection()
</script>

<style>
.table-v2-inline-editing-trigger {
  padding: 4px;
  border: 1px transparent dotted;
}

.table-v2-inline-editing-trigger:hover {
  border-color: var(--el-color-primary);
}
</style>
