import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const buildTime = Date.now().toString()

export default defineConfig({
  base: './',
  define: {
    'import.meta.env.VITE_BUILD_TIME': JSON.stringify(buildTime)
  },
  plugins: [
    vue(),
    tailwindcss(),
    {
      name: 'inject-sw-version',
      closeBundle() {
        const distSw = resolve('dist/sw.js')
        try {
          let content = readFileSync(distSw, 'utf8')
          content = content.replaceAll('__BUILD_VERSION__', buildTime)
          writeFileSync(distSw, content)
        } catch {
          /* ignore if sw missing */
        }
      }
    }
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/jszip')) return 'zip'
          if (id.includes('node_modules/vue') || id.includes('node_modules/vue-router') || id.includes('node_modules/pinia')) return 'vue'
        }
      }
    }
  },
  test: {
    environment: 'node'
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/images': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
