// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  vite: {
    server: {
      proxy: {
        '/translate': {
          target: 'http://34.201.102.73',
          changeOrigin: true,
        },
      },
    },
  },
});
