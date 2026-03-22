import { SlateDescendant } from '@wangeditor/editor'

declare module 'slate' {
  interface CustomTypes {
    // 扩展 text
    Text: {
      text: string
      bold?: boolean
      italic?: boolean
      code?: boolean
      through?: boolean
      underline?: boolean
      sup?: boolean
      sub?: boolean
      color?: string
      bgColor?: string
      fontSize?: string
      fontFamily?: string
    }

    // 扩展 Element 的 type 属性
    Element: {
      type: string
      children: SlateDescendant[]
    }
  }
}

// 临时类型声明，修复第三方 Vite 插件在 TS 下的类型导出解析问题
declare module 'vite-plugin-purge-icons' {
  const PurgeIcons: any
  export default PurgeIcons
}

declare module 'unplugin-vue-macros/vite' {
  const VueMacros: any
  export default VueMacros
}
