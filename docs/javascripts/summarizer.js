// Hugging Face Summarizer for MkDocs
// Uses the free Hugging Face Inference API

// Configuration
const HF_API_URL = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn';
const MAX_INPUT_LENGTH = 1000; // Slightly reduced to be safe
const RATE_LIMIT_DELAY = 1000;

// Global state
let isProcessing = false;
let chatWindow = null;
let isInitialized = false;

// Initialize the summarizer
function initializeSummarizer() {
    if (isInitialized) return;
    
    createChatUI();
    setupEventListeners();
    console.log('Page Summarizer initialized');
    isInitialized = true;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add delay to ensure page is fully loaded
    setTimeout(initializeSummarizer, 500);
});

// Handle MkDocs Material navigation events (for SPA-like behavior)
document.addEventListener('DOMContentLoaded', function() {
    // Listen for MkDocs Material navigation events
    if (typeof location$ !== 'undefined') {
        // MkDocs Material rx.js observable
        location$.subscribe(function() {
            setTimeout(initializeSummarizer, 100);
        });
    }
    
    // Fallback: listen for navigation changes
    let currentUrl = window.location.href;
    const observer = new MutationObserver(function() {
        if (window.location.href !== currentUrl) {
            currentUrl = window.location.href;
            setTimeout(initializeSummarizer, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Also initialize on page load and navigation
window.addEventListener('load', initializeSummarizer);
window.addEventListener('popstate', function() {
    setTimeout(initializeSummarizer, 100);
});

// Create the chat window UI
function createChatUI() {
    // Check if already exists
    if (document.getElementById('summarizer-chat')) return;
    
    // Create chat window container
    const chatHTML = `
        <div id="summarizer-chat" class="summarizer-chat" style="display: none;">
            <div class="chat-header">
                <h4>📄 Page Summarizer</h4>
                <button class="chat-close">&times;</button>
            </div>
            <div class="chat-content">
                <div id="summary-output" class="summary-output">
                    <p>Click "Summarize" to generate an AI summary of this page.</p>
                    <div class="summary-info">
                        <small>🤖 Powered by Hugging Face BART model (free tier)</small>
                    </div>
                </div>
                <div class="chat-controls">
                    <button id="summarize-btn" class="summarize-btn">
                        <span class="btn-text">Summarize This Page</span>
                        <span class="btn-spinner" style="display: none;">⏳ Processing...</span>
                    </button>
                    <div class="chat-tips">
                        <small>💡 <a href="https://huggingface.co/join" target="_blank">Sign in to HuggingFace</a> for better rate limits</small>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Floating button to open chat -->
        <button id="summarizer-toggle" class="summarizer-toggle" title="AI Page Summarizer">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
            <span class="toggle-tooltip">AI Summarizer</span>
        </button>
    `;
    
    // Inject into body
    document.body.insertAdjacentHTML('beforeend', chatHTML);
    chatWindow = document.getElementById('summarizer-chat');
    
    // Add event listeners
    const toggleBtn = document.getElementById('summarizer-toggle');
    const closeBtn = document.querySelector('.chat-close');
    const summarizeBtn = document.getElementById('summarize-btn');
    
    if (toggleBtn) toggleBtn.addEventListener('click', openSummarizer);
    if (closeBtn) closeBtn.addEventListener('click', closeSummarizer);
    if (summarizeBtn) summarizeBtn.addEventListener('click', summarizePage);
    
    // Add styles
    injectStyles();
}

// Setup event listeners
function setupEventListeners() {
    // Close on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatWindow && chatWindow.style.display !== 'none') {
            closeSummarizer();
        }
    });
}

// Open the summarizer chat window
function openSummarizer() {
    if (chatWindow) {
        chatWindow.style.display = 'block';
        const toggleBtn = document.getElementById('summarizer-toggle');
        if (toggleBtn) toggleBtn.style.display = 'none';
    }
}

// Close the summarizer chat window
function closeSummarizer() {
    if (chatWindow) {
        chatWindow.style.display = 'none';
        const toggleBtn = document.getElementById('summarizer-toggle');
        if (toggleBtn) toggleBtn.style.display = 'block';
    }
}

// Extract meaningful text from the current page
function extractPageContent() {
    // Try different content selectors for MkDocs Material theme
    const contentSelectors = [
        'article.md-content__inner',
        '.md-content article',
        '.md-content__inner',
        '.md-content',
        '[role="main"]',
        'main',
        'article'
    ];
    
    let content = '';
    for (const selector of contentSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            // Get text content, remove extra whitespace
            content = element.innerText
                .replace(/\s+/g, ' ')
                .replace(/\n+/g, ' ')
                .trim();
            break;
        }
    }
    
    // Fallback to body if nothing found
    if (!content || content.length < 100) {
        content = document.body.innerText
            .replace(/\s+/g, ' ')
            .replace(/\n+/g, ' ')
            .trim();
    }
    
    // Remove navigation and UI elements
    content = content
        .replace(/Search.*?Results/g, '')
        .replace(/Navigation.*?Toggle/g, '')
        .replace(/Edit.*?Page/g, '')
        .replace(/Summarize.*?Page/g, '')
        .trim();
    
    // Get page title
    const title = document.querySelector('h1')?.innerText || 
                  document.querySelector('.md-content h1')?.innerText || 
                  document.title.replace(' - The Compendium of Distributed Systems', '');
    
    // Combine title and content
    let fullText = content;
    if (title && !content.startsWith(title)) {
        fullText = `${title}: ${content}`;
    }
    
    // Truncate if too long
    if (fullText.length > MAX_INPUT_LENGTH) {
        fullText = fullText.substring(0, MAX_INPUT_LENGTH) + '...';
    }
    
    return fullText;
}

// Call Hugging Face API
async function callHuggingFaceAPI(text) {
    try {
        console.log('Calling Hugging Face API with text length:', text.length);
        
        const response = await fetch(HF_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                inputs: text,
                parameters: {
                    max_length: 130,
                    min_length: 30,
                    do_sample: false
                }
            })
        });
        
        console.log('API Response status:', response.status);
        
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { error: `HTTP ${response.status}` };
            }
            throw new Error(errorData.error || `API Error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('API Result:', result);
        
        if (Array.isArray(result) && result[0]?.summary_text) {
            return result[0].summary_text;
        } else if (result.summary_text) {
            return result.summary_text;
        } else if (result.error) {
            throw new Error(result.error);
        } else {
            throw new Error('No summary generated - unexpected response format');
        }
        
    } catch (error) {
        console.error('Summarization error:', error);
        throw error;
    }
}

// Main summarization function
async function summarizePage() {
    if (isProcessing) return;
    
    isProcessing = true;
    const outputDiv = document.getElementById('summary-output');
    const btnText = document.querySelector('.btn-text');
    const btnSpinner = document.querySelector('.btn-spinner');
    
    if (!outputDiv) {
        console.error('Summary output div not found');
        isProcessing = false;
        return;
    }
    
    // Show loading state
    if (btnText) btnText.style.display = 'none';
    if (btnSpinner) btnSpinner.style.display = 'inline';
    outputDiv.innerHTML = '<p class="loading">📝 Extracting page content...</p>';
    
    try {
        // Extract page content
        const pageContent = extractPageContent();
        console.log('Extracted content length:', pageContent.length);
        console.log('Content preview:', pageContent.substring(0, 200) + '...');
        
        if (!pageContent || pageContent.length < 50) {
            throw new Error('Not enough content to summarize (minimum 50 characters required)');
        }
        
        outputDiv.innerHTML = '<p class="loading">🤖 Generating AI summary via Hugging Face...</p>';
        
        // Call API with retry logic
        let summary;
        let attempts = 0;
        const maxAttempts = 3;
        
        while (attempts < maxAttempts) {
            try {
                summary = await callHuggingFaceAPI(pageContent);
                break;
            } catch (error) {
                attempts++;
                if (error.message.includes('loading') && attempts < maxAttempts) {
                    outputDiv.innerHTML = `<p class="loading">⏳ AI model loading, retrying... (${attempts}/${maxAttempts})</p>`;
                    await new Promise(resolve => setTimeout(resolve, 15000)); // Wait 15 seconds
                } else {
                    throw error;
                }
            }
        }
        
        // Display result
        outputDiv.innerHTML = `
            <div class="summary-result">
                <h5>🧠 AI Summary:</h5>
                <p class="summary-text">${summary}</p>
                <div class="summary-meta">
                    <small>✨ Generated from ${pageContent.length} chars using Hugging Face BART</small>
                    <br><small>🔄 <button class="regenerate-btn" onclick="summarizePage()">Regenerate</button></small>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Summary generation failed:', error);
        
        // Handle specific errors
        let errorMessage = 'Failed to generate summary';
        
        if (error.message.includes('rate limit') || error.message.includes('429')) {
            errorMessage = '⏱️ Rate limit reached. Please wait or <a href="https://huggingface.co/join" target="_blank">sign in to HuggingFace</a> for better limits.';
        } else if (error.message.includes('Not enough content')) {
            errorMessage = '📄 This page doesn\'t have enough content to summarize.';
        } else if (error.message.includes('loading')) {
            errorMessage = '⏳ AI model is loading. Please try again in 30 seconds.';
        } else if (error.message.includes('503') || error.message.includes('500')) {
            errorMessage = '🔧 AI service temporarily unavailable. Please try again later.';
        } else if (error.message.includes('CORS')) {
            errorMessage = '🌐 Network error. Please check your connection and try again.';
        }
        
        outputDiv.innerHTML = `
            <div class="summary-error">
                <p>❌ ${errorMessage}</p>
                <div class="error-details">
                    <small>Technical: ${error.message}</small>
                    <br><small>🔄 <button class="retry-btn" onclick="summarizePage()">Try Again</button></small>
                </div>
            </div>
        `;
    } finally {
        // Reset button state
        if (btnText) btnText.style.display = 'inline';
        if (btnSpinner) btnSpinner.style.display = 'none';
        isProcessing = false;
    }
}

