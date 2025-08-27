// AssemblyScript examples for Indian tech companies
// Ola के ride matching, Swiggy के delivery optimization के लिए

// Example 1: Geospatial calculations for Ola/Uber
// GPS coordinates के बीच distance calculate करना

export class GeoUtils {
  // Haversine formula - Earth पर दो points के बीच distance
  // Mumbai में Bandra से Andheri तक का distance निकालने के लिए
  static haversineDistance(
    lat1: f64, lon1: f64, 
    lat2: f64, lon2: f64
  ): f64 {
    const R: f64 = 6371.0; // Earth radius in kilometers
    
    // Convert degrees to radians
    const lat1Rad: f64 = lat1 * Math.PI / 180.0;
    const lon1Rad: f64 = lon1 * Math.PI / 180.0;
    const lat2Rad: f64 = lat2 * Math.PI / 180.0;
    const lon2Rad: f64 = lon2 * Math.PI / 180.0;
    
    const dLat: f64 = lat2Rad - lat1Rad;
    const dLon: f64 = lon2Rad - lon1Rad;
    
    const a: f64 = Math.sin(dLat / 2.0) * Math.sin(dLat / 2.0) +
                   Math.cos(lat1Rad) * Math.cos(lat2Rad) *
                   Math.sin(dLon / 2.0) * Math.sin(dLon / 2.0);
    
    const c: f64 = 2.0 * Math.atan2(Math.sqrt(a), Math.sqrt(1.0 - a));
    
    return R * c;
  }
  
  // Check if point is inside circle - delivery radius check के लिए
  // Swiggy के 5km radius check
  static isWithinDeliveryRadius(
    centerLat: f64, centerLon: f64,
    pointLat: f64, pointLon: f64,
    radiusKm: f64
  ): bool {
    const distance: f64 = GeoUtils.haversineDistance(
      centerLat, centerLon, pointLat, pointLon
    );
    return distance <= radiusKm;
  }
  
  // Calculate estimated travel time - traffic के साथ
  // Mumbai traffic को consider करके time calculation
  static estimateTravelTime(
    distanceKm: f64,
    hourOfDay: i32,
    dayOfWeek: i32
  ): f64 {
    let baseSpeed: f64 = 25.0; // Base speed in km/h
    
    // Peak hours में speed कम हो जाती है
    if ((hourOfDay >= 8 && hourOfDay <= 11) || 
        (hourOfDay >= 18 && hourOfDay <= 21)) {
      baseSpeed *= 0.4; // 60% slower during peak hours
    }
    
    // Weekend पर थोड़ा better traffic
    if (dayOfWeek == 0 || dayOfWeek == 6) { // Sunday or Saturday
      baseSpeed *= 1.2;
    }
    
    // Monsoon season में और भी slow (June-September)
    // This would be passed as parameter in real implementation
    
    return (distanceKm / baseSpeed) * 60.0; // Return time in minutes
  }
}

// Example 2: Sorting algorithms for Swiggy restaurant recommendations
// Rating, distance, price के basis पर restaurants को sort करना

export class RestaurantRecommendation {
  // Quick sort implementation for restaurant ranking
  static quickSort(
    scores: Float64Array,
    indices: Int32Array,
    low: i32,
    high: i32
  ): void {
    if (low < high) {
      const pivotIndex: i32 = this.partition(scores, indices, low, high);
      
      this.quickSort(scores, indices, low, pivotIndex - 1);
      this.quickSort(scores, indices, pivotIndex + 1, high);
    }
  }
  
  private static partition(
    scores: Float64Array,
    indices: Int32Array,
    low: i32,
    high: i32
  ): i32 {
    const pivot: f64 = scores[high];
    let i: i32 = low - 1;
    
    for (let j: i32 = low; j < high; j++) {
      if (scores[j] >= pivot) { // Sort in descending order (higher score first)
        i++;
        
        // Swap scores
        const tempScore: f64 = scores[i];
        scores[i] = scores[j];
        scores[j] = tempScore;
        
        // Swap indices
        const tempIndex: i32 = indices[i];
        indices[i] = indices[j];
        indices[j] = tempIndex;
      }
    }
    
    // Swap pivot
    const tempScore: f64 = scores[i + 1];
    scores[i + 1] = scores[high];
    scores[high] = tempScore;
    
    const tempIndex: i32 = indices[i + 1];
    indices[i + 1] = indices[high];
    indices[high] = tempIndex;
    
    return i + 1;
  }
  
