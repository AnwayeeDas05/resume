import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import JobDescriptionView from './components/JobDescriptionView';
import ResumeUploadView from './components/ResumeUploadView';
import RankingDashboardView from './components/RankingDashboardView';
import { fetchHealth, fetchJobDescriptions, fetchResumes, runCandidateMatching } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('jd'); // 'jd' | 'resumes' | 'ranking'
  const [health, setHealth] = useState(null);
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [currentJD, setCurrentJD] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [matchRun, setMatchRun] = useState(null);
  const [matching, setMatching] = useState(false);
  const [matchError, setMatchError] = useState(null);

  // Scoring weights configuration (Default: 40% Skills, 30% Semantic, 20% Exp, 10% Edu)
  const [weights, setWeights] = useState({
    skills: 0.40,
    semantic: 0.30,
    experience: 0.20,
    qualification: 0.10
  });

  // Load initial backend state on mount
  useEffect(() => {
    async function init() {
      try {
        const h = await fetchHealth();
        setHealth(h);
      } catch (e) {
        console.warn('Backend not yet reachable:', e);
      }

      try {
        const jds = await fetchJobDescriptions();
        setJobDescriptions(jds);
        if (jds.length > 0) {
          setCurrentJD(jds[0]);
        }
      } catch (e) {
        console.warn('Failed to load JDs:', e);
      }

      try {
        const res = await fetchResumes();
        setCandidates(res);
      } catch (e) {
        console.warn('Failed to load resumes:', e);
      }
    }
    init();
  }, []);

  // Execute matching & ranking
  const handleRunMatch = async () => {
    if (!currentJD) {
      setActiveTab('jd');
      return;
    }
    if (candidates.length === 0) {
      setActiveTab('resumes');
      return;
    }

    setMatching(true);
    setMatchError(null);
    try {
      const response = await runCandidateMatching(currentJD.id, null, weights);
      setMatchRun(response);
      setActiveTab('ranking');
    } catch (err) {
      setMatchError(err.message);
    } finally {
      setMatching(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        candidateCount={candidates.length}
        jdCount={jobDescriptions.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {matchError && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200">
            <strong>Error:</strong> {matchError}
          </div>
        )}

        {activeTab === 'jd' && (
          <JobDescriptionView
            currentJD={currentJD}
            setCurrentJD={(jd) => {
              setCurrentJD(jd);
              setJobDescriptions(prev => [jd, ...prev.filter(x => x.id !== jd.id)]);
            }}
            onNext={() => setActiveTab('resumes')}
            weights={weights}
            setWeights={setWeights}
          />
        )}

        {activeTab === 'resumes' && (
          <ResumeUploadView
            candidates={candidates}
            setCandidates={setCandidates}
            onNext={() => {
              if (currentJD) {
                handleRunMatch();
              } else {
                setActiveTab('jd');
              }
            }}
            hasJD={Boolean(currentJD)}
          />
        )}

        {activeTab === 'ranking' && (
          <RankingDashboardView
            matchRun={matchRun}
            onRunMatch={handleRunMatch}
            matching={matching}
            currentJD={currentJD}
            candidateCount={candidates.length}
            onOpenJDTab={() => setActiveTab('jd')}
            onOpenResumesTab={() => setActiveTab('resumes')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AI Resume Matching & Candidate Ranking System • React + FastAPI + Sentence-Transformers</span>
          <span className="text-[11px] text-slate-500">
            Powered by all-MiniLM-L6-v2, spaCy, PyMuPDF, python-docx & MongoDB
          </span>
        </div>
      </footer>
    </div>
  );
}

