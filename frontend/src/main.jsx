import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { LanguageProvider } from './context/LanguageContext';
import { RouteProvider } from './context/RouteContext';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <LanguageProvider>
      <RouteProvider>
        <App />
      </RouteProvider>
    </LanguageProvider>
  </React.StrictMode>
);
