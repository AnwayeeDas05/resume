# AI Resume Matching & Candidate Ranking System

An enterprise-ready, explainable AI-powered recruitment engine that evaluates and ranks multiple candidate resumes (PDF, DOCX, TXT) against Job Descriptions (JDs) using a hybrid scoring algorithm.

Built with **React.js**, **Tailwind CSS**, **FastAPI**, **Sentence-Transformers (`all-MiniLM-L6-v2`)**, **spaCy**, **PyMuPDF**, **python-docx**, and **MongoDB**.

---

## 🌟 Key Features

1. **Job Description Parsing & Ingestion**:
   - Paste or upload JDs in `.pdf`, `.docx`, or `.txt`.
   - Extracts required skills, preferred/bonus skills, required experience (years), degree qualification levels, and key responsibilities.
   - Includes realistic sample JD presets (*Senior Backend Engineer*, *Full Stack Developer*).

2. **Batch Resume Processing (≥10 Resumes)**:
   - Batch upload 10+ resumes simultaneously via drag-and-drop.
   - Extracts candidate name, contact details (email, phone, links, location), skills, work history with date ranges, education degrees, certifications, and projects.
   - **Fault-Tolerant & Resilient**: Corrupted or unreadable files (e.g. damaged PDFs) are isolated without interrupting or crashing the remaining batch.
   - Includes **11 realistic sample candidate resumes** (PDF and DOCX) + 1 corrupted sample to test batch resilience.

3. **Hybrid AI Matching Algorithm (40 / 30 / 20 / 10)**:
   - **Skill Matching (40%)**: Normalizes aliases (e.g. *AWS* $\leftrightarrow$ *Amazon Web Services*, *React* $\leftrightarrow$ *React.js*, *K8s* $\leftrightarrow$ *Kubernetes*, *Postgres* $\leftrightarrow$ *PostgreSQL*). Calculates exact matches, preferred bonuses, and semantic similarity for fuzzy matches.
   - **Semantic Similarity (30%)**: Section-aware dense embeddings computed with `all-MiniLM-L6-v2` and cosine similarity comparing candidate experience and projects against JD responsibilities and overview.
   - **Relevant Experience Matching (20%)**: Compares verified years of experience against JD required years, with continuous proportional scoring and title relevance assessment.
   - **Qualification Matching (10%)**: Hierarchy-based degree evaluation ($\text{PhD} > \text{Master's} > \text{Bachelor's} > \text{Diploma}$) combined with STEM field relevance check.
   - **Dynamic Weight Redistribution**: Automatically redistributes weights proportionally when a JD requirement category is absent (e.g., if a JD has no degree requirement, the 10% is proportionally distributed across skills, semantic, and experience).
   - **Configurable Scoring Weights**: Recruiter-controlled sliders to customize category weights on the fly.
   - **Bias-Free & Demographic Segregation**: Candidate name, gender, age, ethnicity, phone, email, and photos are strictly excluded from matching scores.

4. **Recruiter Ranking Dashboard**:
   - Ranked list in descending order of matching score (0–100%).
   - Interactive table with candidate name, experience, match percentage, and matched skills chips.
   - Real-time search across candidate names, filenames, and skills.
   - Filter by match tier (*Strong Fit*, *Moderate Fit*, *Potential Match*, *Low Match*).
   - Sort by overall score, experience, or skills count.
   - Export results to **CSV** or **JSON**.

5. **Candidate-Level Deep Analysis Modal**:
   - Full candidate profile details.
   - Visual component score breakdown (radar/gauges for Skills, Semantic, Experience, Education).
   - Matched required skills (green tags), missing skills (rose tags), and preferred skills (indigo tags).
   - Experience comparison (candidate years vs required years with gap analysis).
   - **Supporting Resume Evidence**: Highlighted excerpts extracted directly from the candidate's resume with relevance notes.
   - **Explainable AI Reasoning**: Concrete bullet points explaining the rationale behind the score.
   - Ethical AI disclaimer: *"Scores are decision-support indicators, not automatic hiring decisions."*

