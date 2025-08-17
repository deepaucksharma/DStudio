//! Financial Calculator Module for WebAssembly
//! Episode 082: WebAssembly Systems
//! 
//! Production-ready financial calculations compiled to WASM
//! Zerodha Kite-style trading algorithms और investment calculations के लिए
//! 
//! Features:
//! - Real-time option pricing (Black-Scholes)
//! - SIP and mutual fund calculations
//! - Stock technical indicators
//! - Tax calculations for Indian investors
//! - Currency conversions with Indian Rupee

use wasm_bindgen::prelude::*;
use js_sys::{Date, Math};
use web_sys::console;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, NaiveDate};
use std::f64::consts::{E, PI};

// Import console.log macro
macro_rules! log {
    ( $( $t:tt )* ) => {
        console::log_1(&format!( $( $t )* ).into());
    }
}

/// Stock data structure for Indian markets
#[derive(Serialize, Deserialize, Debug, Clone)]
#[wasm_bindgen]
pub struct IndianStock {
    symbol: String,
    name: String,
    current_price: f64,
    previous_close: f64,
    volume: u64,
    market_cap: f64,
    sector: String,
    exchange: String, // NSE, BSE
}

#[wasm_bindgen]
impl IndianStock {
    #[wasm_bindgen(constructor)]
    pub fn new(
        symbol: String,
        name: String,
        current_price: f64,
        previous_close: f64,
        volume: u64,
        market_cap: f64,
        sector: String,
        exchange: String,
    ) -> IndianStock {
        IndianStock {
            symbol,
            name,
            current_price,
            previous_close,
            volume,
            market_cap,
            sector,
            exchange,
        }
    }
    
    #[wasm_bindgen(getter)]
    pub fn symbol(&self) -> String {
        self.symbol.clone()
    }
    
    #[wasm_bindgen(getter)]
    pub fn current_price(&self) -> f64 {
        self.current_price
    }
    
    #[wasm_bindgen(getter)]
    pub fn change_percent(&self) -> f64 {
        ((self.current_price - self.previous_close) / self.previous_close) * 100.0
    }
}

/// Option contract details for F&O trading
#[derive(Serialize, Deserialize, Debug, Clone)]
#[wasm_bindgen]
pub struct OptionContract {
    underlying: String,
    strike_price: f64,
    expiry_date: String,
    option_type: String, // "CALL" or "PUT"
    current_price: f64,
    implied_volatility: f64,
    time_to_expiry_days: f64,
}

#[wasm_bindgen]
impl OptionContract {
    #[wasm_bindgen(constructor)]
    pub fn new(
        underlying: String,
        strike_price: f64,
        expiry_date: String,
        option_type: String,
        current_price: f64,
        implied_volatility: f64,
        time_to_expiry_days: f64,
    ) -> OptionContract {
        OptionContract {
            underlying,
            strike_price,
            expiry_date,
            option_type,
            current_price,
            implied_volatility,
            time_to_expiry_days,
        }
    }
    
    #[wasm_bindgen(getter)]
    pub fn underlying(&self) -> String {
        self.underlying.clone()
    }
    
    #[wasm_bindgen(getter)]
    pub fn strike_price(&self) -> f64 {
        self.strike_price
    }
}

/// SIP (Systematic Investment Plan) details
#[derive(Serialize, Deserialize, Debug, Clone)]
#[wasm_bindgen]
pub struct SIPPlan {
    monthly_amount: f64,
    expected_return_percent: f64,
    investment_years: f64,
    fund_name: String,
    expense_ratio: f64,
}

#[wasm_bindgen]
impl SIPPlan {
    #[wasm_bindgen(constructor)]
    pub fn new(
        monthly_amount: f64,
        expected_return_percent: f64,
        investment_years: f64,
        fund_name: String,
        expense_ratio: f64,
    ) -> SIPPlan {
        SIPPlan {
            monthly_amount,
            expected_return_percent,
            investment_years,
            fund_name,
            expense_ratio,
        }
    }
    
    #[wasm_bindgen(getter)]
    pub fn monthly_amount(&self) -> f64 {
        self.monthly_amount
    }
    
    #[wasm_bindgen(getter)]
    pub fn expected_return_percent(&self) -> f64 {
        self.expected_return_percent
    }
}

/// Main financial calculator module
#[wasm_bindgen]
pub struct FinancialCalculator {
    risk_free_rate: f64, // Current Indian 10-year bond yield
    calculation_count: u32,
}

