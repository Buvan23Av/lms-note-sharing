import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to FastAPI backend running on port 8000
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      // Proxy static upload files to FastAPI backend
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
