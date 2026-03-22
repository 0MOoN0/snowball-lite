<template>
  <ContentWrap :title="`网格`">
    <div>
      <ElRow :gutter="20" justify="space-between">
        <ElCol :span="6">
          <GridSideBar
            :search-schema="searchSchema"
            :search-data="searchData"
            :grid-analysis-data="gridAnalysisData"
            @register-form="formRegister"
            @add-grid="addGridDialog"
            @edit-grid="editGridDialog"
            @delete-grid="deleteGrid"
            @update-analysis="updateGridAnalysisResult"
            @sync-grid="openSyncGridDialog"
            @sync-record="openSyncRecordDialog"
            @export-grid="exportGridData"
            @export-record="exportGridRecordData"
            @add-grid-type="addGridTypeDialog"
            @upload-grid-type="updateGridType"
            @edit-grid-type="editGridTypeDialog"
            @delete-grid-type="deleteGridType"
          />
        </ElCol>
        <!-- 数据分析展示 -->
        <ElCol :span="18">
          <GridInfoPanel
            :grid-info-schema="gridInfoSchema"
            :current-grid-info="currentGridInfo"
            :asset-data-schema="assetDataSchema"
            :current-asset-data="currentAssetData"
            :grid-analysis-data="gridAnalysisData"
            :grid-type-analysis-schema="gridTypeAnalysisSchema"
            :grid-type-analysis-data="gridTypeAnalysisData"
            :search-data="searchData"
            @show-grid-analysis-detail="showGridAnalysisDetail"
            @show-grid-type-analysis-detail="showGridTypeAnalysisDetail"
            @update-grid-type-analysis-result="updateGridTypeAnalysisResult"
          />
        </ElCol>
      </ElRow>
    </div>
  </ContentWrap>
  <ContentWrap :title="`网格类型详情`" class="mt-20px">
    <ElTabs type="border-card" v-model="activePane">
      <ElTabPane label="网格类型详情" name="grid_detail_data">
        <GridTypeTable
          :grid-type-detail-list="gridTypeDetailList"
          @submit="gridTypeDetailSubmit"
          @delete-rows="deleteRows"
          @refresh-data="refresh"
          :grid-infos="searchData"
          :loading="gridTypeDetailLoading"
        />
      </ElTabPane>
      <ElTabPane label="交易记录" name="grid_record_data" :lazy="true">
        <GridRecord
          :grid-id="searchData.gridId"
          :grid-type-id="searchData.gridTypeId"
          :asset-id="Number(currentGridInfo.gridInfo?.assetId ?? currentAssetData.id ?? 0) || null"
        />
      </ElTabPane>
      <ElTabPane label="交易图表" name="grid_record_analysis" :lazy="true">
        <GridRecordAnalysis :grid-type-id="chartAnalysisData.gridTypeId" />
      </ElTabPane>
    </ElTabs>
  </ContentWrap>
  <!-- 新增或修改网格弹窗 -->
  <GridDialog
    :dialog-title="gridDialogProps.dialogTitle"
    :dialog-visible="gridDialogProps.dialogVisible"
    :grid-info="gridDialogProps.gridInfo"
    @close-dialog="closeGridDialog"
  />
  <!-- 上传网格详情列表弹窗 -->
  <GridTypeDetailUploadDialog
    :dialog-visible="gridTypeDetailUploadDialog.dialogVisible"
    :dialog-title="gridTypeDetailUploadDialog.dialogTitle"
    :grid-type-id="gridTypeDetailUploadDialog.gridTypeId"
    @close-dialog="closeGridTypeDetailUpdateDialog"
  />
  <!-- 网格交易数据分析详情弹窗 -->
  <GridAnalysisResultDialog
    :dialog-title="analysisDetailDialogInfo.title"
    :dialog-visible="analysisDetailDialogInfo.visiable"
    @close-dialog="closeAnalysisDetailDialog"
    :analysis-data="analysisDetailDialogInfo.analysisData"
  />
  <!-- 新增或修改网格类型数据弹窗 -->
  <GridTypeDialog
    :dialog-title="gridTypeDialogProps.dialogTitle"
    :dialog-visible="gridTypeDialogProps.dialogVisible"
    :grid-type-info="gridTypeDialogProps.gridTypeInfo"
    @close-dialog="closeGridTypeDialog"
  >
  </GridTypeDialog>
  <!-- 同步网格数据弹窗 -->
  <GridFileSyncUploadDialog
    :dialog-visible="gridSyncFileUploadDialogParams.dialogVisible"
    @close-dialog="closeGridSyncDialog"
  />
  <!-- 同步网格交易记录数据弹窗 -->
  <GridRecordFileSyncUploadDialog
    :dialog-visible="gridRecordSyncFileUploadDialogParams.dialogVisible"
    @close-dialog="closeRecordSyncDialog"
  />
