import request from '@/config/axios'
export const testCodeConnect = (codeType: string, code: string): Promise<IResponse> => {
  return request.get({ url: 'asset_code/test_conn/' + codeType + '/' + code })
}
