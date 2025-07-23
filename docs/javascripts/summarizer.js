// Hugging Face Summarizer for MkDocs Material
// Uses the free Hugging Face Inference API

// Configuration
const HF_API_URL = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn';
const MAX_INPUT_LENGTH = 1000;
const RATE_LIMIT_DELAY = 1000;

// Global state
let isProcessing = false;
let chatWindow = null;

// Initialize the summarizer using MkDocs Material's document$ observable
document$.subscribe(function() {
    console.log("Initializing Page Summarizer for:", window.location.pathname);
    initializeSummarizer();
});

// Main initialization function
function initializeSummarizer() {
    // Remove existing elements if they exist (prevents duplicates)
    const existingChat = document.getElementById('summarizer-chat');
    const existingToggle = document.getElementById('summarizer-toggle');
    
    if (existingChat) existingChat.remove();
    if (existingToggle) existingToggle.remove();
    
    // Create the UI elements
    createChatUI();
    setupEventListeners();
}

// Create the chat window UI
function createChatUI() {
    // Create chat window container
    const chatHTML = `
        <div id="summarizer-chat" class="summarizer-chat" style="display: none;">
            <div class="chat-header">
                <h4>🤖 AI Page Summarizer</h4>
                <button class="chat-close" aria-label="Close summarizer">&times;</button>
            </div>
            <div class="chat-content">
                <div id="summary-output" class="summary-output">
                    <p>Click "Summarize" to generate an AI summary of this page.</p>
                    <div class="summary-info">
                        <small>⚡ Powered by Hugging Face BART model (free tier)</small>
                    </div>
                </div>
                <div class="chat-controls">
                    <button id="summarize-btn" class="summarize-btn" type="button">
                        <span class="btn-text">📝 Summarize This Page</span>
                        <span class="btn-spinner" style="display: none;">⏳ Processing...</span>
                    </button>
                    <div class="chat-tips">
                        <small>💡 <a href="https://huggingface.co/join" target="_blank" rel="noopener">Sign in to HuggingFace</a> for better rate limits</small>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Floating button to open chat -->
        <button id="summarizer-toggle" class="summarizer-toggle" title="AI Page Summarizer" type="button">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <span class="toggle-tooltip">AI Summarizer</span>
        </button>
    `;
    
    // Inject into body
    document.body.insertAdjacentHTML('beforeend', chatHTML);
    chatWindow = document.getElementById('summarizer-chat');
    
    // Add event listeners with proper cleanup
    setupUIEventListeners();
    
    // Add styles
    injectStyles();
}

// Setup UI event listeners
function setupUIEventListeners() {
    const toggleBtn = document.getElementById('summarizer-toggle');
    const closeBtn = document.querySelector('#summarizer-chat .chat-close');
    const summarizeBtn = document.getElementById('summarize-btn');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', openSummarizer);
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeSummarizer);
    }
    
    if (summarizeBtn) {
        summarizeBtn.addEventListener('click', summarizePage);
    }
}

// Setup global event listeners
function setupEventListeners() {
    // Close on ESC key (only setup once)
    if (!window.summarizerEscListenerAdded) {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && chatWindow && chatWindow.style.display !== 'none') {
                closeSummarizer();
            }
        });
        window.summarizerEscListenerAdded = true;
    }
}

// Open the summarizer chat window
function openSummarizer() {
    if (chatWindow) {
        chatWindow.style.display = 'block';
        chatWindow.setAttribute('aria-hidden', 'false');
        
        const toggleBtn = document.getElementById('summarizer-toggle');
        if (toggleBtn) {
            toggleBtn.style.display = 'none';
            toggleBtn.setAttribute('aria-hidden', 'true');
        }
        
        // Focus management for accessibility
        const summarizeBtn = document.getElementById('summarize-btn');
        if (summarizeBtn) {
            summarizeBtn.focus();
        }
    }
}

