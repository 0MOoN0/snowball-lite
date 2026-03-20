import type { App } from 'vue'

// 需要全局引入一些组件，如ElScrollbar，不然一些下拉项样式有问题
// import { ElLoading, ElScrollbar } from 'element-plus'

// const plugins = [ElLoading]

// const components = [ElScrollbar]
// 全局引入element plus
import ElementPlus from 'element-plus'
import * as Icons from '@element-plus/icons-vue'

export const setupElementPlus = (app: App<Element>) => {
  // plugins.forEach((plugin) => {
  //   app.use(plugin)
  // })

  // components.forEach((component) => {
  //   app.component(component.name, component)
  // })
  // 全局引入element plus icon 组件
  for (const i in Icons) {
    app.component(i, Icons[i])
  }
  app.use(ElementPlus)
}