</template>
<script setup lang="ts">
import * as gridApi from '@/api/snow/grid/index'
import { Grid } from '@/api/snow/grid/types'
import * as gridTypeApi from '@/api/snow/gridType/index'
import { GridType } from '@/api/snow/gridType/types'
import * as gridTypeDetailApi from '@/api/snow/gridTypeDetail/index'
import { ContentWrap } from '@/components/ContentWrap'
import { useForm } from '@/hooks/web/useForm'
import GridDialog from '@/views/Snow/Strategy/grid/GridDialog.vue'
import GridRecord from '@/views/Snow/Strategy/grid/GridRecord/GridRecord.vue'
import GridTypeDialog from '@/views/Snow/Strategy/grid/GridTypeDialog.vue'
import GridSideBar from '@/views/Snow/Strategy/grid/components/GridSideBar.vue'
import GridInfoPanel from '@/views/Snow/Strategy/grid/components/GridInfoPanel.vue'
import { ElCol, ElMessage, ElMessageBox, ElRow } from 'element-plus'
import * as _ from 'lodash-es'
import { onUnmounted, reactive, ref } from 'vue'
import GridRecordFileSyncUploadDialog from '@/views/Snow/Strategy/grid/GridRecordFileSyncUploadDialog.vue'
import GridTypeDetailUploadDialog from '@/views/Snow/Strategy/grid/GridTypeDetailUploadDialog.vue'
import GridTypeTable from '@/views/Snow/Strategy/grid/GridTypeDetail/GridTypeTable.vue'
import GridAnalysisResultDialog from '@/views/Snow/Strategy/grid/analysis/GridAnalysisResultDialog.vue'
// 引入文件上传同步弹窗组件
import * as gridAnalysisApi from '@/api/snow/analysis/GridAnalysisApi'
import * as gridTypeAnalysisApi from '@/api/snow/analysis/GridTypeAnalysisApi'
import * as assetApi from '@/api/snow/asset/AssetApi'
import { formatGridAnalysisData, formatGridTypeAnalysisData } from '@/utils/gridDataFormatter'
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import GridFileSyncUploadDialog from '@/views/Snow/Strategy/grid/GridFileSyncUploadDialog.vue'
import GridRecordAnalysis from '@/views/Snow/Strategy/grid/analysis/GridRecordAnalysis.vue'
import { gridInfoSchema, assetDataSchema, gridTypeAnalysisSchema } from './grid/Grid.data'

const route = useRoute()

// 处理路由参数
onMounted(async () => {
  // 判断路由是否有参数
  if (route.query) {
    const param = route.query
    if ('grid_type_id' in param && param.grid_type_id && 'grid_id' in param && param.grid_id) {
      searchData.value.gridId = param.grid_id
      searchData.value.gridTypeId = param.grid_type_id
      await searchSchema[0].componentProps?.onChange(param.grid_id)
      await searchSchema[1].componentProps?.onChange(param.grid_type_id)
      gridSearchFormMethods.setValues({
        grid: Number(param.grid_id),
        gridType: Number(param.grid_type_id),
      })
    }
  }
})

