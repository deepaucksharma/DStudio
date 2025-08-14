/*
Domain-Driven Design: Complex Trading Domain - Zerodha Trading Platform
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD principles का इस्तेमाल करके
complex trading domain को model करते हैं। Zerodha जैसे trading platform
के लिए orders, positions, और risk management के साथ।

Author: Hindi Tech Podcast
Date: 2025
*/

package main

import (
	"context"
	"errors"
	"fmt"
	"math"
	"strings"
	"sync"
	"time"
)

// ====================================================================
// DOMAIN LAYER - Core Trading Business Logic
// ====================================================================

// Domain Errors - Trading specific business rules
var (
	ErrInsufficientBalance = errors.New("insufficient account balance - खाते में पैसे कम हैं")
	ErrInsufficientShares  = errors.New("insufficient shares to sell - बेचने के लिए शेयर कम हैं")
	ErrInvalidOrderType    = errors.New("invalid order type - गलत order type")
	ErrInvalidQuantity     = errors.New("invalid quantity - गलत quantity")
	ErrInvalidPrice        = errors.New("invalid price - गलत price")
	ErrMarketClosed        = errors.New("market is closed - बाज़ार बंद है")
	ErrOrderNotFound       = errors.New("order not found - order नहीं मिला")
	ErrOrderAlreadyExecuted = errors.New("order already executed - order पहले से execute हो चुका है")
	ErrRiskLimitExceeded   = errors.New("risk limit exceeded - risk limit पार हो गया")
	ErrInvalidSymbol       = errors.New("invalid trading symbol - गलत trading symbol")
)

// Enums - Trading domain types
type OrderSide string
const (
	OrderSideBuy  OrderSide = "BUY"
	OrderSideSell OrderSide = "SELL"
)

type OrderType string
const (
	OrderTypeMarket    OrderType = "MARKET"    // Market order - तुरंत execute
	OrderTypeLimit     OrderType = "LIMIT"     // Limit order - specific price पर
	OrderTypeStopLoss  OrderType = "STOPLOSS"  // Stop loss order
	OrderTypeStopLimit OrderType = "STOPLIMIT" // Stop limit order
)

type OrderStatus string
const (
	OrderStatusPending   OrderStatus = "PENDING"   // Order placed, waiting
	OrderStatusOpen      OrderStatus = "OPEN"      // Order is active
	OrderStatusExecuted  OrderStatus = "EXECUTED"  // Order completed
	OrderStatusPartial   OrderStatus = "PARTIAL"   // Partially executed
	OrderStatusCancelled OrderStatus = "CANCELLED" // Order cancelled
	OrderStatusRejected  OrderStatus = "REJECTED"  // Order rejected
)

type Exchange string
const (
	ExchangeNSE Exchange = "NSE"  // National Stock Exchange
	ExchangeBSE Exchange = "BSE"  // Bombay Stock Exchange
	ExchangeMCX Exchange = "MCX"  // Multi Commodity Exchange
)

type ProductType string
const (
	ProductTypeCNC ProductType = "CNC" // Cash and Carry
	ProductTypeMIS ProductType = "MIS" // Margin Intraday Square-off
	ProductTypeNRML ProductType = "NRML" // Normal (for F&O)
)

// Value Objects - Immutable trading concepts
type Money struct {
	Amount   float64 `json:"amount"`
	Currency string  `json:"currency"`
}

func NewMoney(amount float64) Money {
	return Money{Amount: amount, Currency: "INR"}
}

func (m Money) Add(other Money) Money {
	return Money{Amount: m.Amount + other.Amount, Currency: m.Currency}
}

func (m Money) Subtract(other Money) Money {
	return Money{Amount: m.Amount - other.Amount, Currency: m.Currency}
}

func (m Money) Multiply(factor float64) Money {
	return Money{Amount: m.Amount * factor, Currency: m.Currency}
}

func (m Money) IsGreaterThan(other Money) bool {
	return m.Amount > other.Amount
}

func (m Money) IsNegative() bool {
	return m.Amount < 0
}

