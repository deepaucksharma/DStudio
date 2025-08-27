use wasm_bindgen::prelude::*;
use js_sys::Array;
use web_sys::console;

// Console.log को Rust से use करने के लिए macro
macro_rules! log {
    ( $( $t:tt )* ) => {
        console::log_1(&format!( $( $t )* ).into());
    }
}

// WebAssembly module initialize करते समय panic hook set करें
#[wasm_bindgen(start)]
pub fn main() {
    console_error_panic_hook::set_once();
    log!("🦀 Rust WASM module initialized - Flipkart के लिए high-performance computing ready!");
}

// Example 1: Mathematical Operations - Paytm के लिए transaction processing
#[wasm_bindgen]
pub struct PaymentProcessor {
    transaction_fee_rate: f64,
}

#[wasm_bindgen]
impl PaymentProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new(fee_rate: f64) -> PaymentProcessor {
        log!("💰 PaymentProcessor initialized with fee rate: {}", fee_rate);
        PaymentProcessor {
            transaction_fee_rate: fee_rate,
        }
    }

    // Fast transaction fee calculation - हर second में हजारों transactions
    #[wasm_bindgen]
    pub fn calculate_fee(&self, amount: f64) -> f64 {
        let fee = amount * self.transaction_fee_rate;
        // GST calculation for Indian transactions
        let gst = fee * 0.18;
        fee + gst
    }

    // Bulk transaction processing - Paytm के monthly statements के लिए
    #[wasm_bindgen]
    pub fn process_bulk_transactions(&self, amounts: &[f64]) -> Vec<f64> {
        amounts
            .iter()
            .map(|&amount| self.calculate_fee(amount))
            .collect()
    }

    // Complex mathematical operations - fraud detection algorithms
    #[wasm_bindgen]
    pub fn fraud_risk_score(&self, amount: f64, user_history_count: u32, time_of_day: u8) -> f64 {
        let base_risk = (amount / 10000.0).sqrt(); // Amount risk
        let history_factor = 1.0 / (user_history_count as f64 + 1.0); // New user risk
        let time_factor = if time_of_day >= 22 || time_of_day <= 6 { 1.5 } else { 1.0 }; // Night time risk
        
        (base_risk + history_factor) * time_factor
    }
}

// Example 2: String Processing - Flipkart के product search के लिए
#[wasm_bindgen]
pub struct SearchEngine {
    keywords: Vec<String>,
}

#[wasm_bindgen]
impl SearchEngine {
    #[wasm_bindgen(constructor)]
    pub fn new() -> SearchEngine {
        SearchEngine {
            keywords: Vec::new(),
        }
    }

    // Levenshtein distance for fuzzy search - गलत spelling भी handle करे
    #[wasm_bindgen]
    pub fn levenshtein_distance(&self, s1: &str, s2: &str) -> usize {
        let len1 = s1.chars().count();
        let len2 = s2.chars().count();
        let mut matrix = vec![vec![0; len2 + 1]; len1 + 1];

        // Initialize first row and column
        for i in 0..=len1 {
            matrix[i][0] = i;
        }
        for j in 0..=len2 {
            matrix[0][j] = j;
        }

        let s1_chars: Vec<char> = s1.chars().collect();
        let s2_chars: Vec<char> = s2.chars().collect();

        for i in 1..=len1 {
            for j in 1..=len2 {
                let cost = if s1_chars[i - 1] == s2_chars[j - 1] { 0 } else { 1 };
                matrix[i][j] = std::cmp::min(
                    std::cmp::min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1),
                    matrix[i - 1][j - 1] + cost,
                );
            }
        }

        matrix[len1][len2]
    }

    // Product search with fuzzy matching - "mobile" search करने पर "mobail" भी मिले
    #[wasm_bindgen]
    pub fn search_products(&self, query: &str, products: &Array) -> Array {
        let results = Array::new();
        let threshold = 2; // Maximum distance allowed

        for i in 0..products.length() {
            if let Some(product) = products.get(i).as_string() {
                let distance = self.levenshtein_distance(query, &product.to_lowercase());
                if distance <= threshold {
                    results.push(&JsValue::from(product));
                }
            }
        }

        results
    }
}

// Example 3: Image Processing - Zomato के food images के लिए
#[wasm_bindgen]
pub struct ImageProcessor;

