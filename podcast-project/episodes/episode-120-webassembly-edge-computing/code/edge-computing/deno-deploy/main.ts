/**
 * Deno Deploy Edge Functions for Indian Tech Companies
 * TypeScript-based edge computing examples for Flipkart, Paytm, Ola, Swiggy
 */

import { Application, Router } from "oak";
import { oakCors } from "cors";
import { crypto } from "crypto";
import { v4 } from "uuid";

const app = new Application();
const router = new Router();

// Middleware setup
app.use(oakCors({
  origin: ["https://flipkart.com", "https://paytm.com", "https://olacabs.com", "https://swiggy.com"],
  credentials: true
}));

app.use(async (ctx, next) => {
  console.log(`${ctx.request.method} ${ctx.request.url} - ${new Date().toISOString()}`);
  await next();
});

// Example 1: Indian Railways Seat Availability Check
// IRCTC जैसे real-time seat availability के लिए edge computing
router.get("/api/trains/availability", async (ctx) => {
  const { from, to, date, class: travelClass } = Object.fromEntries(ctx.request.url.searchParams);
  
  if (!from || !to || !date) {
    ctx.response.status = 400;
    ctx.response.body = {
      success: false,
      error: "Missing required parameters: from, to, date"
    };
    return;
  }
  
  // Simulate Indian Railway station codes
  const stationCodes: Record<string, string> = {
    "mumbai": "CSMT",
    "delhi": "NDLS", 
    "bangalore": "SBC",
    "chennai": "MAS",
    "kolkata": "HWH",
    "pune": "PUNE",
    "hyderabad": "HYB"
  };
  
  const fromCode = stationCodes[from.toLowerCase()];
  const toCode = stationCodes[to.toLowerCase()];
  
  if (!fromCode || !toCode) {
    ctx.response.status = 400;
    ctx.response.body = {
      success: false,
      error: "Invalid station names. Supported: mumbai, delhi, bangalore, chennai, kolkata, pune, hyderabad"
    };
    return;
  }
  
  // Mock train data with realistic availability
  const trains = await generateTrainAvailability(fromCode, toCode, date, travelClass || "3A");
  
  // Edge caching for frequently searched routes
  const cacheKey = `${fromCode}-${toCode}-${date}-${travelClass}`;
  
  ctx.response.headers.set("Cache-Control", "public, max-age=300"); // 5 minutes
  ctx.response.headers.set("X-Cache-Key", cacheKey);
  ctx.response.headers.set("X-Edge-Location", Deno.env.get("DENO_REGION") || "unknown");
  
  ctx.response.body = {
    success: true,
    data: {
      route: `${fromCode} → ${toCode}`,
      date: date,
      class: travelClass || "3A",
      trains: trains,
      last_updated: new Date().toISOString()
    }
  };
});

// Example 2: UPI Payment QR Code Generation
// Paytm, PhonePe जैसे instant QR code generation के लिए
router.post("/api/upi/generate-qr", async (ctx) => {
  const body = await ctx.request.body({ type: "json" }).value;
  const { merchant_id, amount, order_id, description } = body;
  
  // Input validation
  if (!merchant_id || !amount || amount <= 0) {
    ctx.response.status = 400;
    ctx.response.body = {
      success: false,
      error: "Valid merchant_id and positive amount required"
    };
    return;
  }
  
  // UPI payment string format
  const upiString = `upi://pay?pa=${merchant_id}@paytm&pn=Merchant&am=${amount}&cu=INR&tn=${encodeURIComponent(description || 'Payment')}&tr=${order_id || v4.generate()}`;
  
  // Generate QR code data (in real implementation, use QR library)
  const qrData = await generateQRCode(upiString);
  
  // Calculate GST for business transactions
  const gstAmount = amount >= 2000 ? (amount * 0.18) : 0;
  
  ctx.response.body = {
    success: true,
    data: {
      qr_string: upiString,
      qr_code: qrData,
      amount: amount,
      gst_amount: gstAmount,
      total_amount: amount + gstAmount,
      expires_at: new Date(Date.now() + 15 * 60 * 1000).toISOString(), // 15 minutes
      order_id: order_id || v4.generate()
    }
  };
});