const gridTypeDetailList = ref([])
const gridTypeDetailLoading = ref(false)

// tabs
let activePane = ref('grid_detail_data')

// 网格弹窗数据
const gridDialogProps = ref({ dialogVisible: false, dialogTitle: '', gridInfo: {} })

// 网格类型弹窗数据
const gridTypeDialogProps = ref({ dialogVisible: false, dialogTitle: '', gridTypeInfo: {} })

// 网格类型详情上传弹窗数据
const gridTypeDetailUploadDialog = ref({ dialogVisible: false, dialogTitle: '', gridTypeId: 0 })

// 当前资产数据
const currentAssetData = ref<any>({})

// 网格文件同步弹窗数据
const gridSyncFileUploadDialogParams = ref({ dialogVisible: false, dialogTitle: '' })

// 网格交易记录文件同步弹窗数据
const gridRecordSyncFileUploadDialogParams = ref({ dialogVisible: false, dialogTitle: '' })

// 搜索表单数据
const searchData = ref<{
  gridId?: number | any
  gridTypeId?: number | any
}>({ gridId: 0, gridTypeId: 0 })

const gridTypeAnalysisData = ref({ loading: false, data: {} })
const gridAnalysisData = ref({ loading: false, data: {} })

const currentGridInfo = ref<any>({ gridInfo: {}, gridTypeInfo: {} })

const gridList = ref([])

const gridTypeList = ref([])

const chartAnalysisData = ref<any>({ gridTypeId: null })

const analysisDetailDialogInfo = reactive({
  title: '',
  visiable: false,
  analysisData: {},
})

const searchSchema = reactive<FormSchema[]>([
  {
    field: 'grid',
    label: '网格：',
    component: 'Select',
    componentProps: {
      options: [],
      onChange: (gridId: number) => {
        if (gridId) {
          initGridType(gridId)
          initGridAnalysisData(gridId)
          initAssetData(gridId)
          _.set(searchData.value, 'gridId', gridId)
          const { setSchema, setValues } = gridSearchFormMethods
          setSchema([
            {
              field: 'gridType',
              path: 'componentProps.options',
              value: [],
            },
          ])
          setValues({ gridType: null })
          delete searchData.value.gridTypeId
        }
      },
      onClear: () => {
        _.set(searchData.value, 'gridId', null)
        _.set(searchData.value, 'gridTypeId', null)
        const { setValues } = gridSearchFormMethods
        setValues({ gridType: null })
      },
    },
  },
  {
    field: 'gridType',
    label: '网格类型：',
    component: 'Select',
    componentProps: {
      options: [],
      onChange: (gridTypeId: number) => {
        if (gridTypeId) {
          initGridTypeDetailTable(gridTypeId)
          initGridTypeAnalysisData(gridTypeId)
          searchData.value.gridTypeId = gridTypeId
          // _.set(searchData.value, 'gridTypeId', gridTypeId)
          chartAnalysisData.value.gridTypeId = gridTypeId
        }
      },
      onClear: () => {
        _.set(searchData.value, 'gridTypeId', null)
      },
    },
  },
])
const { register: formRegister, methods: gridSearchFormMethods } = useForm({ searchSchema })

// 获取网格列表
const initGridList = async () => {
  const res = await gridApi.getGridList()
  if (res.data && res.data.length > 0) {
    const gridsOptions = res.data.map((grid: Grid) => {
      return { label: grid.gridName, value: grid.id }
    })
    gridList.value = res.data
    if (searchSchema && searchSchema.length > 0) {
      if (searchSchema[0].componentProps && searchSchema[0].componentProps.options) {
        searchSchema[0].componentProps.options.length = 0
        searchSchema[0].componentProps.options.push(...gridsOptions)
      }
    }
  }
}
initGridList()

