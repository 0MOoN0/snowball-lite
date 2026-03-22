import { resolve } from 'path'
import type { ConfigEnv, UserConfig } from 'vite'
import { loadEnv } from 'vite'
import Vue from '@vitejs/plugin-vue'
import WindiCSS from 'vite-plugin-windicss'
import VueJsx from '@vitejs/plugin-vue-jsx'
import { createStyleImportPlugin, ElementPlusResolve } from 'vite-plugin-style-import'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import PurgeIcons from 'vite-plugin-purge-icons'
// import {viteMockServe} from 'vite-plugin-mock'
import { createHtmlPlugin } from 'vite-plugin-html'
import VueMarcos from 'unplugin-vue-macros/vite'

// https://vitejs.dev/config/
const root = process.cwd()

function pathResolve(dir: string) {
    return resolve(root, '.', dir)
}

export default ({ command, mode }: ConfigEnv): UserConfig => {
    const env = loadEnv(mode, root)
    const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:5001'

    return {
        base: env.VITE_BASE_PATH,
        plugins: [
            Vue(),
            VueJsx(),
            WindiCSS(),
            createStyleImportPlugin({
                resolves: [ElementPlusResolve()],
                libs: [{
                    libraryName: 'element-plus',
                    esModule: true,
                    resolveStyle: (name) => {
                        return `element-plus/es/components/${name.substring(3)}/style/css`
                    }
                }]
            }),
            // EslintPlugin({
            //   cache: false,
            //   include: ['src/**/*.vue', 'src/**/*.ts', 'src/**/*.tsx'] // 检查的文件
            // }),
            // 移除已弃用的 @intlify/vite-plugin-vue-i18n 插件以避免构建报错
            createSvgIconsPlugin({
                iconDirs: [pathResolve('src/assets/svgs')],
                symbolId: 'icon-[dir]-[name]',
                svgoOptions: true
            }),
            PurgeIcons(),
            //     viteMockServe({
            //         ignore: /^\_/,
            //         mockPath: 'mock',
            //         // localEnabled: !isBuild,
            //         // prodEnabled: isBuild,
            //         localEnabled: true,
            //         prodEnabled: true,
            //         injectCode: `
            //   import { setupProdMockServer } from '../mock/_createProductionServer'

            //   setupProdMockServer()
            //   `
            //     }),
            VueMarcos(),
            createHtmlPlugin({
                inject: {
                    data: {
                        title: env.VITE_APP_TITLE,
                        injectScript: `<script src="./inject.js"></script>`,
                    }
                }
            })
        ],

        css: {
            preprocessorOptions: {
                less: {
                    additionalData: '@import "./src/styles/variables.module.less";',
                    javascriptEnabled: true
                }
            }
        },
        resolve: {
            extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.less', '.css'],
            alias: [
                {
                    find: 'vue-i18n',
                    replacement: 'vue-i18n/dist/vue-i18n.cjs.js'
                },
                {
                    find: /\@\//,
                    replacement: `${pathResolve('src')}/`
                }
            ]
        },
        build: {
            minify: 'terser',
            outDir: env.VITE_OUT_DIR || 'dist',
            sourcemap: env.VITE_SOURCEMAP === 'true' ? 'inline' : false,
            // brotliSize: false,
            terserOptions: {
                compress: {
                    drop_debugger: env.VITE_DROP_DEBUGGER === 'true',
                    drop_console: env.VITE_DROP_CONSOLE === 'true'
                }
            }
        },
        server: {
            port: 4000,
            proxy: {
                '/dev': {
                    target: proxyTarget,
                    changeOrigin: true,
                    rewrite: path => path.replace(/^\/dev/, '')
                }
            },
            hmr: {
                overlay: false,
            },
            host: '0.0.0.0',
            open: false
        },
        optimizeDeps: {
            include: [
                'vue',
                'vue-router',
                'vue-types',
                'element-plus/es/locale/lang/zh-cn',
                'element-plus/es/locale/lang/en',
                '@iconify/iconify',
                '@vueuse/core',
                'axios',
                'qs',
                'echarts',
                'echarts-wordcloud',
                'intro.js',
                'qrcode',
                '@wangeditor/editor',
                '@wangeditor/editor-for-vue'
            ]
        }
    }
}
