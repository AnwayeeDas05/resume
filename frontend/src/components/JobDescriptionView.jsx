import React, { useState, useRef } from 'react';
import { 
  FileText, Upload, Sparkles, CheckCircle2, Sliders, ArrowRight, 
  Briefcase, GraduationCap, Clock, Award, BookOpen, RefreshCw
} from 'lucide-react';
import { createJobDescription, uploadJobDescriptionFile } from '../api';

const SAMPLE_JDS = [
  {
    title: "Senior Backend Engineer",
    company: "CloudScale Technologies",
    text: `Job Title: Senior Backend Engineer
Company: CloudScale Technologies
Location: San Francisco, CA / Remote

About the Role:
CloudScale Technologies is seeking a Senior Backend Engineer to architect, build, and scale our core cloud-native microservices platform. You will design high-performance RESTful APIs, distributed asynchronous systems, and database architectures handling millions of daily operations.

Core Responsibilities:
• Architect, build, and maintain scalable backend microservices and RESTful APIs using Python and FastAPI.
• Design, optimize, and maintain relational databases (PostgreSQL) and in-memory caches (Redis).
• Deploy, scale, and manage containerized applications using Docker and Kubernetes (EKS) on Amazon Web Services (AWS).
• Implement robust CI/CD pipelines, automated testing (unit and integration tests), and infrastructure as code.
• Participate in architectural design reviews and drive engineering best practices across the team.

Required Qualifications & Skills:
• Minimum 5+ years of relevant backend software engineering experience.
• Strong proficiency in Python and modern frameworks (FastAPI, Django, or Flask).
• Extensive experience with Amazon Web Services (AWS) cloud services (EC2, S3, RDS, ECS/EKS).
• Strong hands-on experience with Docker containerization and Kubernetes orchestration.
• Proven expertise with PostgreSQL schema design, indexing, and query optimization.
• Deep understanding of microservices architecture, RESTful API design, and Redis caching.
• Bachelor's or Master's degree in Computer Science, Software Engineering, or related STEM field.

Preferred / Nice-to-Have Skills:
• Experience with Apache Kafka, event streaming, or RabbitMQ message queues.
• Knowledge of Golang or TypeScript.
• Experience with Terraform for infrastructure automation.
• Professional cloud certification (e.g., AWS Certified Solutions Architect or CKA).`
  },
  {
    title: "Full Stack Developer",
    company: "NextGen Digital",
    text: `Job Title: Full Stack Developer
Company: NextGen Digital
Location: New York, NY

Overview:
We are seeking an energetic Full Stack Developer to build modern web interfaces and scalable backend services.

Responsibilities:
• Develop responsive, accessible web user interfaces using React, TypeScript, and Tailwind CSS.
• Build secure, scalable backend APIs with Python or Node.js.
• Work with PostgreSQL and MongoDB databases.
• Deploy applications to cloud environments (AWS).

Requirements:
• 3+ years of full stack software engineering experience.
• Strong experience with React, JavaScript, and TypeScript.
• Experience with Python or Node.js backend services.
• Experience with RESTful APIs, HTML5/CSS3, and Git.
• Bachelor's degree in Computer Science or equivalent work experience.`
  }
];

