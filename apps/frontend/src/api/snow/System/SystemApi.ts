import request from '@/config/axios'

/**
 * 测试token是否有效
 *
 * @param params 包含 token 和 userid
 * @returns {Promise<IResponse>} 返回结果
 */
export const tokenTestResult = (params: { xq_a_token: string; u: string }): Promise<IResponse> => {
  return request.get({ url: '/token_test/result', params })
}
