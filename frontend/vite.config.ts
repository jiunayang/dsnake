import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/dsnake/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    cssCodeSplit: true,
    sourcemap: false,
    chunkSizeWarningLimit: 1500,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
