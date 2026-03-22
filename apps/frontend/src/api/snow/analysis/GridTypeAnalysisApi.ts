import request from '@/config/axios'

export const getGridTypeAnalysis = (grid_type_id: any): Promise<IResponse> => {
    return request.get({ url: '/api/analysis/grid-type-result/' + grid_type_id })
}

export const updateGridTypeAnalysis = (grid_type_id: any): Promise<IResponse> => {
    return request.put({ url: '/api/analysis/grid-type-result/' + grid_type_id })
}