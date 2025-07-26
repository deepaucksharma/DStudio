/**
 * Mobile Enhancements JavaScript
 * Provides interactive features for improved mobile experience
 */

(function() {
    'use strict';

    // Feature detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    // Initialize mobile enhancements
    document.addEventListener('DOMContentLoaded', function() {
        if (isMobile || hasTouch) {
            initMobileEnhancements();
        }
    });

    function initMobileEnhancements() {
        // 1. Enhance table scrolling
        enhanceTableScrolling();
        
        // 2. Add code block enhancements
        enhanceCodeBlocks();
        
        // 3. Initialize image zoom
        initImageZoom();
        
        // 4. Setup mobile TOC
        setupMobileTOC();
        
        // 5. Add reading mode
        setupReadingMode();
        
        // 6. Handle offline status
        setupOfflineDetection();
        
        // 7. Improve formula rendering
        enhanceFormulas();
        
        // 8. Setup gesture hints
        setupGestureHints();
        
        // 9. Mobile-specific navigation
        enhanceNavigation();
        
        // 10. Performance optimizations
        setupPerformanceOptimizations();
    }

    // 1. Table Scrolling Enhancement
    function enhanceTableScrolling() {
        const scrollWraps = document.querySelectorAll('.md-typeset__scrollwrap');
        
        scrollWraps.forEach(wrap => {
            // Add scroll indicators
            wrap.addEventListener('scroll', function() {
                const maxScroll = this.scrollWidth - this.clientWidth;
                const currentScroll = this.scrollLeft;
                
                if (currentScroll >= maxScroll - 10) {
                    this.classList.add('scrolled-right');
                } else {
                    this.classList.remove('scrolled-right');
                }
                
                if (currentScroll <= 10) {
                    this.classList.add('scrolled-left');
                } else {
                    this.classList.remove('scrolled-left');
                }
            });
            
            // Add gesture hint on first interaction
            if (!localStorage.getItem('tableScrollHintShown')) {
                wrap.setAttribute('data-hint', 'true');
                wrap.addEventListener('touchstart', function() {
                    localStorage.setItem('tableScrollHintShown', 'true');
                    this.removeAttribute('data-hint');
                }, { once: true });
            }
        });
    }

    // 2. Code Block Enhancements
    function enhanceCodeBlocks() {
        const codeBlocks = document.querySelectorAll('pre code');
        
        codeBlocks.forEach(block => {
            const pre = block.parentElement;
            
            // Add language indicator
            const lang = block.className.match(/language-(\w+)/);
            if (lang) {
                pre.setAttribute('data-lang', lang[1].toUpperCase());
            }
            
            // Add line numbers for long code blocks
            const lines = block.textContent.split('\n').length;
            if (lines > 10) {
                pre.classList.add('line-numbers');
            }
            
            // Enable horizontal scroll momentum
            pre.style.webkitOverflowScrolling = 'touch';
        });
    }

    // 3. Image Zoom
    function initImageZoom() {
        const images = document.querySelectorAll('.md-typeset img:not(.no-zoom)');
        
        images.forEach(img => {
            // Skip small images
            if (img.naturalWidth < 200 || img.naturalHeight < 200) return;
            
            img.classList.add('zoomable');
            
            img.addEventListener('click', function(e) {
                e.preventDefault();
                this.classList.toggle('zoomed');
                
                // Create overlay for zoomed images
                if (this.classList.contains('zoomed')) {
                    const overlay = document.createElement('div');
                    overlay.className = 'zoom-overlay';
                    overlay.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(0,0,0,0.8);
                        z-index: 999;
                    `;
                    overlay.addEventListener('click', () => {
                        this.classList.remove('zoomed');
                        overlay.remove();
                    });
                    document.body.appendChild(overlay);
                } else {
                    const overlay = document.querySelector('.zoom-overlay');
                    if (overlay) overlay.remove();
                }
            });
        });
    }

    // 4. Mobile Table of Contents
    function setupMobileTOC() {
        const tocItems = document.querySelectorAll('.md-nav--secondary .md-nav__item');
        
        if (tocItems.length > 0) {
            // Create mobile TOC button
            const tocButton = document.createElement('button');
            tocButton.className = 'mobile-toc-toggle';
            tocButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M3 4h18v2H3zm0 7h18v2H3zm0 7h18v2H3z"/></svg>';
            tocButton.setAttribute('aria-label', 'Table of Contents');
            
            // Create mobile TOC container
            const mobileTOC = document.createElement('div');
            mobileTOC.className = 'mobile-toc';
            
            // Clone TOC items
            tocItems.forEach(item => {
                const link = item.querySelector('a');
                if (link) {
                    const tocItem = document.createElement('div');
                    tocItem.className = 'toc-item';
                    tocItem.innerHTML = link.innerHTML;
                    tocItem.addEventListener('click', () => {
                        window.location.href = link.href;
                        mobileTOC.classList.remove('active');
                    });
                    mobileTOC.appendChild(tocItem);
                }
            });
            
            // Toggle TOC
            tocButton.addEventListener('click', () => {
                mobileTOC.classList.toggle('active');
            });
            
            // Only add if not already present
            if (!document.querySelector('.mobile-toc-toggle')) {
                document.body.appendChild(tocButton);
                document.body.appendChild(mobileTOC);
            }
        }
    }

    // 5. Reading Mode
    function setupReadingMode() {
        const readingButton = document.createElement('button');
        readingButton.className = 'reading-mode-toggle';
        readingButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.1 20.45 5.05 20 6.5 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zm0 13.5c-1.1-.35-2.3-.5-3.5-.5-1.7 0-4.15.65-5.5 1.5V8c1.35-.85 3.8-1.5 5.5-1.5 1.2 0 2.4.15 3.5.5v11.5z"/></svg>';
        readingButton.setAttribute('aria-label', 'Toggle Reading Mode');
        
        readingButton.addEventListener('click', () => {
            document.body.classList.toggle('reading-mode');
            const isReadingMode = document.body.classList.contains('reading-mode');
            localStorage.setItem('readingMode', isReadingMode);
            
            // Update button icon
            if (isReadingMode) {
                readingButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
            }
        });
        
        // Restore reading mode preference
        if (localStorage.getItem('readingMode') === 'true') {
            document.body.classList.add('reading-mode');
        }
        
        // Only add if not already present
        if (!document.querySelector('.reading-mode-toggle')) {
            document.body.appendChild(readingButton);
        }
    }

    // 6. Offline Detection
    function setupOfflineDetection() {
        const offlineBanner = document.createElement('div');
        offlineBanner.className = 'offline-banner';
        offlineBanner.textContent = 'You are currently offline. Some features may be limited.';
        document.body.appendChild(offlineBanner);
        
        function updateOnlineStatus() {
            if (navigator.onLine) {
                document.body.classList.remove('offline');
            } else {
                document.body.classList.add('offline');
            }
        }
        
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
        updateOnlineStatus();
    }

    // 7. Formula Enhancement
    function enhanceFormulas() {
        const formulas = document.querySelectorAll('.arithmatex, .MathJax_Display, .katex-display');
        
        formulas.forEach(formula => {
            // Make formulas scrollable
            formula.style.overflowX = 'auto';
            formula.style.webkitOverflowScrolling = 'touch';
            
            // Add pinch-to-zoom for complex formulas
            let scale = 1;
            let startDistance = 0;
            
            formula.addEventListener('touchstart', function(e) {
                if (e.touches.length === 2) {
                    startDistance = getDistance(e.touches[0], e.touches[1]);
                }
            });
            
            formula.addEventListener('touchmove', function(e) {
                if (e.touches.length === 2) {
                    e.preventDefault();
                    const currentDistance = getDistance(e.touches[0], e.touches[1]);
                    scale = Math.min(Math.max(scale * (currentDistance / startDistance), 0.5), 3);
                    this.style.transform = `scale(${scale})`;
                    startDistance = currentDistance;
                }
            });
        });
    }

    // 8. Gesture Hints
    function setupGestureHints() {
        // Show swipe hints for new users
        if (!localStorage.getItem('gestureHintsShown')) {
            const hintElements = document.querySelectorAll('[data-swipe-hint]');
            hintElements.forEach(el => {
                const hint = document.createElement('div');
                hint.className = 'gesture-hint';
                hint.textContent = el.getAttribute('data-swipe-hint');
                el.appendChild(hint);
                
                setTimeout(() => hint.remove(), 3000);
            });
            
            localStorage.setItem('gestureHintsShown', 'true');
        }
    }

    // 9. Navigation Enhancement
    function enhanceNavigation() {
        // Swipe navigation
        let touchStartX = 0;
        let touchEndX = 0;
        
        document.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].pageX;
        });
        
        document.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].pageX;
            handleSwipe();
        });
        
        function handleSwipe() {
            const swipeThreshold = 100;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - next page
                    const nextLink = document.querySelector('.md-footer__link--next');
                    if (nextLink) nextLink.click();
                } else {
                    // Swipe right - previous page
                    const prevLink = document.querySelector('.md-footer__link--prev');
                    if (prevLink) prevLink.click();
                }
            }
        }
        
        // Smooth scroll to sections
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // 10. Performance Optimizations
    function setupPerformanceOptimizations() {
        // Lazy load images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Debounce scroll events
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) {
                window.cancelAnimationFrame(scrollTimeout);
            }
            
            scrollTimeout = window.requestAnimationFrame(function() {
                // Update reading progress
                updateReadingProgress();
            });
        });
    }

    // Helper Functions
    function getDistance(touch1, touch2) {
        const dx = touch1.pageX - touch2.pageX;
        const dy = touch1.pageY - touch2.pageY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    function updateReadingProgress() {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        
        const progressBar = document.querySelector('.reading-progress');
        if (progressBar) {
            progressBar.style.transform = `scaleX(${scrolled / 100})`;
            progressBar.setAttribute('data-progress', Math.round(scrolled));
        }
    }

    // Mobile-specific utilities
    window.mobileUtils = {
        isMobile: isMobile,
        hasTouch: hasTouch,
        vibrate: function(pattern) {
            if ('vibrate' in navigator) {
                navigator.vibrate(pattern || 50);
            }
        },
        share: function(title, text, url) {
            if (navigator.share) {
                navigator.share({ title, text, url })
                    .catch(err => console.log('Share failed:', err));
            }
        }
    };

})();