export default function JobDescriptionView({ 
  currentJD, 
  setCurrentJD, 
  onNext, 
  weights, 
  setWeights 
}) {
  const [activeTab, setActiveTab] = useState('paste'); // 'paste' | 'upload'
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [showWeightsConfig, setShowWeightsConfig] = useState(false);

  const fileInputRef = useRef(null);

  const handleSelectSample = (sample) => {
    setTitle(sample.title);
    setCompany(sample.company);
    setText(sample.text);
  };

  const handleAnalyzeText = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setUploadError(null);
    try {
      const derivedTitle = title.trim() || 'Software Engineer';
      const result = await createJobDescription({
        title: derivedTitle,
        company: company.trim() || 'Company',
        text: text,
        weights: weights
      });
      setCurrentJD(result);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setUploadError(null);
    try {
      const result = await uploadJobDescriptionFile(file, title, company);
      setCurrentJD(result);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleWeightChange = (key, val) => {
    const num = parseFloat(val);
    const updated = { ...weights, [key]: num };
    // Normalize so sum is 1.0
    const sum = updated.skills + updated.semantic + updated.experience + updated.qualification;
    if (sum > 0) {
      setWeights({
        skills: Number((updated.skills / sum).toFixed(2)),
        semantic: Number((updated.semantic / sum).toFixed(2)),
        experience: Number((updated.experience / sum).toFixed(2)),
        qualification: Number((updated.qualification / sum).toFixed(2))
      });
    }
  };

  const resetWeights = () => {
    setWeights({
      skills: 0.40,
      semantic: 0.30,
      experience: 0.20,
      qualification: 0.10
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center">
              <FileText className="w-5 h-5 mr-2 text-blue-600" />
              1. Job Description & Scoring Configuration
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Paste or upload a Job Description. Our NLP engine will extract requirements, responsibilities, and experience criteria.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setShowWeightsConfig(!showWeightsConfig)}
              className="flex items-center text-xs font-semibold px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
            >
              <Sliders className="w-3.5 h-3.5 mr-1.5 text-slate-600" />
              Weights: Skills {(weights.skills * 100).toFixed(0)}% | Semantic {(weights.semantic * 100).toFixed(0)}% | Exp {(weights.experience * 100).toFixed(0)}% | Edu {(weights.qualification * 100).toFixed(0)}%
            </button>
          </div>
        </div>

        {/* Scoring Weights Config Expandable Panel */}
        {showWeightsConfig && (
          <div className="mt-4 pt-4 border-t border-slate-100 bg-slate-50/70 -mx-6 -mb-6 p-6 rounded-b-xl">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">Configurable Hybrid Scoring Weights</h4>
                <p className="text-xs text-slate-500">Adjust the importance of each criteria. Weights are automatically normalized to 100%.</p>
              </div>
              <button
                type="button"
                onClick={resetWeights}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center"
              >
                <RefreshCw className="w-3 h-3 mr-1" /> Reset Defaults (40/30/20/10)
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Skills Match</span>
                  <span className="text-blue-600">{(weights.skills * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.80"
                  step="0.05"
                  value={weights.skills}
                  onChange={(e) => handleWeightChange('skills', e.target.value)}
                  className="w-full accent-blue-600"
                />
                <span className="text-[10px] text-slate-400">Canonical aliases + semantic fuzzy</span>
              </div>

              <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Semantic Similarity</span>
                  <span className="text-indigo-600">{(weights.semantic * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.80"
                  step="0.05"
                  value={weights.semantic}
                  onChange={(e) => handleWeightChange('semantic', e.target.value)}
                  className="w-full accent-indigo-600"
                />
                <span className="text-[10px] text-slate-400">Section-aware all-MiniLM-L6-v2 embeddings</span>
              </div>

              <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Relevant Experience</span>
                  <span className="text-emerald-600">{(weights.experience * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.80"
                  step="0.05"
                  value={weights.experience}
                  onChange={(e) => handleWeightChange('experience', e.target.value)}
                  className="w-full accent-emerald-600"
                />
                <span className="text-[10px] text-slate-400">Years required vs accumulated experience</span>
              </div>

              <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Qualification Match</span>
                  <span className="text-amber-600">{(weights.qualification * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.50"
                  step="0.05"
                  value={weights.qualification}
                  onChange={(e) => handleWeightChange('qualification', e.target.value)}
                  className="w-full accent-amber-600"
                />
                <span className="text-[10px] text-slate-400">Degree levels (PhD/MS/BS) & field fit</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 mt-2 italic">
              ℹ️ Notice: If a Job Description has no education requirement or unspecified experience, that category's weight is automatically redistributed proportionally to active categories.
            </p>
          </div>
        )}
      </div>

      {/* Main Grid: Input Form (Left) & Parsed JD Details (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Form / Upload */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-5">
            {/* Quick Sample Selector */}
            <div className="mb-4">
              <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider block mb-2">
                Quick Load Realistic Sample JDs:
              </label>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_JDS.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectSample(s)}
                    className="text-xs px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg border border-blue-200 font-medium transition flex items-center"
                  >
                    <Sparkles className="w-3 h-3 mr-1 text-blue-500" />
                    {s.title}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Mode Tabs */}
            <div className="flex border-b border-slate-200 mb-4">
              <button
                type="button"
                onClick={() => setActiveTab('paste')}
                className={`py-2 px-4 text-xs font-semibold border-b-2 transition ${
                  activeTab === 'paste'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                Paste Job Description
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('upload')}
                className={`py-2 px-4 text-xs font-semibold border-b-2 transition ${
                  activeTab === 'upload'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                Upload File (.pdf / .docx / .txt)
              </button>
            </div>

            {/* Title & Company Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Job Title</label>
                <input
                  type="text"
                  placeholder="e.g. Senior Backend Engineer"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Company (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. CloudScale Tech"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Paste Mode */}
            {activeTab === 'paste' && (
              <form onSubmit={handleAnalyzeText} className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-slate-700 block mb-1">
                    Job Description Content:
                  </label>
                  <textarea
                    rows={12}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste the complete Job Description text here including responsibilities, required skills, and qualification requirements..."
                    className="w-full text-xs p-3 font-mono border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 leading-relaxed"
                    required
                  />
                </div>

                {uploadError && (
                  <div className="p-3 bg-red-50 text-red-700 text-xs rounded-lg border border-red-200">
                    {uploadError}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !text.trim()}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-semibold text-xs transition shadow-sm flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Parsing & Analyzing Entities...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Extract & Save Job Description</span>
                    </>
                  )}
                </button>
              </form>
            )}

            {/* Upload Mode */}
            {activeTab === 'upload' && (
              <div className="space-y-4">
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl p-8 text-center cursor-pointer bg-slate-50/50 hover:bg-blue-50/30 transition"
                >
                  <Upload className="w-10 h-10 mx-auto text-slate-400 mb-2" />
                  <p className="text-xs font-semibold text-slate-700">Click to upload Job Description file</p>
                  <p className="text-[11px] text-slate-500 mt-1">Supports PDF, DOCX, or plain text</p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>

                {uploadError && (
                  <div className="p-3 bg-red-50 text-red-700 text-xs rounded-lg border border-red-200">
                    {uploadError}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Parsed JD Entities Display */}
        <div className="lg:col-span-6 space-y-4">
          {currentJD ? (
            <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-5 space-y-4">
              <div className="flex items-start justify-between border-b border-slate-100 pb-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-full uppercase tracking-wider">
                      Active JD Analyzed
                    </span>
                    <span className="text-xs text-slate-400 font-mono">ID: {currentJD.id}</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mt-1">{currentJD.title}</h3>
                  <p className="text-xs text-slate-500">{currentJD.company}</p>
                </div>
                <button
                  type="button"
                  onClick={onNext}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center transition"
                >
                  Proceed to Resumes <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </button>
              </div>

              {/* Requirement Summary Badges */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                    <Clock className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Experience Required</span>
                    <span className="text-xs font-bold text-slate-800">
                      {currentJD.required_experience_years > 0
                        ? `${currentJD.required_experience_years}+ Years`
                        : 'Open / Unspecified'}
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
                    <GraduationCap className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Degree Level</span>
                    <span className="text-xs font-bold text-slate-800">
                      {currentJD.required_qualifications?.length > 0
                        ? currentJD.required_qualifications.join(', ')
                        : 'Any / Equivalent'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Required Skills Chips */}
              <div>
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-1.5 flex items-center">
                  <Award className="w-3.5 h-3.5 mr-1 text-blue-600" />
                  Required Skills ({currentJD.required_skills?.length || 0}):
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {currentJD.required_skills?.map((skill, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-blue-50 text-blue-800 text-xs font-medium rounded-md border border-blue-200"
                    >
                      {skill}
                    </span>
                  ))}
                  {(!currentJD.required_skills || currentJD.required_skills.length === 0) && (
                    <span className="text-xs text-slate-400 italic">No specific required skills extracted</span>
                  )}
                </div>
              </div>

              {/* Preferred Skills Chips */}
              {currentJD.preferred_skills?.length > 0 && (
                <div>
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-1.5 flex items-center">
                    <Sparkles className="w-3.5 h-3.5 mr-1 text-indigo-500" />
                    Preferred / Bonus Skills ({currentJD.preferred_skills?.length || 0}):
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {currentJD.preferred_skills?.map((skill, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-md border border-indigo-200"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Core Responsibilities */}
              {currentJD.responsibilities?.length > 0 && (
                <div>
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-1.5 flex items-center">
                    <Briefcase className="w-3.5 h-3.5 mr-1 text-slate-600" />
                    Core Responsibilities ({currentJD.responsibilities?.length}):
                  </label>
                  <ul className="space-y-1.5 text-xs text-slate-600">
                    {currentJD.responsibilities.slice(0, 5).map((resp, i) => (
                      <li key={i} className="flex items-start">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mr-1.5 shrink-0 mt-0.5" />
                        <span>{resp}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-50/70 border-2 border-dashed border-slate-200 rounded-xl p-10 text-center flex flex-col items-center justify-center min-h-[360px]">
              <BookOpen className="w-12 h-12 text-slate-300 mb-3" />
              <h4 className="text-sm font-semibold text-slate-700">No Job Description Loaded Yet</h4>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Paste a Job Description on the left, click one of the sample presets, or upload a document to view extracted entities and configure matching.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

