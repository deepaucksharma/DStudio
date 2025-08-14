/*
 * Domain-Driven Design: Repository Pattern - Netflix Content Management
 * Hindi Tech Podcast Series - Episode 40
 * 
 * यह example दिखाता है कि कैसे DDD में Repository pattern का इस्तेमाल करके
 * Netflix content management system बनाते हैं। Repository pattern से
 * domain logic को persistence layer से अलग रखते हैं।
 * 
 * Author: Hindi Tech Podcast  
 * Date: 2025
 */

package com.hindipodcast.ddd.netflix;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

// ====================================================================
// DOMAIN EXCEPTIONS
// ====================================================================

class DomainException extends RuntimeException {
    public DomainException(String message) { super(message); }
}

class ContentNotFoundException extends DomainException {
    public ContentNotFoundException(String message) { super(message); }
}

class InvalidContentException extends DomainException {
    public InvalidContentException(String message) { super(message); }
}

class ContentAlreadyExistsException extends DomainException {
    public ContentAlreadyExistsException(String message) { super(message); }
}

// ====================================================================
// ENUMS
// ====================================================================

enum ContentType {
    MOVIE("Movie"),
    TV_SERIES("TV Series"), 
    DOCUMENTARY("Documentary"),
    STAND_UP("Stand-up Comedy"),
    ANIME("Anime"),
    SHORT_FILM("Short Film");
    
    private final String displayName;
    
    ContentType(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() { return displayName; }
}

enum ContentStatus {
    DRAFT("Draft"),
    IN_PRODUCTION("In Production"),
    POST_PRODUCTION("Post Production"),
    READY_FOR_RELEASE("Ready for Release"),
    RELEASED("Released"),
    ARCHIVED("Archived");
    
    private final String displayName;
    
    ContentStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() { return displayName; }
}

enum Genre {
    ACTION("Action"),
    COMEDY("Comedy"),
    DRAMA("Drama"),
    HORROR("Horror"),
    ROMANCE("Romance"),
    THRILLER("Thriller"),
    SCI_FI("Science Fiction"),
    DOCUMENTARY("Documentary"),
    FAMILY("Family"),
    CRIME("Crime"),
    FANTASY("Fantasy"),
    MYSTERY("Mystery");
    
    private final String displayName;
    
    Genre(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() { return displayName; }
}

enum AgeRating {
    U("U", "Universal - Suitable for all ages"),
    UA("UA", "Parental guidance for children under 12"),
    A("A", "Restricted to adults (18+)"),
    S("S", "Restricted to specialized audiences");
    
    private final String code;
    private final String description;
    
    AgeRating(String code, String description) {
        this.code = code;
        this.description = description;
    }
    
    public String getCode() { return code; }
    public String getDescription() { return description; }
}

enum Region {
    GLOBAL("Global"),
    INDIA("India"),
    US("United States"),
    UK("United Kingdom"),
    KOREA("South Korea"),
    JAPAN("Japan"),
    EUROPE("Europe");
    
    private final String displayName;
    
    Region(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() { return displayName; }
}

// ====================================================================
// VALUE OBJECTS
// ====================================================================

/**
 * Content ID strong-typed identifier
 * Content ID का strong-typed identifier
 */
class ContentId {
    private final String value;
    
    public ContentId(String value) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException("Content ID cannot be empty - Content ID खाली नहीं हो सकता");
        }
        if (!value.matches("^[A-Z0-9]{8,12}$")) {
            throw new IllegalArgumentException("Invalid Content ID format - गलत Content ID format");
        }
        this.value = value.toUpperCase().trim();
    }
    
    public static ContentId generate() {
        return new ContentId("NF" + UUID.randomUUID().toString().replaceAll("-", "").substring(0, 8).toUpperCase());
    }
    
    public String getValue() { return value; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ContentId)) return false;
        ContentId contentId = (ContentId) o;
        return Objects.equals(value, contentId.value);
    }
    
    @Override
    public int hashCode() { return Objects.hash(value); }
    
    @Override
    public String toString() { return value; }
}

/**
 * Content Rating value object
 * Content rating value object
 */
class ContentRating {
    private final double averageRating;
    private final int totalRatings;
    private final Map<Integer, Integer> ratingDistribution; // star -> count
    
    public ContentRating(double averageRating, int totalRatings, Map<Integer, Integer> distribution) {
        if (averageRating < 0 || averageRating > 5) {
            throw new IllegalArgumentException("Rating must be between 0 and 5 - Rating 0 से 5 के बीच होनी चाहिए");
        }
        if (totalRatings < 0) {
            throw new IllegalArgumentException("Total ratings cannot be negative");
        }
        
        this.averageRating = averageRating;
        this.totalRatings = totalRatings;
        this.ratingDistribution = distribution != null ? new HashMap<>(distribution) : new HashMap<>();
    }
    
