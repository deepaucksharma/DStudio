// Custom JavaScript for DStudio Documentation

// Enhanced copy code functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add line numbers toggle for code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const pre = block.parentElement;
        if (pre.classList.contains('highlight')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'line-numbers-toggle';
            toggleBtn.textContent = 'Toggle Line Numbers';
            toggleBtn.onclick = () => {
                pre.classList.toggle('no-line-numbers');
            };
            pre.insertBefore(toggleBtn, pre.firstChild);
        }
    });

    // Enhanced search with keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.blur();
            }
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // Add progress indicator for long pages
    const createProgressIndicator = () => {
        const progress = document.createElement('div');
        progress.className = 'reading-progress';
        progress.innerHTML = '<div class="reading-progress-bar"></div>';
        document.body.appendChild(progress);

        const updateProgress = () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            document.querySelector('.reading-progress-bar').style.width = scrolled + '%';
        };

        window.addEventListener('scroll', updateProgress);
        updateProgress();
    };

    // Only add progress indicator for pages with substantial content
    if (document.querySelector('.md-content__inner').scrollHeight > window.innerHeight * 2) {
        createProgressIndicator();
    }

    // Enhanced table functionality
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        // Make tables responsive
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);

        // Add search functionality to large tables
        if (table.rows.length > 10) {
            const searchBox = document.createElement('input');
            searchBox.type = 'text';
            searchBox.className = 'table-search';
            searchBox.placeholder = 'Search table...';
            
            searchBox.addEventListener('input', function() {
                const filter = this.value.toLowerCase();
                const rows = table.getElementsByTagName('tr');
                
                for (let i = 1; i < rows.length; i++) {
                    const cells = rows[i].getElementsByTagName('td');
                    let found = false;
                    
                    for (let j = 0; j < cells.length; j++) {
                        if (cells[j].textContent.toLowerCase().includes(filter)) {
                            found = true;
                            break;
                        }
                    }
                    
                    rows[i].style.display = found ? '' : 'none';
                }
            });
            
            wrapper.insertBefore(searchBox, table);
        }
    });

    // Add expandable sections for deeply nested navigation
    const nestedNavItems = document.querySelectorAll('.md-nav__item--nested');
    nestedNavItems.forEach(item => {
        const toggle = item.querySelector('.md-nav__toggle');
        if (toggle) {
            // Save expansion state
            const navPath = item.querySelector('.md-nav__link').getAttribute('href');
            const isExpanded = localStorage.getItem(`nav-expanded-${navPath}`);
            
            if (isExpanded === 'true') {
                toggle.checked = true;
            }
            
            toggle.addEventListener('change', function() {
                localStorage.setItem(`nav-expanded-${navPath}`, this.checked);
            });
        }
    });

    // Enhanced print functionality
    window.addEventListener('beforeprint', function() {
        // Expand all collapsible sections
        document.querySelectorAll('details').forEach(details => {
            details.setAttribute('open', '');
        });
        
        // Show all tabbed content
        document.querySelectorAll('.tabbed-content').forEach(tabbed => {
            tabbed.classList.add('print-all-tabs');
        });
    });

    window.addEventListener('afterprint', function() {
        // Restore original state
        document.querySelectorAll('details[open]').forEach(details => {
            if (!details.hasAttribute('data-was-open')) {
                details.removeAttribute('open');
            }
        });
        
        document.querySelectorAll('.tabbed-content').forEach(tabbed => {
            tabbed.classList.remove('print-all-tabs');
        });
    });
});

// Mermaid theme synchronization
document$.subscribe(() => {
    const mermaidElements = document.querySelectorAll('.mermaid');
    if (mermaidElements.length > 0 && typeof mermaid !== 'undefined') {
        const isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
        mermaid.initialize({
            theme: isDark ? 'dark' : 'default',
            themeVariables: {
                primaryColor: '#5448C8',
                primaryTextColor: isDark ? '#ffffff' : '#000000',
                primaryBorderColor: '#5448C8',
                lineColor: '#6366f1',
                sectionBkgColor: isDark ? '#1e293b' : '#f8fafc',
                altSectionBkgColor: isDark ? '#334155' : '#f1f5f9',
                gridColor: isDark ? '#475569' : '#e2e8f0',
                secondaryColor: '#00BCD4',
                tertiaryColor: isDark ? '#475569' : '#f3f4f6'
            }
        });
    }
});