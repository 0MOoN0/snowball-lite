import request from '@/config/axios'

export const getGridAnalysis = (grid_id: any): Promise<IResponse> => {
    return request.get({ url: '/api/analysis/grid-result/' + grid_id })
}

export const updateGridAnalysis = (): Promise<IResponse> => {
    return request.put({ url: '/api/analysis/grid-result/' })
}