import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo el frontend corre en 5173 y redirige /api al backend en 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