// 根据网格ID初始化网格类型
const initGridType = async (gridId: number | any) => {
  currentGridInfo.value.gridInfo = gridList.value.find((grid: Grid) => grid.id == gridId)
  let gridTypeRes = await gridTypeApi.getGridType({ gridId })
  if (gridTypeRes && gridTypeRes.data) {
    const gridTypeOptions = gridTypeRes.data.map((gridType: GridType) => {
      return { label: gridType.typeName, value: gridType.id }
    })
    gridTypeList.value = gridTypeRes.data
    if (searchSchema && searchSchema.length > 0) {
      if (searchSchema[1].componentProps && searchSchema[1].componentProps.options) {
        searchSchema[1].componentProps.options.length = 0
        searchSchema[1].componentProps.options.push(...gridTypeOptions)
      }
    }
  }
}

/**
 * 获取网格类型详情列表数据
 * @param gridTypeId
 */
const initGridTypeDetailTable = async (gridTypeId: number) => {
  gridTypeDetailLoading.value = true
  currentGridInfo.value.gridTypeInfo = gridTypeList.value.find((gridType: GridType) => gridType.id == gridTypeId)
  const res = await gridTypeDetailApi.getGridTypeDetailList({ gridTypeId })
  gridTypeDetailList.value = res.data
  gridTypeDetailLoading.value = false
}

/**
 * 初始化网格类型交易分析数据
 * @param grid_type_id
 */
const initGridTypeAnalysisData = async (grid_type_id: any) => {
  const res = await gridTypeAnalysisApi.getGridTypeAnalysis(grid_type_id)
  // 对返回的原始数据进行格式化处理
  gridTypeAnalysisData.value.data = formatGridTypeAnalysisData(res.data)
}

/**
 * 初始化网格交易分析数据
 * @param grid_id
 */
const initGridAnalysisData = async (grid_id: number) => {
  const res = await gridAnalysisApi.getGridAnalysis(grid_id)
  // 对返回的原始数据进行格式化处理
  const formattedData = formatGridAnalysisData(res.data)
  Object.assign(gridAnalysisData.value, formattedData)
}

/**
 * 初始化资产数据
 * @param gridId 网格ID
 */
const initAssetData = async (gridId: number) => {
  const res = await assetApi.getAssetList({ page: 1, pageSize: 1, gridId })
  if (res && res.success && res.data.items.length > 0) {
    currentAssetData.value = res.data.items[0]
  }
}

/**
 * 网格类型详情提交回调方法
 * @param res
 */
const gridTypeDetailSubmit = async (res: any) => {
  if (res) {
    ElMessage({
      message: '操作成功',
      type: 'success',
    })
    // 刷新网格类型表格数据展示
    await refresh()
  }
}
/**
 * 表格数据删除行
 * @param res
 */
const deleteRows = async (res: any) => {
  ElMessage({
    message: res.message,
    type: 'success',
  })
  await refresh()
}

const refresh = async () => {
  // 刷新网格类型表格数据展示
  const curGridTypeId = _.get(searchData.value, 'gridTypeId', null)
  if (curGridTypeId !== null) {
    await initGridTypeDetailTable(curGridTypeId)
  }
}

/**
 * 打开添加网格弹窗
 */
const addGridDialog = (title: string) => {
  gridDialogProps.value.dialogVisible = true
  gridDialogProps.value.dialogTitle = title
  // if (searchData.value.gridId) {
  //   gridDialogProps.value.gridInfo = { gridId: searchData.value.gridId }
  // }
}

/**
 * 删除当前网格数据
 */
const deleteGrid = async () => {
  const gridId = _.get(searchData.value, 'gridId', null)
  if (gridId == null) {
    ElMessage({
      message: '请选择网格后删除',
      type: 'error',
    })
    return
  }
  const gridRes = await gridApi.deleteById(gridId)
  if (gridRes && gridRes.data) {
    ElMessage({
      message: gridRes.message,
      type: 'success',
    })
    const { setValues } = gridSearchFormMethods
    setValues({ grid: null, gridType: null })
    await initGridList()
    gridTypeDetailList.value = []
  }
}

