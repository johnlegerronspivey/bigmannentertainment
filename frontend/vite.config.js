import { defineConfig, loadEnv, transformWithOxc } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// Plugin to handle JSX in .js files (CRA migration compat)
const transformJsxInJs = () => ({
  name: 'transform-jsx-in-js',
  enforce: 'pre',
  async transform(code, id) {
    if (!id.match(/.*\.js$/)) {
      return null;
    }
    return await transformWithOxc(code, id, {
      lang: 'jsx',
    });
  },
});

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'REACT_APP_');

  // Map process.env.REACT_APP_* to their values for CRA compat
  const processEnvDefine = {};
  for (const key in env) {
    processEnvDefine[`process.env.${key}`] = JSON.stringify(env[key]);
  }

  return {
    plugins: [react(), transformJsxInJs()],
    define: {
      ...processEnvDefine,
      'process.env.NODE_ENV': JSON.stringify(mode === 'production' ? 'production' : 'development'),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
      extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
    },
    server: {
      port: 3000,
      host: '0.0.0.0',
      allowedHosts: true,
      hmr: {
        port: 443,
        clientPort: 443,
        protocol: 'wss',
      },
    },
    build: {
      outDir: 'build',
      sourcemap: false,
      rolldownOptions: {
        moduleTypes: {
          '.js': 'jsx',
        },
      },
    },
    optimizeDeps: {
      rolldownOptions: {
        moduleTypes: {
          '.js': 'jsx',
        },
      },
    },
  };
});
