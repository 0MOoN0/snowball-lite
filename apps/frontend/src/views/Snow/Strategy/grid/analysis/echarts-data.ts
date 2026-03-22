import { EChartsOption } from 'echarts'

// tooltip样式和格式化函数
export const tooltipFormatter = {
  // 主要的formatter函数
  format: (params: any, allMarkPoints: any[]) => {
    // 默认tooltip内容
    let result = ''

    // 获取当前x轴坐标
    const xValue = params[0].axisValue

    // 基本tooltip内容
    if (Array.isArray(params)) {
      // 添加时间标题
      result += `<div style="font-weight:bold;font-size:14px;margin-bottom:8px;border-bottom:1px solid #eee;padding-bottom:5px;">${xValue}</div>`

      // 查找K线数据 - 可能是'data'或'日K'
      const klineItem = params.find(
        (item) => item.seriesName === 'data' || item.seriesName === '日K'
      )

      // 查找成交量数据
      const volumeItem = params.find((item) => item.seriesName === 'Volume')

      // 其他数据（均线等）
      const otherItems = params.filter(
        (item) =>
          item.seriesName !== 'data' && item.seriesName !== '日K' && item.seriesName !== 'Volume'
      )

      // 处理K线数据
      if (klineItem) {
        result += tooltipFormatter.generateKLineHTML(klineItem)
      }

      // 处理成交量数据
      if (volumeItem) {
        result += tooltipFormatter.generateVolumeHTML(volumeItem)
      }

      // 处理其他数据（均线等）
      if (otherItems.length > 0) {
        result += `<div style="margin-top:5px;border-top:1px dashed #eee;padding-top:5px;">`

        otherItems.forEach((item) => {
          result += tooltipFormatter.generateOtherItemHTML(item)
        })

        result += `</div>`
      }
    }

    // 查找当前日期是否有标记点
    const markPoints = allMarkPoints.filter((mp) => mp.date === xValue)

    // 如果有标记点，添加到tooltip
    if (markPoints && markPoints.length > 0) {
      result += `<div style="margin-top:8px;border-top:1px solid #eee;padding-top:5px;">
        <div style="font-weight:bold;margin-bottom:5px;font-size:13px;">交易信号:</div>
      `

      markPoints.forEach((mp) => {
        result += tooltipFormatter.generateMarkPointHTML(mp)
      })

      result += `</div>`
    }

    return result
  },

  // 生成K线数据HTML
  generateKLineHTML: (item: any) => {
    const color = item.color
    const value = item.value

    // 检查K线数据格式：[dataIndex，开盘价, 收盘价, 最低价, 最高价]
    if (Array.isArray(value)) {
      // 标准K线蜡烛图数据格式：[开盘价, 收盘价, 最低价, 最高价]
      if (value.length === 5) {
        const open = value[1]
        const close = value[2]
        const low = value[3]
        const high = value[4]

        // 判断是上涨还是下跌
        const isUp = close >= open
        const priceColor = isUp ? 'rgb(241,90,74)' : 'rgb(41,171,145)'

        return `<div style="margin-bottom:8px;">
          <div style="display:flex;align-items:center;margin-bottom:4px;">
            <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:5px;"></span>
            <span style="font-weight:bold;font-size:13px;">日K线</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;grid-gap:4px;margin-left:15px;">
            <div>开: <span style="font-weight:bold;color:${priceColor}">${open}</span></div>
            <div>收: <span style="font-weight:bold;color:${priceColor}">${close}</span></div>
            <div>低: <span style="font-weight:bold;color:${priceColor}">${low}</span></div>
            <div>高: <span style="font-weight:bold;color:${priceColor}">${high}</span></div>
          </div>
        </div>`
      } else {
        // 其他数组格式，直接显示
        return `<div style="display:flex;align-items:center;margin:3px 0;">
          <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:5px;"></span>
          <span style="margin-right:5px;">日K线:</span>
          <span style="font-weight:bold;">${value.join(', ')}</span>
        </div>`
      }
    } else {
      // 如果不是数组格式，直接显示
      return `<div style="display:flex;align-items:center;margin:3px 0;">
        <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:5px;"></span>
        <span style="margin-right:5px;">日K线:</span>
        <span style="font-weight:bold;">${value}</span>
      </div>`
    }
  },

  // 生成成交量HTML
  generateVolumeHTML: (item: any) => {
    const color = item.color
    const value = item.value

    // 处理不同格式的成交量数据
    let volumeValue = value
    if (typeof value === 'object' && value.value !== undefined) {
      volumeValue = value.value
    }

    // 格式化成交量，添加千位分隔符
    const formattedVolume = String(volumeValue).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

    return `<div style="margin-bottom:6px;">
      <div style="display:flex;align-items:center;">
        <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:5px;"></span>
        <span style="margin-right:5px;">成交量:</span>
        <span style="font-weight:bold;">${formattedVolume}</span>
      </div>
    </div>`
  },

  // 生成其他数据项HTML
  generateOtherItemHTML: (item: any) => {
    const color = item.color
    const seriesName = item.seriesName
    const value = item.value

    return `<div style="display:flex;align-items:center;margin:3px 0;">
      <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:5px;"></span>
      <span style="margin-right:5px;">${seriesName}:</span>
      <span style="font-weight:bold;">${value}</span>
    </div>`
  },

  // 生成标记点HTML
  generateMarkPointHTML: (markPoint: any) => {
    const direction = markPoint.direction === 1 ? '买入' : '卖出'
    const color = markPoint.direction === 1 ? '#FFD700' : '#00FFFF'
    const icon = markPoint.direction === 1 ? '↑' : '↓'
    const bgColor = markPoint.direction === 1 ? 'rgba(255,215,0,0.1)' : 'rgba(0,255,255,0.1)'

    let html = `<div style="background:${bgColor};border-radius:4px;padding:4px 8px;margin-bottom:4px;">
      <div style="display:flex;align-items:center;margin:3px 0;">
        <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:5px;border-radius:50%;"></span>
        <span style="margin-right:5px;font-weight:bold;">${direction} ${icon}</span>
        <span style="font-weight:bold;">${markPoint.price}</span>
      </div>
    `

    // 如果有其他信息，也可以添加
    if (markPoint.price || markPoint.amount || markPoint.reason) {
      html += `<div style="margin-left:15px;font-size:12px;">`

      if (markPoint.price) {
        html += `<div>价格: ${markPoint.price}</div>`
      }
      if (markPoint.amount) {
        html += `<div>数量: ${markPoint.amount}</div>`
      }
      if (markPoint.reason) {
        html += `<div>原因: ${markPoint.reason}</div>`
      }

      html += `</div>`
    }

    html += `</div>`
    return html
  }
}

