// Progressive Disclosure Component
document.addEventListener('DOMContentLoaded', () => {
  // Initialize all progressive disclosure components
  const disclosures = document.querySelectorAll('.progressive-disclosure');
  
  disclosures.forEach(disclosure => {
    const header = disclosure.querySelector('.disclosure-header');
    const content = disclosure.querySelector('.disclosure-content');
    
    if (header && content) {
      header.addEventListener('click', () => {
        const isActive = header.classList.contains('active');
        
        // Toggle active state
        header.classList.toggle('active');
        content.classList.toggle('active');
        
      });
      
      
      // Add keyboard support
      header.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          header.click();
        }
      });
    }
  });
  
  // Auto-expand if URL has a hash matching a disclosure
  const hash = window.location.hash;
  if (hash) {
    const targetDisclosure = document.querySelector(hash);
    if (targetDisclosure && targetDisclosure.classList.contains('progressive-disclosure')) {
      const header = targetDisclosure.querySelector('.disclosure-header');
      if (header) {
        setTimeout(() => header.click(), 300);
      }
    }
  }
});

// Smooth scroll to disclosure when linked
document.addEventListener('click', (e) => {
  const link = e.target.closest('a[href^="#"]');
  if (link) {
    const targetId = link.getAttribute('href');
    const targetDisclosure = document.querySelector(targetId);
    
    if (targetDisclosure && targetDisclosure.classList.contains('progressive-disclosure')) {
      e.preventDefault();
      
      // Scroll to element
      targetDisclosure.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Open disclosure if closed
      const header = targetDisclosure.querySelector('.disclosure-header');
      if (header && !header.classList.contains('active')) {
        setTimeout(() => header.click(), 500);
      }
      
      // Update URL
      window.history.pushState(null, null, targetId);
    }
  }
});