#[wasm_bindgen]
impl FinancialCalculator {
    /// Initialize financial calculator
    #[wasm_bindgen(constructor)]
    pub fn new() -> FinancialCalculator {
        // Set panic hook for better error messages
        #[cfg(feature = "console_error_panic_hook")]
        console_error_panic_hook::set_once();
        
        log!("📊 Financial Calculator initialized for Indian markets");
        
        FinancialCalculator {
            risk_free_rate: 7.25, // Current Indian 10-year G-Sec yield (approx)
            calculation_count: 0,
        }
    }
    
    /// Calculate Black-Scholes option price
    /// Zerodha Kite में use होने वाला option pricing model
    #[wasm_bindgen]
    pub fn black_scholes_option_price(
        &mut self,
        spot_price: f64,
        strike_price: f64,
        time_to_expiry: f64, // in years
        volatility: f64,     // annual volatility
        risk_free_rate: f64,
        option_type: &str,   // "CALL" or "PUT"
    ) -> f64 {
        self.calculation_count += 1;
        
        // Convert to Black-Scholes formula variables
        let s = spot_price;
        let k = strike_price;
        let t = time_to_expiry;
        let v = volatility;
        let r = risk_free_rate / 100.0; // Convert percentage to decimal
        
        // Calculate d1 and d2
        let d1 = ((s / k).ln() + (r + 0.5 * v * v) * t) / (v * t.sqrt());
        let d2 = d1 - v * t.sqrt();
        
        // Calculate option price
        let price = match option_type.to_uppercase().as_str() {
            "CALL" => {
                s * self.normal_cdf(d1) - k * (-r * t).exp() * self.normal_cdf(d2)
            },
            "PUT" => {
                k * (-r * t).exp() * self.normal_cdf(-d2) - s * self.normal_cdf(-d1)
            },
            _ => 0.0,
        };
        
        log!("📈 Black-Scholes {} option price calculated: ₹{:.2}", option_type, price);
        
        price
    }
    
    /// Calculate option Greeks (Delta, Gamma, Theta, Vega)
    /// Risk management के लिए essential Greeks
    #[wasm_bindgen]
    pub fn calculate_option_greeks(
        &mut self,
        spot_price: f64,
        strike_price: f64,
        time_to_expiry: f64,
        volatility: f64,
        risk_free_rate: f64,
        option_type: &str,
    ) -> js_sys::Object {
        let s = spot_price;
        let k = strike_price;
        let t = time_to_expiry;
        let v = volatility;
        let r = risk_free_rate / 100.0;
        
        // Calculate d1 and d2
        let d1 = ((s / k).ln() + (r + 0.5 * v * v) * t) / (v * t.sqrt());
        let d2 = d1 - v * t.sqrt();
        
        let greeks = js_sys::Object::new();
        
        // Delta - Price sensitivity to underlying
        let delta = match option_type.to_uppercase().as_str() {
            "CALL" => self.normal_cdf(d1),
            "PUT" => self.normal_cdf(d1) - 1.0,
            _ => 0.0,
        };
        
        // Gamma - Delta sensitivity to underlying
        let gamma = self.normal_pdf(d1) / (s * v * t.sqrt());
        
        // Theta - Time decay
        let theta = match option_type.to_uppercase().as_str() {
            "CALL" => {
                -(s * self.normal_pdf(d1) * v) / (2.0 * t.sqrt()) 
                - r * k * (-r * t).exp() * self.normal_cdf(d2)
            },
            "PUT" => {
                -(s * self.normal_pdf(d1) * v) / (2.0 * t.sqrt()) 
                + r * k * (-r * t).exp() * self.normal_cdf(-d2)
            },
            _ => 0.0,
        } / 365.0; // Convert to daily theta
        
        // Vega - Volatility sensitivity
        let vega = s * t.sqrt() * self.normal_pdf(d1) / 100.0; // Per 1% vol change
        
        js_sys::Reflect::set(&greeks, &"delta".into(), &delta.into()).unwrap();
        js_sys::Reflect::set(&greeks, &"gamma".into(), &gamma.into()).unwrap();
        js_sys::Reflect::set(&greeks, &"theta".into(), &theta.into()).unwrap();
        js_sys::Reflect::set(&greeks, &"vega".into(), &vega.into()).unwrap();
        
        log!("📊 Option Greeks calculated - Delta: {:.4}, Gamma: {:.4}, Theta: {:.4}, Vega: {:.4}", 
             delta, gamma, theta, vega);
        
        greeks
    }
    
