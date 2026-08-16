import { ConfigProvider } from 'antd'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider
    theme={{
      token: {
        colorPrimary: '#1f2937',
        borderRadius: 8,
        colorBgLayout: '#f5f6f8',
        colorText: '#1f2937',
        colorTextSecondary: '#6b7280',
      },
    }}
    >
      <App />
    </ConfigProvider>
  </StrictMode>,
)
