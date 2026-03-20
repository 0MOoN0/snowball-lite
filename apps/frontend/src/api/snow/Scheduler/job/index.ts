import request from '@/config/axios'

/**
 * 运行指定任务
 *
 * @param data 任务相关数据
 * @returns 返回响应数据
 */
export const runJob = (data: any): Promise<IResponse> => {
    return request.put({ url: 'scheduler/job' + '/run', data: data })
}

/**
 * 暂停任务
 *
 * @param data 请求数据
 * @returns 返回Promise对象，Promise对象resolve为IResponse类型的响应数据
 */
export const pauseJob = (data: any): Promise<IResponse> => {
    return request.put({ url: 'scheduler/job' + '/pause', data: data })
}

/**
 * 恢复已暂停的任务
 *
 * @param data 恢复任务所需的参数
 * @returns 返回IResponse类型的Promise对象，表示恢复任务的结果
 */
export const resumeJob = (data: any): Promise<IResponse> => {
    return request.put({ url: 'scheduler/job' + '/resume', data: data })
}

/**
 * 获取作业日志
 * 
 * 该函数通过发送GET请求到'scheduler/job_log/'接口来获取作业日志信息
 * 它接受一个参数data，这个参数被用来构建请求的URL
 * 函数返回一个Promise对象，解析为IResponse类型，包含请求的响应数据
 * 
 * @param data - 用于构建请求URL的数据，具体结构取决于API设计
 * @returns 返回一个Promise对象，解析为IResponse类型，包含请求的响应数据
 */
export const getJobLog = (data: any): Promise<IResponse> => {
    return request.get({ url: 'scheduler/job_log/' + data })
}