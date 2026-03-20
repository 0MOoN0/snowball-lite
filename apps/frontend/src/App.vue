<script setup lang="ts">
import { computed, onMounted, onBeforeMount } from 'vue'
import { useAppStore } from '@/store/modules/app'
import { ConfigGlobal } from '@/components/ConfigGlobal'
import { isDark } from '@/utils/is'
import { useDesign } from '@/hooks/web/useDesign'
import { useCache } from '@/hooks/web/useCache'

const { getPrefixCls } = useDesign()

const prefixCls = getPrefixCls('app')

const appStore = useAppStore()

const currentSize = computed(() => appStore.getCurrentSize)

const greyMode = computed(() => appStore.getGreyMode)

const { wsCache } = useCache()

// 根据浏览器当前主题设置系统主题色
const setDefaultTheme = () => {
  // 如果缓存中有 isDark 且不为空，则使用缓存中的值
  // 解决了之前 isDark 为 false 时，被认为是不存在的问题
  const isDarkCache = wsCache.get('isDark')
  if (isDarkCache !== null && isDarkCache !== undefined) {
    appStore.setIsDark(isDarkCache)
  } else {
    // 否则使用系统当前主题
    const isDarkTheme = isDark()
    appStore.setIsDark(isDarkTheme)
  }
}

setDefaultTheme()

// 监听系统主题变化
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  appStore.setIsDark(e.matches)
})

onBeforeMount(() => {
  // 根组件即将挂载
})

onMounted(() => {
  // 根组件已挂载
})
</script>

<template>
  <ConfigGlobal :size="currentSize">
    <RouterView :class="greyMode ? `${prefixCls}-grey-mode` : ''" />
  </ConfigGlobal>
</template>

<style lang="less">
@prefix-cls: ~'@{namespace}-app';

.size {
  width: 100%;
  height: 100%;
}

html,
body {
  padding: 0 !important;
  margin: 0;
  overflow: hidden;
  .size;

  #app {
    .size;
  }
}

.@{prefix-cls}-grey-mode {
  filter: grayscale(100%);
}
</style>