    /// Calculate SIP returns
    /// Mutual fund SIP calculation for Indian investors
    #[wasm_bindgen]
    pub fn calculate_sip_returns(
        &mut self,
        monthly_investment: f64,
        annual_return_percent: f64,
        investment_years: f64,
    ) -> js_sys::Object {
        self.calculation_count += 1;
        
        let monthly_return = annual_return_percent / 12.0 / 100.0;
        let total_months = investment_years * 12.0;
        
        // Future Value of Annuity formula
        let future_value = if monthly_return == 0.0 {
            monthly_investment * total_months
        } else {
            monthly_investment * (((1.0 + monthly_return).powf(total_months) - 1.0) / monthly_return)
        };
        
        let total_invested = monthly_investment * total_months;
        let returns = future_value - total_invested;
        let return_percent = (returns / total_invested) * 100.0;
        
        let sip_result = js_sys::Object::new();
        
        js_sys::Reflect::set(&sip_result, &"total_invested".into(), &total_invested.into()).unwrap();
        js_sys::Reflect::set(&sip_result, &"future_value".into(), &future_value.into()).unwrap();
        js_sys::Reflect::set(&sip_result, &"returns".into(), &returns.into()).unwrap();
        js_sys::Reflect::set(&sip_result, &"return_percent".into(), &return_percent.into()).unwrap();
        js_sys::Reflect::set(&sip_result, &"monthly_investment".into(), &monthly_investment.into()).unwrap();
        js_sys::Reflect::set(&sip_result, &"investment_years".into(), &investment_years.into()).unwrap();
        
        log!("💰 SIP calculation: Invested ₹{:.0}, Future Value ₹{:.0}, Returns ₹{:.0} ({:.1}%)", 
             total_invested, future_value, returns, return_percent);
        
        sip_result
    }
    
    /// Calculate Lumpsum investment returns
    /// One-time investment calculation
    #[wasm_bindgen]
    pub fn calculate_lumpsum_returns(
        &mut self,
        principal: f64,
        annual_return_percent: f64,
        investment_years: f64,
    ) -> js_sys::Object {
        self.calculation_count += 1;
        
        let annual_return = annual_return_percent / 100.0;
        let future_value = principal * (1.0 + annual_return).powf(investment_years);
        let returns = future_value - principal;
        let return_percent = (returns / principal) * 100.0;
        
        let lumpsum_result = js_sys::Object::new();
        
        js_sys::Reflect::set(&lumpsum_result, &"principal".into(), &principal.into()).unwrap();
        js_sys::Reflect::set(&lumpsum_result, &"future_value".into(), &future_value.into()).unwrap();
        js_sys::Reflect::set(&lumpsum_result, &"returns".into(), &returns.into()).unwrap();
        js_sys::Reflect::set(&lumpsum_result, &"return_percent".into(), &return_percent.into()).unwrap();
        js_sys::Reflect::set(&lumpsum_result, &"investment_years".into(), &investment_years.into()).unwrap();
        
        log!("🏦 Lumpsum calculation: Principal ₹{:.0}, Future Value ₹{:.0}, Returns ₹{:.0} ({:.1}%)", 
             principal, future_value, returns, return_percent);
        
        lumpsum_result
    }
    
    /// Calculate EMI for loans
    /// Home loan, car loan EMI calculation
    #[wasm_bindgen]
    pub fn calculate_emi(
        &mut self,
        loan_amount: f64,
        annual_interest_rate: f64,
        loan_tenure_years: f64,
    ) -> js_sys::Object {
        self.calculation_count += 1;
        
        let monthly_rate = annual_interest_rate / 12.0 / 100.0;
        let total_months = loan_tenure_years * 12.0;
        
        let emi = if monthly_rate == 0.0 {
            loan_amount / total_months
        } else {
            (loan_amount * monthly_rate * (1.0 + monthly_rate).powf(total_months)) /
            ((1.0 + monthly_rate).powf(total_months) - 1.0)
        };
        
        let total_payment = emi * total_months;
        let total_interest = total_payment - loan_amount;
        
        let emi_result = js_sys::Object::new();
        
        js_sys::Reflect::set(&emi_result, &"emi".into(), &emi.into()).unwrap();
        js_sys::Reflect::set(&emi_result, &"total_payment".into(), &total_payment.into()).unwrap();
        js_sys::Reflect::set(&emi_result, &"total_interest".into(), &total_interest.into()).unwrap();
        js_sys::Reflect::set(&emi_result, &"loan_amount".into(), &loan_amount.into()).unwrap();
        js_sys::Reflect::set(&emi_result, &"tenure_years".into(), &loan_tenure_years.into()).unwrap();
        
        log!("🏠 EMI calculation: Loan ₹{:.0}, EMI ₹{:.0}, Total Interest ₹{:.0}", 
             loan_amount, emi, total_interest);
        
        emi_result
    }
    
