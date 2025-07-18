module.exports = async (page, scenario, vp) => {
  // Set dark mode by clicking the theme toggle button
  await page.evaluate(() => {
    // First try to click the theme toggle button
    const toggleButton = document.querySelector('[data-md-color-scheme-toggle]');
    if (toggleButton) {
      toggleButton.click();
    } else {
      // Fallback: directly set the data attribute
      document.documentElement.setAttribute('data-md-color-scheme', 'slate');
    }
  });
  
  // Wait for theme transition
  await page.waitForTimeout(500);
};