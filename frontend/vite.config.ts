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
      '/console': 'http://localhost:8000',
      '/conversations': 'http://localhost:8000',
      '/distillation': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/swarm': {
        target: process.env.SWARM_URL || 'http://34.74.80.83:8080',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/swarm/, ''),
        ws: true,
      },
    },
  },
})
