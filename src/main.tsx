import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './pages/App'
import { Provider } from 'react-redux'
import { store } from './store'
import { PreferencesProvider } from './preferences'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <PreferencesProvider>
        <App />
      </PreferencesProvider>
    </Provider>
  </React.StrictMode>,
)