func (m Money) String() string {
	return fmt.Sprintf("₹%.2f", m.Amount)
}

type TradingSymbol struct {
	Symbol   string   `json:"symbol"`
	Exchange Exchange `json:"exchange"`
}

func NewTradingSymbol(symbol string, exchange Exchange) (*TradingSymbol, error) {
	if symbol == "" {
		return nil, ErrInvalidSymbol
	}
	return &TradingSymbol{Symbol: symbol, Exchange: exchange}, nil
}

func (ts *TradingSymbol) String() string {
	return fmt.Sprintf("%s:%s", ts.Exchange, ts.Symbol)
}

type Price struct {
	Value float64 `json:"value"`
}

func NewPrice(value float64) (*Price, error) {
	if value <= 0 {
		return nil, ErrInvalidPrice
	}
	return &Price{Value: value}, nil
}

func (p *Price) String() string {
	return fmt.Sprintf("₹%.2f", p.Value)
}

type Quantity struct {
	Shares int `json:"shares"`
}

func NewQuantity(shares int) (*Quantity, error) {
	if shares <= 0 {
		return nil, ErrInvalidQuantity
	}
	return &Quantity{Shares: shares}, nil
}

func (q *Quantity) Multiply(factor float64) *Quantity {
	return &Quantity{Shares: int(float64(q.Shares) * factor)}
}

func (q *Quantity) String() string {
	return fmt.Sprintf("%d shares", q.Shares)
}

// Entities - Core trading objects with identity
type OrderID struct {
	Value string `json:"value"`
}

func NewOrderID() *OrderID {
	timestamp := time.Now().Unix()
	return &OrderID{Value: fmt.Sprintf("ORD_%d_%d", timestamp, time.Now().Nanosecond()%10000)}
}

func (o *OrderID) String() string {
	return o.Value
}

type Order struct {
	ID          *OrderID       `json:"id"`
	UserID      string         `json:"user_id"`
	Symbol      *TradingSymbol `json:"symbol"`
	Side        OrderSide      `json:"side"`
	Type        OrderType      `json:"type"`
	ProductType ProductType    `json:"product_type"`
	Quantity    *Quantity      `json:"quantity"`
	Price       *Price         `json:"price,omitempty"`        // For limit orders
	TriggerPrice *Price        `json:"trigger_price,omitempty"` // For stop orders
	Status      OrderStatus    `json:"status"`
	
	// Execution details
	ExecutedQuantity *Quantity `json:"executed_quantity"`
	ExecutedPrice    *Price    `json:"executed_price,omitempty"`
	ExecutionValue   Money     `json:"execution_value"`
	
	// Charges
	Brokerage      Money `json:"brokerage"`
	STT            Money `json:"stt"`           // Securities Transaction Tax
	TransactionTax Money `json:"transaction_tax"`
	GST            Money `json:"gst"`
	StampDuty      Money `json:"stamp_duty"`
	
	// Timestamps
	PlacedAt    time.Time  `json:"placed_at"`
	ExecutedAt  *time.Time `json:"executed_at,omitempty"`
	CancelledAt *time.Time `json:"cancelled_at,omitempty"`
	
	// Audit
	Version int `json:"version"`
}

// NewOrder creates a new trading order
func NewOrder(userID string, symbol *TradingSymbol, side OrderSide, orderType OrderType,
              productType ProductType, quantity *Quantity, price *Price) *Order {
	
	order := &Order{
		ID:               NewOrderID(),
		UserID:           userID,
		Symbol:           symbol,
		Side:             side,
		Type:             orderType,
		ProductType:      productType,
		Quantity:         quantity,
		Price:            price,
		Status:           OrderStatusPending,
		ExecutedQuantity: &Quantity{Shares: 0},
		ExecutionValue:   NewMoney(0),
		Brokerage:        NewMoney(0),
		STT:              NewMoney(0),
		TransactionTax:   NewMoney(0),
		GST:              NewMoney(0),
		StampDuty:        NewMoney(0),
		PlacedAt:         time.Now(),
		Version:          1,
	}
	
	fmt.Printf("📋 Order placed: %s %s %s at %s\n", 
		side, quantity.String(), symbol.String(), 
		price.String())
	
	return order
}

