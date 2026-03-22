import { EChartsOption } from 'echarts'
import 'echarts-wordcloud'
import { useI18n } from '@/hooks/web/useI18n'

const { t } = useI18n()


export const transacionOptions: EChartsOption = {
  title: {
    text: '收益图',
    left: 'center'
  },
  xAxis: {
    data: [],
    boundaryGap: true,
    axisTick: {
      show: true
    }
  },
  grid: {
    left: 50,
    right: 50,
    bottom: 80,
    top: 80,
    containLabel: false
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    },
    padding: [5, 10]
  },
  yAxis: [
    {
      type: 'value',
      name: '金额/数值',
      axisTick: { show: false }
    },
    {
      type: 'value',
      name: '比率(%)',
      axisTick: { show: false },
      axisLabel: { formatter: (val: number) => `${val}%` }
    }
  ],
  legend: {
    data: ['利润', '现值', '投资收益率', '内部收益率', '年化收益率'],
    selected: { 利润: false, 现值: false, 投资收益率: false },
    top: 50
  },
  series: [],
  dataZoom: [
    {
      type: 'slider',
    },
    {
      type: 'inside',
    },
    {
      type: 'slider',
      yAxisIndex: 0,
    }
  ],
}


export const lineOptions: EChartsOption = {
  title: {
    text: t('analysis.monthlySales'),
    left: 'center'
  },
  xAxis: {
    data: [
      t('analysis.january'),
      t('analysis.february'),
      t('analysis.march'),
      t('analysis.april'),
      t('analysis.may'),
      t('analysis.june'),
      t('analysis.july'),
      t('analysis.august'),
      t('analysis.september'),
      t('analysis.october'),
      t('analysis.november'),
      t('analysis.december')
    ],
    boundaryGap: false,
    axisTick: {
      show: false
    }
  },
  grid: {
    left: 20,
    right: 20,
    bottom: 20,
    top: 80,
    containLabel: true
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    },
    padding: [5, 10]
  },
  yAxis: {
    axisTick: {
      show: false
    }
  },
  legend: {
    data: [t('analysis.estimate'), t('analysis.actual')],
    top: 50
  },
  series: [
    {
      name: t('analysis.estimate'),
      smooth: true,
      type: 'line',
      data: [100, 120, 161, 134, 105, 160, 165, 114, 163, 185, 118, 123],
      animationDuration: 2800,
      animationEasing: 'cubicInOut'
    },
    {
      name: t('analysis.actual'),
      smooth: true,
      type: 'line',
      itemStyle: {},
      data: [120, 82, 91, 154, 162, 140, 145, 250, 134, 56, 99, 123],
      animationDuration: 2800,
      animationEasing: 'quadraticOut'
    }
  ]
}

export const pieOptions: EChartsOption = {
  darkMode: true,
  title: {
    text: '持仓数据',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    data: [
      t('analysis.directAccess'),
      t('analysis.mailMarketing'),
      t('analysis.allianceAdvertising'),
      t('analysis.videoAdvertising'),
      t('analysis.searchEngines')
    ]
  },
  series: [
    {
      name: '持仓数据',
      type: 'pie',
      radius: '55%',
      center: ['65%', '60%'],
      data: [
        { value: 335, name: t('analysis.directAccess') },
        { value: 310, name: t('analysis.mailMarketing') },
        { value: 234, name: t('analysis.allianceAdvertising') },
        { value: 135, name: t('analysis.videoAdvertising') },
        { value: 1548, name: t('analysis.searchEngines') }
      ]
    }
  ]
}

export const barOptions: EChartsOption = {
  title: {
    text: t('analysis.weeklyUserActivity'),
    left: 'center'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: 50,
    right: 20,
    bottom: 20
  },
  xAxis: {
    type: 'category',
    data: [
      t('analysis.monday'),
      t('analysis.tuesday'),
      t('analysis.wednesday'),
      t('analysis.thursday'),
      t('analysis.friday'),
      t('analysis.saturday'),
      t('analysis.sunday')
    ],
    axisTick: {
      alignWithLabel: true
    }
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: t('analysis.activeQuantity'),
      data: [13253, 34235, 26321, 12340, 24643, 1322, 1324],
      type: 'bar'
    }
  ]
}

export const radarOption: EChartsOption = {
  legend: {
    data: [t('workplace.personal'), t('workplace.team')]
  },
  radar: {
    // shape: 'circle',
    indicator: [
      { name: t('workplace.quote'), max: 65 },
      { name: t('workplace.contribution'), max: 160 },
      { name: t('workplace.hot'), max: 300 },
      { name: t('workplace.yield'), max: 130 },
      { name: t('workplace.follow'), max: 100 }
    ]
  },
  series: [
    {
      name: `xxx${t('workplace.index')}`,
      type: 'radar',
      data: [
        {
          value: [42, 30, 20, 35, 80],
          name: t('workplace.personal')
        },
        {
          value: [50, 140, 290, 100, 90],
          name: t('workplace.team')
        }
      ]
    }
  ]
}

export const wordOptions: EChartsOption = {
  series: [
    {
      type: 'wordCloud',
      gridSize: 2,
      sizeRange: [12, 50],
      rotationRange: [-90, 90],
      shape: 'pentagon',
      width: 600,
      height: 400,
      drawOutOfBound: true,
      textStyle: {
        color: function () {
          return (
            'rgb(' +
            [
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160)
            ].join(',') +
            ')'
          )
        }
      },
      data: [
        {
          name: 'Sam S Club',
          value: 10000,
          textStyle: {
            color: 'black'
          },
          // emphasis 属性中的 textStyle 某些字段在类型声明中未包含，移除以通过类型检查
        },
        {
          name: 'Macys',
          value: 6181
        },
        {
          name: 'Amy Schumer',
          value: 4386
        },
        {
          name: 'Jurassic World',
          value: 4055
        },
        {
          name: 'Charter Communications',
          value: 2467
        },
        {
          name: 'Chick Fil A',
          value: 2244
        },
        {
          name: 'Planet Fitness',
          value: 1898
        },
        {
          name: 'Pitch Perfect',
          value: 1484
        },
        {
          name: 'Express',
          value: 1112
        },
        {
          name: 'Home',
          value: 965
        },
        {
          name: 'Johnny Depp',
          value: 847
        },
        {
          name: 'Lena Dunham',
          value: 582
        },
        {
          name: 'Lewis Hamilton',
          value: 555
        },
        {
          name: 'KXAN',
          value: 550
        },
        {
          name: 'Mary Ellen Mark',
          value: 462
        },
        {
          name: 'Farrah Abraham',
          value: 366
        },
        {
          name: 'Rita Ora',
          value: 360
        },
        {
          name: 'Serena Williams',
          value: 282
        },
        {
          name: 'NCAA baseball tournament',
          value: 273
        },
        {
          name: 'Point Break',
          value: 265
        }
      ]
    }
  ]
}

// 网格交易距离百分比图表设置
export const gridPercentOptoins: EChartsOption = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  title: {
    text: '网格交易距离百分比',
    left: 'center'
  },
  legend: {
    top: 50
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: 80,
    containLabel: true
  },
  xAxis: {
    type: 'value'
  },
  yAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun1']
  },
  series: []
}