import { appModules } from '@/config/app'
import { useCache } from '@/hooks/web/useCache'
import { runtimeProfile } from '@/config/runtimeProfile'

const liteRuntimeUser = {
  username: 'lite-local',
  password: '',
  role: 'admin',
  roleId: 'lite-local',
  permissions: ['*.*.*']
}

export const bootstrapRuntimeSession = () => {
  if (runtimeProfile !== 'lite') {
    return
  }

  const { wsCache } = useCache()

  if (!wsCache.get(appModules.userInfo)) {
    wsCache.set(appModules.userInfo, liteRuntimeUser)
  }

  // lite 前端只补本地会话，不假装后端已经支持动态权限接口
  wsCache.set('dynamicRouter', false)
}
