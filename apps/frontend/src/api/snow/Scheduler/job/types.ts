
export interface JobInfo {
    args: Array<any>
    func: string
    jobId: any
    kwargs: JSON
    maxInstances: number
    minutes: number
    misfireGraceTime: number
    name: string
    nextRunTime: string
    startDate: string
    trigger: string
    exception: string
    traceback: string
    executionState: number
    schedulerRunTime: string
}
