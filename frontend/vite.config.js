import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/analyze': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/companies': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/careers': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/upload-resume': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/recommend-companies': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/company-analysis': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
