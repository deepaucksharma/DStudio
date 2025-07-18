// Service Worker for offline support and performance optimization

const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `ds-compendium-${CACHE_VERSION}`;
const RUNTIME_CACHE = `ds-runtime-${CACHE_VERSION}`;

// Resources to cache immediately
const PRECACHE_URLS = [
  '/',
  '/offline/',
  '/manifest.json',
  '/assets/css/main.css',
  '/assets/js/app.min.js',
  // Core pages
  '/introduction/',
  '/part1-axioms/',
  '/part2-pillars/',
  '/reference/glossary/',
  '/tools/'
];

// Cache strategies
const CACHE_STRATEGIES = {
  networkFirst: [
    /\/api\//,
    /\.json$/
  ],
  cacheFirst: [
    /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
    /\.(?:woff|woff2|ttf|otf)$/,
    /\.(?:css|js)$/
  ],
  staleWhileRevalidate: [
    /\.(?:html|md)$/,
    /\/$/ // Directory indexes
  ]
};

// Install event - precache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName.startsWith('ds-') && cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache with strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    // Handle CDN resources
    if (url.hostname.includes('cdn') || url.hostname.includes('fonts')) {
      event.respondWith(cacheFirst(request));
    }
    return;
  }

  // Apply cache strategy based on URL pattern
  const strategy = getStrategy(url.pathname);
  event.respondWith(strategy(request));
});

// Cache strategies implementation
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return createOfflineResponse();
  }
}

async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return createOfflineResponse();
  }
}

async function staleWhileRevalidate(request) {
  const cachedResponse = await caches.match(request);
  
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      const cache = caches.open(RUNTIME_CACHE);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  }).catch(() => null);

  return cachedResponse || fetchPromise || createOfflineResponse();
}

// Determine cache strategy for request
function getStrategy(pathname) {
  for (const [strategyName, patterns] of Object.entries(CACHE_STRATEGIES)) {
    for (const pattern of patterns) {
      if (pattern.test(pathname)) {
        switch (strategyName) {
          case 'networkFirst':
            return networkFirst;
          case 'cacheFirst':
            return cacheFirst;
          case 'staleWhileRevalidate':
            return staleWhileRevalidate;
        }
      }
    }
  }
  return staleWhileRevalidate; // Default strategy
}

// Create offline response
function createOfflineResponse() {
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Offline - DS Compendium</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          margin: 0;
          background: #f5f5f5;
        }
        .offline-message {
          text-align: center;
          padding: 2rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          max-width: 400px;
        }
        h1 { color: #333; margin-bottom: 1rem; }
        p { color: #666; line-height: 1.5; }
        button {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          background: #5448C8;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
      </style>
    </head>
    <body>
      <div class="offline-message">
        <h1>📡 You're Offline</h1>
        <p>The page you're looking for isn't available offline. Please check your connection and try again.</p>
        <button onclick="location.reload()">Retry</button>
      </div>
    </body>
    </html>
  `;

  return new Response(html, {
    headers: { 'Content-Type': 'text/html' },
    status: 503
  });
}

// Background sync for analytics and tool results
self.addEventListener('sync', event => {
  if (event.tag === 'analytics-sync') {
    event.waitUntil(syncAnalytics());
  }
});

async function syncAnalytics() {
  const cache = await caches.open('analytics-queue');
  const requests = await cache.keys();
  
  for (const request of requests) {
    try {
      await fetch(request);
      await cache.delete(request);
    } catch (error) {
      console.error('Failed to sync analytics:', error);
    }
  }
}

// Push notifications for updates
self.addEventListener('push', event => {
  const options = {
    body: event.data?.text() || 'New content available!',
    icon: '/assets/icon-192x192.png',
    badge: '/assets/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    self.registration.showNotification('DS Compendium Update', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});