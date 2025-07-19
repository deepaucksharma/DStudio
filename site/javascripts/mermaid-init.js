// Initialize Mermaid diagrams
document.addEventListener('DOMContentLoaded', function() {
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      themeVariables: {
        primaryColor: '#5448C8',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#5448C8',
        lineColor: '#6366f1',
        sectionBkgColor: '#f8fafc',
        altSectionBkgColor: '#f1f5f9',
        gridColor: '#e2e8f0',
        secondaryColor: '#00BCD4',
        tertiaryColor: '#f3f4f6'
      }
    });
  }
});