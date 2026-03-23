<template>
  <ContentWrap v-if="runtimeCapabilityFlags.scheduler" title="任务列表" class="mt-5">
    <Descriptions title="定时任务概览" :data="displaySchedulerInfo" :schema="schedulerInfoSchema" class="mb-5" />
    <el-alert
      title="策略说明：full 会保留完整执行记录；signal_only 只在成功执行真正处理到业务信号时保留成功记录；error_only 只保留错误和错过执行。点击“设置策略/查看策略”可查看当前任务为什么能改或为什么只读。"
      type="info"
      :closable="false"
      show-icon
      class="mb-4"
    />
    <el-table
      :data="jobList"
      stripe
      :default-sort="{ prop: 'next_run_time', order: 'ascending' }"
      :cell-style="{ textAlign: 'center' }"
    >
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="func" label="调用方法" />
      <el-table-column prop="args" label="参数列表" show-overflow-tooltip width="100px" />
      <el-table-column prop="kwargs" label="关键字参数字典" :formatter="kwargsFormatter" show-overflow-tooltip />
      <el-table-column prop="trigger" label="触发器" show-overflow-tooltip width="70px">
        <template #default="scope">
          <el-tag>{{ scope.row.trigger }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="defaultPolicy" label="默认策略" width="120">
        <template #default="scope">
          <el-tag>{{ scope.row.defaultPolicy || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="effectivePolicy" label="当前生效策略" width="140">
        <template #default="scope">
          <el-tag type="success">{{ scope.row.effectivePolicy || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="policySource" label="策略来源" width="110">
        <template #default="scope">
          <el-tag :type="getPolicySourceTagType(scope.row.policySource)">
            {{ getPolicySourceText(scope.row.policySource) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="nextRunTime" label="下一次运行时间" :formatter="dataFormat" sortable />
      <el-table-column prop="schedulerRunTime" label="最近一次执行时间" :formatter="dataFormat" sortable />
      <el-table-column prop="exectionSate" label="最近一次执行结果">
        <template #default="scope">
          <el-tag :type="getExectionTagStyle(scope.row.executionState)">{{
            getExectionStateText(scope.row.executionState)
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="successRate" label="执行成功率" sortable />
      <el-table-column prop="actions" label="操作" fixed="right" width="240px">
        <template #default="scope">
          <el-space direction="horizontal">
            <el-space direction="vertical">
              <el-button
                size="small"
                type="primary"
                text
                icon="VideoPlay"
                @click="operateJob(scope.row, operationMap.run)"
                :disabled="disRunableList[scope.row.jobId]"
                >立即运行</el-button
              >
              <el-button
                size="small"
                type="success"
                text
                icon="View"
                @click="operateJob(scope.row, operationMap.resume)"
                :disabled="!!scope.row.nextRunTime"
                >恢复任务</el-button
              >
              <el-button
                size="small"
                type="danger"
                text
                icon="Edit"
                @click="operateJob(scope.row, operationMap.pause)"
                :disabled="!scope.row.nextRunTime"
                >停止任务</el-button
              >
            </el-space>
            <el-space direction="vertical">
              <el-button size="small" type="primary" text icon="View" @click="viewJobDetail(scope.row)"
                >查看任务</el-button
              >
              <el-button size="small" type="primary" text icon="Setting" @click="openPolicyDialog(scope.row)">
                {{ jobPolicyReadonly(scope.row) ? '查看策略' : '设置策略' }}
              </el-button>
              <el-button v-if="jobPolicyReadonly(scope.row)" size="small" type="info" text disabled>
                策略只读
              </el-button>
              <el-button size="small" type="primary" text icon="Document" @click="viewLogs(scope.row)"
                >查看日志</el-button
              >
              <el-button size="small" type="danger" text icon="Delete" :disabled="true">删除任务</el-button>
            </el-space>
          </el-space>
        </template>
      </el-table-column>
    </el-table>
  </ContentWrap>
  <ContentWrap v-else title="任务列表" class="mt-5">
    <el-alert title="当前运行配置未开启 scheduler" type="warning" :closable="false" show-icon />
  </ContentWrap>
  <template v-if="runtimeCapabilityFlags.scheduler">
    <JobDetailDialog
      :dialog-visible="jobDetailDialog.dialogVisible"
      :dialog-title="jobDetailDialog.dialogTtile"
      @close-dialog="closeEditDailog"
      :job-info="jobDetailDialog.jobInfo"
    />
    <JobPolicyDialog
      :dialog-visible="jobPolicyDialog.dialogVisible"
      :dialog-title="jobPolicyDialog.dialogTitle"
      :job-info="jobPolicyDialog.jobInfo"
      @close-dialog="closePolicyDialog"
      @saved="handlePolicySaved"
    />
    <JobLogDialog
      :dialog-visible="jobLogDialog.dialogVisible"
      :dialog-title="jobLogDialog.dialogTitle"
      @close-dialog="closeLogDailog"
      :job-info="jobLogDialog.jobInfo ?? undefined"
    />
    <JobRunnerDialog
      :dialog-visible="jobRunnerDialog.dialogVisible"
      :dialog-title="jobRunnerDialog.dialogTitle"
      @close-dialog="closeJobRunnerDialog"
      :job-info="jobRunnerDialog.jobInfo ?? undefined"
      @run-job="runJob"
    />
  </template>
</template>
<script lang="ts" setup>
import * as schedulerApi from '@/api/snow/Scheduler/index'
import * as schedulerJobApi from '@/api/snow/Scheduler/job/index'
import { runtimeCapabilityFlags } from '@/config/runtimeProfile'
import { ContentWrap } from '@/components/ContentWrap'
import { Descriptions } from '@/components/Descriptions'
import JobDetailDialog from './JobDetailDialog.vue'
import JobPolicyDialog from './JobPolicyDialog.vue'
import JobLogDialog from './JobLogDialog.vue'
import JobRunnerDialog from './JobRunnerDialog.vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { cloneDeep, set, has, join } from 'lodash-es'
import { reactive, ref, watch, onUnmounted, computed } from 'vue'
import { JobInfo } from '@/api/snow/Scheduler/job/types'
import type { SchedulerInfo } from '@/api/snow/Scheduler/types'

// === 属性
const schedulerInfo = reactive<SchedulerInfo>({
  current_host: '',
  running: false,
  healthy: false,
  health_message: '',
  runtime_backend: '',
})

const schedulerInfoSchema = reactive<DescriptionsSchema[]>([
  {
    field: 'current_host',
    label: '主机地址',
  },
  {
    field: 'running',
    label: '运行状态',
  },
  {
    field: 'healthy',
    label: '健康状态',
  },
  {
    field: 'runtime_backend',
    label: '调度后端',
  },
])

const jobList = ref<JobInfo[]>([])

const jobDetailDialog = reactive({
  dialogVisible: false,
  dialogTtile: '',
  jobInfo: null as JobInfo | null,
})

const jobPolicyDialog = reactive({
  dialogVisible: false,
  dialogTitle: '',
  jobInfo: null as JobInfo | null,
})

const exectionStateMap = reactive({ 0: '已提交', 1: '已执行', 2: '执行错误', 3: '错过执行' })

const operationMap = reactive({ run: 'run', pause: 'pause', resume: 'resume' })

// 任务日志对话框
const jobLogDialog = reactive({
  dialogVisible: false,
  dialogTitle: '',
  jobInfo: null as JobInfo | null,
})

// 任务提交对话框属性
const jobRunnerDialog = reactive({
  dialogVisible: false,
  dialogTitle: '',
  jobInfo: null as JobInfo | null,
})
// 定时器
const intervalId = ref<NodeJS.Timeout | null>(null)

// 定时器容器，key为jobId，值为定时器
const jobRunnerTimerMap = reactive<Map<string, { timestamp: Date; interval: NodeJS.Timeout }>>(new Map())

// 是否可运行列表
const disRunableList = ref<Record<string, boolean>>({})

// 根据任务列表重建可运行状态映射
const rebuildDisRunableList = (jobs: JobInfo[]) => {
  const map: Record<string, boolean> = {}
  jobs.forEach((job) => {
    map[job.jobId] = jobDisRunnable(job)
  })
  disRunableList.value = map
}

// === 属性 end

/**
 * 初始化定时任务信息
 */
const initSchedulerInfo = async () => {
  if (!runtimeCapabilityFlags.scheduler) {
    return
  }
  const res = await schedulerApi.getSchedulerInfo()
  console.log(`res : `, res)
  if (res) {
    // 只复制数据，不做转换
    Object.assign(schedulerInfo, res.data)
    // 删除这里的转换，因为我们使用计算属性来处理
  }
}
initSchedulerInfo()

const initJobList = async () => {
  if (!runtimeCapabilityFlags.scheduler) {
    return
  }
  const res = await schedulerApi.getJobList()
  if (res && res.data) {
    jobList.value = res.data
    // 遍历列表，填充runableList
    rebuildDisRunableList(jobList.value)
  }
}
initJobList()

// == hook
watch(schedulerInfo, () => {
  console.log(`schedulerInfo : `, schedulerInfo)
})

// == hook end

// 组件卸载时清理轮询定时器
onUnmounted(() => {
  jobRunnerTimerMap.forEach((value) => {
    clearInterval(value.interval)
  })
  jobRunnerTimerMap.clear()
  if (intervalId.value) {
    clearInterval(intervalId.value)
  }
})

// 判断任务是否可以运行
const jobDisRunnable = (jobInfo: JobInfo) => {
  // 打印日志
  // 如果任务执行状态为0并且执行时间小于15分钟，返回false
  if (jobInfo.executionState == 0 && dayjs().diff(dayjs(jobInfo.schedulerRunTime), 'minute') < 15) {
    return true
  }
  return false
}

// 使用日志结果更新指定任务数据，若不存在则回退刷新列表
const updateJobByLog = (jobId: string, log: Partial<JobInfo>) => {
  const idx = jobList.value.findIndex((j) => j.jobId === jobId)
  if (idx !== -1) {
    const job = jobList.value[idx]
    if (typeof log.executionState === 'number') job.executionState = log.executionState
    if (log.schedulerRunTime) job.schedulerRunTime = log.schedulerRunTime as string
    if (typeof log.exception !== 'undefined') job.exception = log.exception as string
    if (typeof log.traceback !== 'undefined') job.traceback = log.traceback as string
    // 如果日志返回了下一次运行时间，则同步更新
    if ((log as any).nextRunTime) job.nextRunTime = (log as any).nextRunTime as string
    // 根据更新后的任务状态重建运行限制
    disRunableList.value[jobId] = jobDisRunnable(job)
  } else {
    // 未找到则整体刷新一次
    refreshJobData()
  }
}

// 子组件触发任务运行事件
const runJob = async (jobId: string) => {
  try {
    // 将当前任务设置为不可运行
    disRunableList.value[jobId] = true
    // 设置运行状态
    jobList.value.forEach((job) => {
      if (job.jobId == jobId) {
        job.executionState = 0
      }
    })
    // 往定时map里面添加一个定时器
    jobRunnerTimerMap.set(jobId, {
      timestamp: new Date(),
      interval: setInterval(async () => {
        try {
          // 打印日志
          const jobLogRes = await schedulerJobApi.getJobLog(jobId)
          const jobRunnerInfo = jobRunnerTimerMap.get(jobId)
          if (!jobRunnerInfo) {
            console.warn(`No timer info found for jobId ${jobId}`)
            return
          }
          // 判断时间状态是否超过15分钟，如果超过了15分钟，清除这个定时器
          if (jobLogRes.data.executionState !== 0 || dayjs().diff(dayjs(jobRunnerInfo.timestamp), 'minute') > 15) {
            // 清除定时器
            clearInterval(jobRunnerInfo.interval)
            jobRunnerTimerMap.delete(jobId)
            // 允许执行任务
            disRunableList.value[jobId] = false
            // 使用日志结果更新该任务，避免不必要的列表刷新
            updateJobByLog(jobId, jobLogRes.data)
          }
        } catch (error) {
          console.error(`Error fetching job log for jobId ${jobId}:`, error)
        }
      }, 5000),
    })
  } catch (error) {
    console.error(`Error starting job with jobId ${jobId}:`, error)
  }
}

// 刷新指定任务的数据，若未找到则回退为刷新全列表
const refreshJobData = async (jobId?: string) => {
  try {
    const res = await schedulerApi.getJobList()
    if (res && res.data) {
      const list: JobInfo[] = res.data
      if (jobId) {
        const fresh = list.find((j) => j.jobId === jobId)
        if (fresh) {
          const idx = jobList.value.findIndex((j) => j.jobId === jobId)
          if (idx !== -1) {
            jobList.value[idx] = fresh
          } else {
            jobList.value.push(fresh)
          }
          disRunableList.value[jobId] = jobDisRunnable(fresh)
          return
        }
      }
      // 若没有提供jobId或未找到对应任务，则刷新整个列表
      jobList.value = list
      rebuildDisRunableList(list)
    }
  } catch (e) {
    console.error('refreshJobData error', e)
  }
}
const dataFormat = (_, __, date) => {
  if (date) {
    return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
  }
  return ''
}

const kwargsFormatter = (_, __, kwargs) => {
  return JSON.stringify(kwargs)
}

const viewJobDetail = (jobInfo: JobInfo) => {
  jobDetailDialog.dialogVisible = true
  // 处理参数列表和关键字参数字典
  jobDetailDialog.jobInfo = cloneDeep(jobInfo)
  // 将关键字字典转为JSON字符串
  set(jobDetailDialog.jobInfo, 'kwargs', JSON.stringify(jobInfo.kwargs || {}))
  // 将args数组转为以,分割的字符串
  if (has(jobInfo, 'args')) {
    set(jobDetailDialog.jobInfo, 'args', join(jobInfo.args, ','))
  }
  jobDetailDialog.dialogTtile = '查看 ' + jobInfo.name + ' 任务详情'
}

const closeEditDailog = () => {
  jobDetailDialog.dialogVisible = false
}

const jobPolicyReadonly = (jobInfo: JobInfo) => {
  return (jobInfo.supportedPolicies || []).length <= 1
}

const openPolicyDialog = (jobInfo: JobInfo) => {
  jobPolicyDialog.dialogVisible = true
  jobPolicyDialog.dialogTitle = `${jobPolicyReadonly(jobInfo) ? '查看' : '设置'} ${jobInfo.name} 策略`
  jobPolicyDialog.jobInfo = cloneDeep(jobInfo)
}

const closePolicyDialog = () => {
  jobPolicyDialog.dialogVisible = false
}

const handlePolicySaved = async (jobId: string) => {
  await refreshJobData(jobId)
}

const getExectionStateText = (state: number) => {
  if (state in exectionStateMap) {
    return exectionStateMap[state]
  }
  return '未知'
}

const getExectionTagStyle = (state: number) => {
  if (state in exectionStateMap) {
    if (state == 0) {
      return ''
    } else if (state == 1) {
      return 'success'
    } else if (state == 2) {
      return 'danger'
    } else if (state == 3) {
      return 'warning'
    }
  }
  return 'info'
}

const getPolicySourceText = (source: string) => {
  if (source === 'override') {
    return '覆盖值'
  }
  return '默认值'
}

const getPolicySourceTagType = (source: string) => {
  if (source === 'override') {
    return 'warning'
  }
  return 'info'
}

// == 日志相关操作
const viewLogs = (jobInfo: JobInfo) => {
  jobLogDialog.dialogVisible = true
  jobLogDialog.dialogTitle = '查看 ' + jobInfo.name + ' 任务日志详情'
  jobLogDialog.jobInfo = jobInfo
}

/**
 * 关闭日志对话框
 */
const closeLogDailog = () => {
  jobLogDialog.dialogVisible = false
}

/**
 * 关闭作业运行器对话框
 *
 * 该函数将作业运行器对话框的可见性设置为 false，从而关闭对话框。
 */
const closeJobRunnerDialog = () => {
  jobRunnerDialog.dialogVisible = false
}

// == scheduler job相关操作
/**
 * 对指定任务进行操作
 *
 * @param jobInfo 任务信息对象
 * @param operation 要执行的操作类型operationMap，字符串类型，可选值为："run"（运行）、"pause"（暂停）、"resume"（恢复）
 * @returns 无返回值
 */
const operateJob = async (jobInfo: JobInfo, operation: string) => {
  // 判断是运行、暂停还是恢复
  var res
  switch (operation) {
    case operationMap.run:
      // res = await schedulerJobApi.runJob({ jobId: jobInfo.jobId })
      //开启jobRunner窗口
      jobRunnerDialog.dialogVisible = true
      jobRunnerDialog.dialogTitle = '运行 ' + jobInfo.name + ' 任务作业'
      jobRunnerDialog.jobInfo = jobInfo
      return
    case operationMap.pause:
      res = await schedulerJobApi.pauseJob({ jobId: jobInfo.jobId })
      break
    case operationMap.resume:
      res = await schedulerJobApi.resumeJob({ jobId: jobInfo.jobId })
      break
    default:
      ElMessage.error('操作类型错误')
  }
  if (res && res.data) {
    ElMessage.success(res.message)
    initJobList()
  }
}

// 创建一个计算属性用于显示
const displaySchedulerInfo = computed(() => {
  return {
    current_host: schedulerInfo.current_host,
    running: schedulerInfo.running ? '已启动' : '未启动',
    healthy: schedulerInfo.running
      ? schedulerInfo.healthy
        ? '运行正常'
        : schedulerInfo.health_message || '假活/卡住'
      : '-',
    runtime_backend: schedulerInfo.runtime_backend || '-',
  }
})
</script>
<style></style>
