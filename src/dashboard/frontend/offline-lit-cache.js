/**
 * Offline Lit 3 Cache with localStorage
 * 
 * This script provides additional offline caching for Lit 3 using localStorage
 * as a backup when the local file is not available.
 */

// Cache key for localStorage
const LIT_CACHE_KEY = 'lit3-cache';
const LIT_CACHE_VERSION = '3.0.0';

/**
 * Check if we have a cached version of Lit 3 in localStorage
 */
function hasCachedLit() {
  try {
    const cached = localStorage.getItem(LIT_CACHE_KEY);
    if (!cached) return false;
    
    const data = JSON.parse(cached);
    return data.version === LIT_CACHE_VERSION && data.content;
  } catch (error) {
    console.warn('Failed to check Lit 3 cache:', error);
    return false;
  }
}

/**
 * Get cached Lit 3 from localStorage
 */
function getCachedLit() {
  try {
    const cached = localStorage.getItem(LIT_CACHE_KEY);
    if (!cached) return null;
    
    const data = JSON.parse(cached);
    if (data.version === LIT_CACHE_VERSION && data.content) {
      return data.content;
    }
  } catch (error) {
    console.warn('Failed to get cached Lit 3:', error);
  }
  return null;
}

/**
 * Cache Lit 3 content in localStorage
 */
function cacheLit(content) {
  try {
    const data = {
      version: LIT_CACHE_VERSION,
      content: content,
      timestamp: Date.now()
    };
    localStorage.setItem(LIT_CACHE_KEY, JSON.stringify(data));
    console.log('✅ Lit 3 cached in localStorage');
  } catch (error) {
    console.warn('Failed to cache Lit 3:', error);
  }
}

/**
 * Preload and cache Lit 3 for offline use
 */
async function preloadLit() {
  try {
    // Try to fetch the local copy first
    const response = await fetch('/static/lib/lit/current/lit-core.min.js');
    if (response.ok) {
      const content = await response.text();
      cacheLit(content);
      return true;
    }
  } catch (error) {
    console.warn('Failed to preload Lit 3:', error);
  }
  return false;
}

// Auto-preload when the page loads
if (typeof window !== 'undefined') {
  // Only preload if we don't already have a cached version
  if (!hasCachedLit()) {
    preloadLit();
  }
}

// Export functions for manual use
if (typeof window !== 'undefined') {
  window.litCache = {
    hasCached: hasCachedLit,
    getCached: getCachedLit,
    cache: cacheLit,
    preload: preloadLit
  };
}
