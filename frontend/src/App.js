import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Analytics from './pages/Analytics';
import InvestmentAdvisor from './pages/InvestmentAdvisor';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/investment-advisor" element={<InvestmentAdvisor />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  );
}

export default App;
