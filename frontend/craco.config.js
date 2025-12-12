// Load configuration from environment or config file
const path = require('path');

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        
        // Disable watch mode
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      } else {
        // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }
      
      return webpackConfig;
    },
  },
  devServer: (devServerConfig) => {
    // Migrate from old webpack-dev-server v4 API to v5 API
    
    // Replace onBeforeSetupMiddleware and onAfterSetupMiddleware with setupMiddlewares
    if (devServerConfig.onBeforeSetupMiddleware || devServerConfig.onAfterSetupMiddleware) {
      const beforeSetup = devServerConfig.onBeforeSetupMiddleware;
      const afterSetup = devServerConfig.onAfterSetupMiddleware;
      
      delete devServerConfig.onBeforeSetupMiddleware;
      delete devServerConfig.onAfterSetupMiddleware;
      
      devServerConfig.setupMiddlewares = (middlewares, devServer) => {
        if (beforeSetup) {
          beforeSetup(devServer);
        }
        if (afterSetup) {
          afterSetup(devServer);
        }
        return middlewares;
      };
    }
    
    // Replace https option with server option
    if (devServerConfig.https !== undefined) {
      if (devServerConfig.https === true) {
        devServerConfig.server = 'https';
      } else if (devServerConfig.https === false) {
        devServerConfig.server = 'http';
      } else if (typeof devServerConfig.https === 'object') {
        devServerConfig.server = {
          type: 'https',
          options: devServerConfig.https,
        };
      }
      delete devServerConfig.https;
    }
    
    return devServerConfig;
  },
};