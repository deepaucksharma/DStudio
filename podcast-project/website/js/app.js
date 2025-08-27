// ===================================
// Hindi Tech Podcast - Main JavaScript
// Mobile-first approach with Mumbai-style interactions
// ===================================

class HindiTechPodcast {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.isPlaying = false;
        this.currentEpisode = null;
        this.audioElement = null;
        this.episodes = [];
        this.filteredEpisodes = [];
        this.currentPage = 1;
        this.episodesPerPage = 12;
        this.searchQuery = '';
        this.activeFilters = {};
        
        this.init();
    }

    init() {
        this.setupTheme();
        this.setupLanguage();
        this.setupNavigation();
        this.setupCarousel();
        this.setupAudioPlayer();
        this.setupSearch();
        this.setupFilters();
        this.setupNewsletterForm();
        this.setupScrollEffects();
        this.setupKeyboardNavigation();
        this.setupAnalytics();
        this.loadEpisodes();
        
        // Performance optimization
        this.setupLazyLoading();
        this.preloadCriticalResources();
        
        console.log('🎧 Hindi Tech Podcast initialized - Mumbai style!');
    }

    // ===================================
    // Theme Management
    // ===================================
    
    setupTheme() {
        const themeToggle = document.getElementById('themeToggle');
        const html = document.documentElement;
        
        // Apply saved theme
        html.setAttribute('data-theme', this.currentTheme);
        this.updateThemeIcon();
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.currentTheme = e.matches ? 'dark' : 'light';
                    html.setAttribute('data-theme', this.currentTheme);
                    this.updateThemeIcon();
                }
            });
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.updateThemeIcon();
        
        // Analytics
        this.trackEvent('theme_toggle', { theme: this.currentTheme });
    }

    updateThemeIcon() {
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = this.currentTheme === 'light' ? '🌙' : '☀️';
        }
    }

    // ===================================
    // Language Management
    // ===================================
    
    setupLanguage() {
        const langToggle = document.getElementById('langToggle');
        
        // Apply saved language
        this.updateLanguage();
        
        if (langToggle) {
            langToggle.addEventListener('click', () => {
                this.toggleLanguage();
            });
        }
    }

    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'en' ? 'hi' : 'en';
        localStorage.setItem('language', this.currentLanguage);
        this.updateLanguage();
        
        // Analytics
        this.trackEvent('language_toggle', { language: this.currentLanguage });
    }

    updateLanguage() {
        const langText = document.querySelector('.lang-text');
        if (langText) {
            langText.textContent = this.currentLanguage === 'en' ? 'हिं' : 'EN';
        }
        
        // Update all elements with language attributes
        const elements = document.querySelectorAll('[data-en][data-hi]');
        elements.forEach(element => {
            const text = element.getAttribute(`data-${this.currentLanguage}`);
            if (text) {
                element.textContent = text;
            }
        });
        
        // Update placeholders
        const inputs = document.querySelectorAll('[data-placeholder-en][data-placeholder-hi]');
        inputs.forEach(input => {
            const placeholder = input.getAttribute(`data-placeholder-${this.currentLanguage}`);
            if (placeholder) {
                input.placeholder = placeholder;
            }
        });
        
        // Update document language
        document.documentElement.lang = this.currentLanguage;
        
        // Update page titles if on episode pages
        this.updatePageTitle();
    }

    updatePageTitle() {
        const titleElement = document.querySelector('title');
        if (titleElement && titleElement.hasAttribute(`data-${this.currentLanguage}`)) {
            titleElement.textContent = titleElement.getAttribute(`data-${this.currentLanguage}`);
        }
    }

    // ===================================
    // Navigation
    // ===================================
    
    setupNavigation() {
        const navHamburger = document.getElementById('navHamburger');
        const navMenu = document.getElementById('navMenu');
        const navbar = document.getElementById('navbar');
        
        // Mobile menu toggle
        if (navHamburger && navMenu) {
            navHamburger.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navHamburger.classList.toggle('active');
                
                // Prevent body scroll when menu is open
                document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navHamburger.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    navHamburger.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
            
            // Close menu when clicking nav links
            const navLinks = navMenu.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('active');
                    navHamburger.classList.remove('active');
                    document.body.style.overflow = '';
                });
            });
        }
        
        // Navbar scroll behavior
        if (navbar) {
            let lastScrollY = window.scrollY;
            let ticking = false;
            
            const updateNavbar = () => {
                const currentScrollY = window.scrollY;
                
                if (currentScrollY > 100) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
                
                // Hide/show navbar on scroll (mobile)
                if (window.innerWidth <= 768) {
                    if (currentScrollY > lastScrollY && currentScrollY > 200) {
                        navbar.style.transform = 'translateY(-100%)';
                    } else {
                        navbar.style.transform = 'translateY(0)';
                    }
                }
                
                lastScrollY = currentScrollY;
                ticking = false;
            };
            
            window.addEventListener('scroll', () => {
                if (!ticking) {
                    requestAnimationFrame(updateNavbar);
                    ticking = true;
                }
            });
        }
        
        // Active link highlighting
        this.updateActiveNavLink();
        
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    const offsetTop = target.getBoundingClientRect().top + window.scrollY - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    updateActiveNavLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath || 
                (currentPath.includes('episode') && link.getAttribute('href').includes('episodes'))) {
                link.classList.add('active');
            }
        });
    }

    // ===================================
    // Episodes Carousel
    // ===================================
    
    setupCarousel() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const episodesContainer = document.getElementById('episodesContainer');
        
        if (!episodesContainer) return;
        
        let currentIndex = 0;
        const episodeCards = episodesContainer.querySelectorAll('.episode-card');
        const totalEpisodes = episodeCards.length;
        const episodesPerView = this.getEpisodesPerView();
        
        const updateCarousel = () => {
            const translateX = -(currentIndex * (100 / episodesPerView));
            episodesContainer.style.transform = `translateX(${translateX}%)`;
            
            // Update button states
            if (prevBtn) {
                prevBtn.disabled = currentIndex === 0;
                prevBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
            }
            
            if (nextBtn) {
                nextBtn.disabled = currentIndex >= totalEpisodes - episodesPerView;
                nextBtn.style.opacity = currentIndex >= totalEpisodes - episodesPerView ? '0.5' : '1';
            }
        };
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateCarousel();
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentIndex < totalEpisodes - episodesPerView) {
                    currentIndex++;
                    updateCarousel();
                }
            });
        }
        
        // Touch/swipe support for mobile
        let startX = 0;
        let endX = 0;
        
        episodesContainer.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        }, { passive: true });
        
        episodesContainer.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            const diff = startX - endX;
            
            if (Math.abs(diff) > 50) { // Minimum swipe distance
                if (diff > 0 && currentIndex < totalEpisodes - episodesPerView) {
                    currentIndex++;
                } else if (diff < 0 && currentIndex > 0) {
                    currentIndex--;
                }
                updateCarousel();
            }
        }, { passive: true });
        
        // Auto-play carousel (optional)
        if (window.innerWidth > 768) {
            setInterval(() => {
                if (currentIndex < totalEpisodes - episodesPerView) {
                    currentIndex++;
                } else {
                    currentIndex = 0;
                }
                updateCarousel();
            }, 8000);
        }
        
        // Initialize
        updateCarousel();
        
        // Update on window resize
        window.addEventListener('resize', () => {
            const newEpisodesPerView = this.getEpisodesPerView();
            if (newEpisodesPerView !== episodesPerView) {
                location.reload(); // Simple solution for responsive changes
            }
        });
    }

    getEpisodesPerView() {
        if (window.innerWidth >= 1024) return 3;
        if (window.innerWidth >= 768) return 2;
        return 1;
    }

    // ===================================
    // Audio Player
    // ===================================
    
    setupAudioPlayer() {
        // Setup play buttons throughout the site
        document.querySelectorAll('.btn-play, .play-overlay, .cover-play-btn, .play-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const episodeId = btn.getAttribute('data-episode') || this.getCurrentEpisodeId();
                this.playEpisode(episodeId);
            });
        });
        
        // Setup download buttons
        document.querySelectorAll('.btn-download').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const episodeId = btn.getAttribute('data-episode');
                this.downloadEpisode(episodeId);
            });
        });
        
        // Setup share buttons
        document.querySelectorAll('.btn-share').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const episodeId = btn.getAttribute('data-episode');
                this.shareEpisode(episodeId);
            });
        });
        
        // Setup bookmark buttons
        document.querySelectorAll('.bookmark-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const episodeId = btn.getAttribute('data-episode');
                this.toggleBookmark(episodeId);
            });
        });
        
        // Initialize audio element if on episode page
        this.audioElement = document.getElementById('audioElement');
        if (this.audioElement) {
            this.setupEpisodePlayer();
        }
    }

    playEpisode(episodeId) {
        if (!episodeId) return;
        
        console.log(`🎵 Playing episode ${episodeId}`);
        
        // Update UI to show playing state
        document.querySelectorAll('.btn-play').forEach(btn => {
            const btnEpisodeId = btn.getAttribute('data-episode');
            const playIcon = btn.querySelector('.play-icon');
            
            if (btnEpisodeId === episodeId) {
                playIcon.textContent = '⏸';
                btn.classList.add('playing');
            } else {
                playIcon.textContent = '▶';
                btn.classList.remove('playing');
            }
        });
        
        this.currentEpisode = episodeId;
        this.isPlaying = true;
        
        // Analytics
        this.trackEvent('episode_play', { 
            episode_id: episodeId,
            source: 'play_button'
        });
        
        // Simulate audio loading (replace with actual audio implementation)
        setTimeout(() => {
            this.showPlayerNotification(`Playing Episode ${episodeId}`);
        }, 500);
    }

    downloadEpisode(episodeId) {
        if (!episodeId) return;
        
        console.log(`📥 Downloading episode ${episodeId}`);
        
        // Analytics
        this.trackEvent('episode_download', { episode_id: episodeId });
        
        // Simulate download (replace with actual download logic)
        this.showPlayerNotification(`Downloading Episode ${episodeId}...`);
        
        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.href = `./audio/episode-${episodeId.padStart(3, '0')}.mp3`;
        downloadLink.download = `Hindi-Tech-Podcast-Episode-${episodeId}.mp3`;
        downloadLink.click();
    }

    shareEpisode(episodeId) {
        if (!episodeId) return;
        
        const episodeUrl = `${window.location.origin}/episodes/episode-${episodeId}.html`;
        const episodeTitle = `Episode ${episodeId} - Hindi Tech Podcast`;
        
        if (navigator.share) {
            // Use native share API if available
            navigator.share({
                title: episodeTitle,
                text: 'Check out this amazing tech episode in Hindi!',
                url: episodeUrl
            }).catch(console.error);
        } else {
            // Fallback to copy to clipboard
            navigator.clipboard.writeText(episodeUrl).then(() => {
                this.showPlayerNotification('Episode link copied to clipboard!');
            }).catch(() => {
                // Further fallback - show share modal
                this.showShareModal(episodeUrl, episodeTitle);
            });
        }
        
        // Analytics
        this.trackEvent('episode_share', { episode_id: episodeId });
    }

    toggleBookmark(episodeId) {
        if (!episodeId) return;
        
        const bookmarked = this.isEpisodeBookmarked(episodeId);
        
        if (bookmarked) {
            this.removeBookmark(episodeId);
            this.showPlayerNotification('Bookmark removed');
        } else {
            this.addBookmark(episodeId);
            this.showPlayerNotification('Episode bookmarked!');
        }
        
        // Update bookmark button UI
        document.querySelectorAll('.bookmark-btn').forEach(btn => {
            if (btn.getAttribute('data-episode') === episodeId) {
                const icon = btn.querySelector('.bookmark-icon');
                icon.textContent = bookmarked ? '🔖' : '📌';
                btn.classList.toggle('bookmarked', !bookmarked);
            }
        });
        
        // Analytics
        this.trackEvent('episode_bookmark', { 
            episode_id: episodeId,
            action: bookmarked ? 'remove' : 'add'
        });
    }

    setupEpisodePlayer() {
        if (!this.audioElement) return;
        
        const playPauseBtn = document.getElementById('playPauseBtn');
        const rewindBtn = document.getElementById('rewindBtn');
        const forwardBtn = document.getElementById('forwardBtn');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const currentTime = document.getElementById('currentTime');
        const totalTime = document.getElementById('totalTime');
        const volumeSlider = document.getElementById('volumeSlider');
        const speedBtn = document.getElementById('speedBtn');
        const speedMenu = document.getElementById('speedMenu');
        
        // Play/Pause functionality
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => {
                if (this.audioElement.paused) {
                    this.audioElement.play();
                    playPauseBtn.querySelector('.player-icon').textContent = '⏸';
                } else {
                    this.audioElement.pause();
                    playPauseBtn.querySelector('.player-icon').textContent = '▶';
                }
            });
        }
        
        // Rewind/Forward
        if (rewindBtn) {
            rewindBtn.addEventListener('click', () => {
                this.audioElement.currentTime = Math.max(0, this.audioElement.currentTime - 10);
            });
        }
        
        if (forwardBtn) {
            forwardBtn.addEventListener('click', () => {
                this.audioElement.currentTime = Math.min(
                    this.audioElement.duration, 
                    this.audioElement.currentTime + 30
                );
            });
        }
        
        // Progress bar
        if (progressBar && progressFill) {
            this.audioElement.addEventListener('timeupdate', () => {
                if (this.audioElement.duration) {
                    const progress = (this.audioElement.currentTime / this.audioElement.duration) * 100;
                    progressBar.value = progress;
                    progressFill.style.width = `${progress}%`;
                    
                    if (currentTime) {
                        currentTime.textContent = this.formatTime(this.audioElement.currentTime);
                    }
                }
            });
            
            progressBar.addEventListener('input', () => {
                if (this.audioElement.duration) {
                    const time = (progressBar.value / 100) * this.audioElement.duration;
                    this.audioElement.currentTime = time;
                }
            });
        }
        
        // Duration
        this.audioElement.addEventListener('loadedmetadata', () => {
            if (totalTime) {
                totalTime.textContent = this.formatTime(this.audioElement.duration);
            }
        });
        
        // Volume control
        if (volumeSlider) {
            volumeSlider.addEventListener('input', () => {
                this.audioElement.volume = volumeSlider.value / 100;
            });
        }
        
        // Speed control
        if (speedBtn && speedMenu) {
            speedBtn.addEventListener('click', () => {
                speedMenu.style.display = speedMenu.style.display === 'flex' ? 'none' : 'flex';
            });
            
            speedMenu.querySelectorAll('.speed-option').forEach(option => {
                option.addEventListener('click', () => {
                    const speed = parseFloat(option.getAttribute('data-speed'));
                    this.audioElement.playbackRate = speed;
                    speedBtn.textContent = `${speed}×`;
                    
                    // Update active state
                    speedMenu.querySelectorAll('.speed-option').forEach(opt => opt.classList.remove('active'));
                    option.classList.add('active');
                    
                    speedMenu.style.display = 'none';
                });
            });
            
            // Close speed menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!speedBtn.contains(e.target) && !speedMenu.contains(e.target)) {
                    speedMenu.style.display = 'none';
                }
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName.toLowerCase() === 'input' || e.target.tagName.toLowerCase() === 'textarea') {
                return; // Don't interfere with form inputs
            }
            
            switch (e.code) {
                case 'Space':
                    e.preventDefault();
                    playPauseBtn.click();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    rewindBtn.click();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    forwardBtn.click();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    volumeSlider.value = Math.min(100, parseInt(volumeSlider.value) + 10);
                    volumeSlider.dispatchEvent(new Event('input'));
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    volumeSlider.value = Math.max(0, parseInt(volumeSlider.value) - 10);
                    volumeSlider.dispatchEvent(new Event('input'));
                    break;
            }
        });
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
    }

    // ===================================
    // Search Functionality
    // ===================================
    
    setupSearch() {
        const searchInput = document.getElementById('episodeSearch');
        const searchSuggestions = document.getElementById('searchSuggestions');
        const searchBtn = document.querySelector('.search-btn');
        
        if (!searchInput) return;
        
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            this.searchQuery = e.target.value.toLowerCase().trim();
            
            searchTimeout = setTimeout(() => {
                this.performSearch();
                this.showSearchSuggestions();
            }, 300);
        });
        
        // Search button click
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch();
                this.hideSearchSuggestions();
            });
        }
        
        // Enter key search
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
                this.hideSearchSuggestions();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchSuggestions?.contains(e.target)) {
                this.hideSearchSuggestions();
            }
        });
        
        // Clear search
        this.setupSearchClear();
    }

    performSearch() {
        if (!this.searchQuery) {
            this.filteredEpisodes = [...this.episodes];
        } else {
            this.filteredEpisodes = this.episodes.filter(episode => 
                episode.title.toLowerCase().includes(this.searchQuery) ||
                episode.description.toLowerCase().includes(this.searchQuery) ||
                episode.tags.some(tag => tag.toLowerCase().includes(this.searchQuery)) ||
                episode.company.toLowerCase().includes(this.searchQuery) ||
                episode.category.toLowerCase().includes(this.searchQuery)
            );
        }
        
        this.applyFilters();
        this.updateEpisodesDisplay();
        this.updateSearchResults();
        
        // Analytics
        if (this.searchQuery) {
            this.trackEvent('episode_search', { 
                query: this.searchQuery,
                results_count: this.filteredEpisodes.length
            });
        }
    }

    showSearchSuggestions() {
        const searchSuggestions = document.getElementById('searchSuggestions');
        if (!searchSuggestions || !this.searchQuery) {
            this.hideSearchSuggestions();
            return;
        }
        
        // Generate suggestions based on search query
        const suggestions = this.generateSearchSuggestions();
        
        if (suggestions.length > 0) {
            searchSuggestions.innerHTML = suggestions.map(suggestion => 
                `<div class="search-suggestion" data-query="${suggestion}">
                    <span class="suggestion-icon">🔍</span>
                    <span class="suggestion-text">${suggestion}</span>
                </div>`
            ).join('');
            
            searchSuggestions.style.display = 'block';
            
            // Add click handlers
            searchSuggestions.querySelectorAll('.search-suggestion').forEach(suggestion => {
                suggestion.addEventListener('click', () => {
                    const query = suggestion.getAttribute('data-query');
                    document.getElementById('episodeSearch').value = query;
                    this.searchQuery = query.toLowerCase();
                    this.performSearch();
                    this.hideSearchSuggestions();
                });
            });
        } else {
            this.hideSearchSuggestions();
        }
    }

    hideSearchSuggestions() {
        const searchSuggestions = document.getElementById('searchSuggestions');
        if (searchSuggestions) {
            searchSuggestions.style.display = 'none';
        }
    }

    generateSearchSuggestions() {
        if (!this.searchQuery || this.searchQuery.length < 2) return [];
        
        const suggestions = new Set();
        const maxSuggestions = 5;
        
        // Add matching episode titles
        this.episodes.forEach(episode => {
            if (episode.title.toLowerCase().includes(this.searchQuery)) {
                suggestions.add(episode.title);
            }
        });
        
        // Add matching tags
        this.episodes.forEach(episode => {
            episode.tags.forEach(tag => {
                if (tag.toLowerCase().includes(this.searchQuery)) {
                    suggestions.add(tag);
                }
            });
        });
        
        // Add matching companies
        this.episodes.forEach(episode => {
            if (episode.company.toLowerCase().includes(this.searchQuery)) {
                suggestions.add(episode.company);
            }
        });
        
        return Array.from(suggestions).slice(0, maxSuggestions);
    }

    setupSearchClear() {
        // Add clear search functionality
        const searchInput = document.getElementById('episodeSearch');
        if (!searchInput) return;
        
        const clearBtn = document.createElement('button');
        clearBtn.className = 'search-clear-btn';
        clearBtn.innerHTML = '×';
        clearBtn.style.display = 'none';
        clearBtn.setAttribute('aria-label', 'Clear search');
        
        searchInput.parentNode.appendChild(clearBtn);
        
        searchInput.addEventListener('input', () => {
            clearBtn.style.display = searchInput.value ? 'block' : 'none';
        });
        
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            this.searchQuery = '';
            this.performSearch();
            clearBtn.style.display = 'none';
            searchInput.focus();
        });
    }

    // ===================================
    // Filters
    // ===================================
    
    setupFilters() {
        const categoryFilter = document.getElementById('categoryFilter');
        const companyFilter = document.getElementById('companyFilter');
        const durationFilter = document.getElementById('durationFilter');
        const sortFilter = document.getElementById('sortFilter');
        const clearFiltersBtn = document.getElementById('clearFilters');
        
        // Filter change handlers
        [categoryFilter, companyFilter, durationFilter, sortFilter].forEach(filter => {
            if (filter) {
                filter.addEventListener('change', () => {
                    this.updateActiveFilters();
                    this.applyFilters();
                    this.updateEpisodesDisplay();
                    this.updateActiveFiltersDisplay();
                });
            }
        });
        
        // Clear filters
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }
        
        // Topic tags (if on episodes page)
        document.querySelectorAll('.topic-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const filter = tag.getAttribute('data-filter');
                document.getElementById('episodeSearch').value = filter;
                this.searchQuery = filter.toLowerCase();
                this.performSearch();
            });
        });
        
        // URL parameter filters
        this.parseURLFilters();
    }

    updateActiveFilters() {
        this.activeFilters = {};
        
        const categoryFilter = document.getElementById('categoryFilter');
        const companyFilter = document.getElementById('companyFilter');
        const durationFilter = document.getElementById('durationFilter');
        const sortFilter = document.getElementById('sortFilter');
        
        if (categoryFilter?.value && categoryFilter.value !== 'all') {
            this.activeFilters.category = categoryFilter.value;
        }
        
        if (companyFilter?.value && companyFilter.value !== 'all') {
            this.activeFilters.company = companyFilter.value;
        }
        
        if (durationFilter?.value && durationFilter.value !== 'all') {
            this.activeFilters.duration = durationFilter.value;
        }
        
        if (sortFilter?.value) {
            this.activeFilters.sort = sortFilter.value;
        }
    }

    applyFilters() {
        let filtered = [...this.filteredEpisodes];
        
        // Apply category filter
        if (this.activeFilters.category) {
            filtered = filtered.filter(episode => 
                episode.category === this.activeFilters.category
            );
        }
        
        // Apply company filter
        if (this.activeFilters.company) {
            if (this.activeFilters.company === 'global') {
                filtered = filtered.filter(episode => 
                    !['flipkart', 'paytm', 'zomato', 'ola', 'swiggy', 'irctc', 'jio', 'phonepe', 'razorpay', 'byju'].includes(episode.company)
                );
            } else {
                filtered = filtered.filter(episode => 
                    episode.company === this.activeFilters.company
                );
            }
        }
        
        // Apply duration filter
        if (this.activeFilters.duration) {
            filtered = filtered.filter(episode => {
                const duration = this.parseDuration(episode.duration);
                switch (this.activeFilters.duration) {
                    case 'short':
                        return duration < 120; // Less than 2 hours
                    case 'medium':
                        return duration >= 120 && duration <= 180; // 2-3 hours
                    case 'long':
                        return duration > 180; // More than 3 hours
                    default:
                        return true;
                }
            });
        }
        
        // Apply sorting
        if (this.activeFilters.sort) {
            filtered.sort((a, b) => {
                switch (this.activeFilters.sort) {
                    case 'latest':
                        return new Date(b.date) - new Date(a.date);
                    case 'oldest':
                        return new Date(a.date) - new Date(b.date);
                    case 'popular':
                        return (b.listens || 0) - (a.listens || 0);
                    case 'duration-asc':
                        return this.parseDuration(a.duration) - this.parseDuration(b.duration);
                    case 'duration-desc':
                        return this.parseDuration(b.duration) - this.parseDuration(a.duration);
                    default:
                        return 0;
                }
            });
        }
        
        this.filteredEpisodes = filtered;
        
        // Analytics
        this.trackEvent('episodes_filtered', {
            filters: this.activeFilters,
            results_count: this.filteredEpisodes.length
        });
    }

    clearAllFilters() {
        // Reset filter selects
        document.getElementById('categoryFilter').value = 'all';
        document.getElementById('companyFilter').value = 'all';
        document.getElementById('durationFilter').value = 'all';
        document.getElementById('sortFilter').value = 'latest';
        
        // Clear search
        const searchInput = document.getElementById('episodeSearch');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Reset state
        this.searchQuery = '';
        this.activeFilters = {};
        this.filteredEpisodes = [...this.episodes];
        
        // Update display
        this.updateEpisodesDisplay();
        this.updateActiveFiltersDisplay();
        
        // Analytics
        this.trackEvent('filters_cleared');
    }

    updateActiveFiltersDisplay() {
        const activeFiltersContainer = document.getElementById('activeFilters');
        if (!activeFiltersContainer) return;
        
        const filterTags = [];
        
        Object.entries(this.activeFilters).forEach(([key, value]) => {
            if (key !== 'sort' && value !== 'all') {
                filterTags.push(`
                    <div class="active-filter-tag">
                        <span>${this.getFilterDisplayName(key, value)}</span>
                        <button class="active-filter-remove" data-filter="${key}" aria-label="Remove filter">×</button>
                    </div>
                `);
            }
        });
        
        if (this.searchQuery) {
            filterTags.push(`
                <div class="active-filter-tag">
                    <span>Search: "${this.searchQuery}"</span>
                    <button class="active-filter-remove" data-filter="search" aria-label="Clear search">×</button>
                </div>
            `);
        }
        
        activeFiltersContainer.innerHTML = filterTags.join('');
        
        // Add remove handlers
        activeFiltersContainer.querySelectorAll('.active-filter-remove').forEach(btn => {
            btn.addEventListener('click', () => {
                const filterType = btn.getAttribute('data-filter');
                this.removeFilter(filterType);
            });
        });
    }

    removeFilter(filterType) {
        if (filterType === 'search') {
            document.getElementById('episodeSearch').value = '';
            this.searchQuery = '';
        } else {
            const filterId = `${filterType}Filter`;
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.value = 'all';
            }
        }
        
        this.updateActiveFilters();
        this.performSearch();
        this.applyFilters();
        this.updateEpisodesDisplay();
        this.updateActiveFiltersDisplay();
    }

    getFilterDisplayName(key, value) {
        const displayNames = {
            category: {
                'distributed-systems': 'Distributed Systems',
                'databases': 'Databases',
                'security': 'Security',
                'microservices': 'Microservices',
                'performance': 'Performance',
                'cloud': 'Cloud & DevOps'
            },
            company: {
                'flipkart': 'Flipkart',
                'paytm': 'Paytm',
                'zomato': 'Zomato',
                'ola': 'Ola',
                'global': 'Global Companies'
            },
            duration: {
                'short': '< 2 hours',
                'medium': '2-3 hours',
                'long': '> 3 hours'
            }
        };
        
        return displayNames[key]?.[value] || value;
    }

    parseURLFilters() {
        const urlParams = new URLSearchParams(window.location.search);
        
        const category = urlParams.get('category');
        const company = urlParams.get('company');
        const search = urlParams.get('search');
        
        if (category) {
            const categoryFilter = document.getElementById('categoryFilter');
            if (categoryFilter) {
                categoryFilter.value = category;
            }
        }
        
        if (company) {
            const companyFilter = document.getElementById('companyFilter');
            if (companyFilter) {
                companyFilter.value = company;
            }
        }
        
        if (search) {
            const searchInput = document.getElementById('episodeSearch');
            if (searchInput) {
                searchInput.value = search;
                this.searchQuery = search.toLowerCase();
            }
        }
        
        // Apply filters after page load
        setTimeout(() => {
            this.updateActiveFilters();
            this.performSearch();
        }, 100);
    }

    parseDuration(durationStr) {
        // Parse duration string like "3:02:18" to minutes
        const parts = durationStr.split(':').map(Number);
        if (parts.length === 3) {
            return parts[0] * 60 + parts[1] + parts[2] / 60;
        } else if (parts.length === 2) {
            return parts[0] + parts[1] / 60;
        }
        return 0;
    }

    // ===================================
    // Episodes Data & Display
    // ===================================
    
    loadEpisodes() {
        // Mock episodes data - replace with actual API call
        this.episodes = this.generateMockEpisodes();
        this.filteredEpisodes = [...this.episodes];
        
        // Update display if on episodes page
        if (document.getElementById('episodesGrid')) {
            this.updateEpisodesDisplay();
        }
        
        // Update episode count
        this.updateEpisodeCount();
    }

    generateMockEpisodes() {
        const categories = ['distributed-systems', 'databases', 'security', 'microservices', 'performance', 'cloud', 'ai-ml', 'frontend', 'mobile', 'blockchain'];
        const companies = ['flipkart', 'paytm', 'zomato', 'ola', 'swiggy', 'irctc', 'jio', 'phonepe', 'razorpay', 'byju'];
        const episodes = [];
        
        for (let i = 91; i >= 1; i--) {
            const category = categories[Math.floor(Math.random() * categories.length)];
            const company = companies[Math.floor(Math.random() * companies.length)];
            
            episodes.push({
                id: i.toString().padStart(3, '0'),
                number: i,
                title: this.generateEpisodeTitle(i, category, company),
                description: this.generateEpisodeDescription(category, company),
                category: category,
                company: company,
                duration: this.generateRandomDuration(),
                date: new Date(2025, 7, 17 - (91 - i)).toISOString().split('T')[0],
                tags: this.generateEpisodeTags(category),
                listens: Math.floor(Math.random() * 50000) + 10000,
                cover: `./images/episode-${i.toString().padStart(3, '0')}-cover.jpg`
            });
        }
        
        return episodes;
    }

    generateEpisodeTitle(number, category, company) {
        const titles = {
            'distributed-systems': [
                'CAP Theorem in Production',
                'Consensus Algorithms Deep Dive',
                'Distributed Transactions',
                'Event Sourcing Patterns'
            ],
            'databases': [
                'Database Indexing Strategies',
                'ACID Properties Explained',
                'Sharding at Scale',
                'NoSQL vs SQL Trade-offs'
            ],
            'security': [
                'OAuth 2.0 Deep Dive',
                'JWT Token Security',
                'API Security Best Practices',
                'Encryption in Transit'
            ],
            'microservices': [
                'Service Mesh Architecture',
                'API Gateway Patterns',
                'Circuit Breaker Implementation',
                'Container Orchestration'
            ]
        };
        
        const categoryTitles = titles[category] || ['System Design Fundamentals'];
        const title = categoryTitles[Math.floor(Math.random() * categoryTitles.length)];
        
        return `${title}: ${company.charAt(0).toUpperCase() + company.slice(1)} Scale`;
    }

    generateEpisodeDescription(category, company) {
        return `Deep dive into ${category.replace('-', ' ')} with real production examples from ${company.charAt(0).toUpperCase() + company.slice(1)}. Learn how they handle millions of users and transactions.`;
    }

    generateRandomDuration() {
        const minutes = Math.floor(Math.random() * 120) + 120; // 2-4 hours
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        const seconds = Math.floor(Math.random() * 60);
        
        return `${hours}:${remainingMinutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    generateEpisodeTags(category) {
        const tagMap = {
            'distributed-systems': ['CAP Theorem', 'Consensus', 'Partitioning', 'Replication'],
            'databases': ['ACID', 'Indexing', 'Sharding', 'Transactions'],
            'security': ['OAuth', 'JWT', 'Encryption', 'Authentication'],
            'microservices': ['Service Mesh', 'API Gateway', 'Circuit Breaker', 'Containers']
        };
        
        const categoryTags = tagMap[category] || ['Architecture', 'Scalability'];
        return categoryTags.slice(0, Math.floor(Math.random() * 3) + 2);
    }

    updateEpisodesDisplay() {
        const episodesGrid = document.getElementById('episodesGrid');
        if (!episodesGrid) return;
        
        const startIndex = (this.currentPage - 1) * this.episodesPerPage;
        const endIndex = startIndex + this.episodesPerPage;
        const episodesToShow = this.filteredEpisodes.slice(startIndex, endIndex);
        
        if (episodesToShow.length === 0) {
            this.showNoResultsState();
            return;
        }
        
        episodesGrid.innerHTML = episodesToShow.map(episode => this.generateEpisodeCard(episode)).join('');
        
        // Add event listeners to new episode cards
        this.setupEpisodeCardListeners();
        
        // Update pagination
        this.updatePagination();
        
        // Update episode count
        this.updateEpisodeCount();
        
        // Hide no results state
        this.hideNoResultsState();
    }

    generateEpisodeCard(episode) {
        return `
            <div class="episode-card" data-episode="${episode.id}">
                <div class="episode-image">
                    <img src="${episode.cover}" alt="Episode ${episode.number} Cover" loading="lazy">
                    <div class="episode-duration">${episode.duration}</div>
                    <button class="play-overlay" data-episode="${episode.id}" aria-label="Play episode">
                        <span class="play-icon">▶</span>
                    </button>
                </div>
                <div class="episode-content">
                    <div class="episode-meta">
                        <span class="episode-number">${episode.number.toString().padStart(3, '0')}</span>
                        <span class="episode-category">${this.formatCategoryName(episode.category)}</span>
                        <span class="episode-date">${this.formatDate(episode.date)}</span>
                    </div>
                    <h3 class="episode-title">${episode.title}</h3>
                    <p class="episode-description">${episode.description}</p>
                    <div class="episode-tags">
                        ${episode.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                    <div class="episode-actions">
                        <button class="btn-play" data-episode="${episode.id}">
                            <span class="play-icon">▶</span>
                            <span data-en="Play Now" data-hi="अभी सुनें">Play Now</span>
                        </button>
                        <button class="btn-download" data-episode="${episode.id}" aria-label="Download episode">
                            <span class="download-icon">⬇</span>
                        </button>
                        <button class="btn-share" data-episode="${episode.id}" aria-label="Share episode">
                            <span class="share-icon">📤</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    formatCategoryName(category) {
        return category.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            year: 'numeric' 
        });
    }

    setupEpisodeCardListeners() {
        // Re-setup audio player buttons for new cards
        this.setupAudioPlayer();
        
        // Setup episode card click to navigate
        document.querySelectorAll('.episode-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Don't navigate if clicking buttons
                if (e.target.closest('.episode-actions')) return;
                
                const episodeId = card.getAttribute('data-episode');
                window.location.href = `./episodes/episode-${episodeId}.html`;
            });
        });
    }

    updateEpisodeCount() {
        const episodeCountElement = document.getElementById('episodeCount');
        const totalEpisodesElement = document.getElementById('totalEpisodes');
        
        if (episodeCountElement) {
            episodeCountElement.textContent = this.filteredEpisodes.length;
        }
        
        if (totalEpisodesElement) {
            totalEpisodesElement.textContent = `${this.episodes.length}+`;
        }
    }

    showNoResultsState() {
        const noResultsState = document.getElementById('noResultsState');
        const episodesGrid = document.getElementById('episodesGrid');
        
        if (noResultsState) {
            noResultsState.style.display = 'block';
        }
        
        if (episodesGrid) {
            episodesGrid.style.display = 'none';
        }
    }

    hideNoResultsState() {
        const noResultsState = document.getElementById('noResultsState');
        const episodesGrid = document.getElementById('episodesGrid');
        
        if (noResultsState) {
            noResultsState.style.display = 'none';
        }
        
        if (episodesGrid) {
            episodesGrid.style.display = 'grid';
        }
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredEpisodes.length / this.episodesPerPage);
        const paginationContainer = document.getElementById('paginationContainer');
        const loadMoreContainer = document.getElementById('loadMoreContainer');
        
        // Show load more for mobile, pagination for desktop
        if (window.innerWidth <= 768) {
            if (loadMoreContainer && this.currentPage * this.episodesPerPage < this.filteredEpisodes.length) {
                loadMoreContainer.style.display = 'block';
                this.setupLoadMore();
            } else if (loadMoreContainer) {
                loadMoreContainer.style.display = 'none';
            }
            
            if (paginationContainer) {
                paginationContainer.style.display = 'none';
            }
        } else {
            if (paginationContainer && totalPages > 1) {
                paginationContainer.style.display = 'block';
                this.setupPagination(totalPages);
            } else if (paginationContainer) {
                paginationContainer.style.display = 'none';
            }
            
            if (loadMoreContainer) {
                loadMoreContainer.style.display = 'none';
            }
        }
    }

    setupLoadMore() {
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (!loadMoreBtn) return;
        
        loadMoreBtn.onclick = () => {
            this.episodesPerPage += 12;
            this.updateEpisodesDisplay();
        };
    }

    setupPagination(totalPages) {
        const prevPageBtn = document.getElementById('prevPage');
        const nextPageBtn = document.getElementById('nextPage');
        const paginationNumbers = document.getElementById('paginationNumbers');
        
        // Update prev/next buttons
        if (prevPageBtn) {
            prevPageBtn.disabled = this.currentPage === 1;
            prevPageBtn.onclick = () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.updateEpisodesDisplay();
                    this.scrollToTop();
                }
            };
        }
        
        if (nextPageBtn) {
            nextPageBtn.disabled = this.currentPage === totalPages;
            nextPageBtn.onclick = () => {
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.updateEpisodesDisplay();
                    this.scrollToTop();
                }
            };
        }
        
        // Update page numbers
        if (paginationNumbers) {
            const pageNumbers = [];
            const maxVisiblePages = 5;
            let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            if (endPage - startPage < maxVisiblePages - 1) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            for (let i = startPage; i <= endPage; i++) {
                pageNumbers.push(`
                    <button class="pagination-number ${i === this.currentPage ? 'active' : ''}" data-page="${i}">
                        ${i}
                    </button>
                `);
            }
            
            paginationNumbers.innerHTML = pageNumbers.join('');
            
            // Add click handlers
            paginationNumbers.querySelectorAll('.pagination-number').forEach(btn => {
                btn.addEventListener('click', () => {
                    this.currentPage = parseInt(btn.getAttribute('data-page'));
                    this.updateEpisodesDisplay();
                    this.scrollToTop();
                });
            });
        }
    }

    scrollToTop() {
        const episodesGrid = document.getElementById('episodesGrid');
        if (episodesGrid) {
            episodesGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // ===================================
    // Newsletter Form
    // ===================================
    
    setupNewsletterForm() {
        const newsletterForm = document.getElementById('newsletterForm');
        if (!newsletterForm) return;
        
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const emailInput = newsletterForm.querySelector('input[type="email"]');
            const email = emailInput?.value;
            
            if (!email || !this.isValidEmail(email)) {
                this.showPlayerNotification('Please enter a valid email address');
                return;
            }
            
            // Simulate newsletter signup
            this.subscribeToNewsletter(email);
            
            // Reset form
            emailInput.value = '';
            
            // Show success message
            this.showPlayerNotification('Successfully subscribed to newsletter!');
            
            // Analytics
            this.trackEvent('newsletter_signup', { email_domain: email.split('@')[1] });
        });
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    subscribeToNewsletter(email) {
        // TODO: Implement actual newsletter subscription
        console.log(`📧 Newsletter subscription: ${email}`);
        
        // Store in localStorage for now
        const subscribers = JSON.parse(localStorage.getItem('newsletter_subscribers') || '[]');
        if (!subscribers.includes(email)) {
            subscribers.push(email);
            localStorage.setItem('newsletter_subscribers', JSON.stringify(subscribers));
        }
    }

    // ===================================
    // Scroll Effects
    // ===================================
    
    setupScrollEffects() {
        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe elements that should animate in
        document.querySelectorAll('.episode-card, .feature, .category-card, .team-member').forEach(el => {
            observer.observe(el);
        });
        
        // Parallax effect for hero section
        const heroPattern = document.querySelector('.hero-pattern');
        if (heroPattern) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                heroPattern.style.transform = `translateY(${rate}px)`;
            });
        }
        
        // Progress bar for reading/listening
        this.setupReadingProgress();
    }

    setupReadingProgress() {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: var(--navbar-height);
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-orange), var(--secondary-yellow));
            z-index: 999;
            transition: width 0.1s ease;
        `;
        
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            
            progressBar.style.width = scrolled + '%';
        });
    }

    // ===================================
    // Accessibility & Keyboard Navigation
    // ===================================
    
    setupKeyboardNavigation() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Skip if user is typing in input
            if (e.target.tagName.toLowerCase() === 'input' || 
                e.target.tagName.toLowerCase() === 'textarea' ||
                e.target.isContentEditable) {
                return;
            }
            
            switch (e.key) {
                case '/':
                    e.preventDefault();
                    this.focusSearch();
                    break;
                case 'Escape':
                    this.closeModals();
                    break;
                case 't':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleTheme();
                    }
                    break;
                case 'l':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleLanguage();
                    }
                    break;
            }
        });
        
        // Skip link for screen readers
        this.addSkipLink();
        
        // Focus trap for modals
        this.setupFocusTrap();
        
        // ARIA live regions
        this.setupLiveRegions();
    }

    focusSearch() {
        const searchInput = document.getElementById('episodeSearch');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    closeModals() {
        // Close any open modals or dropdowns
        document.querySelectorAll('.modal, .dropdown-menu, .speed-menu').forEach(element => {
            element.style.display = 'none';
        });
        
        // Close mobile menu
        const navMenu = document.getElementById('navMenu');
        const navHamburger = document.getElementById('navHamburger');
        if (navMenu && navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            navHamburger.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    addSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    setupFocusTrap() {
        // Implementation for focus trapping in modals
        // This would be used when implementing modals
    }

    setupLiveRegions() {
        // Create ARIA live region for announcements
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        
        document.body.appendChild(liveRegion);
    }

    announceToScreenReader(message) {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }

    // ===================================
    // Utility Functions
    // ===================================
    
    showPlayerNotification(message) {
        // Create or update notification
        let notification = document.getElementById('player-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'player-notification';
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: var(--primary-orange);
                color: var(--primary-white);
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: var(--shadow-lg);
                z-index: 1000;
                transform: translateY(100px);
                opacity: 0;
                transition: all 0.3s ease;
                max-width: 300px;
                font-size: 14px;
            `;
            document.body.appendChild(notification);
        }
        
        notification.textContent = message;
        
        // Show notification
        requestAnimationFrame(() => {
            notification.style.transform = 'translateY(0)';
            notification.style.opacity = '1';
        });
        
        // Hide after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
        
        // Announce to screen readers
        this.announceToScreenReader(message);
    }

    showShareModal(url, title) {
        // Create share modal
        const modal = document.createElement('div');
        modal.className = 'share-modal';
        modal.innerHTML = `
            <div class="share-modal-content">
                <h3>Share Episode</h3>
                <div class="share-options">
                    <button class="share-option" data-platform="twitter">
                        <span class="share-icon">🐦</span>
                        Twitter
                    </button>
                    <button class="share-option" data-platform="facebook">
                        <span class="share-icon">📘</span>
                        Facebook
                    </button>
                    <button class="share-option" data-platform="linkedin">
                        <span class="share-icon">💼</span>
                        LinkedIn
                    </button>
                    <button class="share-option" data-platform="whatsapp">
                        <span class="share-icon">💬</span>
                        WhatsApp
                    </button>
                </div>
                <div class="share-url">
                    <input type="text" value="${url}" readonly>
                    <button class="copy-url-btn">Copy</button>
                </div>
                <button class="close-modal-btn">×</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('.close-modal-btn').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.copy-url-btn').addEventListener('click', () => {
            const input = modal.querySelector('input');
            input.select();
            document.execCommand('copy');
            this.showPlayerNotification('Link copied to clipboard!');
        });
        
        modal.querySelectorAll('.share-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const platform = btn.getAttribute('data-platform');
                this.shareToSocialPlatform(platform, url, title);
                modal.remove();
            });
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    shareToSocialPlatform(platform, url, title) {
        const shareUrls = {
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
            whatsapp: `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`
        };
        
        if (shareUrls[platform]) {
            window.open(shareUrls[platform], '_blank', 'width=600,height=400');
        }
    }

    isEpisodeBookmarked(episodeId) {
        const bookmarks = JSON.parse(localStorage.getItem('bookmarked_episodes') || '[]');
        return bookmarks.includes(episodeId);
    }

    addBookmark(episodeId) {
        const bookmarks = JSON.parse(localStorage.getItem('bookmarked_episodes') || '[]');
        if (!bookmarks.includes(episodeId)) {
            bookmarks.push(episodeId);
            localStorage.setItem('bookmarked_episodes', JSON.stringify(bookmarks));
        }
    }

    removeBookmark(episodeId) {
        const bookmarks = JSON.parse(localStorage.getItem('bookmarked_episodes') || '[]');
        const index = bookmarks.indexOf(episodeId);
        if (index > -1) {
            bookmarks.splice(index, 1);
            localStorage.setItem('bookmarked_episodes', JSON.stringify(bookmarks));
        }
    }

    getCurrentEpisodeId() {
        // Extract episode ID from current URL
        const pathMatch = window.location.pathname.match(/episode-(\d+)/);
        return pathMatch ? pathMatch[1] : null;
    }

    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    preloadCriticalResources() {
        // Preload critical images and fonts
        const criticalResources = [
            './images/logo.svg',
            './images/podcast-cover.jpg'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.svg') || resource.endsWith('.jpg') ? 'image' : 'font';
            if (link.as === 'font') {
                link.crossOrigin = 'anonymous';
            }
            document.head.appendChild(link);
        });
    }

    // ===================================
    // Analytics
    // ===================================
    
    setupAnalytics() {
        // Initialize analytics if available
        if (typeof gtag !== 'undefined') {
            this.analyticsEnabled = true;
            console.log('📊 Analytics initialized');
        } else {
            this.analyticsEnabled = false;
            console.log('📊 Analytics not available');
        }
        
        // Track page view
        this.trackPageView();
        
        // Track user engagement
        this.setupEngagementTracking();
    }

    trackEvent(eventName, parameters = {}) {
        if (!this.analyticsEnabled) {
            console.log(`📊 Event: ${eventName}`, parameters);
            return;
        }
        
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                ...parameters,
                timestamp: Date.now(),
                user_language: this.currentLanguage,
                user_theme: this.currentTheme
            });
        }
    }

    trackPageView() {
        const pageTitle = document.title;
        const pagePath = window.location.pathname;
        
        this.trackEvent('page_view', {
            page_title: pageTitle,
            page_location: window.location.href,
            page_path: pagePath
        });
    }

    setupEngagementTracking() {
        let startTime = Date.now();
        let isActiveTab = true;
        
        // Track time spent on page
        window.addEventListener('beforeunload', () => {
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);
            this.trackEvent('page_engagement', {
                time_spent_seconds: timeSpent,
                page_path: window.location.pathname
            });
        });
        
        // Track tab visibility
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                isActiveTab = false;
                const timeSpent = Math.floor((Date.now() - startTime) / 1000);
                this.trackEvent('tab_hidden', { time_spent_seconds: timeSpent });
            } else {
                isActiveTab = true;
                startTime = Date.now();
                this.trackEvent('tab_visible');
            }
        });
        
        // Track scroll depth
        let maxScrollDepth = 0;
        window.addEventListener('scroll', () => {
            const scrollDepth = Math.round(
                (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
            );
            
            if (scrollDepth > maxScrollDepth) {
                maxScrollDepth = scrollDepth;
                
                // Track milestone scroll depths
                if ([25, 50, 75, 90].includes(scrollDepth)) {
                    this.trackEvent('scroll_depth', {
                        depth_percentage: scrollDepth,
                        page_path: window.location.pathname
                    });
                }
            }
        });
    }

    // ===================================
    // Performance Monitoring
    // ===================================
    
    setupPerformanceMonitoring() {
        // Monitor Core Web Vitals
        if ('PerformanceObserver' in window) {
            // Largest Contentful Paint
            new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                
                this.trackEvent('web_vital_lcp', {
                    value: Math.round(lastEntry.startTime),
                    page_path: window.location.pathname
                });
            }).observe({ entryTypes: ['largest-contentful-paint'] });
            
            // First Input Delay
            new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach(entry => {
                    this.trackEvent('web_vital_fid', {
                        value: Math.round(entry.processingStart - entry.startTime),
                        page_path: window.location.pathname
                    });
                });
            }).observe({ entryTypes: ['first-input'] });
            
            // Cumulative Layout Shift
            let clsValue = 0;
            new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach(entry => {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                });
                
                this.trackEvent('web_vital_cls', {
                    value: Math.round(clsValue * 1000) / 1000,
                    page_path: window.location.pathname
                });
            }).observe({ entryTypes: ['layout-shift'] });
        }
        
        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                
                this.trackEvent('page_performance', {
                    load_time: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                    dom_content_loaded: Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart),
                    first_paint: Math.round(performance.getEntriesByType('paint')[0]?.startTime || 0),
                    page_path: window.location.pathname
                });
            }, 1000);
        });
    }
}

// ===================================
// Episode-specific JavaScript
// ===================================

class EpisodePlayer {
    constructor() {
        this.setupTabs();
        this.setupTranscriptSearch();
        this.setupCodeHighlighting();
        this.setupComments();
    }

    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-tab');
                
                // Update active button
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Update active content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === `${targetTab}Tab`) {
                        content.classList.add('active');
                    }
                });
                
                // Track tab view
                if (window.hindiTechPodcast) {
                    window.hindiTechPodcast.trackEvent('episode_tab_view', {
                        tab: targetTab,
                        episode_id: window.hindiTechPodcast.getCurrentEpisodeId()
                    });
                }
            });
        });
    }

    setupTranscriptSearch() {
        const searchBtn = document.getElementById('transcriptSearchBtn');
        const searchContainer = document.getElementById('transcriptSearch');
        const searchInput = document.querySelector('.transcript-search-input');
        
        if (searchBtn && searchContainer) {
            searchBtn.addEventListener('click', () => {
                const isVisible = searchContainer.style.display === 'block';
                searchContainer.style.display = isVisible ? 'none' : 'block';
                
                if (!isVisible) {
                    searchInput?.focus();
                }
            });
        }
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTranscript(e.target.value);
            });
        }
        
        // Clickable timestamps
        document.querySelectorAll('.transcript-segment .timestamp').forEach(timestamp => {
            timestamp.addEventListener('click', () => {
                const time = timestamp.getAttribute('data-time') || timestamp.textContent;
                this.seekToTime(time);
            });
        });
    }

    searchTranscript(query) {
        const segments = document.querySelectorAll('.transcript-segment');
        const searchResults = document.getElementById('searchResults');
        
        if (!query.trim()) {
            segments.forEach(segment => segment.style.display = 'flex');
            if (searchResults) searchResults.innerHTML = '';
            return;
        }
        
        let matchCount = 0;
        const results = [];
        
        segments.forEach(segment => {
            const text = segment.textContent.toLowerCase();
            const hasMatch = text.includes(query.toLowerCase());
            
            segment.style.display = hasMatch ? 'flex' : 'none';
            
            if (hasMatch) {
                matchCount++;
                results.push({
                    timestamp: segment.querySelector('.timestamp').textContent,
                    text: segment.querySelector('p').textContent.substring(0, 100) + '...'
                });
            }
        });
        
        if (searchResults) {
            searchResults.innerHTML = `
                <div class="search-results-summary">${matchCount} results found</div>
                ${results.slice(0, 5).map(result => `
                    <div class="search-result-item">
                        <span class="result-timestamp">${result.timestamp}</span>
                        <span class="result-text">${result.text}</span>
                    </div>
                `).join('')}
            `;
        }
    }

    seekToTime(timeStr) {
        // Convert time string to seconds and seek audio
        const audioElement = document.getElementById('audioElement');
        if (!audioElement) return;
        
        let seconds = 0;
        
        if (timeStr.includes(':')) {
            const parts = timeStr.split(':').map(Number);
            if (parts.length === 2) {
                seconds = parts[0] * 60 + parts[1];
            } else if (parts.length === 3) {
                seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
            }
        } else {
            seconds = parseInt(timeStr);
        }
        
        audioElement.currentTime = seconds;
        
        // Start playing if not already
        if (audioElement.paused) {
            audioElement.play();
        }
    }

    setupCodeHighlighting() {
        // Setup code tab navigation
        const codeTabBtns = document.querySelectorAll('.code-tab-btn');
        const codeSections = document.querySelectorAll('.code-section');
        
        codeTabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetCode = btn.getAttribute('data-code');
                
                // Update active button
                codeTabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Update active section
                codeSections.forEach(section => {
                    section.classList.remove('active');
                    if (section.id === targetCode) {
                        section.classList.add('active');
                    }
                });
            });
        });
        
        // Setup copy buttons
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-clipboard-target');
                const codeElement = document.querySelector(targetId);
                
                if (codeElement) {
                    const code = codeElement.textContent;
                    
                    navigator.clipboard.writeText(code).then(() => {
                        btn.innerHTML = '<span class="copy-icon">✓</span><span>Copied!</span>';
                        
                        setTimeout(() => {
                            btn.innerHTML = '<span class="copy-icon">📋</span><span data-en="Copy" data-hi="कॉपी">Copy</span>';
                        }, 2000);
                    }).catch(() => {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = code;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        
                        btn.innerHTML = '<span class="copy-icon">✓</span><span>Copied!</span>';
                        setTimeout(() => {
                            btn.innerHTML = '<span class="copy-icon">📋</span><span data-en="Copy" data-hi="कॉपी">Copy</span>';
                        }, 2000);
                    });
                }
            });
        });
    }

    setupComments() {
        const commentForm = document.querySelector('.comment-form');
        const commentInput = document.querySelector('.comment-input');
        const commentSubmit = document.querySelector('.comment-submit');
        
        if (commentForm) {
            commentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const comment = commentInput.value.trim();
                if (!comment) return;
                
                // TODO: Implement actual comment submission
                console.log('Comment submitted:', comment);
                
                // Show success message
                if (window.hindiTechPodcast) {
                    window.hindiTechPodcast.showPlayerNotification('Comment submitted successfully!');
                }
                
                // Clear form
                commentInput.value = '';
                
                // Track comment submission
                if (window.hindiTechPodcast) {
                    window.hindiTechPodcast.trackEvent('comment_submitted', {
                        episode_id: window.hindiTechPodcast.getCurrentEpisodeId(),
                        comment_length: comment.length
                    });
                }
            });
        }
    }
}

// ===================================
// Quick Access Sidebar
// ===================================

class QuickAccessSidebar {
    constructor() {
        this.isOpen = false;
        this.setup();
    }

    setup() {
        const toggleBtn = document.getElementById('quickAccessToggle');
        const sidebar = document.getElementById('quickAccessSidebar');
        const closeBtn = document.getElementById('sidebarClose');
        
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                this.toggle();
            });
        }
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.close();
            });
        }
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !sidebar?.contains(e.target) && 
                !toggleBtn?.contains(e.target)) {
                this.close();
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
        
        this.loadRecentSearches();
        this.loadBookmarkedEpisodes();
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        const sidebar = document.getElementById('quickAccessSidebar');
        if (sidebar) {
            sidebar.classList.add('active');
            this.isOpen = true;
            
            // Update recent data
            this.loadRecentSearches();
            this.loadBookmarkedEpisodes();
        }
    }

    close() {
        const sidebar = document.getElementById('quickAccessSidebar');
        if (sidebar) {
            sidebar.classList.remove('active');
            this.isOpen = false;
        }
    }

    loadRecentSearches() {
        const container = document.getElementById('recentSearches');
        if (!container) return;
        
        const recentSearches = JSON.parse(localStorage.getItem('recent_searches') || '[]');
        
        if (recentSearches.length === 0) {
            container.innerHTML = '<p class="empty-state">No recent searches</p>';
            return;
        }
        
        container.innerHTML = recentSearches.slice(0, 5).map(search => 
            `<div class="recent-search-item" data-search="${search}">
                <span class="search-icon">🔍</span>
                <span class="search-text">${search}</span>
            </div>`
        ).join('');
        
        // Add click handlers
        container.querySelectorAll('.recent-search-item').forEach(item => {
            item.addEventListener('click', () => {
                const search = item.getAttribute('data-search');
                this.performQuickSearch(search);
            });
        });
    }

    loadBookmarkedEpisodes() {
        const container = document.getElementById('bookmarkedEpisodes');
        if (!container) return;
        
        const bookmarks = JSON.parse(localStorage.getItem('bookmarked_episodes') || '[]');
        
        if (bookmarks.length === 0) {
            container.innerHTML = '<p class="empty-state">No bookmarked episodes</p>';
            return;
        }
        
        container.innerHTML = bookmarks.slice(0, 3).map(episodeId => 
            `<div class="bookmarked-episode-item" data-episode="${episodeId}">
                <span class="episode-icon">🎧</span>
                <span class="episode-text">Episode ${episodeId}</span>
            </div>`
        ).join('');
        
        // Add click handlers
        container.querySelectorAll('.bookmarked-episode-item').forEach(item => {
            item.addEventListener('click', () => {
                const episodeId = item.getAttribute('data-episode');
                window.location.href = `./episodes/episode-${episodeId}.html`;
            });
        });
    }

    performQuickSearch(query) {
        const searchInput = document.getElementById('episodeSearch');
        if (searchInput && window.hindiTechPodcast) {
            searchInput.value = query;
            window.hindiTechPodcast.searchQuery = query.toLowerCase();
            window.hindiTechPodcast.performSearch();
            this.close();
        }
    }
}

// ===================================
// Initialize Application
// ===================================

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main application
    window.hindiTechPodcast = new HindiTechPodcast();
    
    // Initialize episode player if on episode page
    if (document.querySelector('.episode-content-section')) {
        window.episodePlayer = new EpisodePlayer();
    }
    
    // Initialize quick access sidebar if on episodes page
    if (document.getElementById('quickAccessSidebar')) {
        window.quickAccessSidebar = new QuickAccessSidebar();
    }
    
    // Performance monitoring
    window.hindiTechPodcast.setupPerformanceMonitoring();
    
    console.log('🎉 Hindi Tech Podcast website fully loaded - Mumbai express style!');
});

// Service Worker registration for PWA functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
            .then(registration => {
                console.log('📱 Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('❌ Service Worker registration failed:', error);
            });
    });
}

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HindiTechPodcast, EpisodePlayer, QuickAccessSidebar };
}