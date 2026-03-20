import request from '@/config/axios'
export const getAllTransaction = (): Promise<IResponse<any>> => {
  return request.get({ url: 'api/charts/transaction/summary' })
}

export const getAmountTransaction = (): Promise<IResponse<any>> => {
  return request.get({ url: 'api/charts/transaction/amount' })
}

export const getTransactionProfitRank = (): Promise<IResponse<any>> => {
  return request.get({ url: 'api/charts/transaction/profit-rank' })
}  