    public static ContentRating createEmpty() {
        return new ContentRating(0.0, 0, new HashMap<>());
    }
    
    public ContentRating addRating(int stars) {
        if (stars < 1 || stars > 5) {
            throw new IllegalArgumentException("Rating must be between 1 and 5 stars");
        }
        
        Map<Integer, Integer> newDistribution = new HashMap<>(this.ratingDistribution);
        newDistribution.merge(stars, 1, Integer::sum);
        
        double totalScore = this.averageRating * this.totalRatings + stars;
        int newTotalRatings = this.totalRatings + 1;
        double newAverage = totalScore / newTotalRatings;
        
        return new ContentRating(newAverage, newTotalRatings, newDistribution);
    }
    
    public double getAverageRating() { return averageRating; }
    public int getTotalRatings() { return totalRatings; }
    public Map<Integer, Integer> getRatingDistribution() { return new HashMap<>(ratingDistribution); }
    
    public String getRatingCategory() {
        if (averageRating >= 4.5) return "Excellent";
        if (averageRating >= 4.0) return "Very Good";
        if (averageRating >= 3.0) return "Good";
        if (averageRating >= 2.0) return "Average";
        return "Poor";
    }
    
    @Override
    public String toString() {
        return String.format("%.1f⭐ (%d ratings)", averageRating, totalRatings);
    }
}

/**
 * Content metadata value object
 * Content metadata value object
 */
class ContentMetadata {
    private final int durationMinutes;
    private final String language;
    private final List<String> subtitleLanguages;
    private final String director;
    private final List<String> cast;
    private final String synopsis;
    private final List<String> keywords;
    
    public ContentMetadata(int durationMinutes, String language, String director, 
                          String synopsis, List<String> cast, List<String> subtitles, 
                          List<String> keywords) {
        if (durationMinutes <= 0) {
            throw new IllegalArgumentException("Duration must be positive - Duration positive होनी चाहिए");
        }
        if (language == null || language.trim().isEmpty()) {
            throw new IllegalArgumentException("Language is required - Language जरूरी है");
        }
        
        this.durationMinutes = durationMinutes;
        this.language = language.trim();
        this.director = director != null ? director.trim() : "";
        this.synopsis = synopsis != null ? synopsis.trim() : "";
        this.cast = cast != null ? new ArrayList<>(cast) : new ArrayList<>();
        this.subtitleLanguages = subtitles != null ? new ArrayList<>(subtitles) : new ArrayList<>();
        this.keywords = keywords != null ? new ArrayList<>(keywords) : new ArrayList<>();
    }
    
    public int getDurationMinutes() { return durationMinutes; }
    public String getLanguage() { return language; }
    public String getDirector() { return director; }
    public String getSynopsis() { return synopsis; }
    public List<String> getCast() { return new ArrayList<>(cast); }
    public List<String> getSubtitleLanguages() { return new ArrayList<>(subtitleLanguages); }
    public List<String> getKeywords() { return new ArrayList<>(keywords); }
    
    public String getFormattedDuration() {
        int hours = durationMinutes / 60;
        int minutes = durationMinutes % 60;
        if (hours > 0) {
            return String.format("%dh %dm", hours, minutes);
        }
        return String.format("%dm", minutes);
    }
    
    @Override
    public String toString() {
        return String.format("%s - %s (%s)", language, getFormattedDuration(), director);
    }
}

// ====================================================================
// DOMAIN ENTITIES
// ====================================================================

/**
 * Content Entity - Main content entity
 * Content Entity - Main content entity
 */
class Content {
    private final ContentId contentId;
    private String title;
    private String originalTitle;
    private ContentType type;
    private ContentStatus status;
    private final Set<Genre> genres;
    private AgeRating ageRating;
    private final Set<Region> availableRegions;
    private LocalDate releaseDate;
    private LocalDate addedToNetflixDate;
    private ContentMetadata metadata;
    private ContentRating rating;
    
    // Analytics and performance
    private long viewCount;
    private long completionCount;
    private double averageWatchTimePercentage;
    
    // Technical details
    private String thumbnailUrl;
    private String trailerUrl;
    private Map<String, String> streamingUrls; // quality -> url
    
    // Audit fields
    private final LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private String createdBy;
    private String updatedBy;
    
