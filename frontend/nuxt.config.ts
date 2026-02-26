// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },

  modules: [
    '@pinia/nuxt',
  ],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
    },
  },

  css: [
    '~/assets/css/tokens.css',
    '~/assets/css/main.css',   // global container + utility classes
  ],

  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { charset: 'utf-8' },
      ],
      link: [
        // Preconnect for Inter font
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap',
        },
      ],
      script: [
        {
          // Anti-FOUC: read theme from cookie before first paint
          children: `(function(){var t=document.cookie.split('; ').find(function(r){return r.startsWith('theme=')});document.documentElement.dataset.theme=t?t.split('=')[1]:'dark';})();`,
          type: 'text/javascript',
        },
      ],
    },
    pageTransition: { name: 'fade-slide', mode: 'out-in' },
  },

  typescript: {
    strict: true,
  },

  nitro: {
    compressPublicAssets: true,
  },
})
