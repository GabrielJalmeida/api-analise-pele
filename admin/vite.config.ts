import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            {
              name: 'react-vendor',
              test: /node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              priority: 30,
            },
            {
              name: 'antd-vendor',
              test: /node_modules[\\/](antd|@ant-design|@rc-component|rc-)/,
              priority: 20,
              maxSize: 450_000,
            },
            {
              name: 'vendor',
              test: /node_modules/,
              priority: 10,
              maxSize: 450_000,
            },
          ],
        },
      },
    },
  },
})
