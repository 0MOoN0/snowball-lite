import request from '@/config/axios'
export const getGridPercent = (params: {} | any | null): Promise<IResponse> => {
    return request.get({ url: 'charts/grid/percent', params })
}
