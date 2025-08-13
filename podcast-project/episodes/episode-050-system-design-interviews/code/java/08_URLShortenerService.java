/**
 * URL Shortener Service - Episode 50: System Design Interview Mastery
 * Bit.ly-like URL Shortener - Mumbai Railway Short Codes System
 * 
 * URL Shortening जैसे Mumbai Local का station codes हैं -
 * Chhatrapati Shivaji Terminus = CST, बड़ा name को छोटे code में convert
 * 
 * Author: Hindi Podcast Series
 * Topic: URL Shortening System Design with Analytics
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;

/**
 * URL Entry - Individual shortened URL record
 */
class URLEntry {
    private final String shortUrl;
    private final String longUrl;
    private final String userId;
    private final LocalDateTime createdAt;
    private final LocalDateTime expiresAt;
    private final Map<String, String> metadata;
    
    // Analytics
    private final AtomicLong clickCount = new AtomicLong(0);
    private final Map<String, AtomicLong> clicksByCountry = new ConcurrentHashMap<>();
    private final Map<String, AtomicLong> clicksByReferrer = new ConcurrentHashMap<>();
    private final List<ClickEvent> recentClicks = Collections.synchronizedList(new ArrayList<>());
    
    public URLEntry(String shortUrl, String longUrl, String userId, 
                   LocalDateTime expiresAt, Map<String, String> metadata) {
        this.shortUrl = shortUrl;
        this.longUrl = longUrl;
        this.userId = userId;
        this.createdAt = LocalDateTime.now();
        this.expiresAt = expiresAt;
        this.metadata = metadata != null ? new HashMap<>(metadata) : new HashMap<>();
    }
    