  // Calculate restaurant recommendation score
  // Rating (40%) + Distance (30%) + Price (20%) + Availability (10%)
  static calculateScore(
    rating: f64,          // 1-5 scale
    distanceKm: f64,      // Distance in km
    avgPrice: f64,        // Average price per person
    isAvailable: bool,    // Restaurant currently accepting orders
    userBudget: f64       // User's budget preference
  ): f64 {
    let score: f64 = 0.0;
    
    // Rating component (40% weightage)
    score += (rating / 5.0) * 0.4;
    
    // Distance component (30% weightage) - closer is better
    const maxDistance: f64 = 10.0; // Max delivery distance
    const distanceScore: f64 = Math.max(0.0, (maxDistance - distanceKm) / maxDistance);
    score += distanceScore * 0.3;
    
    // Price component (20% weightage) - match user budget
    let priceScore: f64 = 1.0;
    if (avgPrice > userBudget) {
      priceScore = Math.max(0.0, (userBudget / avgPrice));
    }
    score += priceScore * 0.2;
    
    // Availability component (10% weightage)
    if (isAvailable) {
      score += 0.1;
    }
    
    return score;
  }
}

// Example 3: String algorithms for search functionality
// Flipkart के product search में typo tolerance के लिए

export class SearchUtils {
  // Edit distance (Levenshtein) for fuzzy search
  // "mobail" search करने पर "mobile" मिल जाए
  static editDistance(s1: string, s2: string): i32 {
    const len1: i32 = s1.length;
    const len2: i32 = s2.length;
    
    // Create DP table
    const dp: Int32Array = new Int32Array((len1 + 1) * (len2 + 1));
    
    // Initialize first row and column
    for (let i: i32 = 0; i <= len1; i++) {
      dp[i * (len2 + 1)] = i;
    }
    for (let j: i32 = 0; j <= len2; j++) {
      dp[j] = j;
    }
    
    // Fill DP table
    for (let i: i32 = 1; i <= len1; i++) {
      for (let j: i32 = 1; j <= len2; j++) {
        const cost: i32 = s1.charCodeAt(i - 1) == s2.charCodeAt(j - 1) ? 0 : 1;
        
        const substitute: i32 = dp[(i - 1) * (len2 + 1) + (j - 1)] + cost;
        const insert: i32 = dp[i * (len2 + 1) + (j - 1)] + 1;
        const delete: i32 = dp[(i - 1) * (len2 + 1) + j] + 1;
        
        dp[i * (len2 + 1) + j] = Math.min(Math.min(substitute, insert), delete);
      }
    }
    
    return dp[len1 * (len2 + 1) + len2];
  }
  
  // KMP string matching for exact product name search
  // Fast string matching algorithm
  static kmpSearch(text: string, pattern: string): Int32Array {
    const textLen: i32 = text.length;
    const patternLen: i32 = pattern.length;
    
    if (patternLen == 0) {
      return new Int32Array(0);
    }
    
    // Build failure function
    const failure: Int32Array = new Int32Array(patternLen);
    let j: i32 = 0;
    
    for (let i: i32 = 1; i < patternLen; i++) {
      while (j > 0 && pattern.charCodeAt(i) != pattern.charCodeAt(j)) {
        j = failure[j - 1];
      }
      if (pattern.charCodeAt(i) == pattern.charCodeAt(j)) {
        j++;
      }
      failure[i] = j;
    }
    
    // Search for pattern
    const matches: i32[] = [];
    j = 0;
    
    for (let i: i32 = 0; i < textLen; i++) {
      while (j > 0 && text.charCodeAt(i) != pattern.charCodeAt(j)) {
        j = failure[j - 1];
      }
      if (text.charCodeAt(i) == pattern.charCodeAt(j)) {
        j++;
      }
      if (j == patternLen) {
        matches.push(i - patternLen + 1);
        j = failure[j - 1];
      }
    }
    
    // Convert to typed array
    const result: Int32Array = new Int32Array(matches.length);
    for (let i: i32 = 0; i < matches.length; i++) {
      result[i] = matches[i];
    }
    
    return result;
  }
}

// Example 4: Mathematical operations for financial calculations
// Paytm, PhonePe के transaction processing के लिए