#[wasm_bindgen]
impl ImageProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new() -> ImageProcessor {
        log!("📸 ImageProcessor initialized for Zomato food image optimization");
        ImageProcessor
    }

    // Gaussian blur for image optimization - slow internet पर fast loading के लिए
    #[wasm_bindgen]
    pub fn gaussian_blur(&self, image_data: &[u8], width: u32, height: u32, sigma: f32) -> Vec<u8> {
        let kernel_size = (6.0 * sigma).ceil() as usize;
        let kernel = self.gaussian_kernel(kernel_size, sigma);
        
        let mut result = vec![0u8; image_data.len()];
        
        // Apply horizontal blur
        for y in 0..height as usize {
            for x in 0..width as usize {
                for c in 0..4 { // RGBA channels
                    let mut sum = 0.0;
                    let mut weight_sum = 0.0;
                    
                    for k in 0..kernel_size {
                        let offset = k as i32 - kernel_size as i32 / 2;
                        let nx = (x as i32 + offset) as usize;
                        
                        if nx < width as usize {
                            let idx = (y * width as usize + nx) * 4 + c;
                            sum += image_data[idx] as f32 * kernel[k];
                            weight_sum += kernel[k];
                        }
                    }
                    
                    let result_idx = (y * width as usize + x) * 4 + c;
                    result[result_idx] = (sum / weight_sum) as u8;
                }
            }
        }
        
        result
    }

    // Generate Gaussian kernel
    fn gaussian_kernel(&self, size: usize, sigma: f32) -> Vec<f32> {
        let mut kernel = vec![0.0; size];
        let center = size / 2;
        let two_sigma_squared = 2.0 * sigma * sigma;
        
        for i in 0..size {
            let x = i as i32 - center as i32;
            kernel[i] = (-((x * x) as f32) / two_sigma_squared).exp();
        }
        
        // Normalize kernel
        let sum: f32 = kernel.iter().sum();
        for k in &mut kernel {
            *k /= sum;
        }
        
        kernel
    }

    // Color space conversion - Instagram-style filters के लिए
    #[wasm_bindgen]
    pub fn rgb_to_hsv(&self, r: u8, g: u8, b: u8) -> Vec<f32> {
        let r = r as f32 / 255.0;
        let g = g as f32 / 255.0;
        let b = b as f32 / 255.0;
        
        let max_val = r.max(g).max(b);
        let min_val = r.min(g).min(b);
        let delta = max_val - min_val;
        
        // Calculate hue
        let hue = if delta == 0.0 {
            0.0
        } else if max_val == r {
            60.0 * (((g - b) / delta) % 6.0)
        } else if max_val == g {
            60.0 * ((b - r) / delta + 2.0)
        } else {
            60.0 * ((r - g) / delta + 4.0)
        };
        
        // Calculate saturation
        let saturation = if max_val == 0.0 { 0.0 } else { delta / max_val };
        
        // Calculate value
        let value = max_val;
        
        vec![hue, saturation, value]
    }
}

// Example 4: Cryptographic Functions - IRCTC के secure booking के लिए
#[wasm_bindgen]
pub struct CryptoUtils;

#[wasm_bindgen]
impl CryptoUtils {
    #[wasm_bindgen(constructor)]
    pub fn new() -> CryptoUtils {
        log!("🔐 CryptoUtils initialized for IRCTC secure transactions");
        CryptoUtils
    }

    // Simple hash function - ticket booking verification के लिए
    #[wasm_bindgen]
    pub fn djb2_hash(&self, data: &str) -> u32 {
        let mut hash: u32 = 5381;
        for byte in data.bytes() {
            hash = hash.wrapping_mul(33).wrapping_add(byte as u32);
        }
        hash
    }

    // Generate secure random ticket ID
    #[wasm_bindgen]
    pub fn generate_ticket_id(&self, prefix: &str, user_id: u32) -> String {
        let timestamp = js_sys::Date::now() as u64;
        let hash = self.djb2_hash(&format!("{}{}{}", prefix, user_id, timestamp));
        format!("{}-{:08X}", prefix, hash)
    }

    // XOR cipher for simple data obfuscation
    #[wasm_bindgen]
    pub fn xor_cipher(&self, data: &[u8], key: u8) -> Vec<u8> {
        data.iter().map(|&b| b ^ key).collect()
    }
}

// Example 5: Performance Benchmarking - WASM vs JavaScript performance comparison
#[wasm_bindgen]
pub struct PerformanceBenchmark;

#[wasm_bindgen]
impl PerformanceBenchmark {
    #[wasm_bindgen(constructor)]
    pub fn new() -> PerformanceBenchmark {
        PerformanceBenchmark
    }

    // Matrix multiplication - scientific computing के लिए
    #[wasm_bindgen]
    pub fn matrix_multiply(&self, a: &[f64], b: &[f64], size: usize) -> Vec<f64> {
        let mut result = vec![0.0; size * size];
        
        for i in 0..size {
            for j in 0..size {
                let mut sum = 0.0;
                for k in 0..size {
                    sum += a[i * size + k] * b[k * size + j];
                }
                result[i * size + j] = sum;
            }
        }
        
        result
    }

    // Prime number calculation - computational intensive task
    #[wasm_bindgen]
    pub fn count_primes_up_to(&self, limit: u32) -> u32 {
        if limit < 2 {
            return 0;
        }
        
        let mut is_prime = vec![true; (limit + 1) as usize];
        is_prime[0] = false;
        is_prime[1] = false;
        
        let sqrt_limit = (limit as f64).sqrt() as u32;
        for i in 2..=sqrt_limit {
            if is_prime[i as usize] {
                let mut j = i * i;
                while j <= limit {
                    is_prime[j as usize] = false;
                    j += i;
                }
            }
        }
        
        is_prime.iter().filter(|&&x| x).count() as u32
    }

    // Fibonacci sequence - recursive algorithm benchmark
    #[wasm_bindgen]
    pub fn fibonacci(&self, n: u32) -> u64 {
        if n <= 1 {
            return n as u64;
        }
        
        let mut a = 0u64;
        let mut b = 1u64;
        
        for _ in 2..=n {
            let temp = a + b;
            a = b;
            b = temp;
        }
        
        b
    }
}