// Example 3: Food Delivery Route Optimization
// Swiggy, Zomato के delivery partner के लिए optimal route
router.post("/api/delivery/optimize-route", async (ctx) => {
  const body = await ctx.request.body({ type: "json" }).value;
  const { delivery_partner_location, orders } = body;
  
  if (!delivery_partner_location || !orders || orders.length === 0) {
    ctx.response.status = 400;
    ctx.response.body = {
      success: false,
      error: "Delivery partner location and orders array required"
    };
    return;
  }
  
  // TSP (Traveling Salesman Problem) approximation for route optimization
  const optimizedRoute = await optimizeDeliveryRoute(delivery_partner_location, orders);
  
  // Calculate total distance and estimated time
  const totalDistance = optimizedRoute.total_distance;
  const estimatedTime = calculateDeliveryTime(totalDistance);
  
  // Mumbai traffic considerations
  const currentHour = new Date().getHours();
  const trafficMultiplier = (currentHour >= 8 && currentHour <= 11) || (currentHour >= 18 && currentHour <= 21) ? 1.8 : 1.2;
  
  ctx.response.body = {
    success: true,
    data: {
      optimized_route: optimizedRoute.route,
      total_distance_km: totalDistance,
      estimated_time_minutes: Math.ceil(estimatedTime * trafficMultiplier),
      traffic_factor: trafficMultiplier,
      fuel_cost_inr: Math.ceil(totalDistance * 5.5), // ₹5.5 per km
      orders_sequence: optimizedRoute.order_sequence
    }
  };
});

// Example 4: E-commerce Dynamic Pricing
// Flipkart, Amazon के dynamic pricing के लिए edge-based pricing
router.get("/api/pricing/dynamic/:productId", async (ctx) => {
  const { productId } = ctx.params;
  const userLocation = ctx.request.headers.get("CF-IPCountry") || "IN";
  const userAgent = ctx.request.headers.get("User-Agent") || "";
  
  // Base product data (mock)
  const baseProduct = await getProductData(productId);
  if (!baseProduct) {
    ctx.response.status = 404;
    ctx.response.body = {
      success: false,
      error: "Product not found"
    };
    return;
  }
  
  // Dynamic pricing factors
  let finalPrice = baseProduct.base_price;
  const pricingFactors = {
    base_price: baseProduct.base_price,
    demand_surge: 0,
    inventory_level: 0,
    competition_price: 0,
    location_factor: 0,
    time_factor: 0
  };
  
  // Demand-based pricing (mock algorithm)
  const currentHour = new Date().getHours();
  const demandScore = await calculateDemandScore(productId, currentHour);
  pricingFactors.demand_surge = demandScore * 0.1 * baseProduct.base_price;
  
  // Inventory-based pricing
  const inventoryLevel = await getInventoryLevel(productId);
  if (inventoryLevel < 10) {
    pricingFactors.inventory_level = 0.05 * baseProduct.base_price; // 5% increase for low inventory
  }
  
  // Location-based pricing (shipping costs)
  const locationMultiplier = getLocationPricingMultiplier(userLocation);
  pricingFactors.location_factor = (locationMultiplier - 1) * baseProduct.base_price;
  
  // Time-based pricing (flash sales, etc.)
  const timeMultiplier = getTimePricingMultiplier(currentHour);
  pricingFactors.time_factor = (timeMultiplier - 1) * baseProduct.base_price;
  
  // Calculate final price
  finalPrice = Object.values(pricingFactors).reduce((sum, factor) => sum + factor, 0);
  
  // Ensure price doesn't go below minimum margin
  const minimumPrice = baseProduct.base_price * 0.8;
  finalPrice = Math.max(finalPrice, minimumPrice);
  
  ctx.response.body = {
    success: true,
    data: {
      product_id: productId,
      current_price: Math.ceil(finalPrice),
      mrp: baseProduct.mrp,
      discount_percentage: Math.ceil(((baseProduct.mrp - finalPrice) / baseProduct.mrp) * 100),
      pricing_factors: pricingFactors,
      valid_until: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // 5 minutes
      location: userLocation
    }
  };
});

