import request from '@/config/axios'
export const getAssetList = (assetId: any): Promise<IResponse> => {
  return request.get({ url: 'asset_relations/'+assetId })
}