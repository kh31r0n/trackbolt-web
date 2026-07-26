// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// La URL canónica del sitio. `infra/desplegar.sh` la sobreescribe con el dominio
// de CloudFront para que el sitemap y las canónicas de la demo no apunten a producción.
const sitio = process.env.TRACKBOLT_URL || 'https://trackbolt.co';

export default defineConfig({
  site: sitio,
  integrations: [
    sitemap({
      // La vista interna no se indexa.
      filter: (page) => !page.includes('/interno'),
    }),
  ],
  build: { inlineStylesheets: 'auto' },
  compressHTML: true,
});
