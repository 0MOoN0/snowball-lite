import { useCache } from '@/hooks/web/useCache'
import { useI18n } from '@/hooks/web/useI18n'
import { useNProgress } from '@/hooks/web/useNProgress'
import { usePageLoading } from '@/hooks/web/usePageLoading'
import { useTitle } from '@/hooks/web/useTitle'
import { useAppStoreWithOut } from '@/store/modules/app'
import { useDictStoreWithOut } from '@/store/modules/dict'
import { useEnumStoreWithOut } from '@/store/modules/enum'
import { usePermissionStoreWithOut } from '@/store/modules/permission'
import { Layout } from '@/utils/routerHelper'
import type { App } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'

const { t } = useI18n()

export const constantRouterMap: AppRouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard/analysis',
    name: 'Root',
    meta: {
      hidden: true
    }
  },
  {
    path: '/redirect',
    component: Layout,
    name: 'Redirect',
    children: [
      {
        path: '/redirect/:path(.*)',
        name: 'Redirect',
        component: () => import('@/views/Redirect/Redirect.vue'),
        meta: {}
      }
    ],
    meta: {
      hidden: true,
      noTagsView: true
    }
  },
  {
    path: '/login',
    component: () => import('@/views/Login/Login.vue'),
    name: 'Login',
    meta: {
      hidden: true,
      title: t('router.login'),
      noTagsView: true
    }
  },
  {
    path: '/404',
    component: () => import('@/views/Error/404.vue'),
    name: 'NoFind',
    meta: {
      hidden: true,
      title: '404',
      noTagsView: true
    }
  }
]