// Inject CSS styles
function injectStyles() {
    if (document.getElementById('summarizer-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'summarizer-styles';
    styles.textContent = `
    .summarizer-chat {
        position: fixed;
        right: 20px;
        top: 100px;
        width: 400px;
        max-width: calc(100vw - 40px);
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        z-index: 10000;
        font-family: var(--md-text-font, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
        border: 1px solid #e0e0e0;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @media (max-width: 768px) {
        .summarizer-chat {
            right: 10px;
            top: 70px;
            width: calc(100vw - 20px);
        }
    }
    
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 24px;
        border-bottom: 1px solid #e0e0e0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px 16px 0 0;
    }
    
    .chat-header h4 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }
    
    .chat-close {
        background: none;
        border: none;
        font-size: 28px;
        cursor: pointer;
        color: rgba(255,255,255,0.8);
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    .chat-close:hover {
        background: rgba(255,255,255,0.2);
        color: white;
    }
    
    .chat-content {
        padding: 24px;
    }
    
    .summary-output {
        min-height: 140px;
        margin-bottom: 18px;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        max-height: 350px;
        overflow-y: auto;
    }
    
    .summary-info {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e0e0e0;
        color: #666;
    }
    
    .summary-output p {
        margin: 0 0 8px 0;
        line-height: 1.6;
        color: #333;
    }
    
    .summary-result h5 {
        margin: 0 0 16px 0;
        color: #667eea;
        font-size: 17px;
        font-weight: 600;
    }
    
    .summary-text {
        font-size: 15px;
        line-height: 1.7;
        color: #2c3e50;
        margin-bottom: 16px !important;
    }
    
    .summary-meta {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #e0e0e0;
        color: #666;
        font-size: 12px;
    }
    
    .regenerate-btn, .retry-btn {
        background: none;
        border: 1px solid #667eea;
        color: #667eea;
        padding: 4px 8px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 11px;
        transition: all 0.2s;
    }
    
    .regenerate-btn:hover, .retry-btn:hover {
        background: #667eea;
        color: white;
    }
    
    .loading {
        color: #667eea;
        font-style: italic;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .summary-error {
        color: #d32f2f;
    }
    
    .summary-error a {
        color: #1976d2;
    }
    
    .error-details {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #ffcdd2;
        font-size: 12px;
    }
    
    .chat-controls {
        display: flex;
        flex-direction: column;
        gap: 14px;
    }
    
    .summarize-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .summarize-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    .summarize-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    
    .chat-tips {
        text-align: center;
        color: #666;
        font-size: 13px;
    }
    
    .chat-tips a {
        color: #667eea;
        text-decoration: none;
    }
    
    .chat-tips a:hover {
        text-decoration: underline;
    }
    
    .summarizer-toggle {
        position: fixed;
        right: 20px;
        bottom: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    
    .summarizer-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
    }
    
    .summarizer-toggle:hover .toggle-tooltip {
        opacity: 1;
        transform: translateX(-10px);
    }
    
    .toggle-tooltip {
        position: absolute;
        right: 100%;
        white-space: nowrap;
        background: #333;
        color: white;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        opacity: 0;
        transition: all 0.3s;
        pointer-events: none;
        margin-right: 15px;
    }
    
    .toggle-tooltip::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 100%;
        transform: translateY(-50%);
        border: 8px solid transparent;
        border-left-color: #333;
    }
    
    /* Dark mode support */
    [data-md-color-scheme="slate"] .summarizer-chat {
        background: #1e1e1e;
        color: #fff;
        border-color: #444;
    }
    
    [data-md-color-scheme="slate"] .summary-output {
        background: #2d2d30;
        border-color: #444;
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-output p {
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-text {
        color: #e8e8e8;
    }
    
    [data-md-color-scheme="slate"] .summary-meta {
        color: #aaa;
        border-top-color: #444;
    }
    
    [data-md-color-scheme="slate"] .summary-info {
        border-top-color: #444;
    }
    `;
    
    document.head.appendChild(styles);
}

// Export functions for global access
window.openSummarizer = openSummarizer;
window.closeSummarizer = closeSummarizer;
window.summarizePage = summarizePage;