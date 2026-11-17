import React from 'react';
import { Target, Layers, Users, Sliders, ShieldCheck, Database, Cpu } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, health, candidateCount, jdCount }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      {/* Top Banner with Ethical AI Notice & System Status */}
      <div className="bg-slate-900 text-slate-300 text-xs px-4 py-1.5 flex flex-wrap items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <span className="flex items-center text-emerald-400 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 mr-1" />
            Ethical & Bias-Free AI: Demographic traits excluded from scoring
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">Scores are decision-support indicators, not automatic hiring decisions</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="flex items-center">
            <Cpu className="w-3.5 h-3.5 text-blue-400 mr-1" />
            NLP: all-MiniLM-L6-v2 & spaCy
          </span>
          <span className="flex items-center">
            <Database className="w-3.5 h-3.5 text-indigo-400 mr-1" />
            DB: {health?.database_mode || 'Connecting...'}
          </span>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Target className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 tracking-tight leading-tight flex items-center">
                TalentMatch AI
                <span className="ml-2 text-[10px] font-semibold bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Hybrid NLP
                </span>
              </h1>
              <p className="text-xs text-slate-500">Resume Matching & Candidate Ranking Dashboard</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('jd')}
              className={`flex items-center px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'jd'
                  ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs border border-blue-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Target className="w-4 h-4 mr-1.5" />
              1. Job Description
              {jdCount > 0 && (
                <span className="ml-2 px-1.5 py-0.2 bg-blue-200 text-blue-800 rounded-full text-xs">
                  {jdCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('resumes')}
              className={`flex items-center px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'resumes'
                  ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs border border-blue-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Users className="w-4 h-4 mr-1.5" />
              2. Candidate Resumes
              {candidateCount > 0 && (
                <span className="ml-2 px-1.5 py-0.2 bg-slate-200 text-slate-800 rounded-full text-xs">
                  {candidateCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('ranking')}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'ranking'
                  ? 'bg-blue-600 text-white font-semibold shadow-sm hover:bg-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Layers className="w-4 h-4 mr-1.5" />
              3. Ranking & Match Analysis
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}

