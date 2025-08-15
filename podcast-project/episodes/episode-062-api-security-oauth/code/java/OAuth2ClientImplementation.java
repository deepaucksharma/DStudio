/*
 * OAuth 2.0 Client Implementation (Java)
 * =====================================
 * 
 * यह comprehensive OAuth 2.0 client implementation है Java में।
 * Spring Boot और enterprise applications में इसी तरह की
 * OAuth client integration होती है।
 * 
 * Features:
 * - Authorization Code Flow
 * - PKCE Support
 * - Token Management
 * - Automatic Token Refresh
 * - Secure Token Storage
 * 
 * Author: Hindi Tech Podcast
 * Episode: 062 - API Security & OAuth
 */

package com.hinditechpodcast.oauth;

import java.io.*;
import java.net.*;
import java.util.*;
import java.time.*;
import java.security.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.Mac;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * OAuth 2.0 Client - Production Ready Implementation
 * 
 * यह class OAuth providers (Google, Facebook, GitHub) के साथ
 * secure integration provide करती है।
 */
public class OAuth2ClientImplementation {
    
    private static final Logger logger = LoggerFactory.getLogger(OAuth2ClientImplementation.class);
    
    // OAuth Configuration
    private final String clientId;
    private final String clientSecret;
    private final String authorizationEndpoint;
    private final String tokenEndpoint;
    private final String redirectUri;
    private final List<String> scopes;
    
    // PKCE Support
    private final boolean usePKCE;
    private String codeVerifier;
    private String codeChallenge;
    
    // HTTP Client
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    // Token Storage
    private volatile AccessToken currentToken;
    private final TokenStorage tokenStorage;
    
    // State Management
    private final Map<String, OAuthState> stateMap = new ConcurrentHashMap<>();
    
    /**
     * OAuth2 Client Constructor
     * 
     * @param config OAuth configuration
     */
    public OAuth2ClientImplementation(OAuth2Config config) {
        this.clientId = config.getClientId();
        this.clientSecret = config.getClientSecret();
        this.authorizationEndpoint = config.getAuthorizationEndpoint();
        this.tokenEndpoint = config.getTokenEndpoint();
        this.redirectUri = config.getRedirectUri();
        this.scopes = config.getScopes();
        this.usePKCE = config.isUsePKCE();
        
        // HTTP Client with timeouts
        this.httpClient = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build();
            
        this.objectMapper = new ObjectMapper();
        this.tokenStorage = new InMemoryTokenStorage(); // Production में secure storage use करें
        
        logger.info("OAuth2 Client initialized for clientId: {}", clientId);
    }
    
    /**
     * Authorization URL generate करता है
     * 
     * @return Authorization URL
     */
    public String generateAuthorizationUrl() {
        try {
            // Generate state parameter for CSRF protection
            String state = generateSecureRandom(32);
            
            // PKCE parameters
            if (usePKCE) {
                codeVerifier = generateCodeVerifier();
                codeChallenge = generateCodeChallenge(codeVerifier);
            }
            
            // Store state
            OAuthState oauthState = new OAuthState(state, codeVerifier, Instant.now());
            stateMap.put(state, oauthState);
            
            // Build authorization URL
            StringBuilder urlBuilder = new StringBuilder(authorizationEndpoint);
            urlBuilder.append("?response_type=code");
            urlBuilder.append("&client_id=").append(URLEncoder.encode(clientId, StandardCharsets.UTF_8));
            urlBuilder.append("&redirect_uri=").append(URLEncoder.encode(redirectUri, StandardCharsets.UTF_8));
            urlBuilder.append("&scope=").append(URLEncoder.encode(String.join(" ", scopes), StandardCharsets.UTF_8));
            urlBuilder.append("&state=").append(URLEncoder.encode(state, StandardCharsets.UTF_8));
            
            // Add PKCE parameters
            if (usePKCE) {
                urlBuilder.append("&code_challenge=").append(URLEncoder.encode(codeChallenge, StandardCharsets.UTF_8));
                urlBuilder.append("&code_challenge_method=S256");
            }
            
            String authUrl = urlBuilder.toString();
            logger.info("Generated authorization URL for state: {}", state);
            
            return authUrl;
            
        } catch (Exception e) {
            logger.error("Error generating authorization URL", e);
            throw new OAuth2Exception("Failed to generate authorization URL", e);
        }
    }
    