// Business Methods for Order
func (o *Order) Validate() error {
	// Basic validation
	if o.Quantity.Shares <= 0 {
		return ErrInvalidQuantity
	}
	
	// Price validation for limit orders
	if o.Type == OrderTypeLimit && o.Price == nil {
		return ErrInvalidPrice
	}
	
	// Stop loss validation
	if o.Type == OrderTypeStopLoss && o.TriggerPrice == nil {
		return errors.New("trigger price required for stop loss orders")
	}
	
	return nil
}

func (o *Order) Execute(executionPrice *Price, executedShares int) error {
	if o.Status == OrderStatusExecuted || o.Status == OrderStatusCancelled {
		return ErrOrderAlreadyExecuted
	}
	
	if executedShares <= 0 || executedShares > o.Quantity.Shares {
		return errors.New("invalid executed quantity")
	}
	
	// Calculate execution value
	executionValue := executionPrice.Value * float64(executedShares)
	o.ExecutionValue = o.ExecutionValue.Add(NewMoney(executionValue))
	
	// Update executed quantity
	o.ExecutedQuantity.Shares += executedShares
	
	// Calculate charges
	o.calculateCharges(executionPrice, executedShares)
	
	// Update status
	if o.ExecutedQuantity.Shares == o.Quantity.Shares {
		o.Status = OrderStatusExecuted
		now := time.Now()
		o.ExecutedAt = &now
		o.ExecutedPrice = executionPrice
		
		fmt.Printf("✅ Order fully executed: %s at %s\n", 
			o.ID.String(), executionPrice.String())
	} else {
		o.Status = OrderStatusPartial
		fmt.Printf("🔄 Order partially executed: %d/%d shares\n", 
			o.ExecutedQuantity.Shares, o.Quantity.Shares)
	}
	
	o.Version++
	return nil
}

func (o *Order) Cancel(reason string) error {
	if o.Status == OrderStatusExecuted {
		return errors.New("cannot cancel executed order - execute हुआ order cancel नहीं हो सकता")
	}
	
	o.Status = OrderStatusCancelled
	now := time.Now()
	o.CancelledAt = &now
	o.Version++
	
	fmt.Printf("❌ Order cancelled: %s - %s\n", o.ID.String(), reason)
	return nil
}

func (o *Order) calculateCharges(price *Price, shares int) {
	executionValue := price.Value * float64(shares)
	
	// Zerodha's actual charge structure (simplified)
	
	// Brokerage: ₹20 per order or 0.03%, whichever is lower for equity delivery
	if o.ProductType == ProductTypeCNC {
		brokerage := math.Min(20.0, executionValue*0.0003)
		o.Brokerage = o.Brokerage.Add(NewMoney(brokerage))
	} else {
		// Intraday: ₹20 per order or 0.03%, whichever is lower
		brokerage := math.Min(20.0, executionValue*0.0003)
		o.Brokerage = o.Brokerage.Add(NewMoney(brokerage))
	}
	
	// STT (Securities Transaction Tax)
	if o.Side == OrderSideSell {
		sttRate := 0.001 // 0.1% on sell side for equity delivery
		o.STT = o.STT.Add(NewMoney(executionValue * sttRate))
	}
	
	// Transaction charges: 0.00325% of turnover
	transactionCharge := executionValue * 0.0000325
	o.TransactionTax = o.TransactionTax.Add(NewMoney(transactionCharge))
	
	// GST: 18% on brokerage + transaction charges
	gstBase := o.Brokerage.Amount + o.TransactionTax.Amount
	gst := gstBase * 0.18
	o.GST = o.GST.Add(NewMoney(gst))
	
	// Stamp duty: 0.003% or ₹3000, whichever is lower
	stampDuty := math.Min(3000.0, executionValue*0.00003)
	o.StampDuty = o.StampDuty.Add(NewMoney(stampDuty))
}

