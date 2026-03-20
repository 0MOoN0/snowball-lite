const runtimeProfile = (import.meta.env.VITE_RUNTIME_PROFILE || 'lite').toLowerCase()

const parseFlag = (value: string | undefined, fallback: boolean) => {
  if (value == null || value === '') {
    return fallback
  }
  return value === 'true'
}

export const runtimeCapabilityFlags = {
  scheduler: parseFlag(import.meta.env.VITE_ENABLE_SCHEDULER, runtimeProfile !== 'lite'),
  systemToken: parseFlag(import.meta.env.VITE_ENABLE_SYSTEM_TOKEN, runtimeProfile !== 'lite'),
}

export const runtimeBackendTarget =
  import.meta.env.VITE_PROXY_TARGET || 'http://127.0.0.1:5001'

export { runtimeProfile }