---

## 🏛 Architecture Overview

```
ai-resume-matcher/
├── backend/
│   ├── app/
│   │   ├── config.py                 # Configuration, weight defaults & directories
│   │   ├── database.py               # MongoDB connection with automatic resilient mock fallback
│   │   ├── models.py                 # Pydantic schemas for JDs, resumes & match runs
│   │   ├── parsers/
│   │   │   ├── pdf_parser.py         # PyMuPDF extractor
│   │   │   ├── docx_parser.py        # python-docx extractor
│   │   │   ├── skill_database.py     # Skill taxonomy & canonical alias normalization
│   │   │   ├── resume_extractor.py   # Candidate entity extraction & demographic segregation
│   │   │   └── jd_extractor.py       # JD requirements extraction (skills, exp, degrees)
│   │   ├── matching/
│   │   │   ├── model_loader.py       # Cached SentenceTransformer ('all-MiniLM-L6-v2')
│   │   │   ├── skill_matcher.py      # Alias normalization & semantic fuzzy skill match
│   │   │   ├── semantic_matcher.py   # Section-aware dense embeddings & cosine similarity
│   │   │   ├── experience_matcher.py # Continuous experience scoring & title relevance
│   │   │   ├── qualification_matcher.py # Degree hierarchy & field relevance
│   │   │   └── scorer.py             # 40/30/20/10 hybrid formula + dynamic redistribution
│   │   ├── routes/
│   │   │   ├── jd_routes.py          # /api/jd endpoints
│   │   │   ├── resume_routes.py      # /api/resumes endpoints (batch upload & sample loader)
│   │   │   └── matching_routes.py    # /api/match endpoints (rankings & candidate analysis)
│   │   └── main.py                   # FastAPI app with CORS & static frontend serving
│   ├── sample_resumes/               # 11 realistic test resumes (PDF/DOCX) + 1 corrupted sample
│   ├── scripts/
│   │   └── generate_sample_resumes.py # Generates realistic test resumes & JDs
│   ├── tests/
│   │   ├── test_matching.py          # Unit tests for matching engine & parsers
│   │   └── test_api_endpoints.py     # End-to-end integration tests for API endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx            # Top nav, status pills, ethical AI banner
│   │   │   ├── JobDescriptionView.jsx # JD input, upload, extracted entities & weights slider
│   │   │   ├── ResumeUploadView.jsx  # Drag-and-drop batch upload, progress, candidate cards
│   │   │   ├── RankingDashboardView.jsx # Candidate ranking table, search, filters & export
│   │   │   └── CandidateDetailModal.jsx # Candidate deep dive, evidence, breakdown & reasons
│   │   ├── api.js                    # API client
│   │   ├── App.jsx                   # Master dashboard state orchestrator
│   │   ├── main.jsx
│   │   └── index.css                 # Tailwind CSS styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

---

## 🧮 Matching Algorithm Explained

The candidate matching score $S \in [0, 100]$ is computed as a weighted sum of four independent component scores:

$$S = w_{\text{skills}} \cdot S_{\text{skills}} + w_{\text{semantic}} \cdot S_{\text{semantic}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{qual}} \cdot S_{\text{qual}}$$

### 1. Default Weights
* $w_{\text{skills}} = 0.40$ (40%)
* $w_{\text{semantic}} = 0.30$ (30%)
* $w_{\text{exp}} = 0.20$ (20%)
* $w_{\text{qual}} = 0.10$ (10%)

### 2. Skill Matching ($S_{\text{skills}}$)
* **Canonical Alias Normalization**: Maps thousands of variations to standardized skills (e.g. `k8s` $\rightarrow$ `Kubernetes`, `react.js` $\rightarrow$ `React`, `aws` $\rightarrow$ `Amazon Web Services (AWS)`).
* **Exact Matches**: Full credit ($1.0$).
* **Semantic Skill Matching**: For unmatched required skills, computes cosine similarity between candidate skills and required skills using `all-MiniLM-L6-v2`. If similarity $\ge 0.72$, candidate receives partial credit ($0.8$).
* **Preferred Skills Boost**: Up to $+15\%$ bonus for matching nice-to-have skills (capped at $100\%$).

### 3. Section-Aware Semantic Similarity ($S_{\text{semantic}}$)
* Candidate work experience descriptions and project contexts are aligned against the JD's core responsibilities and overview.
* Uses Sentence-Transformers (`all-MiniLM-L6-v2`) to compute 384-dimensional dense vectors.
* Cosine similarity is calibrated to a $0–100$ scale:
  $$\text{sim}_{\text{raw}} = 0.6 \cdot \cos(v_{\text{exp}}, v_{\text{resp}}) + 0.4 \cdot \cos(v_{\text{context}}, v_{\text{overview}})$$

### 4. Relevant Experience Matching ($S_{\text{exp}}$)
* Date intervals across employment entries are parsed, merged, and deduplicated to compute verified years.
* If candidate years $Y_{\text{cand}} \ge Y_{\text{req}}$, score is $100\%$.
* If candidate is below required years, score decays smoothly:
  $$S_{\text{exp}} = \max\left(10, \frac{Y_{\text{cand}}}{Y_{\text{req}}} \times 90\right)$$

### 5. Educational Qualification Matching ($S_{\text{qual}}$)
* Degree hierarchy: $\text{PhD (4)} > \text{Master's (3)} > \text{Bachelor's (2)} > \text{Associate/Diploma (1)}$.
* Evaluates whether the candidate meets the minimum required level and whether the field of study is in a relevant STEM discipline.

### 6. Proportional Weight Redistribution
When a JD lacks an explicit requirement category (for example, no minimum education degree or open experience), the absent category's weight is automatically redistributed proportionally to active categories:
$$w_i' = \frac{w_i}{\sum_{k \in \text{active}} w_k}$$

---

## 🚀 Setup & Execution Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ & npm
- (Optional) Local MongoDB instance (`mongodb://localhost:27017`). If MongoDB is not running, the application **automatically falls back to an embedded in-memory MongoDB store (`mongomock`)**, allowing the system to run seamlessly with zero external configuration!