    public Content(ContentId contentId, String title, ContentType type, AgeRating ageRating) {
        if (title == null || title.trim().isEmpty()) {
            throw new IllegalArgumentException("Title is required - Title जरूरी है");
        }
        
        this.contentId = contentId;
        this.title = title.trim();
        this.originalTitle = title.trim();
        this.type = type;
        this.ageRating = ageRating;
        this.status = ContentStatus.DRAFT;
        
        this.genres = new HashSet<>();
        this.availableRegions = new HashSet<>();
        this.rating = ContentRating.createEmpty();
        this.streamingUrls = new HashMap<>();
        
        this.viewCount = 0;
        this.completionCount = 0;
        this.averageWatchTimePercentage = 0.0;
        
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("📺 Content created: " + title + " (" + contentId + ")");
    }
    
    // ====================================================================
    // BUSINESS METHODS
    // ====================================================================
    
    public void updateTitle(String newTitle, String updatedBy) {
        if (newTitle == null || newTitle.trim().isEmpty()) {
            throw new IllegalArgumentException("Title cannot be empty");
        }
        
        String oldTitle = this.title;
        this.title = newTitle.trim();
        this.updatedBy = updatedBy;
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("📝 Title updated: " + oldTitle + " → " + newTitle);
    }
    
    public void addGenre(Genre genre) {
        if (this.genres.add(genre)) {
            this.updatedAt = LocalDateTime.now();
            System.out.println("🏷️ Genre added: " + genre.getDisplayName() + " to " + title);
        }
    }
    
    public void removeGenre(Genre genre) {
        if (this.genres.remove(genre)) {
            this.updatedAt = LocalDateTime.now();
            System.out.println("🗑️ Genre removed: " + genre.getDisplayName() + " from " + title);
        }
    }
    
    public void addRegion(Region region) {
        if (this.availableRegions.add(region)) {
            this.updatedAt = LocalDateTime.now();
            System.out.println("🌍 Region added: " + region.getDisplayName() + " for " + title);
        }
    }
    
    public void removeRegion(Region region) {
        if (this.availableRegions.remove(region)) {
            this.updatedAt = LocalDateTime.now();
            System.out.println("❌ Region removed: " + region.getDisplayName() + " from " + title);
        }
    }
    
    public void updateMetadata(ContentMetadata newMetadata, String updatedBy) {
        this.metadata = newMetadata;
        this.updatedBy = updatedBy;
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("📋 Metadata updated for: " + title);
    }
    
    public void updateStatus(ContentStatus newStatus, String updatedBy) {
        if (newStatus == this.status) return;
        
        ContentStatus oldStatus = this.status;
        this.status = newStatus;
        this.updatedBy = updatedBy;
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("🔄 Status updated for " + title + ": " + 
            oldStatus.getDisplayName() + " → " + newStatus.getDisplayName());
    }
    
    public void setReleaseDate(LocalDate releaseDate) {
        this.releaseDate = releaseDate;
        this.updatedAt = LocalDateTime.now();
        
        if (releaseDate != null && !releaseDate.isAfter(LocalDate.now())) {
            this.addedToNetflixDate = LocalDate.now();
        }
    }
    
    public void addRating(int stars, String userId) {
        if (this.status != ContentStatus.RELEASED) {
            throw new IllegalStateException("Cannot rate unreleased content - Unreleased content को rate नहीं कर सकते");
        }
        
        this.rating = this.rating.addRating(stars);
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("⭐ Rating added: " + stars + " stars for " + title + 
            " (New average: " + String.format("%.1f", rating.getAverageRating()) + ")");
    }
    
