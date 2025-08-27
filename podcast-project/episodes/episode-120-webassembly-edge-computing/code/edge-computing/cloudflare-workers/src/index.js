/**
 * Cloudflare Workers for Indian Tech Companies
 * Flipkart, Paytm, Ola के लिए edge computing examples
 */

import { Router } from 'itty-router';

// Router setup
const router = Router();

// Example 1: E-commerce Product API for Flipkart-style applications
// Heavy traffic के दौरान fast response के लिए edge caching
router.get('/api/products/:productId', async (request, env) => {
  const { productId } = request.params;
  const country = request.cf.country;
  const city = request.cf.city;
  
  // India-specific optimizations
  const isIndianTraffic = country === 'IN';
  const cacheKey = `product:${productId}:${country}`;
  
  try {
    // Try to get from KV cache first (edge caching)
    let product = await env.PRODUCT_CACHE.get(cacheKey, 'json');
    
    if (!product) {
      // Cache miss - fetch from origin and cache
      product = await fetchProductFromOrigin(productId, isIndianTraffic);
      
      // Cache for different durations based on product type
      const ttl = product.category === 'electronics' ? 3600 : 1800; // 1 hour vs 30 min
      await env.PRODUCT_CACHE.put(cacheKey, JSON.stringify(product), {
        expirationTtl: ttl
      });
    }
    
    // Add Indian-specific data
    if (isIndianTraffic) {
      product = await addIndianContext(product, city);
    }
    
    return new Response(JSON.stringify({
      success: true,
      data: product,
      cached: !!product,
      edge_location: request.cf.colo,
      city: city,
      timestamp: new Date().toISOString()
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300', // 5 minutes browser cache
        'CF-Cache-Status': product ? 'HIT' : 'MISS'
      }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Product fetch failed',
      message: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});

// Example 2: Payment Processing for Paytm/Razorpay-style applications
// Edge validation और fraud detection
router.post('/api/payments/validate', async (request, env) => {
  const body = await request.json();
  const clientIP = request.headers.get('CF-Connecting-IP');
  const country = request.cf.country;
  
  // Basic validation
  if (!body.amount || !body.currency || !body.user_id) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Missing required fields'
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // India-specific validations
  if (country === 'IN') {
    // Check for Indian payment methods
    const validCurrency = body.currency === 'INR';
    const validAmount = body.amount >= 1 && body.amount <= 200000; // UPI limits
    
    if (!validCurrency || !validAmount) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Invalid payment parameters for Indian transactions'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
  
  // Edge-based fraud detection
  const fraudScore = await calculateFraudScore(body, clientIP, env);
  
  if (fraudScore > 0.7) {
    // High fraud risk - additional verification required
    return new Response(JSON.stringify({
      success: false,
      requires_verification: true,
      fraud_score: fraudScore,
      message: 'Additional verification required'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Generate payment token
  const paymentToken = await generateSecureToken(body, env);
  
  return new Response(JSON.stringify({
    success: true,
    payment_token: paymentToken,
    fraud_score: fraudScore,
    expires_at: new Date(Date.now() + 15 * 60 * 1000).toISOString() // 15 minutes
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
});

// Example 3: Ride Matching for Ola/Uber-style applications
// Real-time location-based matching using Durable Objects
router.post('/api/rides/request', async (request, env) => {
  const body = await request.json();
  const { user_id, pickup_lat, pickup_lng, destination_lat, destination_lng } = body;
  
  // Input validation
  if (!user_id || !pickup_lat || !pickup_lng) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Missing required location data'
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Get geohash for the pickup location (for sharding)
  const geohash = generateGeohash(pickup_lat, pickup_lng, 5);
  
  // Use Durable Object for ride matching in specific geographic area
  const rideMatchingId = env.RideMatching.idFromName(`geo:${geohash}`);
  const rideMatchingObj = env.RideMatching.get(rideMatchingId);
  
  try {
    const response = await rideMatchingObj.fetch(request);
    return response;
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Ride matching service unavailable',
      retry_after: 5
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});

// Example 4: Content Personalization for Swiggy/Zomato-style applications
// Location और time based restaurant recommendations
router.get('/api/restaurants/recommendations', async (request, env) => {
  const url = new URL(request.url);
  const lat = parseFloat(url.searchParams.get('lat'));
  const lng = parseFloat(url.searchParams.get('lng'));
  const user_id = url.searchParams.get('user_id');
  
  const country = request.cf.country;
  const timezone = request.cf.timezone;
  
  if (!lat || !lng) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Location coordinates required'
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Get current time in user's timezone
  const currentTime = new Date().toLocaleString('en-US', { timeZone: timezone });
  const hour = new Date(currentTime).getHours();
  
  // Time-based cuisine recommendations
  let recommendedCuisines = [];
  if (hour >= 6 && hour <= 11) {
    recommendedCuisines = ['South Indian', 'North Indian', 'Continental'];
  } else if (hour >= 12 && hour <= 16) {
    recommendedCuisines = ['North Indian', 'Chinese', 'Fast Food'];
  } else if (hour >= 17 && hour <= 23) {
    recommendedCuisines = ['Pizza', 'Chinese', 'Biryani', 'Street Food'];
  } else {
    recommendedCuisines = ['Fast Food', 'Desserts', 'Beverages'];
  }
  
  // India-specific optimizations
  if (country === 'IN') {
    // Add popular Indian cuisines based on time
    if (hour >= 19 && hour <= 22) {
      recommendedCuisines.unshift('Biryani', 'North Indian', 'South Indian');
    }
  }
  
  // Cache key based on location and time slot
  const timeSlot = Math.floor(hour / 2) * 2; // 2-hour slots
  const locationKey = `${Math.round(lat * 100)}_${Math.round(lng * 100)}`;
  const cacheKey = `restaurants:${locationKey}:${timeSlot}:${country}`;
  
  // Try cache first
  let restaurants = await env.PRODUCT_CACHE.get(cacheKey, 'json');
  
  if (!restaurants) {
    // Fetch nearby restaurants
    restaurants = await fetchNearbyRestaurants(lat, lng, recommendedCuisines);
    
    // Cache for 1 hour
    await env.PRODUCT_CACHE.put(cacheKey, JSON.stringify(restaurants), {
      expirationTtl: 3600
    });
  }
  
  // Personalize based on user history if available
  if (user_id) {
    const userPreferences = await getUserPreferences(user_id, env);
    restaurants = personalizeRecommendations(restaurants, userPreferences);
  }
  
  return new Response(JSON.stringify({
    success: true,
    data: {
      restaurants: restaurants,
      recommended_cuisines: recommendedCuisines,
      location: { lat, lng },
      current_time: currentTime,
      timezone: timezone
    },
    meta: {
      total_count: restaurants.length,
      cached: !!restaurants,
      edge_location: request.cf.colo
    }
  }), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=600' // 10 minutes
    }
  });
});

// Example 5: A/B Testing and Feature Flags
// नए features को gradually roll out करने के लिए
router.get('/api/config/features', async (request, env) => {
  const url = new URL(request.url);
  const user_id = url.searchParams.get('user_id');
  const app_version = request.headers.get('App-Version');
  const country = request.cf.country;
  
  // Default feature configuration
  let features = {
    new_checkout_flow: false,
    personalized_homepage: false,
    voice_search: false,
    ar_try_on: false,
    live_chat: false
  };
  
  // India-specific features
  if (country === 'IN') {
    features = {
      ...features,
      upi_payments: true,
      hindi_interface: true,
      cod_available: true,
      regional_language_support: true
    };
  }
  
  // A/B testing based on user ID
  if (user_id) {
    const userHash = await hashUserId(user_id);
    const bucket = userHash % 100; // 0-99
    
    // Feature rollouts with percentages
    if (bucket < 20) { // 20% users
      features.new_checkout_flow = true;
    }
    
    if (bucket < 50) { // 50% users
      features.personalized_homepage = true;
    }
    
    if (bucket < 10) { // 10% users (beta feature)
      features.voice_search = true;
    }
    
    // India-specific beta features
    if (country === 'IN' && bucket < 30) {
      features.ar_try_on = true;
    }
  }
  
  // App version-based features
  if (app_version) {
    const version = parseFloat(app_version);
    if (version >= 2.5) {
      features.live_chat = true;
    }
  }
  
  return new Response(JSON.stringify({
    success: true,
    features: features,
    user_bucket: user_id ? await hashUserId(user_id) % 100 : null,
    country: country,
    app_version: app_version,
    timestamp: new Date().toISOString()
  }), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=300'
    }
  });
});

// Health check endpoint
router.get('/health', () => {
  return new Response(JSON.stringify({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
});

// 404 handler
router.all('*', () => {
  return new Response(JSON.stringify({
    success: false,
    error: 'Route not found'
  }), {
    status: 404,
    headers: { 'Content-Type': 'application/json' }
  });
});

// Helper Functions

async function fetchProductFromOrigin(productId, isIndianTraffic) {
  // Mock product data - real implementation would fetch from database
  const baseProduct = {
    id: productId,
    name: `Product ${productId}`,
    category: 'electronics',
    base_price: 10000,
    currency: 'INR',
    availability: true
  };
  
  if (isIndianTraffic) {
    // Add India-specific data
    baseProduct.gst_rate = 18;
    baseProduct.cod_available = true;
    baseProduct.estimated_delivery = '2-3 days';
  }
  
  return baseProduct;
}

async function addIndianContext(product, city) {
  // Add city-specific delivery information
  const deliveryInfo = {
    'Mumbai': { fast_delivery: true, delivery_time: '1-2 days', cod_fee: 40 },
    'Delhi': { fast_delivery: true, delivery_time: '1-2 days', cod_fee: 40 },
    'Bangalore': { fast_delivery: true, delivery_time: '1-2 days', cod_fee: 40 },
    'Chennai': { fast_delivery: false, delivery_time: '2-3 days', cod_fee: 50 },
    'Kolkata': { fast_delivery: false, delivery_time: '2-3 days', cod_fee: 50 }
  };
  
  product.delivery_info = deliveryInfo[city] || {
    fast_delivery: false,
    delivery_time: '3-5 days',
    cod_fee: 60
  };
  
  return product;
}

async function calculateFraudScore(paymentData, clientIP, env) {
  let score = 0.0;
  
  // Basic fraud indicators
  if (paymentData.amount > 50000) score += 0.2; // High amount
  if (paymentData.amount % 1000 === 0) score += 0.1; // Round numbers
  
  // Time-based checks
  const hour = new Date().getHours();
  if (hour >= 0 && hour <= 6) score += 0.3; // Late night transactions
  
  // Velocity checks (simplified)
  const userTransactionKey = `fraud:${paymentData.user_id}:${Date.now()}`;
  const recentTransactions = await env.USER_SESSIONS.get(userTransactionKey);
  if (recentTransactions && parseInt(recentTransactions) > 3) {
    score += 0.4; // Too many transactions
  }
  
  return Math.min(score, 1.0);
}

async function generateSecureToken(paymentData, env) {
  const data = JSON.stringify({
    user_id: paymentData.user_id,
    amount: paymentData.amount,
    timestamp: Date.now()
  });
  
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function generateGeohash(lat, lng, precision) {
  // Simplified geohash implementation
  const latRange = [-90, 90];
  const lngRange = [-180, 180];
  let hash = '';
  let isEven = true;
  
  for (let i = 0; i < precision; i++) {
    if (isEven) {
      const mid = (lngRange[0] + lngRange[1]) / 2;
      if (lng >= mid) {
        hash += '1';
        lngRange[0] = mid;
      } else {
        hash += '0';
        lngRange[1] = mid;
      }
    } else {
      const mid = (latRange[0] + latRange[1]) / 2;
      if (lat >= mid) {
        hash += '1';
        latRange[0] = mid;
      } else {
        hash += '0';
        latRange[1] = mid;
      }
    }
    isEven = !isEven;
  }
  
  return hash;
}

async function fetchNearbyRestaurants(lat, lng, cuisines) {
  // Mock restaurant data
  return [
    {
      id: 'rest_1',
      name: 'Mumbai Tiffin Service',
      cuisine: ['North Indian', 'South Indian'],
      rating: 4.2,
      delivery_time: '30-40 mins',
      distance: 1.2
    },
    {
      id: 'rest_2', 
      name: 'Beijing Bites',
      cuisine: ['Chinese'],
      rating: 4.0,
      delivery_time: '25-35 mins',
      distance: 0.8
    }
  ];
}

async function getUserPreferences(userId, env) {
  const preferences = await env.USER_SESSIONS.get(`prefs:${userId}`, 'json');
  return preferences || { favorite_cuisines: [], dietary_restrictions: [] };
}

function personalizeRecommendations(restaurants, preferences) {
  // Simple personalization logic
  return restaurants.sort((a, b) => {
    const aScore = preferences.favorite_cuisines.some(c => 
      a.cuisine.includes(c)) ? 1 : 0;
    const bScore = preferences.favorite_cuisines.some(c => 
      b.cuisine.includes(c)) ? 1 : 0;
    return bScore - aScore;
  });
}

async function hashUserId(userId) {
  const encoder = new TextEncoder();
  const data = encoder.encode(userId);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.reduce((sum, byte) => sum + byte, 0);
}

// Durable Object for Ride Matching
export class RideMatchingDO {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.drivers = new Map(); // Available drivers in this geo area
    this.requests = new Map(); // Pending ride requests
  }
  
  async fetch(request) {
    const body = await request.json();
    const { action, user_id, user_type, lat, lng } = body;
    
    switch (action) {
      case 'request_ride':
        return this.handleRideRequest(body);
      case 'driver_available':
        return this.handleDriverAvailable(body);
      case 'driver_busy':
        return this.handleDriverBusy(body);
      default:
        return new Response(JSON.stringify({
          success: false,
          error: 'Unknown action'
        }), { status: 400 });
    }
  }
  
  async handleRideRequest(data) {
    const { user_id, pickup_lat, pickup_lng, destination_lat, destination_lng } = data;
    
    // Find nearest available driver
    let nearestDriver = null;
    let minDistance = Infinity;
    
    for (const [driverId, driver] of this.drivers) {
      if (driver.status === 'available') {
        const distance = this.calculateDistance(
          pickup_lat, pickup_lng,
          driver.lat, driver.lng
        );
        
        if (distance < minDistance && distance <= 5) { // Within 5km
          minDistance = distance;
          nearestDriver = { id: driverId, ...driver, distance };
        }
      }
    }
    
    if (nearestDriver) {
      // Match found
      this.drivers.set(nearestDriver.id, {
        ...nearestDriver,
        status: 'busy',
        current_ride: user_id
      });
      
      return new Response(JSON.stringify({
        success: true,
        matched: true,
        driver: {
          id: nearestDriver.id,
          name: nearestDriver.name,
          rating: nearestDriver.rating,
          distance: nearestDriver.distance,
          eta: Math.ceil(nearestDriver.distance * 3) // 3 minutes per km
        }
      }));
    } else {
      // No driver available - add to queue
      this.requests.set(user_id, {
        pickup_lat,
        pickup_lng,
        destination_lat,
        destination_lng,
        timestamp: Date.now()
      });
      
      return new Response(JSON.stringify({
        success: true,
        matched: false,
        queued: true,
        estimated_wait: this.requests.size * 2 // 2 minutes per pending request
      }));
    }
  }
  
  async handleDriverAvailable(data) {
    const { driver_id, lat, lng, name, rating } = data;
    
    this.drivers.set(driver_id, {
      lat,
      lng,
      name,
      rating,
      status: 'available',
      last_update: Date.now()
    });
    
    // Check if any pending requests can be matched
    await this.processPendingRequests();
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Driver status updated'
    }));
  }
  
  async handleDriverBusy(data) {
    const { driver_id } = data;
    
    if (this.drivers.has(driver_id)) {
      this.drivers.set(driver_id, {
        ...this.drivers.get(driver_id),
        status: 'busy'
      });
    }
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Driver marked as busy'
    }));
  }
  
  async processPendingRequests() {
    for (const [userId, request] of this.requests) {
      // Try to match with available drivers
      for (const [driverId, driver] of this.drivers) {
        if (driver.status === 'available') {
          const distance = this.calculateDistance(
            request.pickup_lat, request.pickup_lng,
            driver.lat, driver.lng
          );
          
          if (distance <= 5) { // Within 5km
            // Match found - remove from queue
            this.requests.delete(userId);
            this.drivers.set(driverId, {
              ...driver,
              status: 'busy',
              current_ride: userId
            });
            break;
          }
        }
      }
    }
  }
  
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
}

// Main handler
export default {
  async fetch(request, env, ctx) {
    return router.handle(request, env, ctx);
  }
};