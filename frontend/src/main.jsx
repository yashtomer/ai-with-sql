import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import { ConfigProvider } from './context/ConfigContext'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <ConfigProvider>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </ConfigProvider>
    </AuthProvider>
  </StrictMode>,
)
