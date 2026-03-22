import { useValidator } from '@/hooks/web/useValidator'

const { required } = useValidator()

/**
 * 指数基础字段配置
 * 所有指数类型共有的表单字段
 */
export const createBaseFields = (enumOptions: {
  indexTypeEnum: any[]
  investmentStrategyEnum: any[]
  currencyEnum: any[]
  marketEnum: any[]
  indexStatusEnum: any[]
  weightMethodEnum: any[]
  calculationMethodEnum: any[]
  onIndexTypeChange: (val: number) => void
}): FormSchema[] => {
  const {
    indexTypeEnum,
    investmentStrategyEnum,
    currencyEnum,
    marketEnum,
    indexStatusEnum,
    weightMethodEnum,
    calculationMethodEnum,
    onIndexTypeChange
  } = enumOptions

  return [
    {
      field: 'indexName',
      label: '指数名称',
      component: 'Input',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请输入指数名称',
      },
      formItemProps: {
        rules: [required()],
      },
    },
    {
      field: 'indexCode',
      label: '指数代码',
      component: 'Input',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请输入指数代码',
      },
      formItemProps: {
        rules: [required()],
      },
    },
    {
      field: 'indexType',
      label: '指数类型',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择指数类型',
        options: indexTypeEnum || [],
        onChange: onIndexTypeChange,
      },
      formItemProps: {
        rules: [required()],
      },
    },
    {
      field: 'market',
      label: '市场',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择市场',
        options: marketEnum || [],
      },
      formItemProps: {
        rules: [required()],
      },
    },
    {
      field: 'investmentStrategy',
      label: '投资策略',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择投资策略',
        options: investmentStrategyEnum || [],
      },
    },
    {
      field: 'currency',
      label: '货币类型',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择货币类型',
        options: currencyEnum || [],
      },
    },
    {
      field: 'baseDate',
      label: '基准日期',
      component: 'DatePicker',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择基准日期',
        type: 'date',
        format: 'YYYY-MM-DD',
        valueFormat: 'YYYY-MM-DD',
      },
    },
    {
      field: 'basePoint',
      label: '基准点数',
      component: 'InputNumber',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请输入基准点数',
        min: 0,
      },
    },
    {
      field: 'weightMethod',
      label: '权重方法',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择权重方法',
        options: weightMethodEnum || [],
      },
    },
    {
      field: 'calculationMethod',
      label: '计算方法',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择计算方法',
        options: calculationMethodEnum || [],
      },
    },
    {
      field: 'indexStatus',
      label: '指数状态',
      component: 'Select',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择指数状态',
        options: indexStatusEnum || [],
      },
    },
    {
      field: 'publisher',
      label: '发布机构',
      component: 'Input',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请输入发布机构',
      },
    },
    {
      field: 'publishDate',
      label: '发布日期',
      component: 'DatePicker',
      value: null,
      colProps: {
        span: 12,
      },
      componentProps: {
        placeholder: '请选择发布日期',
        type: 'date',
        format: 'YYYY-MM-DD',
        valueFormat: 'YYYY-MM-DD',
      },
    },
    {
      field: 'description',
      label: '描述',
      component: 'Input',
      value: null,
      colProps: {
        span: 24,
      },
      componentProps: {
        type: 'textarea',
        placeholder: '请输入指数描述',
        rows: 3,
      },
    },
  ]
}