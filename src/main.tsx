import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './pages/App'
import { Provider } from 'react-redux'
import { store } from './store'
import { PreferencesProvider } from './preferences'
import { AuthProvider } from './auth'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <PreferencesProvider>
          <App />
        </PreferencesProvider>
      </AuthProvider>
    </Provider>
  </React.StrictMode>,
)