export const asyncRouterMap: AppRouteRecordRaw[] = [
  {
    path: '/dashboard',
    component: Layout,
    redirect: '/dashboard/analysis',
    name: 'Dashboard',
    meta: {
      title: t('router.dashboard'),
      icon: 'ant-design:dashboard-filled',
      alwaysShow: true,
      noTagsView: true
    },
    children: [
      {
        path: 'analysis',
        component: () => import('@/views/Dashboard/DashboardAnalysis.vue'),
        name: 'DashboardAnalysis',
        meta: {
          title: t('router.analysis'),
          noCache: false,
          affix: true
        }
      },
      {
        path: 'workplace',
        component: () => import('@/views/Dashboard/Workplace.vue'),
        name: 'Workplace',
        meta: {
          title: t('router.workplace'),
          noCache: true
        }
      },
      {
        path: 'notification',
        component: () => import('@/views/Snow/Notification/Notification.vue'),
        name: 'Notification',
        meta: {
          title: '通知管理',
          icon: 'carbon:notification-filled',
          affix: true,
          noCache: true
        },
        children: [
          // 通知详情路由
          {
            path: 'detail',
            component: () => import('@/views/Snow/Notification/NotificationDetail/NotificationDetail.vue'),
            name: 'NotificationDetail',
            meta: {
              title: '通知详情',
              hidden: true,
              noTagsView: false
            }
          }
        ]
      }
    ]
  },
  {
    path: '/analysis',
    component: Layout,
    name: 'Analysis',
    redirect: '/analysis/record',
    meta: {
      title: '数据分析与展示',
      icon: 'icon-park-solid:analysis',
      alwaysShow: true
    },
    children: [
      {
        path: 'record',
        name: 'Record',
        component: () => import('@/views/Snow/Analysis/Record/index.vue'),
        meta: {
          title: '交易记录',
          icon: 'mdi:note-text',

          noCache: true,
          affix: true
        }
      },
      {
        path: 'record/import',
        name: 'RecordImport',

        component: () => import('@/views/Snow/Analysis/Record/Import.vue'),
        meta: {
          title: '导入交易记录',
          hidden: true,
          noTagsView: false,
          activeMenu: '/analysis/record',
          backTo: '/analysis/record'
        }
      }
    ]
  },
  {
    path: '/strategy',
    component: Layout,
    name: 'Strategy',
    redirect: '/strategy/grid',
    meta: {
      title: '策略',
      icon: 'mdi:strategy',
      alwaysShow: true
    },
    children: [
      {
        path: 'grid',
        name: 'Grid',
        component: () => import('@/views/Snow/Strategy/Grid.vue'),
        meta: {
          title: '网格',
          icon: 'vaadin:chart-grid',
          noCache: false,
          affix: true
        }
      }
    ]
  },
  {
    path: '/asset',
    component: Layout,
    name: 'Asset',
    redirect: '/asset/fund/fund',
    meta: {
      title: '元数据管理',
      icon: 'fluent:gift-card-money-24-filled',
      alwaysShow: true
    },
    children: [
      {
        path: 'assetManager',
        name: 'assetManager',
        component: () => import('@/views/Snow/Asset/AssetManager.vue'),
        meta: {
          title: '证券品种管理',
          icon: 'gridicons:refund',
          noCache: false
        }
      },
      {
        path: 'aliasManager',
        name: 'aliasManager',
        component: () => import('@/views/Snow/Asset/AssetAliasManager.vue'),
        meta: {
          title: '资产别名管理',
          icon: 'mdi:format-list-bulleted',
          noCache: false
        }
      },
      {
        path: 'category',
        name: 'category',
        component: () => import('@/views/Snow/Category/Category.vue'),
        meta: {
          title: '分类管理',
          icon: 'material-symbols:Category-outline'
        }
      },
      {
        path: 'indexManager',
        name: 'indexManager',
        component: () => import('@/views/Snow/Index/IndexManager.vue'),
        meta: {
          title: '指数管理',
          icon: 'mdi:chart-line'
        }
      }
    ]
  },
  {
    path: '/setting',
    component: Layout,
    redirect: '/setting/basic',
    name: 'Setting',
    meta: {
      title: '系统设置',
      icon: 'carbon:settings',
      alwaysShow: true,
    },
    children: [
      {
        path: 'basic',
        name: 'basic',
        component: () => import('@/views/Snow/Setting/Basic/BasicSetting.vue'),
        meta: {
          title: '基础设置',
          icon: 'carbon:settings-adjust'
        }
      },
      {
        path: 'notification',
        name: 'notification',
        component: () => import('@/views/Snow/Setting/Notification/NotificationSetting.vue'),
        meta: {
          title: '通知设置',
          icon: 'carbon:notification'
        }
      },
      {
        path: 'scheduler',
        name: 'scheduler',
        component: () => import('@/views/Snow/Setting/Scheduler/Scheduler.vue'),
        meta: {
          title: '定时任务设置',
          icon: 'arcticons:smsscheduler'
        }
      },
      {
        path: 'data',
        name: 'data',
        component: () => import('@/views/Snow/Setting/Data/DataSetting.vue'),
        meta: {
          title: '数据设置',
          icon: 'material-symbols:perm-data-setting-outline'
        }
      },
      {
        path: 'config',
        name: 'config',
        component: () => import('@/views/Snow/Setting/Config/ConfigManagement.vue'),
        meta: {
          title: '系统配置管理',
          icon: 'carbon:settings-services'
        }
      },
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  strict: true,
  routes: constantRouterMap as RouteRecordRaw[],
  scrollBehavior: () => ({ left: 0, top: 0 })
})

export const resetRouter = (): void => {
  const resetWhiteNameList = ['Redirect', 'Login', 'NoFind', 'Root']
  router.getRoutes().forEach((route) => {
    const { name } = route
    if (name && !resetWhiteNameList.includes(name as string)) {
      router.hasRoute(name) && router.removeRoute(name)
    }
  })
}

/**
 * 设置路由守卫
 */
const setupRouterGuard = () => {
  const permissionStore = usePermissionStoreWithOut()
  const appStore = useAppStoreWithOut()
  const dictStore = useDictStoreWithOut()
  const enumStore = useEnumStoreWithOut()
  const { wsCache } = useCache()
  const { start, done } = useNProgress()
  const { loadStart, loadDone } = usePageLoading()

  const whiteList = ['/login'] // 不重定向白名单

  router.beforeEach(async (to, from, next) => {
    start()
    loadStart()

    const userInfo = wsCache.get(appStore.getUserInfo)

    if (userInfo) {
      if (to.path === '/login') {
        next({ path: '/' })
      } else {

        // 检查是否需要更新枚举版本（统一处理已添加路由和未添加路由的情况）
        if (enumStore.shouldCheckGlobalVersion) {
          try {
            await enumStore.updateGlobalVersion()

            // 检查是否是首次加载（没有任何枚举数据）
            const hasAnyEnumData = Object.keys(enumStore.enumData).length > 0

            if (!hasAnyEnumData) {
              // 首次加载：使用版本驱动的枚举管理来获取可用枚举列表并预加载数据
              await enumStore.versionDrivenEnumManagement()
            } else {
              // 非首次加载：只检查和更新过期的枚举
              await enumStore.checkAndUpdateExpiredEnums()
            }
          } catch (enumError) {
            // 枚举版本检查失败，静默处理
            console.error('[Router Guard] 枚举版本检查失败:', enumError)
          }
        }

        if (permissionStore.getIsAddRouters) {
          next()
          return
        }

        if (!dictStore.getIsSetDict) {
          // 获取所有字典
          // const res = await getDictApi()
          // if (res) {
          //   dictStore.setDictObj(res.data)
          //   dictStore.setIsSetDict(true)
          // }
        }

        // 开发者可根据实际情况进行修改
        const roleRouters = wsCache.get('roleRouters') || []

        // 是否使用动态路由
        if (appStore.getDynamicRouter) {
          if (userInfo.role === 'admin') {
            await permissionStore.generateRoutes('admin', roleRouters as AppCustomRouteRecordRaw[])
          } else {
            await permissionStore.generateRoutes('test', roleRouters as string[])
          }
        } else {
          await permissionStore.generateRoutes('none')
        }

        permissionStore.getAddRouters.forEach((route) => {
          router.addRoute(route as unknown as RouteRecordRaw) // 动态添加可访问路由表
        })

        const redirectPath = from.query.redirect || to.path
        const redirect = decodeURIComponent(redirectPath as string)
        const nextData = to.path === redirect ? { ...to, replace: true } : { path: redirect }

        permissionStore.setIsAddRouters(true)
        next(nextData)
      }
    } else {
      if (whiteList.indexOf(to.path) !== -1) {
        next()
      } else {
        next(`/login?redirect=${to.path}`) // 否则全部重定向到登录页
      }
    }
  })

  router.afterEach((to) => {
    useTitle(to?.meta?.title as string)
    done() // 结束Progress
    loadDone()
  })
}

/**
 * 设置路由
 * @param app Vue应用实例
 */
export const setupRouter = (app: App<Element>) => {
  app.use(router)
  // 在路由挂载后设置路由守卫
  setupRouterGuard()
}

export default router
