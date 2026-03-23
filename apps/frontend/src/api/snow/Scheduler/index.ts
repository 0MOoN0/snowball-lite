import request from '@/config/axios'
import type {
  SchedulerInfo,
  SchedulerPersistencePolicyView,
  UpdateSchedulerPersistencePolicyPayload
} from './types'
import type { JobInfo } from './job/types'

const serivceUrl = 'scheduler'

export const getSchedulerInfo = (): Promise<IResponse<SchedulerInfo>> => {
  return request.get({ url: serivceUrl })
}

export const getJobList = (): Promise<IResponse<JobInfo[]>> => {
  return request.get({ url: serivceUrl + '/jobs' })
}

export const updateJobPersistencePolicy = (
  data: UpdateSchedulerPersistencePolicyPayload
): Promise<IResponse<SchedulerPersistencePolicyView>> => {
  return request.put({ url: serivceUrl + '/persistence-policies', data })
}