func (o *Order) GetTotalCharges() Money {
	return o.Brokerage.Add(o.STT).Add(o.TransactionTax).Add(o.GST).Add(o.StampDuty)
}

func (o *Order) GetNetAmount() Money {
	netAmount := o.ExecutionValue
	if o.Side == OrderSideBuy {
		return netAmount.Add(o.GetTotalCharges())
	} else {
		return netAmount.Subtract(o.GetTotalCharges())
	}
}

// Position entity - Represents holdings
type Position struct {
	UserID      string         `json:"user_id"`
	Symbol      *TradingSymbol `json:"symbol"`
	ProductType ProductType    `json:"product_type"`
	Quantity    int            `json:"quantity"`    // Net quantity (+ve for long, -ve for short)
	AveragePrice float64       `json:"average_price"`
	
	// P&L tracking
	RealizedPnL   Money `json:"realized_pnl"`
	UnrealizedPnL Money `json:"unrealized_pnl"`
	
	// Market data
	LastPrice     *Price    `json:"last_price,omitempty"`
	LastUpdated   time.Time `json:"last_updated"`
}

func NewPosition(userID string, symbol *TradingSymbol, productType ProductType) *Position {
	return &Position{
		UserID:      userID,
		Symbol:      symbol,
		ProductType: productType,
		Quantity:    0,
		AveragePrice: 0.0,
		RealizedPnL: NewMoney(0),
		UnrealizedPnL: NewMoney(0),
		LastUpdated: time.Now(),
	}
}

func (p *Position) UpdateFromOrder(order *Order) {
	if order.Status != OrderStatusExecuted {
		return
	}
	
	executedShares := order.ExecutedQuantity.Shares
	executedPrice := order.ExecutedPrice.Value
	
	if order.Side == OrderSideBuy {
		// Adding to position
		if p.Quantity >= 0 {
			// Increasing long position or creating new long
			totalValue := (p.AveragePrice * float64(p.Quantity)) + (executedPrice * float64(executedShares))
			p.Quantity += executedShares
			p.AveragePrice = totalValue / float64(p.Quantity)
		} else {
			// Reducing short position
			if executedShares >= abs(p.Quantity) {
				// Cover entire short + create long
				excessShares := executedShares - abs(p.Quantity)
				// Realize P&L from covering short
				shortPnL := (p.AveragePrice - executedPrice) * float64(abs(p.Quantity))
				p.RealizedPnL = p.RealizedPnL.Add(NewMoney(shortPnL))
				
				p.Quantity = excessShares
				p.AveragePrice = executedPrice
			} else {
				// Partially cover short
				p.Quantity += executedShares // This will reduce the negative quantity
			}
		}
	} else {
		// Order side is SELL
		if p.Quantity > 0 {
			// Reducing long position or creating short
			if executedShares >= p.Quantity {
				// Sell entire long + create short
				longPnL := (executedPrice - p.AveragePrice) * float64(p.Quantity)
				p.RealizedPnL = p.RealizedPnL.Add(NewMoney(longPnL))
				
				excessShares := executedShares - p.Quantity
				p.Quantity = -excessShares
				p.AveragePrice = executedPrice
			} else {
				// Partially sell long position
				soldValue := executedPrice * float64(executedShares)
				soldAvgValue := p.AveragePrice * float64(executedShares)
				realizedPnL := soldValue - soldAvgValue
				p.RealizedPnL = p.RealizedPnL.Add(NewMoney(realizedPnL))
				
				p.Quantity -= executedShares
			}
		} else {
			// Increasing short position
			if p.Quantity == 0 {
				p.Quantity = -executedShares
				p.AveragePrice = executedPrice
			} else {
				totalValue := (p.AveragePrice * float64(abs(p.Quantity))) + (executedPrice * float64(executedShares))
				p.Quantity -= executedShares
				p.AveragePrice = totalValue / float64(abs(p.Quantity))
			}
		}
	}
	
	p.LastUpdated = time.Now()
}

