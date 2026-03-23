export interface SchedulerInfo {
  current_host: string
  running: boolean
}

export type SchedulerPolicySource = 'default' | 'override'

export interface SchedulerPersistencePolicyView {
  jobId: string
  defaultPolicy: string
  effectivePolicy: string
  policySource: SchedulerPolicySource
  supportedPolicies: string[]
}

export interface UpdateSchedulerPersistencePolicyPayload {
  jobId: string
  policy: string
}
