import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [vue(), visualizer({
    open: false, // 服务器无界面环境，禁止自动打开浏览器
    filename: "bundle-analysis.html", // 报告文件名
    gzipSize: true, // 显示 gzip 压缩后的大小
    brotliSize: true, // 显示 brotli 压缩后的大小
  })],
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index-[hash].js',
        chunkFileNames: 'assets/index-[hash].js',
        assetFileNames: 'assets/index-[hash].[ext]'
      }
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0'
  }
})