export class FinancialUtils {
  // Calculate compound interest - investment apps के लिए
  // Zerodha, Groww के SIP calculators में use होता है
  static compoundInterest(
    principal: f64,
    rate: f64,
    time: f64,
    frequency: i32 = 12
  ): f64 {
    const ratePerPeriod: f64 = rate / (100.0 * frequency as f64);
    const totalPeriods: f64 = frequency as f64 * time;
    
    return principal * Math.pow(1.0 + ratePerPeriod, totalPeriods);
  }
  
  // Calculate EMI - loan applications के लिए
  // BankBazaar, PolicyBazaar के EMI calculators में
  static calculateEMI(
    principal: f64,
    annualRate: f64,
    tenureMonths: i32
  ): f64 {
    const monthlyRate: f64 = (annualRate / 100.0) / 12.0;
    const tenure: f64 = tenureMonths as f64;
    
    if (monthlyRate == 0.0) {
      return principal / tenure;
    }
    
    const emi: f64 = (principal * monthlyRate * Math.pow(1.0 + monthlyRate, tenure)) / 
                     (Math.pow(1.0 + monthlyRate, tenure) - 1.0);
    
    return emi;
  }
  
  // Tax calculation for Indian slab system
  // Income tax calculator - ClearTax, TaxGuru के लिए
  static calculateIncomeTax(income: f64, financialYear: i32 = 2024): f64 {
    let tax: f64 = 0.0;
    
    // Income tax slabs for FY 2024-25 (New regime)
    if (income > 300000.0) {
      if (income <= 600000.0) {
        tax += (income - 300000.0) * 0.05; // 5% for 3-6 lakhs
      } else {
        tax += 300000.0 * 0.05; // 5% for 3-6 lakhs
        
        if (income <= 900000.0) {
          tax += (income - 600000.0) * 0.10; // 10% for 6-9 lakhs
        } else {
          tax += 300000.0 * 0.10; // 10% for 6-9 lakhs
          
          if (income <= 1200000.0) {
            tax += (income - 900000.0) * 0.15; // 15% for 9-12 lakhs
          } else {
            tax += 300000.0 * 0.15; // 15% for 9-12 lakhs
            
            if (income <= 1500000.0) {
              tax += (income - 1200000.0) * 0.20; // 20% for 12-15 lakhs
            } else {
              tax += 300000.0 * 0.20; // 20% for 12-15 lakhs
              tax += (income - 1500000.0) * 0.30; // 30% for above 15 lakhs
            }
          }
        }
      }
    }
    
    return tax;
  }
}

// Example 5: Data compression for efficient storage
// WhatsApp, Telegram के message compression के लिए

export class CompressionUtils {
  // Run-length encoding - simple compression
  // Repeated characters को compress करना
  static runLengthEncode(input: string): string {
    if (input.length == 0) {
      return "";
    }
    
    let result: string = "";
    let currentChar: string = input.charAt(0);
    let count: i32 = 1;
    
    for (let i: i32 = 1; i < input.length; i++) {
      const char: string = input.charAt(i);
      
      if (char == currentChar) {
        count++;
      } else {
        result += currentChar;
        if (count > 1) {
          result += count.toString();
        }
        currentChar = char;
        count = 1;
      }
    }
    
    // Add the last character and count
    result += currentChar;
    if (count > 1) {
      result += count.toString();
    }
    
    return result;
  }
  
  // Run-length decode
  static runLengthDecode(input: string): string {
    if (input.length == 0) {
      return "";
    }
    
    let result: string = "";
    let i: i32 = 0;
    
    while (i < input.length) {
      const char: string = input.charAt(i);
      i++;
      
      // Check if next characters are digits
      let count: i32 = 1;
      let numStr: string = "";
      
      while (i < input.length && this.isDigit(input.charAt(i))) {
        numStr += input.charAt(i);
        i++;
      }
      
      if (numStr.length > 0) {
        count = parseInt(numStr);
      }
      
      // Add character count times
      for (let j: i32 = 0; j < count; j++) {
        result += char;
      }
    }
    
    return result;
  }
  
  private static isDigit(char: string): bool {
    const code: i32 = char.charCodeAt(0);
    return code >= 48 && code <= 57; // '0' to '9'
  }
}

// Utility functions for testing and benchmarking
export function allocateArray(size: i32): Float64Array {
  return new Float64Array(size);
}

export function fillArrayWithRandom(arr: Float64Array): void {
  for (let i: i32 = 0; i < arr.length; i++) {
    arr[i] = Math.random() * 100.0;
  }
}

// Memory management utilities
export function getMemorySize(): i32 {
  return memory.size();
}

export function growMemory(pages: i32): i32 {
  return memory.grow(pages);
}