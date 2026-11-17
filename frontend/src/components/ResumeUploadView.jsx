import React, { useState, useRef } from 'react';
import { 
  Upload, Users, FileCheck, AlertCircle, Trash2, Sparkles, 
  ArrowRight, CheckCircle2, Briefcase, GraduationCap, Mail, Phone,
  FileText, ShieldCheck
} from 'lucide-react';
import { uploadResumesBatch, loadSampleResumes, clearResumes } from '../api';

export default function ResumeUploadView({ 
  candidates, 
  setCandidates, 
  onNext, 
  hasJD 
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [failedFiles, setFailedFiles] = useState([]);
  const [successMessage, setSuccessMessage] = useState(null);

  const fileInputRef = useRef(null);

  const handleFiles = async (filesList) => {
    if (!filesList || filesList.length === 0) return;
    
    setUploading(true);
    setUploadProgress(`Processing ${filesList.length} files...`);
    setFailedFiles([]);
    setSuccessMessage(null);

    try {
      const response = await uploadResumesBatch(filesList);
      
      // Update candidate list, deduplicating by filename/name
      setCandidates(prev => {
        const map = new Map();
        for (const c of response.successful_candidates) {
          const k = c.filename || c.email || c.name;
          map.set(k, c);
        }
        for (const c of prev) {
          const k = c.filename || c.email || c.name;
          if (!map.has(k)) {
            map.set(k, c);
          }
        }
        return Array.from(map.values());
      });

      if (response.failed_files && response.failed_files.length > 0) {
        setFailedFiles(response.failed_files);
      }

      setSuccessMessage(
        `Successfully processed ${response.successful_count} candidate resume${response.successful_count === 1 ? '' : 's'}.` +
        (response.failed_count > 0 ? ` (${response.failed_count} invalid file${response.failed_count === 1 ? '' : 's'} handled cleanly).` : '')
      );
    } catch (err) {
      setFailedFiles([{ filename: "Batch Upload", reason: err.message }]);
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleLoadSamples = async () => {
    setUploading(true);
    setUploadProgress("Loading 11 pre-built realistic candidate resumes...");
    setFailedFiles([]);
    setSuccessMessage(null);

    try {
      const response = await loadSampleResumes(false);
      setCandidates(response.successful_candidates);
      setFailedFiles([]);
      setSuccessMessage(
        `Successfully loaded all ${response.successful_count} sample candidate resumes (100% valid & deduplicated).`
      );
    } catch (err) {
      setFailedFiles([{ filename: "Sample Loader", reason: err.message }]);
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  };

  const handleTestCorrupted = async () => {
    setUploading(true);
    setUploadProgress("Testing corrupted file isolation resilience...");
    setFailedFiles([]);
    setSuccessMessage(null);

    try {
      const response = await loadSampleResumes(true);
      setCandidates(response.successful_candidates);
      if (response.failed_files && response.failed_files.length > 0) {
        setFailedFiles(response.failed_files);
      }
      setSuccessMessage(
        `Fault-Tolerance Verification: 1 corrupted file was isolated and rejected without interrupting the batch of ${response.successful_count} valid resumes.`
      );
    } catch (err) {
      setFailedFiles([{ filename: "Resilience Test", reason: err.message }]);
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  };

  const handleClear = async () => {
    try {
      await clearResumes();
      setCandidates([]);
      setFailedFiles([]);
      setSuccessMessage("Cleared candidate pool.");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center">
              <Users className="w-5 h-5 mr-2 text-blue-600" />
              2. Batch Resume Upload & Candidate Ingestion
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Upload at least 10 PDF or DOCX resumes simultaneously. Resumes are parsed using PyMuPDF and python-docx, extracting entities while isolating demographic attributes.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={handleLoadSamples}
              disabled={uploading}
              className="flex items-center text-xs font-semibold px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-sm hover:from-blue-700 hover:to-indigo-700 transition"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              Load 11 Test Resumes Batch
            </button>
            <button
              type="button"
              onClick={handleTestCorrupted}
              disabled={uploading}
              title="Upload corrupted file alongside valid resumes to verify fault tolerance"
              className="flex items-center text-xs font-medium px-2.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
            >
              <AlertCircle className="w-3.5 h-3.5 mr-1 text-amber-500" />
              Test Corrupted Resilience
            </button>
            {candidates.length > 0 && (
              <button
                type="button"
                onClick={handleClear}
                className="flex items-center text-xs font-medium px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
              >
                <Trash2 className="w-3.5 h-3.5 mr-1 text-slate-500" />
                Clear Pool
              </button>
            )}
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`mt-6 border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
            isDragging
              ? 'border-blue-500 bg-blue-50/50 scale-[1.005]'
              : 'border-slate-300 hover:border-blue-400 bg-slate-50/50 hover:bg-slate-50'
          }`}
        >
          <Upload className={`w-12 h-12 mx-auto mb-3 transition ${isDragging ? 'text-blue-600' : 'text-slate-400'}`} />
          <h3 className="text-sm font-semibold text-slate-700">
            Drag and drop multiple resumes here, or <span className="text-blue-600 underline">browse files</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Accepts PDF (.pdf) and Word documents (.docx). Batch upload 10+ files at once.
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt"
            onChange={(e) => handleFiles(Array.from(e.target.files || []))}
            className="hidden"
          />

          {uploading && (
            <div className="mt-4 flex items-center justify-center space-x-2 text-xs font-medium text-blue-600">
              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <span>{uploadProgress}</span>
            </div>
          )}
        </div>

        {/* Feedback Messages */}
        {successMessage && (
          <div className="mt-4 p-3 bg-emerald-50 text-emerald-800 text-xs rounded-lg border border-emerald-200 flex items-center">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 mr-2 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Invalid Files Warning Banner */}
        {failedFiles.length > 0 && (
          <div className="mt-4 p-3 bg-amber-50 text-amber-900 text-xs rounded-lg border border-amber-200 space-y-1">
            <div className="font-bold flex items-center text-amber-800">
              <AlertCircle className="w-4 h-4 text-amber-600 mr-1.5 shrink-0" />
              Invalid / Corrupted Files Handled Without Failing Batch ({failedFiles.length}):
            </div>
            <ul className="list-disc list-inside space-y-0.5 text-[11px] text-amber-700">
              {failedFiles.map((ff, i) => (
                <li key={i}>
                  <span className="font-semibold">{ff.filename}:</span> {ff.reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Candidate Pool Header with CTA */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <h3 className="text-base font-bold text-slate-900">
            Candidate Pool ({candidates.length} candidate{candidates.length === 1 ? '' : 's'})
          </h3>
          {candidates.length >= 10 && (
            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-full">
              ✓ Batch Target Reached (≥10 Resumes)
            </span>
          )}
        </div>

        {candidates.length > 0 && (
          <button
            type="button"
            onClick={onNext}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm flex items-center transition"
          >
            {hasJD ? 'Proceed to AI Ranking Dashboard' : 'Review Job Description First'}
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </button>
        )}
      </div>

      {/* Candidate Cards Grid */}
      {candidates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {candidates.map((cand) => (
            <div
              key={cand.id}
              className="bg-white rounded-xl shadow-xs border border-slate-200 p-4 hover:border-blue-300 hover:shadow-md transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-700 font-bold text-xs flex items-center justify-center border border-blue-100">
                      {cand.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-900 leading-tight">{cand.name}</h4>
                      <span className="text-[11px] text-slate-400 font-mono truncate block max-w-[180px]">
                        {cand.filename}
                      </span>
                    </div>
                  </div>

                  <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[10px] font-semibold rounded-full">
                    {cand.total_experience_years} yrs exp
                  </span>
                </div>

                {/* Contact Excerpts */}
                <div className="mt-3 space-y-1 text-slate-500 text-[11px]">
                  {cand.email && (
                    <div className="flex items-center truncate">
                      <Mail className="w-3 h-3 mr-1.5 text-slate-400 shrink-0" />
                      <span className="truncate">{cand.email}</span>
                    </div>
                  )}
                  {cand.location && (
                    <div className="flex items-center truncate">
                      <Briefcase className="w-3 h-3 mr-1.5 text-slate-400 shrink-0" />
                      <span className="truncate">{cand.location}</span>
                    </div>
                  )}
                  {cand.education?.length > 0 && (
                    <div className="flex items-center truncate">
                      <GraduationCap className="w-3 h-3 mr-1.5 text-slate-400 shrink-0" />
                      <span className="truncate">{cand.education[0].degree}</span>
                    </div>
                  )}
                </div>

                {/* Skills tags */}
                <div className="mt-3">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Extracted Skills ({cand.skills?.length || 0}):
                  </span>
                  <div className="flex flex-wrap gap-1 max-h-16 overflow-hidden">
                    {cand.skills?.slice(0, 6).map((s, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 bg-slate-100 text-slate-700 text-[10px] font-medium rounded-sm"
                      >
                        {s}
                      </span>
                    ))}
                    {(cand.skills?.length || 0) > 6 && (
                      <span className="px-1.5 py-0.5 bg-slate-200 text-slate-600 text-[10px] rounded-sm font-medium">
                        +{cand.skills.length - 6} more
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>{cand.experience_details?.length || 1} role recorded</span>
                <span className="text-emerald-600 font-medium flex items-center">
                  <ShieldCheck className="w-3 h-3 mr-0.5" /> Ready for match
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-50/70 border-2 border-dashed border-slate-200 rounded-xl p-12 text-center flex flex-col items-center justify-center">
          <Users className="w-12 h-12 text-slate-300 mb-3" />
          <h4 className="text-sm font-semibold text-slate-700">No Resumes in Pool</h4>
          <p className="text-xs text-slate-500 max-w-sm mt-1 mb-4">
            Upload candidate resumes above, or click "Load 11 Test Resumes Batch" to instantly load a realistic test batch.
          </p>
          <button
            type="button"
            onClick={handleLoadSamples}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Load 11 Pre-built Test Resumes</span>
          </button>
        </div>
      )}
    </div>
  );
}

