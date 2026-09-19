const isBrowser = typeof window !== 'undefined';
const isLocalhost = isBrowser && (
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname === '0.0.0.0'
);

let rawBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/$/, '');
if (rawBase && !rawBase.endsWith('/api')) {
  rawBase += '/api';
}

// In production, fallback to '/api' if VITE_API_BASE_URL is not set,
// never to localhost:8000 which triggers browser Mixed Content security blocks.
export const API_BASE = rawBase || (
  isLocalhost
    ? (window.location.origin.includes('3000') ? '/api' : 'http://localhost:8000/api')
    : '/api'
);

/**
 * Smart fetch wrapper that:
 * 1. Honors server HTTP error status codes (400, 404, 500) and returns the Response
 *    object so callers can inspect and parse server error messages.
 * 2. Does NOT fall back to localhost:8000 in production.
 * 3. Catches network failures (e.g. Render free tier cold-start sleep) and surfaces
 *    a human-readable explanation instead of raw "Failed to fetch".
 * 4. Supports an automatic timeout (default 60s) to accommodate Render container spin-up.
 */
export async function smartFetch(url, options = {}, timeoutMs = 60000) {
  const targetUrl = `${API_BASE}${url}`;

  // Set up abort controller for timeout if caller hasn't provided their own signal
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  const fetchOptions = {
    ...options,
    signal: options.signal || controller.signal,
  };

  try {
    const res = await fetch(targetUrl, fetchOptions);
    clearTimeout(timeoutId);
    // Return res directly (even if res.ok is false, like 400 or 500),
    // so caller services can handle HTTP errors and read error.detail.
    return res;
  } catch (err) {
    clearTimeout(timeoutId);

    // Only attempt localhost fallback when genuinely in local development
    if (isLocalhost && API_BASE !== 'http://localhost:8000/api') {
      try {
        console.warn(`Primary fetch to ${targetUrl} failed, trying local fallback http://localhost:8000/api${url}...`);
        const fallbackRes = await fetch(`http://localhost:8000/api${url}`, options);
        return fallbackRes;
      } catch (fallbackErr) {
        console.error(`Fetch failed for both primary and fallback endpoints: ${url}`);
      }
    }

    // Friendly error messaging for Render spin-down / network failures
    const isAbort = err.name === 'AbortError';
    const isNetworkError = err.name === 'TypeError' || err.message?.toLowerCase().includes('fetch');

    if (isAbort) {
      throw new Error(
        'The request timed out. If your backend is hosted on Render free tier, it takes 50–60 seconds to wake up from inactivity. Please wait a moment and try again.'
      );
    }

    if (isNetworkError) {
      throw new Error(
        'Unable to reach backend server. If using Render free tier, the service sleeps after 15 minutes of inactivity and takes ~60 seconds to wake up. Please verify the server is awake and try again.'
      );
    }

    throw err;
  }
}