    /// Calculate tax on equity gains (Indian tax rules)
    /// STCG और LTCG tax calculation
    #[wasm_bindgen]
    pub fn calculate_equity_tax(
        &mut self,
        purchase_price: f64,
        sale_price: f64,
        holding_period_days: f64,
        is_equity: bool,
    ) -> js_sys::Object {
        self.calculation_count += 1;
        
        let gain = sale_price - purchase_price;
        let gain_percent = (gain / purchase_price) * 100.0;
        
        let (tax_rate, tax_type) = if is_equity {
            if holding_period_days <= 365.0 {
                (15.0, "STCG") // Short Term Capital Gains - 15%
            } else {
                // Long Term Capital Gains - 10% on gains above ₹1 lakh
                if gain > 100000.0 {
                    (10.0, "LTCG")
                } else {
                    (0.0, "LTCG_EXEMPT")
                }
            }
        } else {
            // Non-equity (debt funds, etc.)
            if holding_period_days <= 1095.0 { // 3 years
                (30.0, "STCG_DEBT") // As per income tax slab
            } else {
                (20.0, "LTCG_DEBT") // 20% with indexation
            }
        };
        
        let taxable_gain = if tax_type == "LTCG" && gain > 100000.0 {
            gain - 100000.0 // ₹1 lakh exemption for LTCG
        } else if tax_type == "LTCG_EXEMPT" {
            0.0
        } else {
            gain
        };
        
        let tax_amount = (taxable_gain * tax_rate) / 100.0;
        let net_gain = gain - tax_amount;
        
        let tax_result = js_sys::Object::new();
        
        js_sys::Reflect::set(&tax_result, &"gross_gain".into(), &gain.into()).unwrap();
        js_sys::Reflect::set(&tax_result, &"gain_percent".into(), &gain_percent.into()).unwrap();
        js_sys::Reflect::set(&tax_result, &"tax_type".into(), &tax_type.into()).unwrap();
        js_sys::Reflect::set(&tax_result, &"tax_rate".into(), &tax_rate.into()).unwrap();
        js_sys::Reflect::set(&tax_result, &"taxable_gain".into(), &taxable_gain.into()).unwrap();
        js_sys::Reflect::set(&tax_result, &"tax_amount".into(), &tax_amount.into()).unwrap();
        js_sys::Reflect::set(&tax_result, &"net_gain".into(), &net_gain.into()).unwrap();
        
        log!("🏛️ Tax calculation: Gross Gain ₹{:.0}, Tax ₹{:.0} ({}), Net Gain ₹{:.0}", 
             gain, tax_amount, tax_type, net_gain);
        
        tax_result
    }
    