// Example 5: Real-time Chat Moderation
// WhatsApp Business, Instagram के automated content moderation
router.post("/api/chat/moderate", async (ctx) => {
  const body = await ctx.request.body({ type: "json" }).value;
  const { message, user_id, chat_type } = body;
  
  if (!message || !user_id) {
    ctx.response.status = 400;
    ctx.response.body = {
      success: false,
      error: "Message and user_id required"
    };
    return;
  }
  
  // Multi-language content moderation (English + Hindi)
  const moderationResult = await moderateContent(message);
  
  // Spam detection
  const spamScore = await calculateSpamScore(message, user_id);
  
  // Sentiment analysis
  const sentimentScore = await analyzeSentiment(message);
  
  // Profanity filter (Hindi + English)
  const profanityDetected = await detectProfanity(message);
  
  // Final moderation decision
  let action = "allow";
  let confidence = 0.9;
  
  if (profanityDetected.detected || moderationResult.harmful) {
    action = "block";
    confidence = 0.95;
  } else if (spamScore > 0.7) {
    action = "flag";
    confidence = 0.8;
  } else if (sentimentScore < -0.8) {
    action = "flag";
    confidence = 0.7;
  }
  
  ctx.response.body = {
    success: true,
    data: {
      action: action,
      confidence: confidence,
      moderation_details: {
        spam_score: spamScore,
        sentiment_score: sentimentScore,
        profanity_detected: profanityDetected.detected,
        harmful_content: moderationResult.harmful,
        language_detected: moderationResult.language
      },
      processed_at: new Date().toISOString()
    }
  };
});

// Health check endpoint
router.get("/health", (ctx) => {
  ctx.response.body = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    deno_version: Deno.version.deno,
    region: Deno.env.get("DENO_REGION") || "unknown"
  };
});

// Helper Functions

async function generateTrainAvailability(from: string, to: string, date: string, travelClass: string) {
  const trains = [
    {
      number: "12137",
      name: "Punjab Mail",
      departure: "15:40",
      arrival: "08:35+1",
      duration: "16h 55m"
    },
    {
      number: "12953",
      name: "August Kranti Rajdhani",
      departure: "17:15",
      arrival: "09:55+1",
      duration: "16h 40m"
    },
    {
      number: "12615",
      name: "Grand Trunk Express",
      departure: "21:35",
      arrival: "14:20+1",
      duration: "16h 45m"
    }
  ];
  
  return trains.map(train => ({
    ...train,
    availability: Math.floor(Math.random() * 50) + 1, // Random availability 1-50
    fare: Math.floor(Math.random() * 2000) + 1000,  // Random fare ₹1000-3000
    status: Math.random() > 0.7 ? "RAC" : "Available"
  }));
}

