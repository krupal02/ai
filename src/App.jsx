import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { AccessibilityProvider } from './context/AccessibilityContext';
import Header from './components/Header/Header';
import LeftPanel from './components/LeftPanel/LeftPanel';
import ChatInterface from './components/ChatInterface/ChatInterface';
import RightPanel from './components/RightPanel/RightPanel';
import NavigationModal from './components/Navigation/NavigationModal';
import OnboardingModal from './components/Onboarding/OnboardingModal';
import FoodFinder from './components/FoodFinder/FoodFinder';
import SecurityInfo from './components/SecurityInfo/SecurityInfo';
import './index.css';

function AppContent() {
  const {
    showNavigation, toggleNavigation, mobilePanel, toggleMobilePanel,
    onboardingComplete, completeOnboarding, userProfile,
    showFoodFinder, setShowFoodFinder,
    showSecurityInfo, setShowSecurityInfo,
  } = useApp();

  return (
    <div className="app-layout">
      {/* Onboarding gate */}
      {!onboardingComplete && (
        <OnboardingModal onComplete={completeOnboarding} />
      )}

      <a href="#chat-input" className="sr-only">Skip to chat</a>
      <Header />
      <div className="main-content">
        <LeftPanel />
        <ChatInterface />
        <RightPanel />
      </div>

      {/* Mobile bottom tabs */}
      <nav className="mobile-tabs" aria-label="Mobile navigation">
        <button className={`mobile-tab ${mobilePanel === 'left' ? 'active' : ''}`} onClick={() => toggleMobilePanel('left')}>
          <span className="mobile-tab-icon">📊</span>
          Status
        </button>
        <button className="mobile-tab active" onClick={() => toggleMobilePanel(null)}>
          <span className="mobile-tab-icon">💬</span>
          Chat
        </button>
        <button className={`mobile-tab ${mobilePanel === 'right' ? 'active' : ''}`} onClick={() => toggleMobilePanel('right')}>
          <span className="mobile-tab-icon">📍</span>
          Nearby
        </button>
      </nav>

      {showNavigation && <NavigationModal onClose={toggleNavigation} />}
      {showFoodFinder && <FoodFinder onClose={() => setShowFoodFinder(false)} />}
      {showSecurityInfo && <SecurityInfo onClose={() => setShowSecurityInfo(false)} />}
    </div>
  );
}

export default function App() {
  return (
    <AccessibilityProvider>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </AccessibilityProvider>
  );
}