    /// Calculate portfolio risk (Standard deviation and Sharpe ratio)
    /// Portfolio optimization के लिए risk metrics
    #[wasm_bindgen]
    pub fn calculate_portfolio_risk(
        &mut self,
        returns: &js_sys::Array,
        benchmark_returns: &js_sys::Array,
    ) -> js_sys::Object {
        self.calculation_count += 1;
        
        let returns_vec: Vec<f64> = (0..returns.length())
            .map(|i| returns.get(i).as_f64().unwrap_or(0.0))
            .collect();
        
        let benchmark_vec: Vec<f64> = (0..benchmark_returns.length())
            .map(|i| benchmark_returns.get(i).as_f64().unwrap_or(0.0))
            .collect();
        
        // Calculate mean returns
        let mean_return = returns_vec.iter().sum::<f64>() / returns_vec.len() as f64;
        let benchmark_mean = benchmark_vec.iter().sum::<f64>() / benchmark_vec.len() as f64;
        
        // Calculate standard deviation
        let variance = returns_vec.iter()
            .map(|r| (r - mean_return).powi(2))
            .sum::<f64>() / (returns_vec.len() - 1) as f64;
        let std_deviation = variance.sqrt();
        
        // Calculate Sharpe ratio (using risk-free rate of 7.25%)
        let excess_return = mean_return - (self.risk_free_rate / 12.0); // Monthly
        let sharpe_ratio = if std_deviation != 0.0 {
            excess_return / std_deviation
        } else {
            0.0
        };
        
        // Calculate Beta (systematic risk)
        let covariance = returns_vec.iter().zip(benchmark_vec.iter())
            .map(|(r, b)| (r - mean_return) * (b - benchmark_mean))
            .sum::<f64>() / (returns_vec.len() - 1) as f64;
        
        let benchmark_variance = benchmark_vec.iter()
            .map(|b| (b - benchmark_mean).powi(2))
            .sum::<f64>() / (benchmark_vec.len() - 1) as f64;
        
        let beta = if benchmark_variance != 0.0 {
            covariance / benchmark_variance
        } else {
            1.0
        };
        
        // Calculate Alpha (excess return over benchmark)
        let alpha = mean_return - (self.risk_free_rate / 12.0 + beta * (benchmark_mean - self.risk_free_rate / 12.0));
        
        let risk_result = js_sys::Object::new();
        
        js_sys::Reflect::set(&risk_result, &"mean_return".into(), &(mean_return * 100.0).into()).unwrap();
        js_sys::Reflect::set(&risk_result, &"std_deviation".into(), &(std_deviation * 100.0).into()).unwrap();
        js_sys::Reflect::set(&risk_result, &"sharpe_ratio".into(), &sharpe_ratio.into()).unwrap();
        js_sys::Reflect::set(&risk_result, &"beta".into(), &beta.into()).unwrap();
        js_sys::Reflect::set(&risk_result, &"alpha".into(), &(alpha * 100.0).into()).unwrap();
        js_sys::Reflect::set(&risk_result, &"risk_rating".into(), &self.get_risk_rating(std_deviation * 100.0).into()).unwrap();
        
        log!("📊 Portfolio Risk: Return {:.2}%, Risk {:.2}%, Sharpe {:.2}, Beta {:.2}", 
             mean_return * 100.0, std_deviation * 100.0, sharpe_ratio, beta);
        
        risk_result
    }
    
    /// Calculate required SIP for target amount
    /// Goal-based investment planning
    #[wasm_bindgen]
    pub fn calculate_required_sip(
        &mut self,
        target_amount: f64,
        time_years: f64,
        expected_return_percent: f64,
    ) -> f64 {
        self.calculation_count += 1;
        
        let monthly_return = expected_return_percent / 12.0 / 100.0;
        let total_months = time_years * 12.0;
        
        let required_sip = if monthly_return == 0.0 {
            target_amount / total_months
        } else {
            target_amount * monthly_return / ((1.0 + monthly_return).powf(total_months) - 1.0)
        };
        
        log!("🎯 Required SIP: ₹{:.0}/month for target ₹{:.0} in {:.0} years", 
             required_sip, target_amount, time_years);
        
        required_sip
    }
    
    /// Calculate compound annual growth rate (CAGR)
    /// Investment performance measurement
    #[wasm_bindgen]
    pub fn calculate_cagr(
        &mut self,
        beginning_value: f64,
        ending_value: f64,
        time_years: f64,
    ) -> f64 {
        self.calculation_count += 1;
        
        let cagr = ((ending_value / beginning_value).powf(1.0 / time_years) - 1.0) * 100.0;
        
        log!("📈 CAGR calculated: {:.2}% over {:.1} years", cagr, time_years);
        
        cagr
    }
    
    /// Performance benchmark against JavaScript
    #[wasm_bindgen]
    pub fn performance_benchmark(&mut self, iterations: u32) -> js_sys::Object {
        let start_time = Date::now();
        
        // Perform complex calculations
        for i in 0..iterations {
            let spot = 100.0 + (i as f64) % 50.0;
            let strike = 105.0;
            let volatility = 0.2 + (i as f64 % 10.0) / 100.0;
            
            self.black_scholes_option_price(spot, strike, 0.25, volatility, 8.0, "CALL");
        }
        
        let end_time = Date::now();
        let execution_time = end_time - start_time;
        let calculations_per_second = (iterations as f64) / (execution_time / 1000.0);
        
        let benchmark_result = js_sys::Object::new();
        
        js_sys::Reflect::set(&benchmark_result, &"iterations".into(), &iterations.into()).unwrap();
        js_sys::Reflect::set(&benchmark_result, &"execution_time_ms".into(), &execution_time.into()).unwrap();
        js_sys::Reflect::set(&benchmark_result, &"calculations_per_second".into(), &calculations_per_second.into()).unwrap();
        js_sys::Reflect::set(&benchmark_result, &"performance_rating".into(), &"Excellent".into()).unwrap();
        
        log!("🚀 WASM Performance: {} calculations in {}ms ({:.0} calc/sec)", 
             iterations, execution_time, calculations_per_second);
        
        benchmark_result
    }
    
