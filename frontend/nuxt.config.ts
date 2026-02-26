// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  
  modules: [
    '@pinia/nuxt',
  ],

  css: [
    '~/assets/css/tokens.css',
  ],

  app: {
    head: {
      htmlAttrs: {
        lang: 'ru',
      },
      script: [
        {
          children: `
            (function() {
              const theme = document.cookie.split('; ').find(row => row.startsWith('theme='))?.split('=')[1] || 'dark';
              document.documentElement.dataset.theme = theme;
            })();
          `,
          type: 'text/javascript',
        }
      ]
    },
  },

  typescript: {
    strict: true,
  },

  nitro: {
    compressPublicAssets: true,
  }
})
