import React from 'react';
import { 
  X, Award, Briefcase, GraduationCap, Sparkles, CheckCircle2, 
  XCircle, Clock, ShieldCheck, FileText, ChevronRight, Info,
  TrendingUp, Layers, Check, ExternalLink
} from 'lucide-react';

export default function CandidateDetailModal({ candidate, jd, onClose }) {
  if (!candidate) return null;

  const {
    candidate_name,
    overall_score,
    rank,
    component_scores,
    applied_weights,
    matched_skills,
    missing_skills,
    preferred_matched_skills,
    candidate_experience_years,
    required_experience_years,
    candidate_education_level,
    required_education_level,
    supporting_evidence,
    reasons,
    status,
    email,
    phone,
    filename
  } = candidate;

  // Status color styles
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
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5">
      <div 
        className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <span className="w-8 h-8 rounded-lg bg-blue-600 text-white font-bold text-sm flex items-center justify-center">
              #{rank}
            </span>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold tracking-tight text-white">{candidate_name}</h3>
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${getStatusBadge(status)}`}>
                  {status}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Resume: {filename} {email && `• ${email}`} {phone && `• ${phone}`}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Decision-Support Banner */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl flex items-start space-x-2.5 text-xs text-blue-900">
            <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Decision-Support System:</span> The matching score reflects automated multi-criteria relevance against the job description requirements. Demographic traits are excluded to ensure fair, unbiased assessment. Treat scores as decision-support indicators, not automatic hiring decisions.
            </div>
          </div>

          {/* Overall Score & Component Score Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
            {/* Overall Score Hero Card */}
            <div className="md:col-span-4 bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-xl p-5 flex flex-col justify-between shadow-md">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  Overall Match Score
                </span>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-4xl font-extrabold text-white tracking-tight">
                    {overall_score.toFixed(1)}
                  </span>
                  <span className="text-slate-400 text-sm font-semibold">/ 100%</span>
                </div>
                <div className="mt-3 w-full bg-slate-700/60 rounded-full h-2.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      overall_score >= 80 ? 'bg-emerald-400' : overall_score >= 65 ? 'bg-blue-400' : 'bg-amber-400'
                    }`}
                    style={{ width: `${Math.min(overall_score, 100)}%` }}
                  />
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-700/60 text-xs text-slate-300 space-y-1">
                <div className="flex justify-between">
                  <span>Target Role:</span>
                  <span className="font-semibold text-white truncate max-w-[130px]">{jd?.title || 'Target Job'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Candidate Rank:</span>
                  <span className="font-semibold text-emerald-400">#{rank} Ranked</span>
                </div>
              </div>
            </div>

            {/* 4 Component Scoring Gauges */}
            <div className="md:col-span-8 bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3.5">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Weighted Component Breakdown
                </h4>
                <span className="text-[11px] text-slate-500">
                  Applied Weights Sum: 100%
                </span>
              </div>

              {/* Skills Score Bar */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span className="flex items-center">
                    <Award className="w-3.5 h-3.5 mr-1 text-blue-600" />
                    Skills Match (Weight: {(applied_weights?.skills * 100).toFixed(0)}%)
                  </span>
                  <span className="text-blue-600 font-bold">
                    {component_scores?.skills?.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-blue-600 h-full rounded-full" 
                    style={{ width: `${Math.min(component_scores?.skills || 0, 100)}%` }} 
                  />
                </div>
              </div>

              {/* Semantic Similarity Bar */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span className="flex items-center">
                    <Sparkles className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                    Semantic Similarity (Weight: {(applied_weights?.semantic * 100).toFixed(0)}%)
                  </span>
                  <span className="text-indigo-600 font-bold">
                    {component_scores?.semantic?.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-indigo-600 h-full rounded-full" 
                    style={{ width: `${Math.min(component_scores?.semantic || 0, 100)}%` }} 
                  />
                </div>
              </div>

              {/* Experience Match Bar */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span className="flex items-center">
                    <Clock className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                    Relevant Experience (Weight: {(applied_weights?.experience * 100).toFixed(0)}%)
                  </span>
                  <span className="text-emerald-600 font-bold">
                    {component_scores?.experience?.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-emerald-600 h-full rounded-full" 
                    style={{ width: `${Math.min(component_scores?.experience || 0, 100)}%` }} 
                  />
                </div>
              </div>

              {/* Qualification Match Bar */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span className="flex items-center">
                    <GraduationCap className="w-3.5 h-3.5 mr-1 text-amber-600" />
                    Qualification Match (Weight: {(applied_weights?.qualification * 100).toFixed(0)}%)
                  </span>
                  <span className="text-amber-600 font-bold">
                    {component_scores?.qualification?.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-amber-600 h-full rounded-full" 
                    style={{ width: `${Math.min(component_scores?.qualification || 0, 100)}%` }} 
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Matched vs Missing Skills */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Detailed Skills Comparison
            </h4>

            <div className="space-y-3">
              {/* Matched Skills */}
              <div>
                <span className="text-xs font-bold text-emerald-700 flex items-center mb-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                  Matched Required Skills ({matched_skills?.length || 0}):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {matched_skills?.map((s, idx) => (
                    <span 
                      key={idx} 
                      className="px-2 py-1 bg-emerald-50 text-emerald-800 text-xs font-medium rounded-md border border-emerald-200 flex items-center"
                    >
                      <Check className="w-3 h-3 mr-1 text-emerald-600" />
                      {s}
                    </span>
                  ))}
                  {(!matched_skills || matched_skills.length === 0) && (
                    <span className="text-xs text-slate-400 italic">No direct required skills matched</span>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              {missing_skills?.length > 0 && (
                <div>
                  <span className="text-xs font-bold text-rose-700 flex items-center mb-1.5">
                    <XCircle className="w-3.5 h-3.5 mr-1 text-rose-500" />
                    Missing Required Skills ({missing_skills.length}):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {missing_skills.map((s, idx) => (
                      <span 
                        key={idx} 
                        className="px-2 py-1 bg-rose-50 text-rose-800 text-xs font-medium rounded-md border border-rose-200"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Preferred Skills Matched */}
              {preferred_matched_skills?.length > 0 && (
                <div>
                  <span className="text-xs font-bold text-indigo-700 flex items-center mb-1.5">
                    <Sparkles className="w-3.5 h-3.5 mr-1 text-indigo-500" />
                    Bonus / Preferred Skills Matched ({preferred_matched_skills.length}):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {preferred_matched_skills.map((s, idx) => (
                      <span 
                        key={idx} 
                        className="px-2 py-1 bg-indigo-50 text-indigo-800 text-xs font-medium rounded-md border border-indigo-200"
                      >
                        ★ {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Experience & Education Comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                Experience Comparison
              </span>
              <div className="flex items-center justify-between text-xs mt-2">
                <div>
                  <span className="text-slate-500 block">Candidate:</span>
                  <span className="text-base font-bold text-slate-900">{candidate_experience_years} Years</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 block">Required:</span>
                  <span className="text-base font-bold text-slate-900">
                    {required_experience_years > 0 ? `${required_experience_years}+ Years` : 'Unspecified'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                Education Qualification Comparison
              </span>
              <div className="flex items-center justify-between text-xs mt-2">
                <div>
                  <span className="text-slate-500 block">Candidate Degree:</span>
                  <span className="text-base font-bold text-slate-900">{candidate_education_level}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 block">Required:</span>
                  <span className="text-base font-bold text-slate-900">{required_education_level}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Explainable AI: Reasons Behind the Score */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1.5 text-blue-600" />
              Reasons Behind the Score & Recruiter Insights:
            </h4>
            <ul className="space-y-2">
              {reasons?.map((reason, i) => (
                <li key={i} className="flex items-start text-xs text-slate-700 leading-relaxed">
                  <ChevronRight className="w-3.5 h-3.5 text-blue-500 mr-1.5 shrink-0 mt-0.5" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Supporting Evidence Snippets from Resume */}
          {supporting_evidence?.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center">
                <FileText className="w-4 h-4 mr-1.5 text-indigo-600" />
                Supporting Resume Evidence:
              </h4>
              <div className="grid grid-cols-1 gap-2.5">
                {supporting_evidence.map((ev, i) => (
                  <div key={i} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-blue-700">{ev.category}</span>
                      <span className="text-[10px] font-medium text-slate-500">{ev.relevance_note}</span>
                    </div>
                    <p className="text-slate-600 italic bg-white p-2 rounded border border-slate-100 font-serif">
                      "{ev.snippet}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-lg transition"
          >
            Close Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

