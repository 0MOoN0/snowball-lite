import request from '@/config/axios'

const systemSettingUrl = 'system'

export const updateToken = (data: any): Promise<IResponse<any>> => {
    return request.put({ url: systemSettingUrl + '/token', data: data })
}

export const getToken = (): Promise<IResponse<any>> => {
    return request.get({ url: systemSettingUrl + '/token' })
}