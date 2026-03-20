/**
 * 根据给定数字对数字进行格式化
 * @param num
 * @currency 是否作为货币处理
 * @potions 自定义参数
 * @return str 返回一个格式化后的字符串
 */
const numFormat = (num: number, currency = false, options = {}): string => {
  if (options) {
    return num.toLocaleString('zh-CN', options)
  }
  // 处理货币信息
  if (currency) {
    options = {
      style: 'currency',
      currency: 'CNY',
      maximumSignificantDigits: 3
    }
    return num.toLocaleString('zh-CN', options)
  }
  // 默认为数字处理
  options = {
    style: 'decimal',
    maximumSignificantDigits: 3
  }
  return num.toLocaleString('zh-CN', options)
}

export { numFormat }
