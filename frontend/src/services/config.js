let rawBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
if (rawBase && !rawBase.endsWith('/api')) {
  rawBase += '/api';
}

export const API_BASE = rawBase || (
  (typeof window !== 'undefined' && window.location.origin.includes('3000'))
    ? '/api'
    : 'http://localhost:8000/api'
);

export async function smartFetch(url, options = {}) {
  // Try primary API_BASE
  try {
    const res = await fetch(`${API_BASE}${url}`, options);
    if (res.ok) return res;
  } catch (err) {
    console.warn(`Primary fetch to ${API_BASE}${url} failed, trying fallback...`);
  }

  // Fallback to direct backend URL in local development
  try {
    const fallbackRes = await fetch(`http://localhost:8000/api${url}`, options);
    return fallbackRes;
  } catch (fallbackErr) {
    console.error(`Fetch failed for both primary and fallback endpoints: ${url}`);
    throw fallbackErr;
  }
}
