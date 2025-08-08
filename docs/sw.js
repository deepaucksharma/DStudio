// Service Worker for The Compendium of Distributed Systems
// Provides offline support and performance optimization

const CACHE_NAME = 'dstudio-v1';
const OFFLINE_URL = 'reference/offline/';

// Files to cache immediately
const PRECACHE_URLS = [
  './',
  'reference/offline/',
  'stylesheets/calculator.css',
  'stylesheets/content-limits.css',
  'stylesheets/custom.css',
  'stylesheets/extra.css',
  'stylesheets/hide-toc.css',
  'stylesheets/pattern-filtering.css',
  'stylesheets/progress-tracker.css',
  'stylesheets/responsive-table.css',
  'stylesheets/visual-components.css',
  'javascripts/custom.js',
  'javascripts/mathjax-config.js',
  'javascripts/mermaid-init.js',
  'javascripts/pattern-filtering.js',
  'javascripts/progress-tracker.js'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching essential files');
        return cache.addAll(PRECACHE_URLS.map(url => new Request(url, {cache: 'reload'})));
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache when possible
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // Return cached version and update in background
          fetchAndCache(event.request);
          return cachedResponse;
        }

        // Not in cache, fetch from network
        return fetchAndCache(event.request);
      })
      .catch(() => {
        // Network failed, return offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match(OFFLINE_URL);
        }

        // For other requests, return a fallback response
        return new Response('Offline', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({
            'Content-Type': 'text/plain'
          })
        });
      })
  );
});

// Helper function to fetch and cache
function fetchAndCache(request) {
  return fetch(request)
    .then(response => {
      // Don't cache bad responses
      if (!response || response.status !== 200 || response.type !== 'basic') {
        return response;
      }

      // Clone the response
      const responseToCache = response.clone();

      caches.open(CACHE_NAME)
        .then(cache => {
          cache.put(request, responseToCache);
        });

      return response;
    });
}

// Message handling for cache control
self.addEventListener('message', event => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }

  if (event.data.action === 'clearCache') {
    caches.delete(CACHE_NAME).then(() => {
      console.log('Service Worker: Cache cleared');
    });
  }
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-analytics') {
    event.waitUntil(syncAnalytics());
  }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', event => {
  if (event.tag === 'update-content') {
    event.waitUntil(updateContent());
  }
});

// Helper functions
async function syncAnalytics() {
  // Sync any offline analytics data
  console.log('Service Worker: Syncing analytics');
}

async function updateContent() {
  // Update cached content in background
  const cache = await caches.open(CACHE_NAME);
  const requests = await cache.keys();

  // Update HTML pages
  const htmlRequests = requests.filter(request =>
    request.url.endsWith('/') || request.url.endsWith('.html')
  );

  for (const request of htmlRequests) {
    try {
      const response = await fetch(request);
      if (response.ok) {
        await cache.put(request, response);
      }
    } catch (error) {
      console.log('Service Worker: Failed to update', request.url);
    }
  }
}
