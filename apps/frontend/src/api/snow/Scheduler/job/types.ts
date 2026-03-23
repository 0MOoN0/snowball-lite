export interface JobInfo {
  args: unknown[]
  defaultPolicy: string
  effectivePolicy: string
  exception: string
  executionState: number
  func: string
  jobId: string
  kwargs: Record<string, unknown>
  maxInstances: number
  minutes: number
  misfireGraceTime: number
  name: string
  nextRunTime: string | null
  policySource: string
  schedulerRunTime: string | null
  startDate: string
  supportedPolicies: string[]
  traceback: string
  trigger: string
}
