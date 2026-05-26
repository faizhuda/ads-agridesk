import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Prevent Vite/rolldown from mangling module initialization order,
    // which causes "Cannot access 'x' before initialization" in framer-motion.
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('framer-motion')) return 'framer-motion';
          if (id.includes('react-dom') || id.includes('react-router-dom')) return 'react-vendor';
          if (id.includes('node_modules/react/')) return 'react-vendor';
        },
      },
    },
  },
})