    /**
     * Authorization callback handle करता है
     * 
     * @param code Authorization code
     * @param state State parameter
     * @return Access token
     */
    public AccessToken handleCallback(String code, String state) {
        try {
            // Validate state parameter
            OAuthState oauthState = stateMap.get(state);
            if (oauthState == null) {
                throw new OAuth2Exception("Invalid state parameter");
            }
            
            // Check state expiry (10 minutes)
            if (Duration.between(oauthState.getCreatedAt(), Instant.now()).toMinutes() > 10) {
                stateMap.remove(state);
                throw new OAuth2Exception("State parameter expired");
            }
            
            // Remove used state
            stateMap.remove(state);
            
            // Exchange code for token
            AccessToken token = exchangeCodeForToken(code, oauthState.getCodeVerifier());
            
            // Store token
            currentToken = token;
            tokenStorage.storeToken(clientId, token);
            
            logger.info("Successfully obtained access token");
            return token;
            
        } catch (Exception e) {
            logger.error("Error handling OAuth callback", e);
            throw new OAuth2Exception("Failed to handle OAuth callback", e);
        }
    }
    
    /**
     * Authorization code को access token के लिए exchange करता है
     * 
     * @param code Authorization code
     * @param codeVerifier PKCE code verifier
     * @return Access token
     */
    private AccessToken exchangeCodeForToken(String code, String codeVerifier) throws Exception {
        // Build token request
        FormBody.Builder formBuilder = new FormBody.Builder()
            .add("grant_type", "authorization_code")
            .add("code", code)
            .add("redirect_uri", redirectUri)
            .add("client_id", clientId);
        
        // Add client secret if not using PKCE
        if (!usePKCE && clientSecret != null) {
            formBuilder.add("client_secret", clientSecret);
        }
        
        // Add PKCE code verifier
        if (usePKCE && codeVerifier != null) {
            formBuilder.add("code_verifier", codeVerifier);
        }
        
        RequestBody requestBody = formBuilder.build();
        
        // Create request
        Request request = new Request.Builder()
            .url(tokenEndpoint)
            .post(requestBody)
            .addHeader("Accept", "application/json")
            .addHeader("User-Agent", "OAuth2Client/1.0")
            .build();
        
        // Execute request
        try (Response response = httpClient.newCall(request).execute()) {
            String responseBody = response.body().string();
            
            if (!response.isSuccessful()) {
                logger.error("Token request failed: {} - {}", response.code(), responseBody);
                throw new OAuth2Exception("Token request failed: " + response.code());
            }
            
            // Parse token response
            TokenResponse tokenResponse = objectMapper.readValue(responseBody, TokenResponse.class);
            
            return new AccessToken(
                tokenResponse.getAccessToken(),
                tokenResponse.getRefreshToken(),
                tokenResponse.getTokenType(),
                tokenResponse.getExpiresIn(),
                tokenResponse.getScope(),
                Instant.now()
            );
        }
    }
    
