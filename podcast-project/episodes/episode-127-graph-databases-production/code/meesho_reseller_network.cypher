/*
 * Meesho Reseller Network - Neo4j Cypher Implementation
 * ====================================================
 * 
 * यह script Meesho के complete reseller network को model करती है।
 * 13 million resellers का hierarchical structure with commission tracking।
 * 
 * Features:
 * - Multi-level reseller hierarchy
 * - Commission calculation algorithms
 * - Influence scoring with PageRank
 * - Product recommendation engine
 * - Performance analytics
 * 
 * Scale: 13M resellers, 5M products, 100M customers
 * Commission processed: ₹500 crores monthly
 * 
 * Author: Mumbai Social Commerce Team
 */

// ============================================================================
// SCHEMA CREATION - Meesho Graph Structure
// ============================================================================

// Create constraints for data integrity
CREATE CONSTRAINT reseller_phone_unique FOR (r:Reseller) REQUIRE r.phone IS UNIQUE;
CREATE CONSTRAINT customer_phone_unique FOR (c:Customer) REQUIRE c.phone IS UNIQUE;
CREATE CONSTRAINT product_id_unique FOR (p:Product) REQUIRE p.product_id IS UNIQUE;

// Create indexes for performance optimization
CREATE INDEX reseller_city_index FOR (r:Reseller) ON (r.city);
CREATE INDEX reseller_tier_index FOR (r:Reseller) ON (r.tier);
CREATE INDEX product_category_index FOR (p:Product) ON (p.category);
CREATE INDEX order_date_index FOR (o:Order) ON (o.order_date);

// Full-text search indexes for product discovery
CREATE FULLTEXT INDEX product_search_index FOR (p:Product) ON EACH [p.name, p.description, p.brand];

// ============================================================================
// SAMPLE DATA CREATION - Mumbai Social Commerce Network
// ============================================================================

// Tier 1 Resellers (Platinum) - Mumbai Business Leaders
CREATE (sunita:Reseller {
    reseller_id: "RES_001",
    name: "सुनीता बेन पटेल",
    phone: "+91-9876543210",
    email: "sunita.patel@email.com",
    city: "Mumbai",
    state: "Maharashtra",
    tier: "Platinum",
    joined_date: date("2020-01-15"),
    monthly_sales: 350000,
    total_sales: 8400000,
    commission_rate: 0.15,
    downline_count: 45,
    rating: 4.8,
    verified: true,
    bank_account: "ENCRYPTED_BANK_DETAILS",
    preferred_categories: ["Ethnic Wear", "Jewelry", "Home Decor"]
})

CREATE (rajesh:Reseller {
    reseller_id: "RES_002", 
    name: "राजेश शर्मा",
    phone: "+91-9876543211",
    email: "rajesh.sharma@email.com",
    city: "Delhi",
    state: "Delhi",
    tier: "Platinum",
    joined_date: date("2019-11-20"),
    monthly_sales: 420000,
    total_sales: 12600000,
    commission_rate: 0.15,
    downline_count: 62,
    rating: 4.9,
    verified: true,
    bank_account: "ENCRYPTED_BANK_DETAILS",
    preferred_categories: ["Electronics", "Fashion", "Sports"]
})

// Tier 2 Resellers (Gold) - Active Business Builders
CREATE (priya:Reseller {
    reseller_id: "RES_003",
    name: "प्रिया गुप्ता", 
    phone: "+91-9876543212",
    email: "priya.gupta@email.com",
    city: "Pune",
    state: "Maharashtra",
    tier: "Gold",
    joined_date: date("2021-03-10"),
    monthly_sales: 180000,
    total_sales: 3240000,
    commission_rate: 0.12,
    downline_count: 28,
    rating: 4.6,
    verified: true,
    bank_account: "ENCRYPTED_BANK_DETAILS",
    preferred_categories: ["Beauty", "Fashion", "Kids"]
})

CREATE (amit:Reseller {
    reseller_id: "RES_004",
    name: "अमित कुमार",
    phone: "+91-9876543213", 
    email: "amit.kumar@email.com",
    city: "Bangalore",
    state: "Karnataka",
    tier: "Gold",
    joined_date: date("2021-07-22"),
    monthly_sales: 220000,
    total_sales: 3960000,
    commission_rate: 0.12,
    downline_count: 34,
    rating: 4.7,
    verified: true,
    bank_account: "ENCRYPTED_BANK_DETAILS",
    preferred_categories: ["Electronics", "Gadgets", "Books"]
})

