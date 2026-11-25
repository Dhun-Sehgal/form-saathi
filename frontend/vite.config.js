import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    // GitHub Pages serves the preview build from /<repo>/; the Flask build is served from /.
    base: env.VITE_BASE || '/',
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@shared': fileURLToPath(new URL('../shared', import.meta.url)),
      },
    },
    server: {
      port: 5173,
      fs: { allow: ['..'] },
      proxy: { '/api': { target: 'http://127.0.0.1:5000', changeOrigin: false } },
    },
    css: { preprocessorOptions: { scss: { api: 'modern-compiler', quietDeps: true, silenceDeprecations: ['import', 'global-builtin', 'color-functions'] } } },
    build: { chunkSizeWarningLimit: 900 },
    test: { environment: 'node' },
  }
})
