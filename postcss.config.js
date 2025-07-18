module.exports = {
  plugins: [
    // Import statements
    require('postcss-import')({
      path: ['docs/stylesheets']
    }),
    
    // Modern CSS features
    require('postcss-preset-env')({
      stage: 1,
      features: {
        'custom-properties': false, // Keep custom properties
        'nesting-rules': true,
        'custom-media-queries': true,
        'is-pseudo-class': true
      }
    }),
    
    // Autoprefixer for browser compatibility
    require('autoprefixer')({
      grid: true
    }),
    
    // Minification for production
    ...(process.env.NODE_ENV === 'production' ? [
      require('cssnano')({
        preset: ['default', {
          discardComments: {
            removeAll: true
          },
          normalizeWhitespace: true
        }]
      })
    ] : [])
  ]
};