// Tier 3 Resellers (Silver) - Growing Entrepreneurs  
CREATE (kavita:Reseller {
    reseller_id: "RES_005",
    name: "कविता देवी",
    phone: "+91-9876543214",
    email: "kavita.devi@email.com", 
    city: "Lucknow",
    state: "Uttar Pradesh",
    tier: "Silver",
    joined_date: date("2022-05-15"),
    monthly_sales: 85000,
    total_sales: 765000,
    commission_rate: 0.10,
    downline_count: 12,
    rating: 4.4,
    verified: true,
    bank_account: "ENCRYPTED_BANK_DETAILS",
    preferred_categories: ["Traditional Wear", "Handicrafts"]
})

// Product Categories और Products
CREATE (ethnic_wear:Category {
    category_id: "CAT_001",
    name: "Ethnic Wear",
    parent_category: "Fashion",
    commission_rate: 0.08,
    demand_score: 92
})

CREATE (electronics:Category {
    category_id: "CAT_002", 
    name: "Electronics",
    parent_category: "Technology",
    commission_rate: 0.05,
    demand_score: 88
})

// High-demand products
CREATE (saree:Product {
    product_id: "PROD_001",
    name: "Banarasi Silk Saree",
    brand: "Craftsvilla",
    category: "Ethnic Wear",
    price: 2499,
    cost_price: 1800,
    margin: 28,
    rating: 4.3,
    review_count: 2847,
    in_stock: true,
    weight: 0.6,
    dimensions: "5.5m x 1.2m",
    colors: ["Red", "Blue", "Green", "Golden"],
    sizes: ["Free Size"],
    description: "Handwoven Banarasi silk saree with traditional motifs"
})

CREATE (smartphone:Product {
    product_id: "PROD_002",
    name: "Redmi Note 12 Pro",
    brand: "Xiaomi", 
    category: "Electronics",
    price: 23999,
    cost_price: 20000,
    margin: 17,
    rating: 4.4,
    review_count: 15632,
    in_stock: true,
    weight: 0.2,
    dimensions: "164.2 x 76.1 x 8.1 mm",
    colors: ["Midnight Black", "Frosted Blue", "Polar White"],
    storage: ["128GB", "256GB"],
    description: "50MP camera, 67W fast charging, AMOLED display"
})

// Customer profiles
CREATE (customer1:Customer {
    customer_id: "CUST_001",
    name: "आरती सिंह",
    phone: "+91-9876543215",
    email: "aarti.singh@email.com",
    city: "Mumbai", 
    state: "Maharashtra",
    age: 28,
    gender: "Female",
    joined_date: date("2022-01-20"),
    total_orders: 15,
    total_spent: 45600,
    preferred_categories: ["Fashion", "Beauty"],
    last_active: datetime("2024-01-20T15:30:00")
})

CREATE (customer2:Customer {
    customer_id: "CUST_002",
    name: "विकास जैन", 
    phone: "+91-9876543216",
    email: "vikas.jain@email.com",
    city: "Delhi",
    state: "Delhi", 
    age: 35,
    gender: "Male",
    joined_date: date("2021-11-10"),
    total_orders: 8,
    total_spent: 67800,
    preferred_categories: ["Electronics", "Gadgets"],
    last_active: datetime("2024-01-19T20:45:00")
})

// ============================================================================
// RELATIONSHIP CREATION - Network Connections
// ============================================================================

// Reseller mentorship hierarchy (Commission flow)
CREATE (sunita)-[:MENTORS {
    since: date("2021-03-10"),
    commission_share: 0.03,
    support_level: "High",
    training_provided: true,
    monthly_commission: 5400
}]->(priya)

CREATE (rajesh)-[:MENTORS {
    since: date("2021-07-22"),
    commission_share: 0.03,
    support_level: "High", 
    training_provided: true,
    monthly_commission: 6600
}]->(amit)

CREATE (priya)-[:MENTORS {
    since: date("2022-05-15"),
    commission_share: 0.02,
    support_level: "Medium",
    training_provided: true,
    monthly_commission: 1700
}]->(kavita)

// Product promotion relationships
CREATE (sunita)-[:PROMOTES {
    since: date("2020-02-01"),
    total_sales: 285,
    monthly_sales: 45,
    conversion_rate: 0.18,
    avg_rating: 4.7,
    commission_earned: 67500
}]->(saree)

CREATE (priya)-[:PROMOTES {
    since: date("2021-04-15"),
    total_sales: 156,
    monthly_sales: 28,
    conversion_rate: 0.15,
    avg_rating: 4.5,
    commission_earned: 38900
}]->(saree)