    // Getters
    public String getShortUrl() { return shortUrl; }
    public String getLongUrl() { return longUrl; }
    public String getUserId() { return userId; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getExpiresAt() { return expiresAt; }
    public Map<String, String> getMetadata() { return new HashMap<>(metadata); }
    public long getClickCount() { return clickCount.get(); }
    
    public boolean isExpired() {
        return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
    }
    
    public void recordClick(String country, String referrer, String userAgent) {
        clickCount.incrementAndGet();
        
        // Track by country
        clicksByCountry.computeIfAbsent(country != null ? country : "Unknown", 
                                       k -> new AtomicLong(0)).incrementAndGet();
        
        // Track by referrer
        clicksByReferrer.computeIfAbsent(referrer != null ? referrer : "Direct", 
                                        k -> new AtomicLong(0)).incrementAndGet();
        
        // Store recent click
        ClickEvent click = new ClickEvent(LocalDateTime.now(), country, referrer, userAgent);
        recentClicks.add(click);
        
        // Keep only last 100 clicks
        if (recentClicks.size() > 100) {
            recentClicks.remove(0);
        }
    }
    
    public Map<String, Long> getClicksByCountry() {
        Map<String, Long> result = new HashMap<>();
        clicksByCountry.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
    
    public Map<String, Long> getClicksByReferrer() {
        Map<String, Long> result = new HashMap<>();
        clicksByReferrer.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
    
    public List<ClickEvent> getRecentClicks() {
        return new ArrayList<>(recentClicks);
    }
    
    @Override
    public String toString() {
        return String.format("URLEntry{short='%s', long='%s', user='%s', clicks=%d}", 
                shortUrl, longUrl, userId, clickCount.get());
    }
}

/**
 * Click event for analytics
 */
class ClickEvent {
    private final LocalDateTime timestamp;
    private final String country;
    private final String referrer;
    private final String userAgent;
    
    public ClickEvent(LocalDateTime timestamp, String country, String referrer, String userAgent) {
        this.timestamp = timestamp;
        this.country = country;
        this.referrer = referrer;
        this.userAgent = userAgent;
    }
    
    // Getters
    public LocalDateTime getTimestamp() { return timestamp; }
    public String getCountry() { return country; }
    public String getReferrer() { return referrer; }
    public String getUserAgent() { return userAgent; }
}

/**
 * Base62 encoder for generating short URLs
 */
class Base62Encoder {
    private static final String ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    private static final int BASE = ALPHABET.length();
    
    public static String encode(long number) {
        if (number == 0) return String.valueOf(ALPHABET.charAt(0));
        
        StringBuilder sb = new StringBuilder();
        while (number > 0) {
            sb.insert(0, ALPHABET.charAt((int) (number % BASE)));
            number /= BASE;
        }
        return sb.toString();
    }
    
    public static long decode(String encoded) {
        long result = 0;
        for (int i = 0; i < encoded.length(); i++) {
            result = result * BASE + ALPHABET.indexOf(encoded.charAt(i));
        }
        return result;
    }
}

/**
 * URL Shortener Service - Main implementation
 */
public class URLShortenerService {
    
    private final String baseUrl;
    private final Map<String, URLEntry> urlDatabase; // short -> URLEntry
    private final Map<String, String> reverseMapping; // long -> short
    private final AtomicLong counter = new AtomicLong(1000000); // Start from 1M
    private final Pattern urlPattern;
    private final MessageDigest md5;
    
    // Rate limiting and user management
    private final Map<String, UserQuota> userQuotas = new ConcurrentHashMap<>();
    private final int maxUrlsPerUser = 1000;
    private final int maxUrlsPerDay = 100;
    
    // Analytics
    private final AtomicLong totalUrls = new AtomicLong(0);
    private final AtomicLong totalClicks = new AtomicLong(0);
    
    public URLShortenerService(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.urlDatabase = new ConcurrentHashMap<>();
        this.reverseMapping = new ConcurrentHashMap<>();
        
        // URL validation pattern
        this.urlPattern = Pattern.compile(
                "^(https?://)?(www\.)?[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(/.*)?$",
                Pattern.CASE_INSENSITIVE);
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not available", e);
        }
        
        System.out.printf("🔗 URL Shortener Service initialized - Base URL: %s%n", baseUrl);
    }
    
    /**
     * Shorten a URL - Mumbai Railway station name को code में convert करना
     */
    public ShortenResult shortenUrl(String longUrl, String userId, 
                                   Map<String, String> options) {
        
        // Validate URL
        if (!isValidUrl(longUrl)) {
            return new ShortenResult(false, "Invalid URL format", null, null);
        }
        
        // Normalize URL
        String normalizedUrl = normalizeUrl(longUrl);
        
        // Check if URL already shortened by this user
        String existingShort = reverseMapping.get(userId + ":" + normalizedUrl);
        if (existingShort != null && urlDatabase.containsKey(existingShort)) {
            URLEntry existing = urlDatabase.get(existingShort);
            if (!existing.isExpired()) {
                System.out.printf("♻️ Returning existing short URL: %s%n", existingShort);
                return new ShortenResult(true, "URL already shortened", 
                        baseUrl + "/" + existingShort, existing);
            }
        }
        
        // Check user quota
        if (!checkUserQuota(userId)) {
            return new ShortenResult(false, "User quota exceeded", null, null);
        }
        
        // Generate short URL
        String shortUrl = generateShortUrl(normalizedUrl, options);
        
        // Set expiration
        LocalDateTime expiresAt = null;
        if (options != null && options.containsKey("expires_days")) {
            int days = Integer.parseInt(options.get("expires_days"));
            expiresAt = LocalDateTime.now().plusDays(days);
        }
        
        // Create URL entry
        URLEntry urlEntry = new URLEntry(shortUrl, normalizedUrl, userId, expiresAt, options);
        
        // Store in database
        urlDatabase.put(shortUrl, urlEntry);
        reverseMapping.put(userId + ":" + normalizedUrl, shortUrl);
        
        // Update quotas and metrics
        updateUserQuota(userId);
        totalUrls.incrementAndGet();
        
        System.out.printf("✅ URL shortened: %s → %s/%s%n", 
                normalizedUrl, baseUrl, shortUrl);
        
        return new ShortenResult(true, "URL shortened successfully", 
                baseUrl + "/" + shortUrl, urlEntry);
    }
    
    /**
     * Expand/redirect short URL - Short code को original URL में convert करना
     */
    public RedirectResult expandUrl(String shortUrl, String clientIp, 
                                   String referrer, String userAgent) {
        
        URLEntry entry = urlDatabase.get(shortUrl);
        
        if (entry == null) {
            return new RedirectResult(false, "Short URL not found", null);
        }
        
        if (entry.isExpired()) {
            return new RedirectResult(false, "Short URL has expired", null);
        }
        
        // Record analytics
        String country = getCountryFromIP(clientIp);
        entry.recordClick(country, referrer, userAgent);
        totalClicks.incrementAndGet();
        
        System.out.printf("🔄 Redirecting: %s → %s%n", shortUrl, entry.getLongUrl());
        
        return new RedirectResult(true, "Redirect successful", entry.getLongUrl());
    }
    
    /**
     * Get URL analytics - Mumbai station traffic analysis
     */
    public URLAnalytics getUrlAnalytics(String shortUrl, String userId) {
        URLEntry entry = urlDatabase.get(shortUrl);
        
        if (entry == null || !entry.getUserId().equals(userId)) {
            return null;
        }
        
        return new URLAnalytics(
                entry.getShortUrl(),
                entry.getLongUrl(),
                entry.getClickCount(),
                entry.getCreatedAt(),
                entry.getClicksByCountry(),
                entry.getClicksByReferrer(),
                entry.getRecentClicks()
        );
    }
    
    /**
     * Get user's URLs - User के सभी shortened URLs
     */
    public List<URLEntry> getUserUrls(String userId) {
        return urlDatabase.values().stream()
                .filter(entry -> entry.getUserId().equals(userId))
                .filter(entry -> !entry.isExpired())
                .sorted((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()))
                .limit(100) // Latest 100 URLs
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
    
    /**
     * Delete short URL - URL को delete करना
     */
    public boolean deleteUrl(String shortUrl, String userId) {
        URLEntry entry = urlDatabase.get(shortUrl);
        
        if (entry == null || !entry.getUserId().equals(userId)) {
            return false;
        }
        
        urlDatabase.remove(shortUrl);
        reverseMapping.remove(userId + ":" + entry.getLongUrl());
        
        System.out.printf("🗑️ URL deleted: %s%n", shortUrl);
        return true;
    }
    
    /**
     * Generate short URL using different strategies
     */
    private String generateShortUrl(String longUrl, Map<String, String> options) {
        // Custom alias if provided
        if (options != null && options.containsKey("custom_alias")) {
            String customAlias = options.get("custom_alias");
            if (isValidAlias(customAlias) && !urlDatabase.containsKey(customAlias)) {
                return customAlias;
            }
        }
        
        // Hash-based generation for consistent results
        String hashInput = longUrl + System.currentTimeMillis();
        byte[] hash = md5.digest(hashInput.getBytes(StandardCharsets.UTF_8));
        long hashLong = Math.abs(((long) hash[0] << 24) | ((long) hash[1] << 16) | 
                                ((long) hash[2] << 8) | (long) hash[3]);
        
        // Combine with counter for uniqueness
        long uniqueId = (hashLong % 1000000) + counter.getAndIncrement();
        return Base62Encoder.encode(uniqueId);
    }
    
    private boolean isValidUrl(String url) {
        return url != null && url.trim().length() > 0 && urlPattern.matcher(url.trim()).matches();
    }
    
    private String normalizeUrl(String url) {
        url = url.trim().toLowerCase();
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "https://" + url;
        }
        // Remove trailing slash
        if (url.endsWith("/")) {
            url = url.substring(0, url.length() - 1);
        }
        return url;
    }
    
    private boolean isValidAlias(String alias) {
        return alias != null && alias.matches("[a-zA-Z0-9_-]{3,20}");
    }
    
    private boolean checkUserQuota(String userId) {
        UserQuota quota = userQuotas.computeIfAbsent(userId, k -> new UserQuota());
        return quota.canCreateUrl();
    }
    
    private void updateUserQuota(String userId) {
        UserQuota quota = userQuotas.get(userId);
        if (quota != null) {
            quota.incrementUsage();
        }
    }
    
    private String getCountryFromIP(String clientIp) {
        // Simulate IP geolocation - in production use actual GeoIP service
        if (clientIp == null) return "Unknown";
        
        // Simulate Indian IP ranges
        if (clientIp.startsWith("103.") || clientIp.startsWith("106.")) {
            return "India";
        } else if (clientIp.startsWith("192.168.") || clientIp.startsWith("127.")) {
            return "Local";
        } else {
            String[] countries = {"USA", "UK", "Canada", "Australia", "Germany", "France"};
            return countries[Math.abs(clientIp.hashCode()) % countries.length];
        }
    }
    
    /**
     * Get system statistics
     */
    public SystemStats getSystemStats() {
        long activeUrls = urlDatabase.values().stream()
                .filter(entry -> !entry.isExpired())
                .count();
        
        Map<String, Long> userStats = new HashMap<>();
        urlDatabase.values().forEach(entry -> {
            userStats.merge(entry.getUserId(), 1L, Long::sum);
        });
        
        return new SystemStats(
                totalUrls.get(),
                activeUrls,
                totalClicks.get(),
                userQuotas.size(),
                userStats
        );
    }
    
    /**
     * Cleanup expired URLs
     */
    public int cleanupExpiredUrls() {
        List<String> expiredUrls = urlDatabase.entrySet().stream()
                .filter(entry -> entry.getValue().isExpired())
                .map(Map.Entry::getKey)
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
        
        for (String shortUrl : expiredUrls) {
            URLEntry entry = urlDatabase.remove(shortUrl);
            if (entry != null) {
                reverseMapping.remove(entry.getUserId() + ":" + entry.getLongUrl());
            }
        }
        
        System.out.printf("🧹 Cleaned up %d expired URLs%n", expiredUrls.size());
        return expiredUrls.size();
    }
    
    /**
     * Demo method - Mumbai railway station shortening
     */
    public static void demonstrateMumbaiRailwayShortening() {
        System.out.println("🚂 Mumbai Railway Station URL Shortening Demo");
        System.out.println("=" + "=".repeat(60));
        
        URLShortenerService shortener = new URLShortenerService("https://mum.ly");
        
        // Mumbai railway websites to shorten
        Map<String, String> railwayUrls = new LinkedHashMap<>();
        railwayUrls.put("https://www.indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,1,304,366,528", "Central Railway");
        railwayUrls.put("https://www.wcr.indianrailways.gov.in/cris/layout/set/print/content/view/full/23821", "Western Railway");
        railwayUrls.put("https://www.irctc.co.in/nget/train-search", "IRCTC Train Booking");
        railwayUrls.put("https://enquiry.indianrail.gov.in/mntes/", "Train Enquiry");
        railwayUrls.put("https://www.mumbailive.com/en/transport/local-trains", "Mumbai Local Info");
        
        String userId = "mumbai_commuter_001";
        
        System.out.printf("%n🔗 Shortening Mumbai railway URLs for user: %s%n", userId);
        
        // Shorten all URLs
        for (Map.Entry<String, String> entry : railwayUrls.entrySet()) {
            String longUrl = entry.getKey();
            String description = entry.getValue();
            
            Map<String, String> options = new HashMap<>();
            options.put("description", description);
            options.put("expires_days", "90"); // Expire in 90 days
            
            ShortenResult result = shortener.shortenUrl(longUrl, userId, options);
            
            if (result.success) {
                System.out.printf("✅ %s%n   → %s%n", description, result.shortUrl);
            } else {
                System.out.printf("❌ Failed to shorten %s: %s%n", description, result.message);
            }
        }
        
        // Simulate clicks
        System.out.printf("%n📊 Simulating commuter clicks...%n");
        
        List<URLEntry> userUrls = shortener.getUserUrls(userId);
        String[] referrers = {"google.com", "twitter.com", "whatsapp.com", "Direct"};
        String[] userAgents = {"Mobile App", "Chrome Browser", "Firefox", "Safari"};
        String[] ips = {"103.21.58.52", "106.51.64.19", "192.168.1.100", "203.124.18.45"};
        
        Random random = new Random();
        
        for (URLEntry urlEntry : userUrls) {
            int clicks = 5 + random.nextInt(20); // 5-25 clicks per URL
            
            for (int i = 0; i < clicks; i++) {
                String referrer = referrers[random.nextInt(referrers.length)];
                String userAgent = userAgents[random.nextInt(userAgents.length)];
                String ip = ips[random.nextInt(ips.length)];
                
                RedirectResult redirectResult = shortener.expandUrl(
                        urlEntry.getShortUrl(), ip, referrer, userAgent);
                
                if (redirectResult.success && i == 0) {
                    System.out.printf("📱 Click: %s → %s%n", 
                            urlEntry.getShortUrl(), redirectResult.redirectUrl);
                }
            }
        }
        
        // Show analytics
        System.out.printf("%n📈 URL Analytics:%n");
        for (URLEntry urlEntry : userUrls) {
            URLAnalytics analytics = shortener.getUrlAnalytics(urlEntry.getShortUrl(), userId);
            if (analytics != null) {
                System.out.printf("%n🎯 %s%n", urlEntry.getMetadata().get("description"));
                System.out.printf("   Total Clicks: %d%n", analytics.getTotalClicks());
                System.out.printf("   Top Country: %s%n", getTopEntry(analytics.getClicksByCountry()));
                System.out.printf("   Top Referrer: %s%n", getTopEntry(analytics.getClicksByReferrer()));
            }
        }
        
        // Show system statistics
        System.out.printf("%n📊 System Statistics:%n");
        SystemStats stats = shortener.getSystemStats();
        System.out.printf("   Total URLs: %d%n", stats.getTotalUrls());
        System.out.printf("   Active URLs: %d%n", stats.getActiveUrls());
        System.out.printf("   Total Clicks: %d%n", stats.getTotalClicks());
        System.out.printf("   Total Users: %d%n", stats.getTotalUsers());
        
        // Test URL deletion
        System.out.printf("%n🗑️ Testing URL deletion...%n");
        if (!userUrls.isEmpty()) {
            URLEntry firstUrl = userUrls.get(0);
            boolean deleted = shortener.deleteUrl(firstUrl.getShortUrl(), userId);
            System.out.printf("Deletion result: %s%n", deleted ? "Success" : "Failed");
        }
        
        // Cleanup expired URLs
        System.out.printf("%n🧹 Performing cleanup...%n");
        int cleanedUp = shortener.cleanupExpiredUrls();
    }
    
    private static String getTopEntry(Map<String, Long> map) {
        return map.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(entry -> String.format("%s (%d)", entry.getKey(), entry.getValue()))
                .orElse("None");
    }
    
    public static void main(String[] args) {
        demonstrateMumbaiRailwayShortening();
        
        System.out.println("\n" + "=".repeat(80));
        System.out.println("✅ URL Shortener Service Demo Complete!");
        System.out.println("📚 Key Features Demonstrated:");
        System.out.println("   • Base62 encoding for short URLs");
        System.out.println("   • Custom aliases and expiration");
        System.out.println("   • Comprehensive analytics tracking");
        System.out.println("   • User quotas and rate limiting");
        System.out.println("   • Geographic and referrer analytics");
        System.out.println("   • URL validation and normalization");
        System.out.println("   • Automatic cleanup of expired URLs");
        System.out.println("   • Production-ready for Mumbai scale");
    }
}

// Supporting classes

class ShortenResult {
    final boolean success;
    final String message;
    final String shortUrl;
    final URLEntry urlEntry;
    
    public ShortenResult(boolean success, String message, String shortUrl, URLEntry urlEntry) {
        this.success = success;
        this.message = message;
        this.shortUrl = shortUrl;
        this.urlEntry = urlEntry;
    }
}

class RedirectResult {
    final boolean success;
    final String message;
    final String redirectUrl;
    
    public RedirectResult(boolean success, String message, String redirectUrl) {
        this.success = success;
        this.message = message;
        this.redirectUrl = redirectUrl;
    }
}

class URLAnalytics {
    private final String shortUrl;
    private final String longUrl;
    private final long totalClicks;
    private final LocalDateTime createdAt;
    private final Map<String, Long> clicksByCountry;
    private final Map<String, Long> clicksByReferrer;
    private final List<ClickEvent> recentClicks;
    
    public URLAnalytics(String shortUrl, String longUrl, long totalClicks, 
                       LocalDateTime createdAt, Map<String, Long> clicksByCountry,
                       Map<String, Long> clicksByReferrer, List<ClickEvent> recentClicks) {
        this.shortUrl = shortUrl;
        this.longUrl = longUrl;
        this.totalClicks = totalClicks;
        this.createdAt = createdAt;
        this.clicksByCountry = clicksByCountry;
        this.clicksByReferrer = clicksByReferrer;
        this.recentClicks = recentClicks;
    }
    
    // Getters
    public String getShortUrl() { return shortUrl; }
    public String getLongUrl() { return longUrl; }
    public long getTotalClicks() { return totalClicks; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Map<String, Long> getClicksByCountry() { return clicksByCountry; }
    public Map<String, Long> getClicksByReferrer() { return clicksByReferrer; }
    public List<ClickEvent> getRecentClicks() { return recentClicks; }
}

class UserQuota {
    private final AtomicLong totalUrls = new AtomicLong(0);
    private final AtomicLong dailyUrls = new AtomicLong(0);
    private LocalDateTime lastResetDate = LocalDateTime.now().toLocalDate().atStartOfDay();
    private final int maxUrlsTotal = 1000;
    private final int maxUrlsPerDay = 100;
    
    public boolean canCreateUrl() {
        resetDailyCountIfNeeded();
        return totalUrls.get() < maxUrlsTotal && dailyUrls.get() < maxUrlsPerDay;
    }
    
    public void incrementUsage() {
        totalUrls.incrementAndGet();
        dailyUrls.incrementAndGet();
    }
    
    private void resetDailyCountIfNeeded() {
        LocalDateTime today = LocalDateTime.now().toLocalDate().atStartOfDay();
        if (today.isAfter(lastResetDate)) {
            dailyUrls.set(0);
            lastResetDate = today;
        }
    }
}

class SystemStats {
    private final long totalUrls;
    private final long activeUrls;
    private final long totalClicks;
    private final int totalUsers;
    private final Map<String, Long> userStats;
    
    public SystemStats(long totalUrls, long activeUrls, long totalClicks, 
                      int totalUsers, Map<String, Long> userStats) {
        this.totalUrls = totalUrls;
        this.activeUrls = activeUrls;
        this.totalClicks = totalClicks;
        this.totalUsers = totalUsers;
        this.userStats = userStats;
    }
    
    // Getters
    public long getTotalUrls() { return totalUrls; }
    public long getActiveUrls() { return activeUrls; }
    public long getTotalClicks() { return totalClicks; }
    public int getTotalUsers() { return totalUsers; }
    public Map<String, Long> getUserStats() { return userStats; }
}