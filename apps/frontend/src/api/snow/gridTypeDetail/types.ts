interface GridTypeDetail {
  /**
   * 实际出股数
   */
  actualSellShares?: number
  /**
   * 档位
   */
  gear?: string
  /**
   * 对应的网格ID
   */
  gridId?: number
  /**
   * 网格类型ID
   */
  gridTypeId?: number
  /**
   * 主键ID
   */
  id?: number
  /**
   * 是否处于当前档位
   */
  isCurrent?: boolean
  /**
   * 收益（单位:分）
   */
  profit?: number
  /**
   * 买入金额（单位:分）
   */
  purchaseAmount?: number
  /**
   * 买入价格（单位:分）
   */
  purchasePrice?: number
  /**
   * 入股数
   */
  purchaseShares?: number
  /**
   * 留存股数
   */
  saveShare?: number
  /**
   * 留股收益（单位:分）
   */
  saveShareProfit?: number
  /**
   * 卖出金额（单位:分）
   */
  sellAmount?: number
  /**
   * 卖出价格（单位:分）
   */
  sellPrice?: number
  /**
   * 出股数
   */
  sellShares?: number
  /**
   * 卖出触发价（单位:分）
   */
  triggerPurchasePrice?: number
  /**
   * 卖出触发价（单位:分）
   */
  triggerSellPrice?: number
}
