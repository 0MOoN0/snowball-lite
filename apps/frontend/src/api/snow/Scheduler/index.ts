import request from '@/config/axios'

const serivceUrl = 'scheduler'

export const getSchedulerInfo = (): Promise<IResponse> => {
    return request.get({ url: serivceUrl })
}

export const getJobList = (): Promise<IResponse> => {
    return request.get({ url: serivceUrl+'/jobs' })
}