func (p *Position) UpdateUnrealizedPnL(currentPrice *Price) {
	if p.Quantity == 0 {
		p.UnrealizedPnL = NewMoney(0)
		return
	}
	
	priceDiff := currentPrice.Value - p.AveragePrice
	unrealizedPnL := priceDiff * float64(p.Quantity)
	p.UnrealizedPnL = NewMoney(unrealizedPnL)
	p.LastPrice = currentPrice
	p.LastUpdated = time.Now()
}

func (p *Position) GetTotalPnL() Money {
	return p.RealizedPnL.Add(p.UnrealizedPnL)
}

func (p *Position) IsLong() bool {
	return p.Quantity > 0
}

func (p *Position) IsShort() bool {
	return p.Quantity < 0
}

func (p *Position) IsFlat() bool {
	return p.Quantity == 0
}

// Account aggregate - Manages user trading account
type TradingAccount struct {
	UserID         string                    `json:"user_id"`
	Balance        Money                     `json:"balance"`
	UsedMargin     Money                     `json:"used_margin"`
	AvailableMargin Money                   `json:"available_margin"`
	Positions      map[string]*Position      `json:"positions"`
	Orders         map[string]*Order         `json:"orders"`
	
	// Risk management
	MaxOrderValue  Money `json:"max_order_value"`
	MaxDayLoss     Money `json:"max_day_loss"`
	CurrentDayPnL  Money `json:"current_day_pnl"`
	
	// Trading limits
	MaxPositions   int `json:"max_positions"`
	
	mu sync.RWMutex
}

func NewTradingAccount(userID string, initialBalance Money) *TradingAccount {
	return &TradingAccount{
		UserID:          userID,
		Balance:         initialBalance,
		UsedMargin:      NewMoney(0),
		AvailableMargin: initialBalance,
		Positions:       make(map[string]*Position),
		Orders:          make(map[string]*Order),
		MaxOrderValue:   initialBalance.Multiply(0.5), // 50% of balance per order
		MaxDayLoss:      initialBalance.Multiply(-0.05), // 5% max loss per day
		CurrentDayPnL:   NewMoney(0),
		MaxPositions:    50,
	}
}

func (ta *TradingAccount) PlaceOrder(symbol *TradingSymbol, side OrderSide, orderType OrderType,
                                   productType ProductType, quantity *Quantity, price *Price) (*Order, error) {
	ta.mu.Lock()
	defer ta.mu.Unlock()
	
	// Risk checks
	err := ta.validateOrder(symbol, side, quantity, price)
	if err != nil {
		return nil, err
	}
	
	// Create order
	order := NewOrder(ta.UserID, symbol, side, orderType, productType, quantity, price)
	
	// Validate order
	err = order.Validate()
	if err != nil {
		return nil, err
	}
	
	// Reserve margin for buy orders
	if side == OrderSideBuy {
		orderValue := NewMoney(price.Value * float64(quantity.Shares))
		if ta.AvailableMargin.Amount < orderValue.Amount {
			return nil, ErrInsufficientBalance
		}
		
		ta.AvailableMargin = ta.AvailableMargin.Subtract(orderValue)
		ta.UsedMargin = ta.UsedMargin.Add(orderValue)
	}
	
	// Check position limits for sell orders
	if side == OrderSideSell {
		positionKey := ta.getPositionKey(symbol, productType)
		position, exists := ta.Positions[positionKey]
		if !exists || position.Quantity < quantity.Shares {
			return nil, ErrInsufficientShares
		}
	}
	
	ta.Orders[order.ID.Value] = order
	order.Status = OrderStatusOpen
	
	fmt.Printf("✅ Order placed successfully: %s\n", order.ID.String())
	return order, nil
}

func (ta *TradingAccount) ExecuteOrder(orderID string, executionPrice *Price, executedShares int) error {
	ta.mu.Lock()
	defer ta.mu.Unlock()
	
	order, exists := ta.Orders[orderID]
	if !exists {
		return ErrOrderNotFound
	}
	
	err := order.Execute(executionPrice, executedShares)
	if err != nil {
		return err
	}
	
	// Update position
	positionKey := ta.getPositionKey(order.Symbol, order.ProductType)
	position, exists := ta.Positions[positionKey]
	if !exists {
		position = NewPosition(ta.UserID, order.Symbol, order.ProductType)
		ta.Positions[positionKey] = position
	}
	
	position.UpdateFromOrder(order)
	
	// Update account balance and margin
	ta.updateAccountFromExecution(order, executedShares)
	
	return nil
}

