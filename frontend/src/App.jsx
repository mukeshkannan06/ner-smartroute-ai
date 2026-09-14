import React, { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DataModeBanner } from './components/layout/DataModeBanner';
import { Chatbot } from './components/chat/Chatbot';

import { DashboardPage } from './pages/DashboardPage';
import { SmartRoutesPage } from './pages/SmartRoutesPage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { GovernmentPage } from './pages/GovernmentPage';
import { IncidentsPage } from './pages/IncidentsPage';

import './App.css';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage />;
      case 'planner':
        return <SmartRoutesPage />;
      case 'twin':
        return <DigitalTwinPage />;
      case 'gov':
        return <GovernmentPage />;
      case 'incidents':
        return <IncidentsPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content">
        <Header />
        <DataModeBanner />
        <main className="page-container">
          {renderPage()}
        </main>
      </div>
      <Chatbot />
    </div>
  );
}
