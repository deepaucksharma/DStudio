---
title: Offline Mode
description: You're viewing this page offline
hide:
  - navigation
  - toc
  - footer
---

# 📡 You're Offline

<div style="text-align: center; padding: 2rem;">
  <span style="font-size: 5rem;">🔌</span>
  
  <h2>No Internet Connection</h2>
  
  <p style="font-size: 1.2rem; color: var(--md-default-fg-color--light);">
    It looks like you're offline. Some features may be limited.
  </p>
  
  <div style="margin: 2rem 0;">
    <h3>What You Can Do:</h3>
    <ul style="list-style: none; padding: 0;">
      <li>✅ View previously cached pages</li>
      <li>✅ Read downloaded content</li>
      <li>✅ Use keyboard shortcuts</li>
      <li>❌ Search functionality (limited)</li>
      <li>❌ Load new pages</li>
      <li>❌ View external resources</li>
    </ul>
  </div>
  
  <div style="margin-top: 3rem;">
    <button onclick="window.location.reload()" style="
      background: var(--md-primary-fg-color);
      color: var(--md-primary-bg-color);
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      font-size: 1rem;
      cursor: pointer;
    ">
      🔄 Try Again
    </button>
  </div>
  
  <div style="margin-top: 2rem;">
    <p>
      <strong>Tip:</strong> The Compendium works best with an internet connection, 
      but we've cached essential pages for offline reading.
    </p>
  </div>
</div>

<script>
// Check connection status periodically
setInterval(() => {
  if (navigator.onLine) {
    window.location.reload();
  }
}, 5000);

// Reload when connection is restored
window.addEventListener('online', () => {
  window.location.reload();
});
</script>

<style>
/* Center content vertically */
.md-content__inner {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
}
</style>