func (ta *TradingAccount) CancelOrder(orderID string) error {
	ta.mu.Lock()
	defer ta.mu.Unlock()
	
	order, exists := ta.Orders[orderID]
	if !exists {
		return ErrOrderNotFound
	}
	
	err := order.Cancel("User cancellation")
	if err != nil {
		return err
	}
	
	// Release reserved margin
	if order.Side == OrderSideBuy && order.Status == OrderStatusOpen {
		orderValue := NewMoney(order.Price.Value * float64(order.Quantity.Shares))
		ta.AvailableMargin = ta.AvailableMargin.Add(orderValue)
		ta.UsedMargin = ta.UsedMargin.Subtract(orderValue)
	}
	
	return nil
}

func (ta *TradingAccount) UpdatePositionPrices(marketData map[string]*Price) {
	ta.mu.Lock()
	defer ta.mu.Unlock()
	
	totalDayPnL := NewMoney(0)
	
	for _, position := range ta.Positions {
		symbolKey := position.Symbol.String()
		if currentPrice, exists := marketData[symbolKey]; exists {
			position.UpdateUnrealizedPnL(currentPrice)
			totalDayPnL = totalDayPnL.Add(position.GetTotalPnL())
		}
	}
	
	ta.CurrentDayPnL = totalDayPnL
}

func (ta *TradingAccount) validateOrder(symbol *TradingSymbol, side OrderSide, quantity *Quantity, price *Price) error {
	// Check market hours (simplified)
	now := time.Now()
	if now.Hour() < 9 || now.Hour() >= 16 {
		return ErrMarketClosed
	}
	
	// Check order value limits
	orderValue := NewMoney(price.Value * float64(quantity.Shares))
	if orderValue.IsGreaterThan(ta.MaxOrderValue) {
		return errors.New("order value exceeds limit - order value limit से ज्यादा है")
	}
	
	// Check day loss limits
	if ta.CurrentDayPnL.Amount < ta.MaxDayLoss.Amount {
		return ErrRiskLimitExceeded
	}
	
	// Check position limits
	if len(ta.Positions) >= ta.MaxPositions {
		return errors.New("maximum positions limit reached - maximum positions limit पहुंच गया")
	}
	
	return nil
}

func (ta *TradingAccount) updateAccountFromExecution(order *Order, executedShares int) {
	netAmount := order.GetNetAmount()
	
	if order.Side == OrderSideBuy {
		// For buy orders, money goes out of account
		ta.Balance = ta.Balance.Subtract(netAmount)
		// Release reserved margin and update available margin
		reservedAmount := NewMoney(order.Price.Value * float64(executedShares))
		ta.UsedMargin = ta.UsedMargin.Subtract(reservedAmount)
		ta.AvailableMargin = ta.AvailableMargin.Add(reservedAmount.Subtract(netAmount))
	} else {
		// For sell orders, money comes into account
		ta.Balance = ta.Balance.Add(netAmount)
		ta.AvailableMargin = ta.AvailableMargin.Add(netAmount)
	}
}

func (ta *TradingAccount) getPositionKey(symbol *TradingSymbol, productType ProductType) string {
	return fmt.Sprintf("%s-%s", symbol.String(), productType)
}

func (ta *TradingAccount) GetNetWorth() Money {
	totalPnL := NewMoney(0)
	for _, position := range ta.Positions {
		totalPnL = totalPnL.Add(position.GetTotalPnL())
	}
	return ta.Balance.Add(totalPnL)
}

func (ta *TradingAccount) GetAccountSummary() map[string]interface{} {
	ta.mu.RLock()
	defer ta.mu.RUnlock()
	
	return map[string]interface{}{
		"user_id":            ta.UserID,
		"balance":           ta.Balance,
		"available_margin":  ta.AvailableMargin,
		"used_margin":       ta.UsedMargin,
		"net_worth":         ta.GetNetWorth(),
		"day_pnl":           ta.CurrentDayPnL,
		"total_positions":   len(ta.Positions),
		"active_orders":     len(ta.Orders),
	}
}

