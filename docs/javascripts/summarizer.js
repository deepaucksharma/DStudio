// Hugging Face Summarizer for MkDocs
// Uses the free Hugging Face Inference API

// Configuration
const HF_API_URL = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn';
const MAX_INPUT_LENGTH = 1024; // BART has max token limit
const RATE_LIMIT_DELAY = 1000; // 1 second between requests

// Global state
let isProcessing = false;
let chatWindow = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    createChatUI();
    setupEventListeners();
});

// Create the chat window UI
function createChatUI() {
    // Create chat window container
    const chatHTML = `
        <div id="summarizer-chat" class="summarizer-chat" style="display: none;">
            <div class="chat-header">
                <h4>📄 Page Summarizer</h4>
                <button class="chat-close" onclick="closeSummarizer()">×</button>
            </div>
            <div class="chat-content">
                <div id="summary-output" class="summary-output">
                    <p>Click "Summarize" to generate a summary of this page.</p>
                </div>
                <div class="chat-controls">
                    <button id="summarize-btn" class="summarize-btn" onclick="summarizePage()">
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
        <button id="summarizer-toggle" class="summarizer-toggle" onclick="openSummarizer()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span class="toggle-tooltip">Summarize Page</span>
        </button>
    `;
    
    // Inject into body
    document.body.insertAdjacentHTML('beforeend', chatHTML);
    chatWindow = document.getElementById('summarizer-chat');
}

// Setup event listeners
function setupEventListeners() {
    // Close on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatWindow.style.display !== 'none') {
            closeSummarizer();
        }
    });
}

// Open the summarizer chat window
function openSummarizer() {
    chatWindow.style.display = 'block';
    document.getElementById('summarizer-toggle').style.display = 'none';
}

// Close the summarizer chat window
function closeSummarizer() {
    chatWindow.style.display = 'none';
    document.getElementById('summarizer-toggle').style.display = 'block';
}

// Extract meaningful text from the current page
function extractPageContent() {
    // Try different content selectors for MkDocs Material theme
    const contentSelectors = [
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
                .trim();
            break;
        }
    }
    
    // Get page title
    const title = document.querySelector('h1')?.innerText || document.title;
    
    // Combine title and content
    let fullText = `Title: ${title}\n\nContent: ${content}`;
    
    // Truncate if too long
    if (fullText.length > MAX_INPUT_LENGTH) {
        fullText = fullText.substring(0, MAX_INPUT_LENGTH) + '...';
    }
    
    return fullText;
}

// Call Hugging Face API
async function callHuggingFaceAPI(text) {
    try {
        const response = await fetch(HF_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Optional: Add your HF token here for better rate limits
                // 'Authorization': 'Bearer YOUR_HF_TOKEN'
            },
            body: JSON.stringify({
                inputs: text,
                parameters: {
                    max_length: 150,
                    min_length: 30,
                    do_sample: false
                }
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `API Error: ${response.status}`);
        }
        
        const result = await response.json();
        return result[0]?.summary_text || 'No summary generated';
        
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
    
    // Show loading state
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline';
    outputDiv.innerHTML = '<p class="loading">📝 Extracting page content...</p>';
    
    try {
        // Extract page content
        const pageContent = extractPageContent();
        
        if (!pageContent || pageContent.length < 50) {
            throw new Error('Not enough content to summarize');
        }
        
        outputDiv.innerHTML = '<p class="loading">🤖 Generating summary...</p>';
        
        // Call API
        const summary = await callHuggingFaceAPI(pageContent);
        
        // Display result
        outputDiv.innerHTML = `
            <div class="summary-result">
                <h5>📋 Summary:</h5>
                <p>${summary}</p>
                <div class="summary-meta">
                    <small>Generated from ${pageContent.length} characters</small>
                </div>
            </div>
        `;
        
    } catch (error) {
        // Handle errors
        let errorMessage = 'Failed to generate summary';
        
        if (error.message.includes('rate limit')) {
            errorMessage = '⏱️ Rate limit reached. Please wait a moment or <a href="https://huggingface.co/join" target="_blank">sign in to HuggingFace</a> for better limits.';
        } else if (error.message.includes('Not enough content')) {
            errorMessage = '📄 This page doesn\'t have enough content to summarize.';
        } else if (error.message.includes('loading')) {
            errorMessage = '⏳ Model is loading. Please try again in 20-30 seconds.';
        }
        
        outputDiv.innerHTML = `
            <div class="summary-error">
                <p>❌ ${errorMessage}</p>
                <small>${error.message}</small>
            </div>
        `;
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
        isProcessing = false;
    }
}

// Add styles
const styles = `
    <style>
    .summarizer-chat {
        position: fixed;
        right: 20px;
        top: 80px;
        width: 380px;
        max-width: 90vw;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        z-index: 1000;
        font-family: var(--md-text-font-family);
    }
    
    @media (max-width: 768px) {
        .summarizer-chat {
            right: 10px;
            top: 60px;
            width: calc(100vw - 20px);
        }
    }
    
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid #e0e0e0;
        background: #f8f9fa;
        border-radius: 12px 12px 0 0;
    }
    
    .chat-header h4 {
        margin: 0;
        font-size: 18px;
        color: #333;
    }
    
    .chat-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: all 0.2s;
    }
    
    .chat-close:hover {
        background: #e0e0e0;
        color: #333;
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
    }
    
    .summary-output p {
        margin: 0 0 8px 0;
        line-height: 1.6;
        color: #333;
    }
    
    .summary-result h5 {
        margin: 0 0 12px 0;
        color: #2196F3;
        font-size: 16px;
    }
    
    .summary-meta {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e0e0e0;
        color: #666;
    }
    
    .loading {
        color: #666;
        font-style: italic;
    }
    
    .summary-error {
        color: #d32f2f;
    }
    
    .summary-error a {
        color: #2196F3;
    }
    
    .chat-controls {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .summarize-btn {
        background: #2196F3;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .summarize-btn:hover {
        background: #1976D2;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
    }
    
    .summarize-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
    
    .chat-tips {
        text-align: center;
        color: #666;
    }
    
    .chat-tips a {
        color: #2196F3;
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
        background: #2196F3;
        color: white;
        border: none;
        border-radius: 28px;
        cursor: pointer;
        box-shadow: 0 2px 12px rgba(33, 150, 243, 0.4);
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }
    
    .summarizer-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 20px rgba(33, 150, 243, 0.6);
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
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 14px;
        opacity: 0;
        transition: all 0.3s;
        pointer-events: none;
        margin-right: 8px;
    }
    
    /* Dark mode support */
    [data-md-color-scheme="slate"] .summarizer-chat {
        background: #1e1e1e;
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .chat-header {
        background: #2b2b2b;
        border-bottom-color: #444;
    }
    
    [data-md-color-scheme="slate"] .chat-header h4 {
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .chat-close {
        color: #aaa;
    }
    
    [data-md-color-scheme="slate"] .chat-close:hover {
        background: #444;
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-output {
        background: #2b2b2b;
        border-color: #444;
    }
    
    [data-md-color-scheme="slate"] .summary-output p {
        color: #fff;
    }
    
    [data-md-color-scheme="slate"] .summary-meta {
        color: #aaa;
        border-top-color: #444;
    }
    </style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', styles);