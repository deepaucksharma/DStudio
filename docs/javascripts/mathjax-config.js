window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true,
    processRefs: true,
    packages: {
      '[+]': ['boldsymbol', 'mathtools', 'physics', 'ams', 'color', 'cancel', 'cases']
    },
    macros: {
      // Common mathematical operations
      argmax: '\\operatorname{arg\\,max}',
      argmin: '\\operatorname{arg\\,min}',
      // Distributed systems specific
      latency: '\\mathcal{L}',
      throughput: '\\mathcal{T}',
      availability: '\\mathcal{A}',
      consistency: '\\mathcal{C}',
      partition: '\\mathcal{P}',
      // Probability and statistics
      E: '\\mathbb{E}',
      Var: '\\operatorname{Var}',
      Cov: '\\operatorname{Cov}',
      Pr: '\\operatorname{Pr}',
      // Complexity notations
      BigO: '\\mathcal{O}',
      BigOmega: '\\Omega',
      BigTheta: '\\Theta',
      // Vector and matrix operations
      norm: ['\\lVert #1 \\rVert', 1],
      abs: ['\\lvert #1 \\rvert', 1],
      // Common sets
      R: '\\mathbb{R}',
      N: '\\mathbb{N}',
      Z: '\\mathbb{Z}',
      Q: '\\mathbb{Q}',
      C: '\\mathbb{C}'
    },
    tags: 'ams',
    tagSide: 'right',
    tagIndent: '0.8em',
    multlineWidth: '85%',
    useLabelIds: true
  },
  chtml: {
    scale: 1,
    displayAlign: 'center',
    displayIndent: '0',
    minScale: 0.5,
    mtextInheritFont: false,
    merrorInheritFont: true,
    merrorFont: 'serif',
    unknownFamily: 'serif',
    fontURL: 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2',
    adaptiveCSS: true
  },
  svg: {
    scale: 1,
    displayAlign: 'center',
    displayIndent: '0',
    minScale: 0.5,
    mtextInheritFont: false,
    merrorInheritFont: true,
    merrorFont: 'serif',
    unknownFamily: 'serif',
    fontCache: 'global'
  },
  loader: {
    load: ['[tex]/boldsymbol', '[tex]/mathtools', '[tex]/physics', '[tex]/ams', '[tex]/color', '[tex]/cancel', '[tex]/cases']
  },
  startup: {
    ready: () => {
      MathJax.startup.defaultReady();
      MathJax.startup.document.inputJax[0].preFilters.add(({math}) => {
        if (math.display === false) {
          math.math = '\\displaystyle{' + math.math + '}';
        }
      });
    }
  }
};