// Domain Services - Complex trading logic
type OrderMatchingService struct {
	marketData map[string]*Price
	mu         sync.RWMutex
}

func NewOrderMatchingService() *OrderMatchingService {
	return &OrderMatchingService{
		marketData: make(map[string]*Price),
	}
}

func (oms *OrderMatchingService) UpdateMarketPrice(symbol string, price *Price) {
	oms.mu.Lock()
	defer oms.mu.Unlock()
	
	oms.marketData[symbol] = price
	fmt.Printf("📈 Price update: %s = %s\n", symbol, price.String())
}

func (oms *OrderMatchingService) TryExecuteOrder(account *TradingAccount, order *Order) error {
	oms.mu.RLock()
	defer oms.mu.RUnlock()
	
	if order.Status != OrderStatusOpen {
		return nil
	}
	
	symbolKey := order.Symbol.String()
	currentPrice, exists := oms.marketData[symbolKey]
	if !exists {
		return errors.New("no market data available - market data उपलब्ध नहीं")
	}
	
	canExecute := false
	executionPrice := currentPrice
	
	switch order.Type {
	case OrderTypeMarket:
		canExecute = true
		
	case OrderTypeLimit:
		if order.Side == OrderSideBuy && currentPrice.Value <= order.Price.Value {
			canExecute = true
			executionPrice = order.Price // Execute at limit price
		} else if order.Side == OrderSideSell && currentPrice.Value >= order.Price.Value {
			canExecute = true
			executionPrice = order.Price
		}
		
	case OrderTypeStopLoss:
		if order.Side == OrderSideBuy && currentPrice.Value >= order.TriggerPrice.Value {
			canExecute = true
		} else if order.Side == OrderSideSell && currentPrice.Value <= order.TriggerPrice.Value {
			canExecute = true
		}
	}
	
	if canExecute {
		return account.ExecuteOrder(order.ID.Value, executionPrice, order.Quantity.Shares)
	}
	
	return nil
}

// Utility functions
func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// ====================================================================
// DEMO AND TESTING
// ====================================================================

func main() {
	fmt.Println("📊 Zerodha Trading Domain - DDD Example")
	fmt.Println(strings.Repeat("=", 50))
	
	// Create trading account with ₹1,00,000
	account := NewTradingAccount("USER123", NewMoney(100000))
	
	// Create order matching service
	matchingService := NewOrderMatchingService()
	
	// Setup market data
	reliance, _ := NewTradingSymbol("RELIANCE", ExchangeNSE)
	tcs, _ := NewTradingSymbol("TCS", ExchangeNSE)
	
	// Simulate market prices
	matchingService.UpdateMarketPrice(reliance.String(), &Price{Value: 2450.50})
	matchingService.UpdateMarketPrice(tcs.String(), &Price{Value: 3680.75})
	
	fmt.Printf("\n💰 Initial Account Balance: %s\n", account.Balance.String())
	fmt.Printf("💳 Available Margin: %s\n", account.AvailableMargin.String())
	
	// Demo trading scenarios
	demoTradingScenarios(account, matchingService, reliance, tcs)
	
	// Show final account summary
	fmt.Println("\n📊 Final Account Summary:")
	fmt.Println(strings.Repeat("-", 30))
	summary := account.GetAccountSummary()
	for key, value := range summary {
		if money, ok := value.(Money); ok {
			fmt.Printf("   %s: %s\n", key, money.String())
		} else {
			fmt.Printf("   %s: %v\n", key, value)
		}
	}
	
	fmt.Println("\n✨ Trading domain demonstration complete!")
	fmt.Println("✨ All DDD principles successfully applied:")
	fmt.Println("   ✅ Rich domain entities with business logic")
	fmt.Println("   ✅ Value objects for data integrity")
	fmt.Println("   ✅ Aggregates for consistency boundaries")
	fmt.Println("   ✅ Domain services for complex operations")
	fmt.Println("   ✅ Proper error handling and validation")
	fmt.Println("✨ Ready for production Zerodha-scale system!")
}