CREATE (amit)-[:PROMOTES {
    since: date("2021-08-10"),
    total_sales: 89,
    monthly_sales: 12,
    conversion_rate: 0.22,
    avg_rating: 4.6,
    commission_earned: 213000
}]->(smartphone)

// Customer purchase relationships
CREATE (customer1)-[:BOUGHT_FROM {
    order_date: date("2024-01-15"),
    order_id: "ORD_001",
    quantity: 2,
    unit_price: 2499,
    total_amount: 4998,
    payment_method: "UPI",
    delivery_status: "Delivered",
    rating_given: 5,
    review: "Beautiful saree, excellent quality!"
}]->(sunita)

CREATE (customer1)-[:PURCHASED {
    order_date: date("2024-01-15"),
    order_id: "ORD_001", 
    quantity: 2,
    unit_price: 2499,
    total_amount: 4998,
    discount_applied: 200,
    final_amount: 4798
}]->(saree)

CREATE (customer2)-[:BOUGHT_FROM {
    order_date: date("2024-01-10"),
    order_id: "ORD_002",
    quantity: 1,
    unit_price: 23999,
    total_amount: 23999,
    payment_method: "Credit Card",
    delivery_status: "Delivered", 
    rating_given: 4,
    review: "Good phone, fast delivery"
}]->(amit)

// Product-Category relationships
CREATE (saree)-[:BELONGS_TO]->(ethnic_wear)
CREATE (smartphone)-[:BELONGS_TO]->(electronics)

// ============================================================================
// COMMISSION CALCULATION QUERIES
// ============================================================================

// Real-time commission calculation for multi-level network
// Mumbai dabba delivery system की तरह - हर level पर commission
MATCH path = (top_reseller:Reseller)-[:MENTORS*1..5]->(seller:Reseller)
-[:BOUGHT_FROM]-(customer:Customer)-[:PURCHASED]->(product:Product)
WHERE seller.reseller_id = "RES_005"  // Kavita's sales
  AND customer.order_date >= date() - duration({days: 30})

WITH top_reseller, seller, customer, product, length(path) as hierarchy_level
WHERE hierarchy_level <= 3  // Maximum 3 levels for commission

// Calculate commission based on hierarchy level and tier
WITH top_reseller, seller, customer, product, hierarchy_level,
     CASE hierarchy_level
       WHEN 1 THEN product.price * 0.025    // Direct mentor: 2.5%
       WHEN 2 THEN product.price * 0.015    // Second level: 1.5%
       WHEN 3 THEN product.price * 0.010    // Third level: 1.0%
       ELSE 0
     END as base_commission

// Tier-based multiplier
WITH top_reseller, seller, customer, product, hierarchy_level, base_commission,
     CASE top_reseller.tier
       WHEN "Platinum" THEN 1.5
       WHEN "Gold" THEN 1.2
       WHEN "Silver" THEN 1.0
       ELSE 0.8
     END as tier_multiplier

RETURN top_reseller.name as reseller_name,
       top_reseller.tier as tier,
       seller.name as seller_name,
       product.name as product_sold,
       hierarchy_level,
       base_commission * tier_multiplier as final_commission,
       sum(base_commission * tier_multiplier) as total_monthly_commission
ORDER BY total_monthly_commission DESC;

// ============================================================================
// INFLUENCE SCORING - PageRank Algorithm
// ============================================================================

// Create graph projection for influence calculation
CALL gds.graph.project(
    'meesho-influence-network',
    {
        Reseller: {
            properties: ['monthly_sales', 'rating', 'tier', 'downline_count']
        },
        Customer: {
            properties: ['total_spent', 'total_orders']
        }
    },
    {
        MENTORS: {
            orientation: 'NATURAL',
            properties: ['commission_share', 'support_level']
        },
        BOUGHT_FROM: {
            orientation: 'NATURAL', 
            properties: ['total_amount', 'rating_given']
        },
        PROMOTES: {
            orientation: 'NATURAL',
            properties: ['conversion_rate', 'commission_earned']
        }
    }
);

// Run PageRank algorithm with relationship weights
CALL gds.pageRank.stream('meesho-influence-network', {
    relationshipWeightProperty: 'commission_share',
    dampingFactor: 0.85,
    maxIterations: 20,
    tolerance: 0.0000001
})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) as node, score
WHERE node:Reseller

// Combine PageRank with business metrics
WITH node,
     score as pagerank_score,
     node.monthly_sales as sales,
     node.rating as rating,
     node.downline_count as network_size,
     CASE node.tier
       WHEN "Platinum" THEN 100
       WHEN "Gold" THEN 75
       WHEN "Silver" THEN 50
       ELSE 25
     END as tier_score

