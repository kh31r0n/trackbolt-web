// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://trackbolt.co',
  integrations: [
    sitemap({
      // La vista interna no se indexa.
      filter: (page) => !page.includes('/interno'),
    }),
  ],
  build: { inlineStylesheets: 'auto' },
  compressHTML: true,
});