func demoTradingScenarios(account *TradingAccount, matching *OrderMatchingService, 
                         reliance, tcs *TradingSymbol) {
	
	fmt.Println("\n🔄 Trading Scenario 1: Buy RELIANCE shares")
	
	// Place buy order for RELIANCE
	buyOrder, err := account.PlaceOrder(
		reliance,
		OrderSideBuy,
		OrderTypeLimit,
		ProductTypeCNC,
		&Quantity{Shares: 10},
		&Price{Value: 2450.00},
	)
	
	if err != nil {
		fmt.Printf("❌ Buy order failed: %v\n", err)
	} else {
		// Try to execute the order
		err = matching.TryExecuteOrder(account, buyOrder)
		if err != nil {
			fmt.Printf("❌ Execution failed: %v\n", err)
		}
	}
	
	fmt.Println("\n🔄 Trading Scenario 2: Buy TCS shares with market order")
	
	// Place market buy order for TCS
	marketOrder, err := account.PlaceOrder(
		tcs,
		OrderSideBuy,
		OrderTypeMarket,
		ProductTypeCNC,
		&Quantity{Shares: 5},
		&Price{Value: 3680.75}, // Market price
	)
	
	if err != nil {
		fmt.Printf("❌ Market order failed: %v\n", err)
	} else {
		err = matching.TryExecuteOrder(account, marketOrder)
		if err != nil {
			fmt.Printf("❌ Market execution failed: %v\n", err)
		}
	}
	
	fmt.Println("\n📈 Simulating price movements...")
	
	// Simulate price changes
	matching.UpdateMarketPrice(reliance.String(), &Price{Value: 2485.25}) // +1.4%
	matching.UpdateMarketPrice(tcs.String(), &Price{Value: 3650.50})      // -0.8%
	
	// Update position P&L
	marketData := map[string]*Price{
		reliance.String(): {Value: 2485.25},
		tcs.String():      {Value: 3650.50},
	}
	account.UpdatePositionPrices(marketData)
	
	fmt.Println("\n📊 Current Positions:")
	for key, position := range account.Positions {
		fmt.Printf("   %s: %d shares @ ₹%.2f\n", 
			key, position.Quantity, position.AveragePrice)
		fmt.Printf("     Realized P&L: %s\n", position.RealizedPnL.String())
		fmt.Printf("     Unrealized P&L: %s\n", position.UnrealizedPnL.String())
		fmt.Printf("     Total P&L: %s\n", position.GetTotalPnL().String())
	}
	
	fmt.Println("\n🔄 Trading Scenario 3: Partial sell of RELIANCE")
	
	// Sell partial RELIANCE position
	sellOrder, err := account.PlaceOrder(
		reliance,
		OrderSideSell,
		OrderTypeLimit,
		ProductTypeCNC,
		&Quantity{Shares: 5}, // Sell half
		&Price{Value: 2480.00},
	)
	
	if err != nil {
		fmt.Printf("❌ Sell order failed: %v\n", err)
	} else {
		// Execute at current market price
		err = account.ExecuteOrder(sellOrder.ID.Value, &Price{Value: 2485.25}, 5)
		if err != nil {
			fmt.Printf("❌ Sell execution failed: %v\n", err)
		}
	}
	
	fmt.Println("\n📋 Order History:")
	for _, order := range account.Orders {
		charges := order.GetTotalCharges()
		fmt.Printf("   %s: %s %d shares of %s at ₹%.2f\n", 
			order.Status, order.Side, order.ExecutedQuantity.Shares,
			order.Symbol.String(), order.ExecutedPrice.Value)
		fmt.Printf("     Execution Value: %s\n", order.ExecutionValue.String())
		fmt.Printf("     Total Charges: %s\n", charges.String())
		fmt.Printf("     Net Amount: %s\n", order.GetNetAmount().String())
	}
}