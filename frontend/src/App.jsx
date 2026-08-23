import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Downtime from './pages/Downtime'
import Configure from './pages/Configure'
import HealthCheck from './pages/HealthCheck'
import ThreatIntelligence from './pages/ThreatIntelligence'
import AssessmentPipeline from './pages/AssessmentPipeline'
import KnowledgeSharing from './pages/KnowledgeSharing'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="downtime" element={<Downtime />} />
          <Route path="health-check" element={<HealthCheck />} />
          <Route path="threat-intel" element={<ThreatIntelligence />} />
          <Route path="assessment" element={<AssessmentPipeline />} />
          <Route path="knowledge-sharing" element={<KnowledgeSharing />} />
          <Route path="configure" element={<Configure />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