    public void recordView() {
        if (this.status != ContentStatus.RELEASED) {
            throw new IllegalStateException("Cannot record view for unreleased content");
        }
        
        this.viewCount++;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void recordCompletion(double watchTimePercentage) {
        if (this.status != ContentStatus.RELEASED) {
            throw new IllegalStateException("Cannot record completion for unreleased content");
        }
        
        if (watchTimePercentage >= 90.0) { // Completed if 90%+ watched
            this.completionCount++;
        }
        
        // Update average watch time percentage
        double totalWatchTime = this.averageWatchTimePercentage * (this.viewCount - 1) + watchTimePercentage;
        this.averageWatchTimePercentage = totalWatchTime / this.viewCount;
        
        this.updatedAt = LocalDateTime.now();
    }
    
    public void addStreamingUrl(String quality, String url) {
        this.streamingUrls.put(quality, url);
        this.updatedAt = LocalDateTime.now();
    }
    
    // ====================================================================
    // QUERY METHODS
    // ====================================================================
    
    public boolean isAvailableInRegion(Region region) {
        return this.availableRegions.contains(region);
    }
    
    public boolean hasGenre(Genre genre) {
        return this.genres.contains(genre);
    }
    
    public boolean isReleased() {
        return this.status == ContentStatus.RELEASED;
    }
    
    public boolean isPopular() {
        return this.viewCount > 10000 && this.rating.getAverageRating() >= 4.0;
    }
    
    public double getCompletionRate() {
        return this.viewCount > 0 ? (double) this.completionCount / this.viewCount : 0.0;
    }
    
    public Map<String, Object> getAnalytics() {
        Map<String, Object> analytics = new HashMap<>();
        analytics.put("viewCount", viewCount);
        analytics.put("completionCount", completionCount);
        analytics.put("completionRate", getCompletionRate());
        analytics.put("averageWatchTimePercentage", averageWatchTimePercentage);
        analytics.put("rating", rating.getAverageRating());
        analytics.put("totalRatings", rating.getTotalRatings());
        analytics.put("isPopular", isPopular());
        return analytics;
    }
    
    // ====================================================================
    // GETTERS
    // ====================================================================
    
    public ContentId getContentId() { return contentId; }
    public String getTitle() { return title; }
    public String getOriginalTitle() { return originalTitle; }
    public ContentType getType() { return type; }
    public ContentStatus getStatus() { return status; }
    public Set<Genre> getGenres() { return new HashSet<>(genres); }
    public AgeRating getAgeRating() { return ageRating; }
    public Set<Region> getAvailableRegions() { return new HashSet<>(availableRegions); }
    public LocalDate getReleaseDate() { return releaseDate; }
    public LocalDate getAddedToNetflixDate() { return addedToNetflixDate; }
    public ContentMetadata getMetadata() { return metadata; }
    public ContentRating getRating() { return rating; }
    public long getViewCount() { return viewCount; }
    public long getCompletionCount() { return completionCount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Content)) return false;
        Content content = (Content) o;
        return Objects.equals(contentId, content.contentId);
    }
    
    @Override
    public int hashCode() { return Objects.hash(contentId); }
    
    @Override
    public String toString() {
        return String.format("Content(%s: %s - %s)", contentId, title, type.getDisplayName());
    }
}

// ====================================================================
// REPOSITORY INTERFACES - Domain layer contracts
// ====================================================================

/**
 * Content Repository interface - Domain contract
 * Content Repository interface - Domain contract
 */
interface ContentRepository {
    
    // Basic CRUD operations
    void save(Content content);
    Optional<Content> findById(ContentId contentId);
    void delete(ContentId contentId);
    List<Content> findAll();
    
    // Domain-specific queries
    List<Content> findByStatus(ContentStatus status);
    List<Content> findByType(ContentType type);
    List<Content> findByGenre(Genre genre);
    List<Content> findByRegion(Region region);
    List<Content> findByAgeRating(AgeRating ageRating);
    
    // Complex queries
    List<Content> findByTitle(String title);
    List<Content> findByTitleContaining(String titlePart);
    List<Content> findByDirector(String director);
    List<Content> findByCastMember(String actorName);
    List<Content> findByLanguage(String language);
    
    // Analytics queries
    List<Content> findMostViewed(int limit);
    List<Content> findHighestRated(int limit);
    List<Content> findMostCompleted(int limit);
    List<Content> findTrendingContent();
    
    // Date-based queries
    List<Content> findReleasedBetween(LocalDate startDate, LocalDate endDate);
    List<Content> findAddedToNetflixBetween(LocalDate startDate, LocalDate endDate);
    List<Content> findRecentlyAdded(int days);
    
    // Custom specifications
    List<Content> findBySpecification(ContentSpecification specification);
}

/**
 * Specification pattern for complex queries
 * Complex queries के लिए specification pattern
 */
interface ContentSpecification {
    boolean isSatisfiedBy(Content content);
}

// ====================================================================
// REPOSITORY IMPLEMENTATION - Infrastructure layer
// ====================================================================

/**
 * In-Memory Content Repository Implementation
 * In-Memory content repository implementation
 */
class InMemoryContentRepository implements ContentRepository {
    
    private final Map<ContentId, Content> contentStore;
    
    public InMemoryContentRepository() {
        this.contentStore = new ConcurrentHashMap<>();
        System.out.println("🗄️ In-Memory Content Repository initialized");
    }
    
