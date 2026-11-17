import React, { useState, useMemo } from 'react';
import { 
  Layers, Search, SlidersHorizontal, ArrowUpDown, Download, 
  ExternalLink, ChevronRight, Award, Clock, Sparkles, Filter,
  CheckCircle2, RefreshCw, FileSpreadsheet, Eye
} from 'lucide-react';
import CandidateDetailModal from './CandidateDetailModal';

export default function RankingDashboardView({ 
  matchRun, 
  onRunMatch, 
  matching, 
  currentJD, 
  candidateCount,
  onOpenJDTab,
  onOpenResumesTab
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL'); // 'ALL' | 'Strong Fit' | 'Moderate Fit' | 'Potential Match' | 'Low Match'
  const [sortBy, setSortBy] = useState('score_desc'); // 'score_desc' | 'score_asc' | 'exp_desc' | 'skills_desc'
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Filtered and sorted candidates
  const filteredCandidates = useMemo(() => {
    if (!matchRun?.ranked_candidates) return [];

    let list = [...matchRun.ranked_candidates];

    // Search filter
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      list = list.filter(c => 
        c.candidate_name.toLowerCase().includes(q) ||
        c.filename.toLowerCase().includes(q) ||
        c.matched_skills.some(s => s.toLowerCase().includes(q))
      );
    }

    // Status tier filter
    if (statusFilter !== 'ALL') {
      list = list.filter(c => c.status === statusFilter);
    }

    // Sorting
    list.sort((a, b) => {
      if (sortBy === 'score_desc') return b.overall_score - a.overall_score;
      if (sortBy === 'score_asc') return a.overall_score - b.overall_score;
      if (sortBy === 'exp_desc') return b.candidate_experience_years - a.candidate_experience_years;
      if (sortBy === 'skills_desc') return b.matched_skills.length - a.matched_skills.length;
      return 0;
    });

    return list;
  }, [matchRun, searchTerm, statusFilter, sortBy]);

  // Export to CSV
  const handleExportCSV = () => {
    if (!matchRun?.ranked_candidates) return;
    const headers = ['Rank', 'Candidate Name', 'Overall Score (%)', 'Status', 'Experience (Yrs)', 'Skills Score', 'Semantic Score', 'Exp Score', 'Edu Score', 'Matched Skills', 'Filename'];
    const rows = matchRun.ranked_candidates.map(c => [
      c.rank,
      `"${c.candidate_name}"`,
      c.overall_score,
      `"${c.status}"`,
      c.candidate_experience_years,
      c.component_scores.skills,
      c.component_scores.semantic,
      c.component_scores.experience,
      c.component_scores.qualification,
      `"${c.matched_skills.join('; ')}"`,
      `"${c.filename}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Candidate_Rankings_${matchRun.jd_title.replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Export to JSON
  const handleExportJSON = () => {
    if (!matchRun) return;
    const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(matchRun, null, 2));
    const link = document.createElement('a');
    link.setAttribute('href', jsonStr);
    link.setAttribute('download', `Candidate_Rankings_${matchRun.jd_title.replace(/\s+/g, '_')}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (st) => {
    switch (st) {
      case 'Strong Fit':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'Moderate Fit':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Potential Match':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Match Execution Bar */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center">
              <Layers className="w-5 h-5 mr-2 text-blue-600" />
              3. Candidate Ranking & AI Evaluation Dashboard
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Compare candidates against{' '}
              <span className="font-semibold text-slate-800">"{currentJD?.title || 'Selected Job'}"</span>{' '}
              using hybrid skill matching (40%), sentence-transformers semantic similarity (30%), experience fit (20%), and qualification level (10%).
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={onRunMatch}
              disabled={matching || !currentJD || candidateCount === 0}
              className="flex items-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-bold text-xs shadow-sm transition"
            >
              {matching ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  <span>Computing Embeddings & Scoring...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-1.5" />
                  <span>Run AI Ranking ({candidateCount} Resumes)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Missing Prerequisites Warning */}
        {(!currentJD || candidateCount === 0) && (
          <div className="mt-4 p-4 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="font-bold block">Prerequisites for Ranking:</span>
              <span>
                {!currentJD && 'Please set or upload a Job Description. '}
                {candidateCount === 0 && 'Please upload or load at least 10 candidate resumes.'}
              </span>
            </div>
            <div className="flex space-x-2 shrink-0">
              {!currentJD && (
                <button
                  type="button"
                  onClick={onOpenJDTab}
                  className="px-2.5 py-1 bg-amber-200 text-amber-900 rounded font-semibold text-xs"
                >
                  Set JD
                </button>
              )}
              {candidateCount === 0 && (
                <button
                  type="button"
                  onClick={onOpenResumesTab}
                  className="px-2.5 py-1 bg-amber-200 text-amber-900 rounded font-semibold text-xs"
                >
                  Load Resumes
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Main Ranking Table Card */}
      {matchRun ? (
        <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
          {/* Controls Bar: Search, Filters, Sorting & Export */}
          <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search candidates by name, filename, or skill..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs border border-slate-200 rounded-lg bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>

            {/* Filter and Sort Controls */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Status Filter */}
              <div className="flex items-center text-xs space-x-1 bg-white border border-slate-200 rounded-lg p-1">
                <span className="text-slate-400 pl-1">Tier:</span>
                {['ALL', 'Strong Fit', 'Moderate Fit', 'Potential Match'].map((st) => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                      statusFilter === st
                        ? 'bg-blue-600 text-white font-bold'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>

              {/* Sort By Dropdown */}
              <div className="flex items-center text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5">
                <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 mr-1.5" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-transparent text-xs text-slate-700 font-medium focus:outline-hidden cursor-pointer"
                >
                  <option value="score_desc">Overall Score (High → Low)</option>
                  <option value="score_asc">Overall Score (Low → High)</option>
                  <option value="exp_desc">Experience (Most → Least)</option>
                  <option value="skills_desc">Skills Count (Most → Least)</option>
                </select>
              </div>

              {/* Export Buttons */}
              <button
                type="button"
                onClick={handleExportCSV}
                title="Export Rankings to CSV"
                className="px-2.5 py-1.5 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg flex items-center transition"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                CSV
              </button>
              <button
                type="button"
                onClick={handleExportJSON}
                title="Export Full Results to JSON"
                className="px-2.5 py-1.5 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg flex items-center transition"
              >
                <Download className="w-3.5 h-3.5 mr-1 text-blue-600" />
                JSON
              </button>
            </div>
          </div>

          {/* Table View */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-4 w-12 text-center">Rank</th>
                  <th className="py-3 px-4">Candidate Name</th>
                  <th className="py-3 px-4">Experience</th>
                  <th className="py-3 px-4">Match %</th>
                  <th className="py-3 px-4">Matched Skills</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredCandidates.map((cand) => (
                  <tr
                    key={cand.candidate_id}
                    onClick={() => setSelectedCandidate(cand)}
                    className="hover:bg-blue-50/40 transition cursor-pointer group"
                  >
                    {/* Rank Badge */}
                    <td className="py-3.5 px-4 text-center font-bold">
                      <span
                        className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-extrabold ${
                          cand.rank === 1
                            ? 'bg-amber-400 text-slate-900 shadow-xs'
                            : cand.rank === 2
                            ? 'bg-slate-300 text-slate-800'
                            : cand.rank === 3
                            ? 'bg-amber-700/30 text-amber-900'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {cand.rank}
                      </span>
                    </td>

                    {/* Candidate Name & File */}
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900 group-hover:text-blue-600 transition flex items-center">
                        {cand.candidate_name}
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono truncate max-w-[200px]">
                        {cand.filename}
                      </div>
                    </td>

                    {/* Experience */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="font-bold text-slate-800">{cand.candidate_experience_years} Yrs</span>
                      <span className="text-[10px] text-slate-400 block">
                        {cand.required_experience_years > 0
                          ? `Req: ${cand.required_experience_years} yrs`
                          : 'Open Exp'}
                      </span>
                    </td>

                    {/* Match Score Progress Bar */}
                    <td className="py-3.5 px-4 min-w-[140px]">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-extrabold text-slate-900">
                          {cand.overall_score.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${
                            cand.overall_score >= 80
                              ? 'bg-emerald-500'
                              : cand.overall_score >= 65
                              ? 'bg-blue-500'
                              : 'bg-amber-500'
                          }`}
                          style={{ width: `${Math.min(cand.overall_score, 100)}%` }}
                        />
                      </div>
                    </td>

                    {/* Matched Skills Chips */}
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="flex flex-wrap gap-1">
                        {cand.matched_skills.slice(0, 4).map((s, idx) => (
                          <span
                            key={idx}
                            className="px-1.5 py-0.5 bg-emerald-50 text-emerald-800 text-[10px] font-semibold rounded-xs border border-emerald-200"
                          >
                            {s}
                          </span>
                        ))}
                        {cand.matched_skills.length > 4 && (
                          <span className="px-1.5 py-0.5 bg-slate-100 text-slate-600 text-[10px] rounded-xs font-semibold">
                            +{cand.matched_skills.length - 4} more
                          </span>
                        )}
                        {cand.matched_skills.length === 0 && (
                          <span className="text-[11px] text-slate-400 italic">None matched</span>
                        )}
                      </div>
                    </td>

                    {/* Status Badge */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${getStatusBadge(cand.status)}`}>
                        {cand.status}
                      </span>
                    </td>

                    {/* Action Button */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedCandidate(cand);
                        }}
                        className="inline-flex items-center px-2.5 py-1 bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 text-xs font-semibold rounded-md border border-slate-200 transition"
                      >
                        <Eye className="w-3.5 h-3.5 mr-1" />
                        Analyze
                      </button>
                    </td>
                  </tr>
                ))}

                {filteredCandidates.length === 0 && (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400 text-xs">
                      No candidates matched your search and filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="p-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex flex-wrap items-center justify-between">
            <span>Showing {filteredCandidates.length} of {matchRun.ranked_candidates.length} evaluated candidates</span>
            <span>Click any candidate row to inspect evidence, skill breakdown, and explainable AI reasons</span>
          </div>
        </div>
      ) : (
        <div className="bg-slate-50/70 border-2 border-dashed border-slate-200 rounded-xl p-12 text-center flex flex-col items-center justify-center">
          <Layers className="w-12 h-12 text-slate-300 mb-3" />
          <h4 className="text-sm font-semibold text-slate-700">No Ranking Evaluation Executed Yet</h4>
          <p className="text-xs text-slate-500 max-w-md mt-1 mb-4">
            Click "Run AI Ranking" above to execute our 4-dimension hybrid matching model against the active Job Description.
          </p>
          <button
            type="button"
            onClick={onRunMatch}
            disabled={matching || !currentJD || candidateCount === 0}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center space-x-1.5"
          >
            <Sparkles className="w-4 h-4" />
            <span>Execute AI Matching Now</span>
          </button>
        </div>
      )}

      {/* Candidate Detail Modal */}
      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          jd={currentJD}
          onClose={() => setSelectedCandidate(null)}
        />
      )}
    </div>
  );
}

