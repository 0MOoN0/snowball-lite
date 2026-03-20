// 导入Decimal库，用于格式化数字
import Decimal from 'decimal.js'

/**
 * 根据给定数字对数字进行格式化
 * @param num
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

// 使用Decimal库格式化数字，并返回带有人民币符号的字符串，参数带有乘数和被除数
const numFormatWithCurrency = (num: number | string, multiplier: number | string |any , dividend: number | string |any , decimalPlaces:number=0): string => {
  let decimal = new Decimal(num)
  // 如果乘数不为空
  if (multiplier){
    decimal = decimal.mul(new Decimal(multiplier))
  }
  if(dividend){
    decimal = decimal.div(new Decimal(dividend))
  }

  return '￥'+decimal.toFixed(decimalPlaces)
}

export const webHelper = {
  numFormat,
  numFormatWithCurrency
}