// Calculate comprehensive influence score
WITH node,
     pagerank_score * 1000 as pr_score,
     (sales / 10000) as sales_score,
     rating * 20 as rating_score,
     network_size as network_score,
     tier_score,
     (pagerank_score * 1000 + sales/10000 + rating * 20 + network_size + tier_score) as total_influence_score

RETURN node.name as reseller_name,
       node.city as city,
       node.tier as tier,
       node.monthly_sales as monthly_sales,
       pr_score,
       sales_score,
       rating_score,
       network_score,
       tier_score,
       total_influence_score
ORDER BY total_influence_score DESC
LIMIT 20;

// ============================================================================
// PRODUCT RECOMMENDATION ENGINE
// ============================================================================

// Collaborative filtering for reseller product recommendations
// Mumbai ke shopkeeper की recommendation की तरह - similar taste
MATCH (target_reseller:Reseller {reseller_id: "RES_003"})  // Priya

// Find similar resellers based on city, tier, and category preferences
MATCH (target_reseller)-[:PROMOTES]->(common_product:Product)
<-[:PROMOTES]-(similar_reseller:Reseller)
WHERE similar_reseller <> target_reseller
  AND similar_reseller.city IN ["Mumbai", "Pune", "Nashik"]  // Regional similarity
  AND similar_reseller.tier IN ["Gold", "Platinum"]  // Tier compatibility

// Find products promoted by similar resellers but not by target
MATCH (similar_reseller)-[:PROMOTES]->(recommended_product:Product)
WHERE NOT (target_reseller)-[:PROMOTES]->(recommended_product)
  AND recommended_product.in_stock = true

// Calculate recommendation score based on multiple factors
WITH recommended_product,
     count(DISTINCT similar_reseller) as similar_reseller_count,
     avg(similar_reseller.conversion_rate) as avg_conversion_rate,
     recommended_product.margin as profit_margin,
     recommended_product.rating as product_rating,
     recommended_product.price as price

// Market demand analysis
MATCH (all_resellers:Reseller)-[promotes:PROMOTES]->(recommended_product)
WHERE promotes.since >= date() - duration({months: 3})
WITH recommended_product, similar_reseller_count, avg_conversion_rate, 
     profit_margin, product_rating, price,
     count(all_resellers) as total_promoters,
     sum(promotes.monthly_sales) as total_monthly_sales

// Final recommendation scoring
WITH recommended_product,
     similar_reseller_count * 0.25 as similarity_score,
     avg_conversion_rate * 100 as conversion_score, 
     profit_margin as margin_score,
     product_rating * 10 as quality_score,
     (total_monthly_sales / 100) as demand_score,
     CASE 
       WHEN price <= 1000 THEN 20
       WHEN price <= 5000 THEN 15
       WHEN price <= 15000 THEN 10
       ELSE 5
     END as price_accessibility_score

RETURN recommended_product.name as product_name,
       recommended_product.brand as brand,
       recommended_product.category as category,
       recommended_product.price as price,
       profit_margin,
       similar_reseller_count as recommenders,
       avg_conversion_rate as expected_conversion,
       total_monthly_sales as market_demand,
       (similarity_score + conversion_score + margin_score + quality_score + demand_score + price_accessibility_score) as recommendation_score
ORDER BY recommendation_score DESC
LIMIT 15;

// ============================================================================
// NETWORK GROWTH ANALYSIS
// ============================================================================

// Identify potential new resellers from customer base
// Mumbai network expansion strategy
MATCH (active_customer:Customer)-[:BOUGHT_FROM]->(reseller:Reseller)
WHERE active_customer.total_orders >= 5  // Frequent customers
  AND active_customer.total_spent >= 15000  // High value customers
  AND active_customer.last_active >= datetime() - duration({months: 1})

// Calculate customer engagement and spending patterns  
WITH active_customer,
     count(DISTINCT reseller) as reseller_diversity,
     active_customer.total_spent / active_customer.total_orders as avg_order_value,
     active_customer.total_orders / 
     duration.between(date(active_customer.joined_date), date()).months as orders_per_month

// Find customers with high engagement who aren't resellers yet
WHERE reseller_diversity >= 2  // Shops from multiple resellers
  AND avg_order_value >= 2000   // High order values
  AND orders_per_month >= 1      // Regular shopping
  AND NOT EXISTS {
    MATCH (active_customer)-[:IS_RESELLER]->(:Reseller)
  }

