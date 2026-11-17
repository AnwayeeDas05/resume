const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function createJobDescription(data) {
  const res = await fetch(`${API_BASE}/jd`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create Job Description');
  }
  return res.json();
}

export async function uploadJobDescriptionFile(file, title, company) {
  const formData = new FormData();
  formData.append('file', file);
  if (title) formData.append('title', title);
  if (company) formData.append('company', company);

  const res = await fetch(`${API_BASE}/jd/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload JD file');
  }
  return res.json();
}

export async function fetchJobDescriptions() {
  const res = await fetch(`${API_BASE}/jd`);
  if (!res.ok) throw new Error('Failed to fetch job descriptions');
  return res.json();
}

export async function uploadResumesBatch(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }

  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload batch of resumes');
  }
  return res.json();
}

export async function loadSampleResumes(includeCorrupted = false) {
  const url = includeCorrupted
    ? `${API_BASE}/resumes/load-samples?include_corrupted=true`
    : `${API_BASE}/resumes/load-samples`;
  const res = await fetch(url, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to load sample resumes');
  }
  return res.json();
}

export async function testCorruptedUpload() {
  const res = await fetch(`${API_BASE}/resumes/test-corrupted-upload`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to test corrupted file');
  }
  return res.json();
}


export async function fetchResumes() {
  const res = await fetch(`${API_BASE}/resumes`);
  if (!res.ok) throw new Error('Failed to fetch resumes');
  return res.json();
}

export async function clearResumes() {
  const res = await fetch(`${API_BASE}/resumes/clear`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to clear resumes');
  return res.json();
}

export async function runCandidateMatching(jdId, candidateIds = null, customWeights = null) {
  const payload = { jd_id: jdId };
  if (candidateIds && candidateIds.length > 0) payload.candidate_ids = candidateIds;
  if (customWeights) payload.custom_weights = customWeights;

  const res = await fetch(`${API_BASE}/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to execute candidate matching');
  }
  return res.json();
}

export async function fetchMatchRun(matchId) {
  const res = await fetch(`${API_BASE}/match/${matchId}`);
  if (!res.ok) throw new Error('Failed to fetch match run');
  return res.json();
}

export async function fetchCandidateAnalysis(matchId, candidateId) {
  const res = await fetch(`${API_BASE}/match/${matchId}/candidate/${candidateId}`);
  if (!res.ok) throw new Error('Failed to fetch candidate analysis');
  return res.json();
}

