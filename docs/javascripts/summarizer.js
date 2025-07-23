// Hugging Face Summarizer for MkDocs
// Uses the free Hugging Face Inference API

// Configuration
const HF_API_URL = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn';
const MAX_INPUT_LENGTH = 1000; // Slightly reduced to be safe
const RATE_LIMIT_DELAY = 1000;

// Global state
let isProcessing = false;
let chatWindow = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add delay to ensure page is fully loaded
    setTimeout(() => {
        createChatUI();
        setupEventListeners();
        console.log('Page Summarizer initialized');
    }, 1000);
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
                    <p>Click "Summarize" to generate a summary of this page using AI.</p>
                </div>
                <div class="chat-controls">
                    <button id="summarize-btn" class="summarize-btn">
                        <span class="btn-text">Summarize This Page</span>
                        <span class="btn-spinner" style="display: none;">⏳ Processing...</span>
                    </button>
                    <div class="chat-tips">
                        <small>💡 Tip: <a href="https://huggingface.co/join" target="_blank">Sign in to HuggingFace</a> for better rate limits</small>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Floating button to open chat -->
        <button id="summarizer-toggle" class="summarizer-toggle">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
            <span class="toggle-tooltip">Summarize Page</span>
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
    
    // Get page title
    const title = document.querySelector('h1')?.innerText || 
                  document.querySelector('.md-content h1')?.innerText || 
                  document.title;
    
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
        
        if (!pageContent || pageContent.length < 50) {
            throw new Error('Not enough content to summarize (minimum 50 characters required)');
        }
        
        outputDiv.innerHTML = '<p class="loading">🤖 Generating summary via Hugging Face AI...</p>';
        
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
                    outputDiv.innerHTML = `<p class="loading">⏳ Model is loading, retrying... (${attempts}/${maxAttempts})</p>`;
                    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
                } else {
                    throw error;
                }
            }
        }
        
        // Display result
        outputDiv.innerHTML = `
            <div class="summary-result">
                <h5>📋 AI Summary:</h5>
                <p>${summary}</p>
                <div class="summary-meta">
                    <small>✨ Generated from ${pageContent.length} characters using Hugging Face BART model</small>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Summary generation failed:', error);
        
        // Handle specific errors
        let errorMessage = 'Failed to generate summary';
        
        if (error.message.includes('rate limit') || error.message.includes('429')) {
            errorMessage = '⏱️ Rate limit reached. Please wait a moment or <a href="https://huggingface.co/join" target="_blank">sign in to HuggingFace</a> for better limits.';
        } else if (error.message.includes('Not enough content')) {
            errorMessage = '📄 This page doesn\'t have enough content to summarize (minimum 50 characters).';
        } else if (error.message.includes('loading')) {
            errorMessage = '⏳ AI model is loading. Please try again in 20-30 seconds.';
        } else if (error.message.includes('503') || error.message.includes('500')) {
            errorMessage = '🔧 AI service temporarily unavailable. Please try again later.';
        }
        
        outputDiv.innerHTML = `
            <div class="summary-error">
                <p>❌ ${errorMessage}</p>
                <small>Technical details: ${error.message}</small>
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
        width: 380px;
        max-width: calc(100vw - 40px);
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: var(--md-text-font, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
        border: 1px solid #e0e0e0;
    }
    
    @media (max-width: 768px) {
        .summarizer-chat {
            right: 10px;
            top: 80px;
            width: calc(100vw - 20px);
        }
    }
    
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid #e0e0e0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px 12px 0 0;
    }
    
    .chat-header h4 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }
    
    .chat-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: rgba(255,255,255,0.8);
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: all 0.2s;
    }
    
    .chat-close:hover {
        background: rgba(255,255,255,0.2);
        color: white;
    }
    
    .chat-content {
        padding: 20px;
    }
    
    .summary-output {
        min-height: 120px;
        margin-bottom: 16px;
        padding: 16px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .summary-output p {
        margin: 0 0 8px 0;
        line-height: 1.6;
        color: #333;
    }
    
    .summary-result h5 {
        margin: 0 0 12px 0;
        color: #667eea;
        font-size: 16px;
        font-weight: 600;
    }
    
    .summary-meta {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e0e0e0;
        color: #666;
    }
    
    .loading {
        color: #667eea;
        font-style: italic;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .summary-error {
        color: #d32f2f;
    }
    
    .summary-error a {
        color: #1976d2;
    }
    
    .chat-controls {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .summarize-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
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
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    
    .summarize-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    
    .chat-tips {
        text-align: center;
        color: #666;
        font-size: 12px;
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
        width: 56px;
        height: 56px;
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
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    .summarizer-toggle:hover .toggle-tooltip {
        opacity: 1;
        transform: translateX(-8px);
    }
    
    .toggle-tooltip {
        position: absolute;
        right: 100%;
        white-space: nowrap;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        opacity: 0;
        transition: all 0.3s;
        pointer-events: none;
        margin-right: 12px;
    }
    
    .toggle-tooltip::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 100%;
        transform: translateY(-50%);
        border: 6px solid transparent;
        border-left-color: #333;
    }
    
    /* Dark mode support */
    [data-md-color-scheme="slate"] .summarizer-chat {
        background: #1e1e1e;
        color: #fff;
        border-color: #444;
    }
    
    [data-md-color-scheme="slate"] .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-md-color-scheme="slate"] .summary-output {
        background: #2d2d30;
        border-color: #444;
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-output p {
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-meta {
        color: #aaa;
        border-top-color: #444;
    }
    `;
    
    document.head.appendChild(styles);
}

// Export functions for global access
window.openSummarizer = openSummarizer;
window.closeSummarizer = closeSummarizer;
window.summarizePage = summarizePage;