// Find potential mentors for these customers
MATCH (active_customer)-[:BOUGHT_FROM]->(potential_mentor:Reseller)
WHERE potential_mentor.tier IN ["Gold", "Platinum"]
  AND potential_mentor.downline_count < 50  // Not overwhelmed

WITH active_customer, potential_mentor,
     avg_order_value, orders_per_month, reseller_diversity,
     potential_mentor.rating as mentor_rating,
     potential_mentor.commission_rate as mentor_commission

// Calculate recruitment potential score
WITH active_customer, potential_mentor,
     (avg_order_value / 1000) as spending_score,
     (orders_per_month * 10) as frequency_score,
     (reseller_diversity * 5) as diversity_score,
     (mentor_rating * 10) as mentor_quality_score,
     CASE active_customer.city
       WHEN potential_mentor.city THEN 20
       ELSE 10
     END as location_match_score

RETURN active_customer.name as potential_reseller,
       active_customer.city as city,
       active_customer.total_spent as lifetime_value,
       avg_order_value,
       orders_per_month,
       potential_mentor.name as suggested_mentor,
       mentor_rating,
       (spending_score + frequency_score + diversity_score + mentor_quality_score + location_match_score) as recruitment_score
ORDER BY recruitment_score DESC
LIMIT 25;

// ============================================================================
// PERFORMANCE ANALYTICS - Mumbai Business Intelligence
// ============================================================================

// Monthly performance dashboard for resellers
MATCH (reseller:Reseller)
OPTIONAL MATCH (reseller)-[:BOUGHT_FROM]-(customer:Customer)-[:PURCHASED]->(product:Product)
WHERE customer.order_date >= date() - duration({months: 1})

// Calculate key metrics
WITH reseller,
     count(DISTINCT customer) as unique_customers,
     count(DISTINCT product) as products_sold,
     sum(customer.total_amount) as monthly_revenue,
     avg(customer.rating_given) as avg_customer_rating

// Commission and growth metrics
OPTIONAL MATCH (reseller)-[:MENTORS]->(downline:Reseller)
WITH reseller, unique_customers, products_sold, monthly_revenue, avg_customer_rating,
     count(downline) as direct_downlines

// Calculate month-over-month growth
OPTIONAL MATCH (reseller)-[:BOUGHT_FROM]-(prev_customer:Customer)-[:PURCHASED]->(prev_product:Product)
WHERE prev_customer.order_date >= date() - duration({months: 2})
  AND prev_customer.order_date < date() - duration({months: 1})

WITH reseller, unique_customers, products_sold, monthly_revenue, avg_customer_rating, direct_downlines,
     sum(prev_customer.total_amount) as prev_month_revenue

// Performance categorization
WITH reseller,
     unique_customers,
     products_sold, 
     monthly_revenue,
     avg_customer_rating,
     direct_downlines,
     CASE 
       WHEN prev_month_revenue = 0 THEN 100
       ELSE ((monthly_revenue - prev_month_revenue) / prev_month_revenue) * 100
     END as growth_rate

// Tier-based performance evaluation
WITH reseller,
     unique_customers,
     products_sold,
     monthly_revenue,
     avg_customer_rating,
     direct_downlines,
     growth_rate,
     CASE 
       WHEN reseller.tier = "Platinum" AND monthly_revenue >= 300000 THEN "Exceeding"
       WHEN reseller.tier = "Gold" AND monthly_revenue >= 150000 THEN "Exceeding"
       WHEN reseller.tier = "Silver" AND monthly_revenue >= 75000 THEN "Exceeding"
       WHEN monthly_revenue >= reseller.monthly_sales * 0.8 THEN "Meeting"
       ELSE "Below Target"
     END as performance_status

RETURN reseller.name as reseller_name,
       reseller.city as city,
       reseller.tier as tier,
       unique_customers,
       products_sold,
       monthly_revenue,
       reseller.monthly_sales as target_sales,
       avg_customer_rating,
       direct_downlines,
       growth_rate,
       performance_status
ORDER BY 
  CASE performance_status
    WHEN "Exceeding" THEN 3
    WHEN "Meeting" THEN 2
    WHEN "Below Target" THEN 1
  END DESC,
  monthly_revenue DESC;

// ============================================================================
// CLEANUP COMMANDS
// ============================================================================

// Drop graph projection when analysis is complete
// CALL gds.graph.drop('meesho-influence-network');

// Performance monitoring query
// Check query execution time and memory usage
/*
PROFILE 
MATCH (r:Reseller)-[:MENTORS*1..3]-(downline:Reseller)
WHERE r.tier = "Platinum"
RETURN r.name, count(downline) as network_size
ORDER BY network_size DESC
LIMIT 10;
*/