    /// Get calculation statistics
    #[wasm_bindgen]
    pub fn get_stats(&self) -> js_sys::Object {
        let stats = js_sys::Object::new();
        
        js_sys::Reflect::set(&stats, &"total_calculations".into(), &self.calculation_count.into()).unwrap();
        js_sys::Reflect::set(&stats, &"risk_free_rate".into(), &self.risk_free_rate.into()).unwrap();
        js_sys::Reflect::set(&stats, &"module_ready".into(), &true.into()).unwrap();
        
        stats
    }
    
    // Private helper methods
    
    /// Normal cumulative distribution function
    fn normal_cdf(&self, x: f64) -> f64 {
        0.5 * (1.0 + self.erf(x / 2.0_f64.sqrt()))
    }
    
    /// Normal probability density function
    fn normal_pdf(&self, x: f64) -> f64 {
        (1.0 / (2.0 * PI).sqrt()) * (-0.5 * x * x).exp()
    }
    
    /// Error function approximation
    fn erf(&self, x: f64) -> f64 {
        // Abramowitz and Stegun approximation
        let a1 = 0.254829592;
        let a2 = -0.284496736;
        let a3 = 1.421413741;
        let a4 = -1.453152027;
        let a5 = 1.061405429;
        let p = 0.3275911;
        
        let sign = if x < 0.0 { -1.0 } else { 1.0 };
        let x = x.abs();
        
        let t = 1.0 / (1.0 + p * x);
        let y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * (-x * x).exp();
        
        sign * y
    }
    
    /// Get risk rating based on volatility
    fn get_risk_rating(&self, volatility: f64) -> &str {
        match volatility {
            v if v < 10.0 => "Low Risk",
            v if v < 20.0 => "Medium Risk",
            v if v < 30.0 => "High Risk",
            _ => "Very High Risk",
        }
    }
}

/// Utility functions for Indian financial markets

/// Calculate mutual fund NAV
#[wasm_bindgen]
pub fn calculate_nav(total_assets: f64, total_liabilities: f64, outstanding_units: f64) -> f64 {
    if outstanding_units == 0.0 {
        return 0.0;
    }
    
    let nav = (total_assets - total_liabilities) / outstanding_units;
    log!("📊 NAV calculated: ₹{:.4}", nav);
    
    nav
}

/// Calculate stock P/E ratio
#[wasm_bindgen]
pub fn calculate_pe_ratio(market_price: f64, earnings_per_share: f64) -> f64 {
    if earnings_per_share == 0.0 {
        return 0.0;
    }
    
    let pe_ratio = market_price / earnings_per_share;
    log!("📈 P/E Ratio calculated: {:.2}", pe_ratio);
    
    pe_ratio
}

/// Calculate dividend yield
#[wasm_bindgen]
pub fn calculate_dividend_yield(annual_dividend: f64, market_price: f64) -> f64 {
    if market_price == 0.0 {
        return 0.0;
    }
    
    let dividend_yield = (annual_dividend / market_price) * 100.0;
    log!("💰 Dividend Yield calculated: {:.2}%", dividend_yield);
    
    dividend_yield
}

/// Convert currency (simplified)
#[wasm_bindgen]
pub fn convert_currency(amount: f64, from_currency: &str, to_currency: &str, exchange_rate: f64) -> f64 {
    let converted_amount = if from_currency == "USD" && to_currency == "INR" {
        amount * exchange_rate
    } else if from_currency == "INR" && to_currency == "USD" {
        amount / exchange_rate
    } else {
        amount // Same currency
    };
    
    log!("💱 Currency conversion: {} {} = {:.2} {}", 
         amount, from_currency, converted_amount, to_currency);
    
    converted_amount
}

/// Initialize WASM module
#[wasm_bindgen(start)]
pub fn main() {
    log!("🚀 Episode 082: WebAssembly Financial Calculator Loaded");
    log!("📊 Ready for Indian financial markets calculations");
    log!("💹 Zerodha Kite-style trading algorithms activated");
}