---

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy English model & pre-warm Sentence-Transformer
python -m spacy download en_core_web_sm
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Generate the 11 test resumes + 1 corrupted sample (if not already generated)
python scripts/generate_sample_resumes.py
```

### Step 2: Run Tests

Run the complete test suite (unit and API integration tests):

```bash
cd backend
PYTHONPATH=. ./venv/bin/pytest tests/ -v
```

All 11 tests should pass:
```
tests/test_api_endpoints.py::test_health_endpoint PASSED
tests/test_api_endpoints.py::test_create_and_get_job_description PASSED
tests/test_api_endpoints.py::test_batch_resume_upload_with_corrupted_file PASSED
tests/test_api_endpoints.py::test_load_all_samples_and_run_matching PASSED
tests/test_matching.py::test_skill_alias_normalization PASSED
tests/test_matching.py::test_extract_skills_from_text PASSED
tests/test_matching.py::test_parse_sample_pdf_resume PASSED
tests/test_matching.py::test_parse_sample_docx_resume PASSED
tests/test_matching.py::test_corrupted_file_handling PASSED
tests/test_matching.py::test_matching_algorithm_scoring PASSED
tests/test_matching.py::test_dynamic_weight_redistribution PASSED
```

---

### Step 3: Frontend Build & Run

#### Option A: Single-Server Unified Run (FastAPI serves built React app)

```bash
# 1. Build frontend
cd frontend
npm install
npm run build

# 2. Start FastAPI server
cd ../backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8088
```

Open **`http://127.0.0.1:8088`** in your browser. Both the API and the React application will be served simultaneously!

#### Option B: Dual Dev Servers (Vite hot-reloading + FastAPI API)

In Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload
```

In Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Open **`http://localhost:5173`** in your browser.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health, database connection mode, model status & weights |
| `POST` | `/api/jd` | Create and analyze a Job Description from raw text |
| `POST` | `/api/jd/upload` | Upload a JD document (`.pdf`, `.docx`, `.txt`) |
| `GET` | `/api/jd` | List all stored Job Descriptions |
| `GET` | `/api/jd/{jd_id}` | Retrieve details of a specific Job Description |
| `POST` | `/api/resumes/upload` | Batch upload multiple resumes with invalid file isolation |
| `POST` | `/api/resumes/load-samples` | 1-click batch loader for 11 realistic test resumes |
| `GET` | `/api/resumes` | List all parsed candidate resumes |
| `GET` | `/api/resumes/{candidate_id}` | Get individual candidate parsed profile |
| `DELETE` | `/api/resumes/clear` | Clear candidate pool |
| `POST` | `/api/match` | Execute hybrid matching & ranking against a JD |
| `GET` | `/api/match/{match_id}` | Retrieve ranked candidate list for a match run |
| `GET` | `/api/match/{match_id}/candidate/{candidate_id}` | Deep candidate analysis (breakdown, evidence, reasons) |
| `GET` | `/api/matches` | List previous match runs |

---

## 🧪 Testing with the Included Sample Resumes

The application includes 11 diverse test resumes and 1 corrupted file located in `backend/sample_resumes/`:

1. **Alex Rivera** (`01_Alex_Rivera_Senior_Backend.pdf`): Senior Backend Engineer (8.9 yrs exp, Python, FastAPI, AWS, Docker, Kubernetes, PostgreSQL, Redis; Master's in CS). **Rank #1 for Senior Backend JD**.
2. **Sarah Kim** (`11_Sarah_Kim_Cloud_Native_Backend.pdf`): Cloud Native Backend (7.9 yrs exp, Python, Go, GCP, AWS, Kubernetes, Docker, PostgreSQL; Master's in CS). **Rank #2**.
3. **Sophia Chen** (`02_Sophia_Chen_FullStack_Cloud.docx`): Full Stack Engineer (5.5 yrs exp, React, TypeScript, Python, FastAPI, AWS, Docker; Bachelor's). **Rank #3**.
4. **Marcus Johnson** (`03_Marcus_Johnson_DevOps_Cloud.pdf`): Lead DevOps / Platform (8 yrs exp, Kubernetes, Terraform, AWS, Docker, Linux, Python).
5. **David Miller** (`05_David_Miller_Mid_Python_Dev.pdf`): Mid-level Python Dev (3 yrs exp, Django, FastAPI, PostgreSQL).
6. **Priya Sharma** (`04_Priya_Sharma_Data_AI_Engineer.docx`): ML & Data Engineer (4.5 yrs exp, PyTorch, Python, NLP, SQL; Master's).
7. **Dr. Amina Kassid** (`08_Dr_Amina_Kassid_ML_Research.pdf`): AI Research Scientist (6 yrs exp, PhD in CS, Transformers, PyTorch).
8. **James Wilson** (`07_James_Wilson_Junior_Developer.pdf`): Junior Developer (1 yr exp, React, Python basics).
9. **Elena Rostova** (`06_Elena_Rostova_Frontend_Specialist.docx`): Senior Frontend Engineer (6 yrs exp, React, TypeScript, Next.js, Tailwind).
10. **Robert Taylor** (`09_Robert_Taylor_Legacy_Java_Dev.docx`): Enterprise Java Developer (10 yrs exp, Java, Spring Boot, Oracle SQL).
11. **Chloe Dupont** (`10_Chloe_Dupont_Product_Manager.pdf`): Technical Product Manager (6 yrs exp, MBA, Agile, Scrum).
12. **Corrupted File** (`12_Corrupted_Invalid_Sample.pdf`): Broken stream header to verify fault tolerance.

Clicking **"Load 11 Test Resumes Batch"** in the UI ingests this complete batch, isolating the corrupted file cleanly, and enables immediate 1-click ranking!