/**
 * 删除当前网格类型数据
 */
const deleteGridType = async () => {
  // 判断当前网格ID和网格类型ID是否为空
  if (!searchData.value || !searchData.value.gridTypeId) {
    ElMessage({
      message: '请选择网格和网格类型',
      type: 'error',
    })
    return
  }
  const gridId = _.get(searchData.value, 'gridId', null)
  ElMessageBox.confirm('操作会删除当前网格类型数据和关联的网格类型详情数据. 是否继续?', '警告！', {
    confirmButtonText: '确认继续',
    cancelButtonText: '取消',
    type: 'warning',
    center: true,
  }).then(async () => {
    const gridTypeId = _.get(searchData.value, 'gridTypeId', null)
    const gridTypeRes = await gridTypeApi.deleteGridTypeById(gridTypeId)
    if (gridTypeRes && gridTypeRes.data) {
      ElMessage({
        message: gridTypeRes.message,
        type: 'success',
      })
      const { setValues } = gridSearchFormMethods
      setValues({ gridType: null })
      await initGridType(Number(gridId))
      gridTypeDetailList.value = []
    }
  })
}

/**
 * 打开编辑网格弹窗
 * @param title
 */
const editGridDialog = (title: string) => {
  gridDialogProps.value.dialogVisible = true
  gridDialogProps.value.dialogTitle = title
  gridDialogProps.value.gridInfo = searchData.value
}

/**
 * 关闭网格弹窗，刷新网格数据
 */
const closeGridDialog = async () => {
  gridDialogProps.value.dialogVisible = false
  gridDialogProps.value.gridInfo = {}
  // 如果是编辑网格，关闭弹窗后刷新网格数据
  if (searchData.value && searchData.value.gridId) {
    await initGridList()
    return
  }
  // 如果是新增网格，关闭弹窗后刷新网格数据
  await initGridList()
}

/**
 * 关闭网格类型数据上传表单
 */
const closeGridTypeDetailUpdateDialog = () => {
  gridTypeDetailUploadDialog.value.dialogVisible = false
  gridTypeDetailUploadDialog.value.gridTypeId = 0
  if (searchData.value && searchData.value.gridId) {
    initGridType(searchData.value.gridId)
  }
  refresh()
}

/**
 * 点击上传网格类型详情数据按钮
 */
const updateGridType = () => {
  if (!searchData.value || !searchData.value.gridTypeId) {
    ElMessage({
      message: '请选择网格和网格类型',
      type: 'error',
    })
    return
  }
  gridTypeDetailUploadDialog.value.dialogVisible = true
  gridTypeDetailUploadDialog.value.gridTypeId = searchData.value.gridTypeId
  gridTypeDetailUploadDialog.value.dialogTitle = '上传网格类型详情数据'
}

/**
 * 显示网格类型数据分析详情
 */
const showGridTypeAnalysisDetail = () => {
  analysisDetailDialogInfo.visiable = true
  analysisDetailDialogInfo.title = '网格类型数据详情'
  // 传递格式化后的数据
  analysisDetailDialogInfo.analysisData = gridTypeAnalysisData.value.data
}

/**
 * 显示网格数据分析详情
 */
const showGridAnalysisDetail = () => {
  analysisDetailDialogInfo.visiable = true
  analysisDetailDialogInfo.title = '网格数据详情'
  // 传递格式化后的数据
  analysisDetailDialogInfo.analysisData = gridAnalysisData
}

/**
 * 关闭网格显示详情
 */
const closeAnalysisDetailDialog = () => {
  analysisDetailDialogInfo.visiable = false
}

/**
 *  打开网格类型详情表格数据新增弹窗
 * @param title  弹窗标题
 */