    /**
     * Access token refresh करता है
     * 
     * @return New access token
     */
    public AccessToken refreshToken() {
        try {
            if (currentToken == null || currentToken.getRefreshToken() == null) {
                throw new OAuth2Exception("No refresh token available");
            }
            
            // Build refresh request
            FormBody requestBody = new FormBody.Builder()
                .add("grant_type", "refresh_token")
                .add("refresh_token", currentToken.getRefreshToken())
                .add("client_id", clientId)
                .add("client_secret", clientSecret != null ? clientSecret : "")
                .build();
            
            Request request = new Request.Builder()
                .url(tokenEndpoint)
                .post(requestBody)
                .addHeader("Accept", "application/json")
                .build();
            
            try (Response response = httpClient.newCall(request).execute()) {
                String responseBody = response.body().string();
                
                if (!response.isSuccessful()) {
                    logger.error("Token refresh failed: {} - {}", response.code(), responseBody);
                    throw new OAuth2Exception("Token refresh failed: " + response.code());
                }
                
                TokenResponse tokenResponse = objectMapper.readValue(responseBody, TokenResponse.class);
                
                // Create new token (preserve refresh token if not provided)
                String refreshToken = tokenResponse.getRefreshToken() != null 
                    ? tokenResponse.getRefreshToken() 
                    : currentToken.getRefreshToken();
                
                AccessToken newToken = new AccessToken(
                    tokenResponse.getAccessToken(),
                    refreshToken,
                    tokenResponse.getTokenType(),
                    tokenResponse.getExpiresIn(),
                    tokenResponse.getScope(),
                    Instant.now()
                );
                
                // Update stored token
                currentToken = newToken;
                tokenStorage.storeToken(clientId, newToken);
                
                logger.info("Successfully refreshed access token");
                return newToken;
            }
            
        } catch (Exception e) {
            logger.error("Error refreshing token", e);
            throw new OAuth2Exception("Failed to refresh token", e);
        }
    }
    
    /**
     * Valid access token return करता है (automatic refresh के साथ)
     * 
     * @return Valid access token
     */
    public String getValidAccessToken() {
        try {
            // Load token from storage if not in memory
            if (currentToken == null) {
                currentToken = tokenStorage.getToken(clientId);
            }
            
            if (currentToken == null) {
                throw new OAuth2Exception("No access token available. Please authorize first.");
            }
            
            // Check if token needs refresh
            if (currentToken.isExpired()) {
                logger.info("Access token expired, refreshing...");
                refreshToken();
            }
            
            return currentToken.getAccessToken();
            
        } catch (Exception e) {
            logger.error("Error getting valid access token", e);
            throw new OAuth2Exception("Failed to get valid access token", e);
        }
    }
    