// echarts的样式
export const lineOptions: EChartsOption = {
  title: {
    text: '交易图表',
    left: 'center'
  },
  xAxis: [
    // {
    //   type: 'category',
    //   data: [],
    //   boundaryGap: true,
    //   axisTick: {
    //     show: true
    //   }
    // },
    {
      type: 'category',
      data: [],
      boundaryGap: false,
      axisLine: { onZero: false },
      splitLine: { show: false },
      min: 'dataMin',
      max: 'dataMax',
      axisPointer: {
        z: 100
      }
    },
    {
      type: 'category',
      gridIndex: 1,
      data: [],
      boundaryGap: false,
      axisLine: { onZero: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      min: 'dataMin',
      max: 'dataMax'
    }
  ],
  yAxis: [
    // {
    //   axisTick: {
    //     show: false
    //   },
    //   // 取消y轴分割线
    //   splitLine: {
    //     show: false
    //   }
    // },
    {
      scale: true,
      splitArea: {
        show: true
      },
      splitLine: {
        show: false
      },
      position: 'left',
      axisLabel: {
        inside: false,
        formatter: '{value}\n'
      }
    },
    {
      scale: true,
      gridIndex: 1,
      splitNumber: 2,
      position: 'left',
      axisLine: { show: true },
      axisTick: { show: true },
      splitLine: { show: true },
      axisLabel: {
        inside: false,
        formatter: function (value) {
          return Math.abs(value).toString()
        }
      }
    }
  ],
  grid: [
    {
      left: 50,
      right: 50,
      top: 80,
      height: '60%',
      containLabel: true
    },
    {
      left: 50,
      right: 50,
      top: '75%',
      height: '20%',
      containLabel: true
    }
  ],
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      axis: 'auto'
    },
    padding: [5, 10]
  },
  legend: {
    data: ['data', 'unitCost', 'MA20', 'MA51', 'MA120', 'MA250'],
    // 默认显示 data，不显示 unitCost 和均线
    selected: {
      data: true,
      unitCost: false,
      MA20: false,
      MA51: false,
      MA120: false,
      MA250: false
    },
    top: 50
  },
  series: [],
  dataZoom: [
    {
      type: 'slider',
      xAxisIndex: [0, 1],
      start: 70,
      end: 100
    },
    {
      type: 'inside',
      xAxisIndex: [0, 1]
    }
  ],
  axisPointer: {
    link: [
      {
        xAxisIndex: 'all'
      }
    ],
    label: {
      backgroundColor: '#777'
    }
  }
}

/**
 * 主数据格式样式设置
 */
export const chartsMainSeries = {
  name: `data`,
  smooth: true,
  type: 'line',
  data: [],
  animationDuration: 500,
  animationEasing: 'cubicInOut',
  markPoint: {
    symbol: 'circle',
    symbolSize: 10,
    emphasis: {
      scale: 1.5,
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0,0,0,0.3)'
      }
    },
    itemStyle: {
      borderColor: '#000',
      borderWidth: 1,
      shadowBlur: 3,
      shadowColor: 'rgba(0,0,0,0.2)'
    },
    label: {
      position: 'top',
      offset: [0, -3],
      color: '#000',
      fontSize: 11,
      backgroundColor: 'rgba(255,255,255,0.7)',
      padding: [1, 3]
    },
    data: []
  },
  markLine: {
    symbol: ['none', 'none'],
    data: [],
    lineStyle: {
      type: 'dashed'
    }
  },
  lineStyle: {
    width: 1
  }
}

export const chartsLineSeries = {
  name: 'MA',
  type: 'line',
  data: [],
  smooth: true,
  lineStyle: {
    opacity: 0.5
  }
}

export const chartsVolumnSeries = {
  name: 'Volume',
  type: 'bar',
  xAxisIndex: 1,
  yAxisIndex: 1,
  data: [],
  itemStyle: {
    color: function (params: any) {
      const isUp = params.data.isUp
      return isUp ? 'rgb(241,90,74)' : 'rgb(41,171,145)'
    }
  }
}
