import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/specialists': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
      '/usage': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
