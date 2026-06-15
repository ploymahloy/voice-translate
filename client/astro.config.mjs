// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  vite: {
    server: {
      proxy: {
        '/translate': {
          target: 'http://3.211.23.246:8000/',
          changeOrigin: true,
        },
      },
    },
  },
});