async function generateQRCode(data: string): Promise<string> {
  // In real implementation, use a QR code library
  // This is a mock base64 QR code representation
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest("SHA-256", dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return "data:image/png;base64," + btoa(String.fromCharCode(...hashArray.slice(0, 32)));
}

async function optimizeDeliveryRoute(startLocation: {lat: number, lng: number}, orders: Array<{lat: number, lng: number, order_id: string}>) {
  // Simplified nearest neighbor algorithm for TSP approximation
  const route = [startLocation];
  const remainingOrders = [...orders];
  let totalDistance = 0;
  const orderSequence = [];
  
  while (remainingOrders.length > 0) {
    const currentLocation = route[route.length - 1];
    let nearestIndex = 0;
    let minDistance = Number.MAX_VALUE;
    
    for (let i = 0; i < remainingOrders.length; i++) {
      const distance = calculateHaversineDistance(
        currentLocation.lat, currentLocation.lng,
        remainingOrders[i].lat, remainingOrders[i].lng
      );
      
      if (distance < minDistance) {
        minDistance = distance;
        nearestIndex = i;
      }
    }
    
    const nearestOrder = remainingOrders.splice(nearestIndex, 1)[0];
    route.push(nearestOrder);
    orderSequence.push(nearestOrder.order_id);
    totalDistance += minDistance;
  }
  
  return {
    route: route,
    total_distance: totalDistance,
    order_sequence: orderSequence
  };
}

function calculateHaversineDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function calculateDeliveryTime(distanceKm: number): number {
  // Mumbai delivery time estimation
  const avgSpeed = 12; // km/hour in Mumbai traffic
  return (distanceKm / avgSpeed) * 60; // minutes
}

async function getProductData(productId: string) {
  // Mock product database
  const products: Record<string, any> = {
    "phone_001": {
      name: "Samsung Galaxy S24",
      base_price: 79999,
      mrp: 89999,
      category: "electronics"
    },
    "laptop_001": {
      name: "MacBook Air M2",
      base_price: 114900,
      mrp: 119900,
      category: "computers"
    }
  };
  
  return products[productId] || null;
}

async function calculateDemandScore(productId: string, hour: number): Promise<number> {
  // Mock demand calculation based on time
  if (hour >= 20 && hour <= 23) return 0.8; // High evening demand
  if (hour >= 12 && hour <= 14) return 0.6; // Lunch time demand
  return 0.3; // Normal demand
}

async function getInventoryLevel(productId: string): Promise<number> {
  // Mock inventory levels
  return Math.floor(Math.random() * 50) + 1;
}

function getLocationPricingMultiplier(location: string): number {
  const locationMultipliers: Record<string, number> = {
    "IN": 1.0,    // India - base price
    "US": 1.15,   // International shipping
    "GB": 1.12,   // International shipping
    "AU": 1.18,   // International shipping
  };
  
  return locationMultipliers[location] || 1.1;
}

function getTimePricingMultiplier(hour: number): number {
  // Flash sale during specific hours
  if (hour >= 14 && hour <= 16) return 0.9; // Afternoon sale
  if (hour >= 21 && hour <= 23) return 0.85; // Night sale
  return 1.0;
}

async function moderateContent(message: string) {
  // Simplified content moderation
  const harmfulKeywords = ["spam", "scam", "fake", "धोखा", "झूठ"];
  const harmful = harmfulKeywords.some(keyword => 
    message.toLowerCase().includes(keyword.toLowerCase())
  );
  
  // Simple language detection
  const hindiPattern = /[\u0900-\u097F]/;
  const language = hindiPattern.test(message) ? "hi" : "en";
  
  return { harmful, language };
}

async function calculateSpamScore(message: string, userId: string): Promise<number> {
  let score = 0;
  
  // URL detection
  if (message.includes("http") || message.includes("www")) score += 0.3;
  
  // Repeated characters
  if (/(.)\1{3,}/.test(message)) score += 0.2;
  
  // All caps
  if (message === message.toUpperCase() && message.length > 10) score += 0.2;
  
  // Phone numbers
  if (/\d{10}/.test(message)) score += 0.1;
  
  return Math.min(score, 1.0);
}

async function analyzeSentiment(message: string): Promise<number> {
  // Simplified sentiment analysis
  const positiveWords = ["good", "great", "amazing", "love", "excellent", "अच्छा", "बहुत बढ़िया"];
  const negativeWords = ["bad", "terrible", "hate", "awful", "worst", "बुरा", "गलत"];
  
  let score = 0;
  const words = message.toLowerCase().split(/\s+/);
  
  for (const word of words) {
    if (positiveWords.includes(word)) score += 0.1;
    if (negativeWords.includes(word)) score -= 0.1;
  }
  
  return Math.max(-1, Math.min(1, score));
}

async function detectProfanity(message: string) {
  // Basic profanity detection (Hindi + English)
  const profanityWords = ["badword1", "badword2", "गाली"]; // Simplified list
  
  const detected = profanityWords.some(word => 
    message.toLowerCase().includes(word.toLowerCase())
  );
  
  return { detected };
}

// Setup routes
app.use(router.routes());
app.use(router.allowedMethods());

// Error handling
app.addEventListener("error", (evt) => {
  console.error("Unhandled error:", evt.error);
});

// Start server
console.log("🚀 Deno Deploy server starting for Indian tech companies...");
await app.listen({ port: 8000 });