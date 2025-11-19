import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Investments from './pages/Investments';
import Analytics from './pages/Analytics';
import InvestmentAdvisor from './pages/InvestmentAdvisor';
import WinningStrategy from './pages/WinningStrategy';
import Preferences from './pages/Preferences';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/investments" element={<Investments />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/investment-advisor" element={<InvestmentAdvisor />} />
            <Route path="/winning-strategy" element={<WinningStrategy />} />
            <Route path="/preferences" element={<Preferences />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  );
}

export default App;