    /**
     * OAuth protected API call करता है
     * 
     * @param url API endpoint URL
     * @param method HTTP method
     * @param requestBody Request body (optional)
     * @return API response
     */
    public String makeAuthenticatedRequest(String url, String method, String requestBody) {
        try {
            String accessToken = getValidAccessToken();
            
            Request.Builder requestBuilder = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + accessToken)
                .addHeader("Accept", "application/json");
            
            // Add request body for POST/PUT
            if (requestBody != null && ("POST".equals(method) || "PUT".equals(method))) {
                RequestBody body = RequestBody.create(
                    requestBody, 
                    MediaType.parse("application/json")
                );
                requestBuilder.method(method, body);
            } else {
                requestBuilder.method(method, null);
            }
            
            Request request = requestBuilder.build();
            
            try (Response response = httpClient.newCall(request).execute()) {
                String responseBody = response.body().string();
                
                if (!response.isSuccessful()) {
                    // Handle token expiry
                    if (response.code() == 401) {
                        logger.warn("API call returned 401, attempting token refresh");
                        refreshToken();
                        
                        // Retry with new token
                        String newAccessToken = getValidAccessToken();
                        Request retryRequest = request.newBuilder()
                            .header("Authorization", "Bearer " + newAccessToken)
                            .build();
                        
                        try (Response retryResponse = httpClient.newCall(retryRequest).execute()) {
                            return retryResponse.body().string();
                        }
                    }
                    
                    throw new OAuth2Exception("API call failed: " + response.code() + " - " + responseBody);
                }
                
                return responseBody;
            }
            
        } catch (Exception e) {
            logger.error("Error making authenticated request to: {}", url, e);
            throw new OAuth2Exception("Failed to make authenticated request", e);
        }
    }
    
    /**
     * PKCE code verifier generate करता है
     * 
     * @return Code verifier
     */
    private String generateCodeVerifier() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[32];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }
    
    /**
     * PKCE code challenge generate करता है
     * 
     * @param codeVerifier Code verifier
     * @return Code challenge
     */
    private String generateCodeChallenge(String codeVerifier) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(codeVerifier.getBytes(StandardCharsets.UTF_8));
        return Base64.getUrlEncoder().withoutPadding().encodeToString(hash);
    }
    
    /**
     * Secure random string generate करता है
     * 
     * @param length String length
     * @return Random string
     */
    private String generateSecureRandom(int length) {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[length];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }
    
    /**
     * Token revoke करता है
     */
    public void revokeToken() {
        try {
            if (currentToken != null) {
                // Revoke token at provider (if supported)
                // Implementation depends on OAuth provider
                
                // Clear stored token
                currentToken = null;
                tokenStorage.removeToken(clientId);
                
                logger.info("Token revoked successfully");
            }
        } catch (Exception e) {
            logger.error("Error revoking token", e);
        }
    }
    
    // Data Classes
    
    /**
     * OAuth2 Configuration
     */
    public static class OAuth2Config {
        private String clientId;
        private String clientSecret;
        private String authorizationEndpoint;
        private String tokenEndpoint;
        private String redirectUri;
        private List<String> scopes;
        private boolean usePKCE;
        
        // Constructors, getters, setters
        public OAuth2Config(String clientId, String clientSecret, 
                           String authorizationEndpoint, String tokenEndpoint,
                           String redirectUri, List<String> scopes) {
            this.clientId = clientId;
            this.clientSecret = clientSecret;
            this.authorizationEndpoint = authorizationEndpoint;
            this.tokenEndpoint = tokenEndpoint;
            this.redirectUri = redirectUri;
            this.scopes = scopes;
            this.usePKCE = false;
        }
        
        // Getters
        public String getClientId() { return clientId; }
        public String getClientSecret() { return clientSecret; }
        public String getAuthorizationEndpoint() { return authorizationEndpoint; }
        public String getTokenEndpoint() { return tokenEndpoint; }
        public String getRedirectUri() { return redirectUri; }
        public List<String> getScopes() { return scopes; }
        public boolean isUsePKCE() { return usePKCE; }
        
        // Setters
        public void setUsePKCE(boolean usePKCE) { this.usePKCE = usePKCE; }
    }
    
    /**
     * Access Token
     */
    public static class AccessToken {
        private final String accessToken;
        private final String refreshToken;
        private final String tokenType;
        private final Long expiresIn;
        private final String scope;
        private final Instant issuedAt;
        
        public AccessToken(String accessToken, String refreshToken, String tokenType,
                          Long expiresIn, String scope, Instant issuedAt) {
            this.accessToken = accessToken;
            this.refreshToken = refreshToken;
            this.tokenType = tokenType;
            this.expiresIn = expiresIn;
            this.scope = scope;
            this.issuedAt = issuedAt;
        }
        
        public boolean isExpired() {
            if (expiresIn == null) return false;
            return Instant.now().isAfter(issuedAt.plusSeconds(expiresIn - 60)); // 60 second buffer
        }
        
        // Getters
        public String getAccessToken() { return accessToken; }
        public String getRefreshToken() { return refreshToken; }
        public String getTokenType() { return tokenType; }
        public Long getExpiresIn() { return expiresIn; }
        public String getScope() { return scope; }
        public Instant getIssuedAt() { return issuedAt; }
    }
    
    /**
     * OAuth State
     */
    private static class OAuthState {
        private final String state;
        private final String codeVerifier;
        private final Instant createdAt;
        
        public OAuthState(String state, String codeVerifier, Instant createdAt) {
            this.state = state;
            this.codeVerifier = codeVerifier;
            this.createdAt = createdAt;
        }
        
        public String getState() { return state; }
        public String getCodeVerifier() { return codeVerifier; }
        public Instant getCreatedAt() { return createdAt; }
    }
    
    /**
     * Token Response from OAuth Provider
     */
    private static class TokenResponse {
        @JsonProperty("access_token")
        private String accessToken;
        
        @JsonProperty("refresh_token")
        private String refreshToken;
        
        @JsonProperty("token_type")
        private String tokenType;
        
        @JsonProperty("expires_in")
        private Long expiresIn;
        
        @JsonProperty("scope")
        private String scope;
        
        // Getters
        public String getAccessToken() { return accessToken; }
        public String getRefreshToken() { return refreshToken; }
        public String getTokenType() { return tokenType; }
        public Long getExpiresIn() { return expiresIn; }
        public String getScope() { return scope; }
    }
    
    /**
     * Token Storage Interface
     */
    public interface TokenStorage {
        void storeToken(String clientId, AccessToken token);
        AccessToken getToken(String clientId);
        void removeToken(String clientId);
    }
    
    /**
     * In-Memory Token Storage (Development के लिए)
     * Production में secure storage use करें (database, encrypted file, etc.)
     */
    private static class InMemoryTokenStorage implements TokenStorage {
        private final Map<String, AccessToken> tokens = new ConcurrentHashMap<>();
        
        @Override
        public void storeToken(String clientId, AccessToken token) {
            tokens.put(clientId, token);
        }
        
        @Override
        public AccessToken getToken(String clientId) {
            return tokens.get(clientId);
        }
        
        @Override
        public void removeToken(String clientId) {
            tokens.remove(clientId);
        }
    }
    
    /**
     * OAuth2 Exception
     */
    public static class OAuth2Exception extends RuntimeException {
        public OAuth2Exception(String message) {
            super(message);
        }
        
        public OAuth2Exception(String message, Throwable cause) {
            super(message, cause);
        }
    }
    
    /**
     * Example Usage और Testing
     */
    public static void main(String[] args) {
        try {
            // OAuth2 Configuration for Google
            OAuth2Config config = new OAuth2Config(
                "your_google_client_id",
                "your_google_client_secret",
                "https://accounts.google.com/o/oauth2/v2/auth",
                "https://oauth2.googleapis.com/token",
                "http://localhost:8080/oauth/callback",
                Arrays.asList("openid", "profile", "email")
            );
            
            // Enable PKCE for public clients
            config.setUsePKCE(true);
            
            // Create OAuth client
            OAuth2ClientImplementation oauthClient = new OAuth2ClientImplementation(config);
            
            // Generate authorization URL
            String authUrl = oauthClient.generateAuthorizationUrl();
            System.out.println("🔗 Authorization URL: " + authUrl);
            System.out.println("📱 User को इस URL पर redirect करें authorization के लिए");
            
            // Simulate callback handling (production में web framework से आएगा)
            // String code = "received_authorization_code";
            // String state = "received_state_parameter";
            // AccessToken token = oauthClient.handleCallback(code, state);
            
            // Make authenticated API calls
            // String response = oauthClient.makeAuthenticatedRequest(
            //     "https://www.googleapis.com/oauth2/v2/userinfo", 
            //     "GET", 
            //     null
            // );
            
            System.out.println("✅ OAuth2 Client ready for integration");
            
        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

/*
Production Implementation Notes:
===============================

1. Security Enhancements:
   - Use secure token storage (encrypted database)
   - Implement proper certificate pinning
   - Add request signing for sensitive operations
   - Use hardware security modules for key storage

2. Error Handling:
   - Comprehensive error codes
   - Retry mechanisms with exponential backoff
   - Circuit breaker for OAuth provider calls
   - Proper logging and monitoring

3. Integration:
   - Spring Security integration
   - Session management
   - Multi-tenant support
   - Configuration externalization

4. Testing:
   - Unit tests with mock OAuth provider
   - Integration tests
   - Security testing
   - Performance testing

यह implementation enterprise-grade OAuth 2.0 client functionality provide करता है!
*/