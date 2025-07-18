const path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const { GenerateSW } = require('workbox-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

const isDevelopment = process.env.NODE_ENV !== 'production';

module.exports = {
  mode: isDevelopment ? 'development' : 'production',
  devtool: isDevelopment ? 'source-map' : false,
  
  entry: {
    // Core bundle
    app: './docs/javascripts/core/app.js',
    
    // Separate bundles for different sections
    tools: [
      './docs/javascripts/tools/latency-calculator.js',
      './docs/javascripts/tools/capacity-planner.js',
      './docs/javascripts/tools/consistency-visualizer.js',
      './docs/javascripts/tools/cap-explorer.js',
      './docs/javascripts/tools/failure-calculator.js',
      './docs/javascripts/tools/coordination-cost.js'
    ],
    
    // Vendor bundle
    vendor: ['chart.js', 'd3', 'mermaid']
  },
  
  output: {
    path: path.resolve(__dirname, 'site/assets/js'),
    filename: isDevelopment ? '[name].js' : '[name].[contenthash].js',
    chunkFilename: isDevelopment ? '[name].chunk.js' : '[name].[contenthash].chunk.js',
    publicPath: '/assets/js/'
  },
  
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            cacheDirectory: true
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader'
        ]
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
        generator: {
          filename: '../images/[name].[hash][ext]'
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: '../fonts/[name].[hash][ext]'
        }
      }
    ]
  },
  
  plugins: [
    new CleanWebpackPlugin(),
    
    new MiniCssExtractPlugin({
      filename: isDevelopment ? '../css/[name].css' : '../css/[name].[contenthash].css',
      chunkFilename: isDevelopment ? '../css/[id].css' : '../css/[id].[contenthash].css'
    }),
    
    // Define environment variables
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
      'process.env.VERSION': JSON.stringify(require('./package.json').version)
    }),
    
    // Generate service worker
    !isDevelopment && new GenerateSW({
      clientsClaim: true,
      skipWaiting: true,
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.googleapis\.com/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'google-fonts-stylesheets'
          }
        },
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-webfonts',
            expiration: {
              maxEntries: 30,
              maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
            }
          }
        },
        {
          urlPattern: /\.(?:png|gif|jpg|jpeg|webp|svg)$/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'images',
            expiration: {
              maxEntries: 60,
              maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
            }
          }
        }
      ]
    }),
    
    // Bundle analyzer (only in analyze mode)
    process.env.ANALYZE && new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      generateStatsFile: true
    })
  ].filter(Boolean),
  
  optimization: {
    minimize: !isDevelopment,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: !isDevelopment,
            drop_debugger: !isDevelopment
          },
          format: {
            comments: false
          }
        },
        extractComments: false
      })
    ],
    
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
          reuseExistingChunk: true
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true
        }
      }
    },
    
    runtimeChunk: 'single',
    
    moduleIds: 'deterministic'
  },
  
  performance: {
    hints: isDevelopment ? false : 'warning',
    maxAssetSize: 250000, // 250kb
    maxEntrypointSize: 400000 // 400kb
  },
  
  resolve: {
    extensions: ['.js', '.json'],
    alias: {
      '@': path.resolve(__dirname, 'docs/javascripts'),
      '@core': path.resolve(__dirname, 'docs/javascripts/core'),
      '@components': path.resolve(__dirname, 'docs/javascripts/components'),
      '@tools': path.resolve(__dirname, 'docs/javascripts/tools'),
      '@utils': path.resolve(__dirname, 'docs/javascripts/utils')
    }
  },
  
  // Development server configuration
  devServer: {
    static: {
      directory: path.join(__dirname, 'site')
    },
    compress: true,
    hot: true,
    port: 9000,
    proxy: {
      '/': 'http://localhost:8000'
    }
  }
};