    @Override
    public void save(Content content) {
        if (content == null) {
            throw new IllegalArgumentException("Content cannot be null");
        }
        
        ContentId id = content.getContentId();
        boolean isNew = !contentStore.containsKey(id);
        
        contentStore.put(id, content);
        
        if (isNew) {
            System.out.println("💾 Content saved: " + content.getTitle() + " (" + id + ")");
        } else {
            System.out.println("🔄 Content updated: " + content.getTitle() + " (" + id + ")");
        }
    }
    
    @Override
    public Optional<Content> findById(ContentId contentId) {
        Content content = contentStore.get(contentId);
        return Optional.ofNullable(content);
    }
    
    @Override
    public void delete(ContentId contentId) {
        Content removed = contentStore.remove(contentId);
        if (removed != null) {
            System.out.println("🗑️ Content deleted: " + removed.getTitle() + " (" + contentId + ")");
        } else {
            throw new ContentNotFoundException("Content not found: " + contentId);
        }
    }
    
    @Override
    public List<Content> findAll() {
        return new ArrayList<>(contentStore.values());
    }
    
    @Override
    public List<Content> findByStatus(ContentStatus status) {
        return contentStore.values().stream()
            .filter(content -> content.getStatus() == status)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByType(ContentType type) {
        return contentStore.values().stream()
            .filter(content -> content.getType() == type)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByGenre(Genre genre) {
        return contentStore.values().stream()
            .filter(content -> content.hasGenre(genre))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByRegion(Region region) {
        return contentStore.values().stream()
            .filter(content -> content.isAvailableInRegion(region))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByAgeRating(AgeRating ageRating) {
        return contentStore.values().stream()
            .filter(content -> content.getAgeRating() == ageRating)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByTitle(String title) {
        return contentStore.values().stream()
            .filter(content -> content.getTitle().equalsIgnoreCase(title))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByTitleContaining(String titlePart) {
        return contentStore.values().stream()
            .filter(content -> content.getTitle().toLowerCase().contains(titlePart.toLowerCase()))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByDirector(String director) {
        return contentStore.values().stream()
            .filter(content -> content.getMetadata() != null)
            .filter(content -> content.getMetadata().getDirector().equalsIgnoreCase(director))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByCastMember(String actorName) {
        return contentStore.values().stream()
            .filter(content -> content.getMetadata() != null)
            .filter(content -> content.getMetadata().getCast().stream()
                .anyMatch(actor -> actor.equalsIgnoreCase(actorName)))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findByLanguage(String language) {
        return contentStore.values().stream()
            .filter(content -> content.getMetadata() != null)
            .filter(content -> content.getMetadata().getLanguage().equalsIgnoreCase(language))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findMostViewed(int limit) {
        return contentStore.values().stream()
            .filter(Content::isReleased)
            .sorted((a, b) -> Long.compare(b.getViewCount(), a.getViewCount()))
            .limit(limit)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findHighestRated(int limit) {
        return contentStore.values().stream()
            .filter(Content::isReleased)
            .filter(content -> content.getRating().getTotalRatings() >= 100) // Minimum 100 ratings
            .sorted((a, b) -> Double.compare(b.getRating().getAverageRating(), a.getRating().getAverageRating()))
            .limit(limit)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findMostCompleted(int limit) {
        return contentStore.values().stream()
            .filter(Content::isReleased)
            .filter(content -> content.getViewCount() >= 1000) // Minimum 1000 views
            .sorted((a, b) -> Double.compare(b.getCompletionRate(), a.getCompletionRate()))
            .limit(limit)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findTrendingContent() {
        // Simple trending algorithm: high views in recent period + good completion rate
        return contentStore.values().stream()
            .filter(Content::isReleased)
            .filter(content -> content.getViewCount() >= 5000)
            .filter(content -> content.getCompletionRate() >= 0.7)
            .filter(content -> content.getRating().getAverageRating() >= 3.5)
            .sorted((a, b) -> {
                // Composite score: views * completion_rate * rating
                double scoreA = a.getViewCount() * a.getCompletionRate() * a.getRating().getAverageRating();
                double scoreB = b.getViewCount() * b.getCompletionRate() * b.getRating().getAverageRating();
                return Double.compare(scoreB, scoreA);
            })
            .limit(20)
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findReleasedBetween(LocalDate startDate, LocalDate endDate) {
        return contentStore.values().stream()
            .filter(content -> content.getReleaseDate() != null)
            .filter(content -> !content.getReleaseDate().isBefore(startDate))
            .filter(content -> !content.getReleaseDate().isAfter(endDate))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findAddedToNetflixBetween(LocalDate startDate, LocalDate endDate) {
        return contentStore.values().stream()
            .filter(content -> content.getAddedToNetflixDate() != null)
            .filter(content -> !content.getAddedToNetflixDate().isBefore(startDate))
            .filter(content -> !content.getAddedToNetflixDate().isAfter(endDate))
            .collect(Collectors.toList());
    }
    
    @Override
    public List<Content> findRecentlyAdded(int days) {
        LocalDate cutoffDate = LocalDate.now().minusDays(days);
        return findAddedToNetflixBetween(cutoffDate, LocalDate.now());
    }
    
    @Override
    public List<Content> findBySpecification(ContentSpecification specification) {
        return contentStore.values().stream()
            .filter(specification::isSatisfiedBy)
            .collect(Collectors.toList());
    }
    
    // Additional utility methods
    public long countByStatus(ContentStatus status) {
        return contentStore.values().stream()
            .mapToLong(content -> content.getStatus() == status ? 1 : 0)
            .sum();
    }
    
    public Map<ContentType, Long> getContentTypeStatistics() {
        return contentStore.values().stream()
            .collect(Collectors.groupingBy(Content::getType, Collectors.counting()));
    }
}

// ====================================================================
// SPECIFICATION IMPLEMENTATIONS
// ====================================================================

class PopularContentSpecification implements ContentSpecification {
    @Override
    public boolean isSatisfiedBy(Content content) {
        return content.isPopular();
    }
}

class FamilyFriendlySpecification implements ContentSpecification {
    @Override
    public boolean isSatisfiedBy(Content content) {
        return content.getAgeRating() == AgeRating.U || content.getAgeRating() == AgeRating.UA;
    }
}

class RecentHindiContentSpecification implements ContentSpecification {
    private final LocalDate cutoffDate = LocalDate.now().minusMonths(6);
    
    @Override
    public boolean isSatisfiedBy(Content content) {
        return content.getMetadata() != null &&
               content.getMetadata().getLanguage().equalsIgnoreCase("Hindi") &&
               content.getAddedToNetflixDate() != null &&
               content.getAddedToNetflixDate().isAfter(cutoffDate);
    }
}

// ====================================================================
// DEMO AND TESTING
// ====================================================================

/**
 * Netflix Content Repository Demo
 * Netflix content repository demo
 */
public class NetflixContentRepository {
    
    public static void main(String[] args) {
        System.out.println("📺 Netflix Content Repository - DDD Example");
        System.out.println("=" + "=".repeat(55));
        
        // Create repository
        ContentRepository contentRepo = new InMemoryContentRepository();
        
        try {
            System.out.println("\n📝 Step 1: Creating Sample Content");
            
            // Create sample content
            createSampleContent(contentRepo);
            
            System.out.println("\n🔍 Step 2: Basic Repository Queries");
            
            // Test basic queries
            testBasicQueries(contentRepo);
            
            System.out.println("\n📊 Step 3: Analytics Queries");
            
            // Test analytics queries
            testAnalyticsQueries(contentRepo);
            
            System.out.println("\n🎯 Step 4: Specification Pattern");
            
            // Test specification pattern
            testSpecificationPattern(contentRepo);
            
            System.out.println("\n📈 Step 5: Repository Statistics");
            
            // Show repository statistics
            showRepositoryStatistics(contentRepo);
            
            System.out.println("\n✨ Repository pattern demonstration complete!");
            System.out.println("✨ Domain and persistence layers properly separated!");
            System.out.println("✨ Ready for production Netflix-scale system!");
            
        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void createSampleContent(ContentRepository repo) {
        // Create popular Hindi movie
        Content scam1992 = new Content(ContentId.generate(), "Scam 1992: The Harshad Mehta Story", 
                                     ContentType.TV_SERIES, AgeRating.UA);
        scam1992.addGenre(Genre.DRAMA);
        scam1992.addGenre(Genre.CRIME);
        scam1992.addRegion(Region.INDIA);
        scam1992.addRegion(Region.GLOBAL);
        scam1992.updateStatus(ContentStatus.RELEASED, "content_manager");
        scam1992.setReleaseDate(LocalDate.of(2020, 10, 9));
        
        ContentMetadata scamMetadata = new ContentMetadata(
            600, // 10 hours total
            "Hindi",
            "Hansal Mehta",
            "Based on the life of Harshad Mehta, a stockbroker who single-handedly took the stock market to dizzying heights.",
            Arrays.asList("Pratik Gandhi", "Shreya Dhanwanthary", "Hemant Kher"),
            Arrays.asList("English", "Telugu", "Tamil"),
            Arrays.asList("stock market", "scam", "harshad mehta", "bombay", "finance")
        );
        scam1992.updateMetadata(scamMetadata, "content_manager");
        
        // Simulate views and ratings
        for (int i = 0; i < 50000; i++) scam1992.recordView();
        for (int i = 0; i < 25000; i++) scam1992.recordCompletion(95.0);
        for (int i = 0; i < 10000; i++) scam1992.addRating(5, "user" + i);
        for (int i = 0; i < 5000; i++) scam1992.addRating(4, "user" + (10000 + i));
        
        repo.save(scam1992);
        
        // Create popular international movie
        Content strangerthings = new Content(ContentId.generate(), "Stranger Things", 
                                           ContentType.TV_SERIES, AgeRating.UA);
        strangerthings.addGenre(Genre.SCI_FI);
        strangerthings.addGenre(Genre.HORROR);
        strangerthings.addGenre(Genre.DRAMA);
        strangerthings.addRegion(Region.GLOBAL);
        strangerthings.updateStatus(ContentStatus.RELEASED, "content_manager");
        strangerthings.setReleaseDate(LocalDate.of(2016, 7, 15));
        
        ContentMetadata stMetadata = new ContentMetadata(
            1500, // ~25 hours total
            "English",
            "The Duffer Brothers",
            "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces, and one strange little girl.",
            Arrays.asList("Winona Ryder", "David Harbour", "Millie Bobby Brown", "Finn Wolfhard"),
            Arrays.asList("Hindi", "Spanish", "French", "German", "Japanese"),
            Arrays.asList("80s", "supernatural", "kids", "mystery", "upside down")
        );
        strangerthings.updateMetadata(stMetadata, "content_manager");
        
        // Simulate massive popularity
        for (int i = 0; i < 100000; i++) strangerthings.recordView();
        for (int i = 0; i < 85000; i++) strangerthings.recordCompletion(92.0);
        for (int i = 0; i < 20000; i++) strangerthings.addRating(5, "user" + i);
        for (int i = 0; i < 15000; i++) strangerthings.addRating(4, "user" + (20000 + i));
        
        repo.save(strangerthings);
        
        // Create recent Bollywood movie
        Content gullyboyMovie = new Content(ContentId.generate(), "Gully Boy", 
                                          ContentType.MOVIE, AgeRating.UA);
        gullyboyMovie.addGenre(Genre.DRAMA);
        gullyboyMovie.addGenre(Genre.ROMANCE);
        gullyboyMovie.addRegion(Region.INDIA);
        gullyboyMovie.addRegion(Region.UK);
        gullyboyMovie.addRegion(Region.US);
        gullyboyMovie.updateStatus(ContentStatus.RELEASED, "content_manager");
        gullyboyMovie.setReleaseDate(LocalDate.of(2019, 2, 14));
        
        ContentMetadata gullyMetadata = new ContentMetadata(
            153, // 2h 33m
            "Hindi",
            "Zoya Akhtar",
            "A coming-of-age story based on the lives of street rappers in Mumbai.",
            Arrays.asList("Ranveer Singh", "Alia Bhatt", "Siddhant Chaturvedi"),
            Arrays.asList("English", "Tamil", "Telugu"),
            Arrays.asList("rap", "mumbai", "slums", "music", "dreams")
        );
        gullyboyMovie.updateMetadata(gullyMetadata, "content_manager");
        
        for (int i = 0; i < 30000; i++) gullyboyMovie.recordView();
        for (int i = 0; i < 22000; i++) gullyboyMovie.recordCompletion(88.0);
        for (int i = 0; i < 8000; i++) gullyboyMovie.addRating(4, "user" + i);
        for (int i = 0; i < 5000; i++) gullyboyMovie.addRating(5, "user" + (8000 + i));
        
        repo.save(gullyboyMovie);
        
        System.out.println("✅ Sample content created successfully");
    }
    
    private static void testBasicQueries(ContentRepository repo) {
        // Test finding by status
        List<Content> releasedContent = repo.findByStatus(ContentStatus.RELEASED);
        System.out.println("Released content: " + releasedContent.size() + " items");
        
        // Test finding by type
        List<Content> movies = repo.findByType(ContentType.MOVIE);
        List<Content> series = repo.findByType(ContentType.TV_SERIES);
        System.out.println("Movies: " + movies.size() + ", TV Series: " + series.size());
        
        // Test finding by genre
        List<Content> dramas = repo.findByGenre(Genre.DRAMA);
        System.out.println("Drama content: " + dramas.size() + " items");
        
        // Test finding by region
        List<Content> indiaContent = repo.findByRegion(Region.INDIA);
        System.out.println("Content available in India: " + indiaContent.size() + " items");
        
        // Test search by title
        List<Content> gullyBoyResults = repo.findByTitleContaining("Gully");
        System.out.println("Search 'Gully': " + gullyBoyResults.size() + " results");
        
        // Test finding by language
        List<Content> hindiContent = repo.findByLanguage("Hindi");
        System.out.println("Hindi content: " + hindiContent.size() + " items");
    }
    
    private static void testAnalyticsQueries(ContentRepository repo) {
        // Most viewed content
        List<Content> mostViewed = repo.findMostViewed(3);
        System.out.println("\n🔥 Most Viewed Content:");
        for (int i = 0; i < mostViewed.size(); i++) {
            Content content = mostViewed.get(i);
            System.out.println("   " + (i+1) + ". " + content.getTitle() + " - " + 
                content.getViewCount() + " views");
        }
        
        // Highest rated content
        List<Content> highestRated = repo.findHighestRated(3);
        System.out.println("\n⭐ Highest Rated Content:");
        for (int i = 0; i < highestRated.size(); i++) {
            Content content = highestRated.get(i);
            System.out.println("   " + (i+1) + ". " + content.getTitle() + " - " + 
                String.format("%.1f⭐ (%d ratings)", 
                    content.getRating().getAverageRating(),
                    content.getRating().getTotalRatings()));
        }
        
        // Trending content
        List<Content> trending = repo.findTrendingContent();
        System.out.println("\n📈 Trending Content:");
        for (int i = 0; i < Math.min(3, trending.size()); i++) {
            Content content = trending.get(i);
            Map<String, Object> analytics = content.getAnalytics();
            System.out.println("   " + (i+1) + ". " + content.getTitle() + 
                " - " + analytics.get("viewCount") + " views, " +
                String.format("%.1f%% completion rate", 
                    (Double) analytics.get("completionRate") * 100));
        }
    }
    
    private static void testSpecificationPattern(ContentRepository repo) {
        // Popular content specification
        PopularContentSpecification popularSpec = new PopularContentSpecification();
        List<Content> popularContent = repo.findBySpecification(popularSpec);
        System.out.println("\n🌟 Popular Content (using specification): " + popularContent.size() + " items");
        
        // Family friendly specification
        FamilyFriendlySpecification familySpec = new FamilyFriendlySpecification();
        List<Content> familyContent = repo.findBySpecification(familySpec);
        System.out.println("👨‍👩‍👧‍👦 Family Friendly Content: " + familyContent.size() + " items");
        
        // Recent Hindi content specification
        RecentHindiContentSpecification hindiSpec = new RecentHindiContentSpecification();
        List<Content> recentHindi = repo.findBySpecification(hindiSpec);
        System.out.println("🇮🇳 Recent Hindi Content: " + recentHindi.size() + " items");
        
        // Show some examples
        if (!popularContent.isEmpty()) {
            System.out.println("\n   Popular content examples:");
            popularContent.stream().limit(2).forEach(content -> {
                System.out.println("   - " + content.getTitle() + " (" + 
                    content.getViewCount() + " views, " + 
                    String.format("%.1f⭐)", content.getRating().getAverageRating()));
            });
        }
    }
    
    private static void showRepositoryStatistics(ContentRepository repo) {
        InMemoryContentRepository inMemoryRepo = (InMemoryContentRepository) repo;
        
        // Content type statistics
        Map<ContentType, Long> typeStats = inMemoryRepo.getContentTypeStatistics();
        System.out.println("\n📊 Content Type Distribution:");
        typeStats.forEach((type, count) -> {
            System.out.println("   " + type.getDisplayName() + ": " + count);
        });
        
        // Status statistics  
        System.out.println("\n📈 Content Status:");
        for (ContentStatus status : ContentStatus.values()) {
            long count = inMemoryRepo.countByStatus(status);
            if (count > 0) {
                System.out.println("   " + status.getDisplayName() + ": " + count);
            }
        }
        
        // Total content
        List<Content> allContent = repo.findAll();
        System.out.println("\n📚 Total Content: " + allContent.size() + " items");
        
        // Calculate total views across all content
        long totalViews = allContent.stream().mapToLong(Content::getViewCount).sum();
        System.out.println("👀 Total Views: " + String.format("%,d", totalViews));
        
        // Average rating across all rated content
        OptionalDouble avgRating = allContent.stream()
            .filter(c -> c.getRating().getTotalRatings() > 0)
            .mapToDouble(c -> c.getRating().getAverageRating())
            .average();
        
        if (avgRating.isPresent()) {
            System.out.println("⭐ Average Rating: " + String.format("%.2f", avgRating.getAsDouble()));
        }
    }
}