// Close the summarizer chat window
function closeSummarizer() {
    if (chatWindow) {
        chatWindow.style.display = 'none';
        chatWindow.setAttribute('aria-hidden', 'true');
        
        const toggleBtn = document.getElementById('summarizer-toggle');
        if (toggleBtn) {
            toggleBtn.style.display = 'block';
            toggleBtn.setAttribute('aria-hidden', 'false');
            toggleBtn.focus(); // Return focus to toggle button
        }
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
    let element = null;
    
    // Find the main content element
    for (const selector of contentSelectors) {
        element = document.querySelector(selector);
        if (element) {
            break;
        }
    }
    
    if (element) {
        // Clone the element to avoid modifying the original
        const clonedElement = element.cloneNode(true);
        
        // Remove unwanted elements
        const unwantedSelectors = [
            '.md-source',
            '.md-nav',
            '.md-sidebar',
            '.md-header',
            '.md-footer',
            '.summarizer-chat',
            '.summarizer-toggle',
            '[role="navigation"]',
            'nav',
            'aside'
        ];
        
        unwantedSelectors.forEach(selector => {
            const unwantedElements = clonedElement.querySelectorAll(selector);
            unwantedElements.forEach(el => el.remove());
        });
        
        // Get clean text content
        content = clonedElement.innerText
            .replace(/\s+/g, ' ')
            .replace(/\n+/g, ' ')
            .trim();
    }
    
    // Fallback to body if nothing found
    if (!content || content.length < 100) {
        content = document.body.innerText
            .replace(/\s+/g, ' ')
            .replace(/\n+/g, ' ')
            .trim();
    }
    
    // Get page title
    const title = document.querySelector('h1')?.innerText || 
                  document.querySelector('.md-content h1')?.innerText || 
                  document.title.replace(' - The Compendium of Distributed Systems', '');
    
    // Combine title and content
    let fullText = content;
    if (title && !content.toLowerCase().includes(title.toLowerCase())) {
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
    const summarizeBtn = document.getElementById('summarize-btn');
    
    if (!outputDiv) {
        console.error('Summary output div not found');
        isProcessing = false;
        return;
    }
    
    // Show loading state
    if (btnText) btnText.style.display = 'none';
    if (btnSpinner) btnSpinner.style.display = 'inline';
    if (summarizeBtn) summarizeBtn.disabled = true;
    
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
                    <br><small>🔄 <button class="regenerate-btn" onclick="summarizePage()" type="button">Regenerate</button></small>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Summary generation failed:', error);
        
        // Handle specific errors
        let errorMessage = 'Failed to generate summary';
        
        if (error.message.includes('rate limit') || error.message.includes('429')) {
            errorMessage = '⏱️ Rate limit reached. Please wait or <a href="https://huggingface.co/join" target="_blank" rel="noopener">sign in to HuggingFace</a> for better limits.';
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
                    <br><small>🔄 <button class="retry-btn" onclick="summarizePage()" type="button">Try Again</button></small>
                </div>
            </div>
        `;
    } finally {
        // Reset button state
        if (btnText) btnText.style.display = 'inline';
        if (btnSpinner) btnSpinner.style.display = 'none';
        if (summarizeBtn) summarizeBtn.disabled = false;
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
        width: 420px;
        max-width: calc(100vw - 40px);
        background: white;
        border-radius: 16px;
        box-shadow: 0 12px 48px rgba(0,0,0,0.15);
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
            max-height: calc(100vh - 100px);
        }
    }
    
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 24px;
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
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .chat-close:hover, .chat-close:focus {
        background: rgba(255,255,255,0.2);
        color: white;
        outline: none;
    }
    
    .chat-content {
        padding: 24px;
    }
    
    .summary-output {
        min-height: 160px;
        margin-bottom: 20px;
        padding: 24px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .summary-info {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #dee2e6;
        color: #6c757d;
        font-size: 12px;
    }
    
    .summary-output p {
        margin: 0 0 12px 0;
        line-height: 1.6;
        color: #343a40;
    }
    
    .summary-result h5 {
        margin: 0 0 18px 0;
        color: #667eea;
        font-size: 18px;
        font-weight: 600;
    }
    
    .summary-text {
        font-size: 16px;
        line-height: 1.7;
        color: #2c3e50;
        margin-bottom: 18px !important;
        font-weight: 400;
    }
    
    .summary-meta {
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #dee2e6;
        color: #6c757d;
        font-size: 12px;
    }
    
    .regenerate-btn, .retry-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 11px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .regenerate-btn:hover, .retry-btn:hover, .regenerate-btn:focus, .retry-btn:focus {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        outline: none;
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
        color: #dc3545;
    }
    
    .summary-error a {
        color: #0d6efd;
    }
    
    .error-details {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #f8d7da;
        font-size: 12px;
    }
    
    .chat-controls {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .summarize-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 16px 32px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .summarize-btn:hover, .summarize-btn:focus {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        outline: none;
    }
    
    .summarize-btn:disabled {
        background: #6c757d;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    .chat-tips {
        text-align: center;
        color: #6c757d;
        font-size: 13px;
    }
    
    .chat-tips a {
        color: #667eea;
        text-decoration: none;
    }
    
    .chat-tips a:hover, .chat-tips a:focus {
        text-decoration: underline;
    }
    
    .summarizer-toggle {
        position: fixed;
        right: 24px;
        bottom: 24px;
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    
    .summarizer-toggle:hover, .summarizer-toggle:focus {
        transform: scale(1.1);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6);
        outline: none;
    }
    
    .summarizer-toggle:hover .toggle-tooltip, .summarizer-toggle:focus .toggle-tooltip {
        opacity: 1;
        transform: translateX(-12px);
    }
    
    .toggle-tooltip {
        position: absolute;
        right: 100%;
        white-space: nowrap;
        background: #343a40;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: none;
        margin-right: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .toggle-tooltip::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 100%;
        transform: translateY(-50%);
        border: 8px solid transparent;
        border-left-color: #343a40;
    }
    
    /* Dark mode support */
    [data-md-color-scheme="slate"] .summarizer-chat {
        background: #1e1e1e;
        color: #fff;
        border-color: #444;
    }
    
    [data-md-color-scheme="slate"] .summary-output {
        background: linear-gradient(135deg, #2d2d30 0%, #25262b 100%);
        border-color: #444;
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-output p {
        color: #e9ecef;
    }
    
    [data-md-color-scheme="slate"] .summary-text {
        color: #f8f9fa;
    }
    
    [data-md-color-scheme="slate"] .summary-meta,
    [data-md-color-scheme="slate"] .summary-info {
        color: #adb5bd;
        border-top-color: #495057;
    }
    
    [data-md-color-scheme="slate"] .error-details {
        border-top-color: #495057;
    }
    `;
    
    document.head.appendChild(styles);
}

// Set up global event listeners once
setupEventListeners();

// Export functions for global access
window.openSummarizer = openSummarizer;
window.closeSummarizer = closeSummarizer;
window.summarizePage = summarizePage;