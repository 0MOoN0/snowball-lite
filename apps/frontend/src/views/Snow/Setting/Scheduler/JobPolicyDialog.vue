<template>
  <Dialog v-model="dialogShow" :title="dialogTitle" @close="closeDialog" center width="520px">
    <div class="policy-dialog">
      <el-alert
        title="策略决定任务在成功执行后要不要保留运行记录；错误和错过执行仍会保留。"
        type="info"
        :closable="false"
        show-icon
        class="mb-4"
      />
      <el-alert
        v-if="isReadonly"
        title="当前任务不支持切换策略，只能查看默认值和当前生效值。"
        type="info"
        :closable="false"
        show-icon
        class="mb-4"
      />
      <el-alert
        v-if="props.jobInfo?.policyReason"
        :title="isReadonly ? '当前任务为什么只读' : '当前任务策略说明'"
        type="warning"
        :description="props.jobInfo.policyReason"
        :closable="false"
        show-icon
        class="mb-4"
      />
      <el-descriptions :column="1" border>
        <el-descriptions-item label="任务名称">
          {{ props.jobInfo?.name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="默认策略">
          <el-tag>{{ props.jobInfo?.defaultPolicy || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前生效策略">
          <el-tag type="success">{{ props.jobInfo?.effectivePolicy || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="策略来源">
          <el-tag :type="policySourceTagType">{{ policySourceLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="可选策略">
          {{ supportedPolicyText }}
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions :column="1" border class="mt-4">
        <el-descriptions-item label="策略说明">
          <div class="policy-help-list">
            <div
              v-for="policy in explainedPolicies"
              :key="policy.code"
              class="policy-help-item"
            >
              <el-tag size="small" :type="policy.code === activePolicy ? 'success' : 'info'">
                {{ policyLabel(policy.code) }}
              </el-tag>
              <span class="policy-help-text">{{ policy.description }}</span>
            </div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="来源说明">
          <div class="policy-help-list">
            <div class="policy-help-item">
              <el-tag size="small" type="info">默认值</el-tag>
              <span class="policy-help-text">当前任务没有单独覆盖，直接使用代码里登记的默认策略。</span>
            </div>
            <div class="policy-help-item">
              <el-tag size="small" type="warning">覆盖值</el-tag>
              <span class="policy-help-text">这个任务被单独改过策略，当前生效值来自后端持久化覆盖配置。</span>
            </div>
          </div>
        </el-descriptions-item>
      </el-descriptions>

      <el-form label-width="96px" class="mt-4">
        <el-form-item label="设置策略">
          <el-select
            v-model="formModel.policy"
            placeholder="请选择策略"
            :disabled="isReadonly || saving"
            class="w-full"
          >
            <el-option
              v-for="policy in policyOptions"
              :key="policy"
              :label="policyLabel(policy)"
              :value="policy"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <ElButton @click="closeDialog">关闭</ElButton>
      <ElButton type="primary" :disabled="isReadonly" :loading="saving" @click="savePolicy">
        保存策略
      </ElButton>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import * as schedulerApi from '@/api/snow/Scheduler'
import type { JobInfo } from '@/api/snow/Scheduler/job/types'
import Dialog from '@/components/Dialog/src/Dialog.vue'
import { ElMessage } from 'element-plus'
import { computed, reactive, ref, watch, type PropType } from 'vue'

const emit = defineEmits(['closeDialog', 'saved', 'update:dialogVisible'])

const props = defineProps({
  dialogVisible: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: ''
  },
  jobInfo: {
    type: Object as PropType<JobInfo | null>,
    default: null
  }
})

const dialogShow = computed({
  get: () => props.dialogVisible,
  set: (val) => emit('update:dialogVisible', val)
})

const formModel = reactive({
  policy: ''
})

const saving = ref(false)

const policyOptions = computed(() => props.jobInfo?.supportedPolicies || [])

const isReadonly = computed(() => props.jobInfo?.policySwitchable === false || policyOptions.value.length <= 1)

const POLICY_DESCRIPTIONS: Record<string, string> = {
  full: '保留完整执行轨迹。成功、失败、错过执行都会按当前规则写入运行记录。',
  signal_only: '只在本次成功执行确实处理了业务信号时保留成功记录；空轮询或无结果成功不会额外写入。',
  error_only: '只保留错误和错过执行，成功执行不写成功记录，适合只关心异常的维护型任务。'
}

const explainedPolicies = computed(() => {
  const seen = new Set<string>()
  return policyOptions.value
    .filter((policy) => {
      if (seen.has(policy)) {
        return false
      }
      seen.add(policy)
      return true
    })
    .map((policy) => ({
      code: policy,
      description: POLICY_DESCRIPTIONS[policy] || '当前页面还没有这类策略的专门说明，请以后端返回值为准。'
    }))
})

const activePolicy = computed(
  () => formModel.policy || props.jobInfo?.effectivePolicy || props.jobInfo?.defaultPolicy || ''
)

const supportedPolicyText = computed(() => {
  if (!policyOptions.value.length) {
    return '-'
  }
  return policyOptions.value.join(' / ')
})

const policySourceLabel = computed(() => {
  if (props.jobInfo?.policySource === 'override') {
    return '覆盖值'
  }
  return '默认值'
})

const policySourceTagType = computed(() => {
  if (props.jobInfo?.policySource === 'override') {
    return 'warning'
  }
  return 'info'
})

const policyLabel = (policy: string) => {
  if (policy === props.jobInfo?.defaultPolicy) {
    return `${policy}（默认）`
  }
  return policy
}

const syncFormModel = () => {
  formModel.policy = props.jobInfo?.effectivePolicy || props.jobInfo?.defaultPolicy || ''
}

watch(
  () => props.jobInfo,
  () => {
    syncFormModel()
  },
  { immediate: true, deep: true }
)

watch(
  () => props.dialogVisible,
  (visible) => {
    if (visible) {
      syncFormModel()
    }
  }
)

const closeDialog = () => {
  dialogShow.value = false
  emit('closeDialog')
}

const savePolicy = async () => {
  if (!props.jobInfo?.jobId || !formModel.policy) {
    ElMessage.error('任务或策略不能为空')
    return
  }
  saving.value = true
  try {
    const res = await schedulerApi.updateJobPersistencePolicy({
      jobId: props.jobInfo.jobId,
      policy: formModel.policy
    })
    if (res?.success) {
      ElMessage.success(res.message || '策略保存成功')
      emit('saved', props.jobInfo.jobId)
      closeDialog()
      return
    }
    ElMessage.error(res?.message || '策略保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.policy-dialog {
  width: 100%;
}
</style>
