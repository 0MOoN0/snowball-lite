<script setup lang="ts">
import type { EChartsOption } from 'echarts'
// import echarts from '@/plugins/echarts'
import * as echarts from 'echarts'
import { debounce } from 'lodash-es'
import 'echarts-wordcloud'
import { propTypes } from '@/utils/propTypes'
import { computed, PropType, ref, unref, watch, onMounted, onBeforeUnmount, onActivated } from 'vue'
import { useAppStore } from '@/store/modules/app'
import { isString } from '@/utils/is'
import { useDesign } from '@/hooks/web/useDesign'

const { getPrefixCls, variables } = useDesign()

const prefixCls = getPrefixCls('echart')

const emit = defineEmits(['clickEcharts'])

const appStore = useAppStore()

const props = defineProps({
  options: {
    type: Object as PropType<EChartsOption>,
    required: true
  },
  width: propTypes.oneOfType([Number, String]).def(''),
  height: propTypes.oneOfType([Number, String]).def('500px')
})

const isDark = computed(() => appStore.getIsDark)

const theme = computed(() => {
  const echartTheme: boolean | string = unref(isDark) ? true : 'auto'

  return echartTheme
})

const options = computed(() => {
  return Object.assign(props.options, {
    darkMode: unref(theme)
  })
})

const elRef = ref<ElRef>()

let echartRef: Nullable<echarts.ECharts> = null

const contentEl = ref<Element>()

const styles = computed(() => {
  const width = isString(props.width) ? props.width : `${props.width}px`
  const height = isString(props.height) ? props.height : `${props.height}px`

  return {
    width,
    height
  }
})

const initChart = () => {
  if (unref(elRef) && props.options) {
    echartRef = echarts.init(unref(elRef) as HTMLElement, unref(isDark) ? 'dark' : '')
    echartRef?.setOption(unref(options))
    // 绑定点击事件，并往上传递
    echartRef?.on('click', (params) => {
      emit('clickEcharts', params)
    })
  }
}

watch(
  () => options.value,
  (options) => {
    if (echartRef) {
      echartRef?.setOption(options)
    }
  },
  {
    deep: true
  }
)

const resizeHandler = debounce(() => {
  if (echartRef) {
    echartRef.resize()
  }
}, 100)

const contentResizeHandler = async (e: TransitionEvent) => {
  if (e.propertyName === 'width') {
    resizeHandler()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeHandler)

  contentEl.value = document.getElementsByClassName(`${variables.namespace}-layout-content`)[0]
  unref(contentEl) &&
    (unref(contentEl) as Element).addEventListener('transitionend', contentResizeHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
  unref(contentEl) &&
    (unref(contentEl) as Element).removeEventListener('transitionend', contentResizeHandler)
})

onActivated(() => {
  if (echartRef) {
    echartRef.resize()
  }
})

// 添加获取图表实例的方法
const getChart = () => {
  return echartRef
}

// 暴露方法给父组件使用
defineExpose({
  getChart
})
</script>

<template>
  <div ref="elRef" :class="[$attrs.class, prefixCls]" :style="styles"></div>
</template>
