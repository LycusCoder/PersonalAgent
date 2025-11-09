import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Serve from /static/gui/ in production so Flask can serve built assets from /static/gui
export default defineConfig({
  plugins: [react()],
  base: '/static/gui/',
  build: {
    outDir: path.resolve(__dirname, '../static/gui'),
    emptyOutDir: true,
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:7777'
    }
  }
})
