import { useValidator } from '@/hooks/web/useValidator'

const { required } = useValidator()

/**
 * 指数表单验证规则
 */
export const getFormRules = () => ({
  indexName: [required()],
  indexCode: [required()],
  indexType: [required()],
  market: [required()],
  baseDate: [
    {
      required: false,
      validator: (_rule: any, value: any, callback: any) => {
        if (value && new Date(value) > new Date()) {
          callback(new Error('基准日期不能晚于当前日期'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  basePoint: [
    {
      required: false,
      validator: (_rule: any, value: any, callback: any) => {
        if (value !== null && value !== undefined && value <= 0) {
          callback(new Error('基准点数必须大于0'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  publishDate: [
    {
      required: false,
      validator: (_rule: any, value: any, callback: any) => {
        if (value && new Date(value) > new Date()) {
          callback(new Error('发布日期不能晚于当前日期'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  sampleStockCount: [
    {
      required: false,
      validator: (_rule: any, value: any, callback: any) => {
        if (value !== null && value !== undefined && value <= 0) {
          callback(new Error('样本股票数量必须大于0'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})