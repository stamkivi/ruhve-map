
import { defineConfig } from 'vite'
export default defineConfig({
  root: 'web',
  server: {
    port: 5173,
    strictPort: true
  },
  build: {
    outDir: '../outputs/web-dist',
    emptyOutDir: true
  }
})