const addGridTypeDialog = (title: string) => {
  // 判断gridId是否存在，如果不存在，提示选择网格
  if (!searchData.value || !searchData.value.gridId) {
    ElMessage({
      message: '请选择网格后添加网格类型',
      type: 'error',
    })
    return
  }
  gridTypeDialogProps.value.dialogVisible = true
  gridTypeDialogProps.value.dialogTitle = title
  _.set(gridTypeDialogProps.value.gridTypeInfo, 'gridId', searchData.value.gridId)
}

/**
 * 打开网格类型详情表格数据编辑弹窗
 * @param title  弹窗标题
 */
const editGridTypeDialog = (title: string) => {
  // 判断gridId和gridTypeId是否存在，如果不存在，提示选择网格和网格类型
  if (!searchData.value || !searchData.value.gridId || !searchData.value.gridTypeId) {
    ElMessage({
      message: '请选择网格和网格类型后编辑',
      type: 'error',
    })
    return
  }
  gridTypeDialogProps.value.dialogVisible = true
  gridTypeDialogProps.value.dialogTitle = title
  gridTypeDialogProps.value.gridTypeInfo = searchData.value
}

/**
 * 关闭网格类型弹窗，刷新网格类型数据
 */
const closeGridTypeDialog = async () => {
  gridTypeDialogProps.value.dialogVisible = false
  gridTypeDialogProps.value.gridTypeInfo = {}
  await initGridType(searchData.value.gridId)
}

/**
 * 更新网格类型数据分析结果
 */
const updateGridTypeAnalysisResult = async () => {
  if (!searchData.value || !searchData.value.gridId) {
    ElMessage({
      message: '请选择网格后更新网格类型数据分析结果',
      type: 'error',
    })
    return
  }
  gridTypeAnalysisData.value.loading = true
  const gridTypeId = searchData.value.gridTypeId
  const gridTypeAnalysisRes = await gridTypeAnalysisApi.updateGridTypeAnalysis(gridTypeId)
  if (gridTypeAnalysisRes && gridTypeAnalysisRes.success) {
    ElMessage({
      message: gridTypeAnalysisRes.message,
      type: 'success',
    })
    // 更新成功后重新获取并格式化数据
    await initGridTypeAnalysisData(gridTypeId)
  }
  gridTypeAnalysisData.value.loading = false
}

/**
 * 更新网格数据分析结果
 */
const updateGridAnalysisResult = async () => {
  gridAnalysisData.value.loading = true
  const gridAnalysisRes = await gridAnalysisApi.updateGridAnalysis()
  if (gridAnalysisRes && gridAnalysisRes.success) {
    ElMessage({
      message: gridAnalysisRes.message,
      type: 'success',
    })
    const gridId = searchData.value.gridId
    if (gridId) {
      // 更新成功后重新获取并格式化数据
      await initGridAnalysisData(gridId)
    }
  }
  gridAnalysisData.value.loading = false
}

// 销毁
onUnmounted(() => {
  // 输出销毁提示
  console.log('销毁:', '网格分析')
})

// 打开上传文件同步网格类型数据弹窗
const openSyncGridDialog = () => {
  gridSyncFileUploadDialogParams.value.dialogVisible = true
}

// 关闭上传文件同步网格类型数据弹窗
const closeGridSyncDialog = () => {
  gridSyncFileUploadDialogParams.value.dialogVisible = false
}

// 打开上传文件同步交易记录数据弹窗
const openSyncRecordDialog = () => {
  gridRecordSyncFileUploadDialogParams.value.dialogVisible = true
}

// 关闭上传文件同步交易记录数据弹窗
const closeRecordSyncDialog = () => {
  gridRecordSyncFileUploadDialogParams.value.dialogVisible = false
}

const exportGridData = () => {
  window.open(import.meta.env.VITE_API_BASEPATH + '/grid_type_detail_file_sync/file')
}

// 下载网格交易记录数据
const exportGridRecordData = () => {
  window.open(import.meta.env.VITE_API_BASEPATH + '/grid_record_all_sync/file')
}
</script>
<style></style>
