// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },

  modules: [
    '@pinia/nuxt',
    '@nuxt/image',
    '@nuxt/icon'
  ],

  image: {
    domains: [
      'localhost:8000',
      'localhost:3000',
      '127.0.0.1:8000',
      'backend',
      'sb_api',
      'wifiobd.ru',
      'm.wifiobd.ru',
      'media.wifiobd.ru'
    ],
    alias: {
      // Allows using src="/media/..." which resolves correctly in all environments.
      // We prioritize the environment variable if available, otherwise use a relative path
      // that IPX can resolve locally if the volume is mounted.
      '/media': (process.env.NUXT_PUBLIC_API_BASE || '').replace('/api/v1', '') + '/media'
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://wifiobd.ru',
      telegramBotName: process.env.NUXT_PUBLIC_TELEGRAM_BOT_NAME || process.env.TELEGRAM_BOT_NAME || 'WifiOBD_Bot',
    },
  },

  css: [
    '~/assets/css/tokens.css',
    '~/assets/css/main.css',
  ],

  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      title: 'WifiOBD — Оборудование для диагностики авто',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { charset: 'utf-8' },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'theme-color', content: '#e63946' },
        { name: 'apple-mobile-web-app-title', content: 'WifiOBD2' },
        { property: 'og:site_name', content: 'WifiOBD' },
        { property: 'og:type', content: 'website' },
        { name: 'twitter:card', content: 'summary_large_image' },
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon-96x96.png', sizes: '96x96' },
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'shortcut icon', href: '/favicon.ico' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap',
        },
      ],
      script: [
        {
          innerHTML: `(function(){var t=localStorage.getItem('theme');var s=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t||s);})();`,
          type: 'text/javascript',
        },
      ],
    },
    pageTransition: { name: 'fade-slide', mode: 'out-in' },
  },

  typescript: {
    strict: true,
  },

  routeRules: {
    '/shop': { redirect: '/products' },
    '/shop/**': { redirect: '/products/**' },
    '/admin/products/new': { redirect: '/admin/products/create' },
  },

  nitro: {
    compressPublicAssets: true,
    devProxy: {
      // Nitro strips the key prefix before forwarding, so target must include '/media'
      // to reconstruct: /media/product/x.png → strips '/media' → /product/x.png
      // → appended to target 'http://localhost:8000/media' → correct path
      '/media': {
        target: (process.env.NUXT_PUBLIC_API_BASE
          ? process.env.NUXT_PUBLIC_API_BASE.replace('/api/v1', '')
          : 'http://localhost:8000') + '/media',
        changeOrigin: true,
      },
    },
  },

  icon: {
    // Local bundling for performance and reliability
    serverBundle: 'local',
    collections: ['ph', 'logos', 'simple-icons'],
    endpoint: '/_nuxt_icon'
  }
})
