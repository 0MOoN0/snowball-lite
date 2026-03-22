import { createApp } from 'vue'
import App from './App.vue'

// 引入windi css
import '@/plugins/windi.css'
// 导入全局的svg图标
import '@/plugins/svgIcon'
// 初始化多语言
import { setupI18n } from '@/plugins/vueI18n'
// 引入状态管理
import { setupStore } from '@/store'
// 全局组件
import { setupGlobCom } from '@/components'
// 引入element-plus
import { setupElementPlus } from '@/plugins/elementPlus'
import 'element-plus/dist/index.css'
// 引入全局样式
import '@/styles/index.less'
// 引入动画
import '@/plugins/animate.css'
// 路由
import { setupRouter } from './router'
// 权限
import { setupPermission } from './directives'
import { bootstrapRuntimeSession } from '@/config/runtimeSession'
// 路由守卫
// 路由守卫已集成到 setupRouter 中，无需单独导入

// 创建实例
const bootstrap = async () => {
  const app = createApp(App)

  // Store
  setupStore(app)

  // Multilingual configuration
  // Asynchronous case: language files may be obtained from the server
  setupI18n(app)

  // Global components
  setupGlobCom(app)

  // Element Plus
  setupElementPlus(app)

  // lite 口径下补本地会话，绕开当前仓库缺失的后端 auth 接口
  bootstrapRuntimeSession()

  // Router
  setupRouter(app)

  // Permission directive
  setupPermission(app)

  // Mount the application
  app.mount('#app')
}

bootstrap()
