<script setup lang="ts">
const year = new Date().getFullYear()

const navColumns = [
  {
    title: 'Магазин',
    links: [
      { label: 'Каталог товаров', to: '/products' },
      { label: 'Новинки',         to: '/products?sort=new' },
      { label: 'Акции',           to: '/products?sale=1' },
      { label: 'Корзина',         to: '/cart' },
    ],
  },
  {
    title: 'Информация',
    links: [
      { label: 'Блог',            to: '/blog' },
      { label: 'О нас',           to: '/about' },
      { label: 'Доставка и оплата', to: '/delivery' },
      { label: 'Возврат товара',  to: '/returns' },
    ],
  },
  {
    title: 'Поддержка',
    links: [
      { label: 'Контакты',        to: '/contacts' },
      { label: 'FAQ',             to: '/faq' },
      { label: 'Гарантия',        to: '/warranty' },
    ],
  },
]

const socials = [
  {
    label: 'Telegram',
    href: 'https://t.me/wifiobd',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.447 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.333-.373-.12L7.17 13.956l-2.965-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.537-.194 1.006.131.983.603z"/></svg>`,
  },
  {
    label: 'VK',
    href: 'https://vk.com/wifiobd',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15.684 0H8.316C1.592 0 0 1.592 0 8.316v7.368C0 22.408 1.592 24 8.316 24h7.368C22.408 24 24 22.408 24 15.684V8.316C24 1.592 22.408 0 15.684 0zm3.692 17.123h-1.744c-.66 0-.864-.525-2.05-1.727-1.033-1-1.49-1.135-1.744-1.135-.356 0-.458.102-.458.593v1.575c0 .424-.135.678-1.253.678-1.846 0-3.896-1.118-5.335-3.202C4.624 10.857 4.03 8.57 4.03 8.096c0-.254.102-.491.593-.491h1.744c.44 0 .61.203.78.677.863 2.49 2.303 4.675 2.896 4.675.22 0 .322-.102.322-.66V9.721c-.068-1.186-.695-1.287-.695-1.71 0-.204.17-.407.44-.407h2.744c.373 0 .508.203.508.643v3.473c0 .372.17.508.271.508.22 0 .407-.136.813-.542 1.253-1.406 2.151-3.574 2.151-3.574.119-.254.322-.491.763-.491h1.744c.525 0 .644.27.525.643-.22 1.017-2.354 4.031-2.354 4.031-.186.305-.254.44 0 .78.186.254.796.779 1.203 1.253.745.847 1.32 1.558 1.473 2.05.17.491-.085.745-.576.745z"/></svg>`,
  },
  {
    label: 'YouTube',
    href: 'https://youtube.com/@wifiobd',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/></svg>`,
  },
]
</script>

<template>
  <footer class="footer">
    <div class="container">
      <!-- Top: brand + columns -->
      <div class="footer-top">
        <!-- Brand block -->
        <div class="footer-brand">
          <NuxtLink to="/" class="footer-logo">
            WifiOBD<span class="logo-accent">.shop</span>
          </NuxtLink>
          <p class="footer-tagline">
            Профессиональные OBD2 решения для диагностики и мониторинга автомобилей.
          </p>
          <!-- Socials -->
          <div class="socials">
            <a
              v-for="s in socials"
              :key="s.label"
              :href="s.href"
              class="social-link"
              :aria-label="s.label"
              target="_blank"
              rel="noopener noreferrer"
              v-html="s.icon"
            />
          </div>
          <!-- Contact -->
          <div class="footer-contact">
            <a href="tel:+78001234567" class="contact-link">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                aria-hidden="true">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.18h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.75a16 16 0 0 0 6 6l.95-.95a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
              </svg>
              8 800 123-45-67
            </a>
            <a href="mailto:support@wifiobd.shop" class="contact-link">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                aria-hidden="true">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              support@wifiobd.shop
            </a>
          </div>
        </div>

        <!-- Nav columns -->
        <nav class="footer-columns" aria-label="Навигация по сайту">
          <div
            v-for="col in navColumns"
            :key="col.title"
            class="footer-column"
          >
            <h3 class="column-title">{{ col.title }}</h3>
            <ul class="column-links">
              <li v-for="link in col.links" :key="link.to">
                <NuxtLink :to="link.to" class="column-link">{{ link.label }}</NuxtLink>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <!-- Bottom: legal -->
      <div class="footer-bottom">
        <p class="copyright">&copy; {{ year }} WifiOBD Shop. Все права защищены.</p>
        <div class="legal-links">
          <NuxtLink to="/privacy" class="legal-link">Политика конфиденциальности</NuxtLink>
          <NuxtLink to="/terms"   class="legal-link">Условия использования</NuxtLink>
          <NuxtLink to="/sitemap" class="legal-link">Карта сайта</NuxtLink>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--color-border);
  background-color: var(--color-surface);
  padding: 64px 0 0;
  margin-top: 80px;
}

.footer-top {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 48px;
  padding-bottom: 48px;
  border-bottom: 1px solid var(--color-border);
}

/* Brand */
.footer-logo {
  display: inline-block;
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.5px;
  margin-bottom: 12px;
  transition: opacity var(--transition-fast);
}
.footer-logo:hover { opacity: .8; }
.logo-accent { color: var(--color-accent); }

.footer-tagline {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  line-height: 1.6;
  margin-bottom: 20px;
}

.socials {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  color: var(--color-text-2);
  transition:
    color            var(--transition-fast),
    border-color     var(--transition-fast),
    background-color var(--transition-fast);
}

.social-link:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
  background-color: var(--color-surface-3);
}

.footer-contact {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}
.contact-link:hover { color: var(--color-accent); }

/* Columns */
.footer-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.column-title {
  font-size: var(--text-sm);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--color-text);
  margin-bottom: 16px;
}

.column-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.column-link {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}
.column-link:hover { color: var(--color-accent); }

/* Bottom */
.footer-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  flex-wrap: wrap;
  gap: 12px;
}

.copyright {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.legal-links {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legal-link {
  color: var(--color-muted);
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}
.legal-link:hover { color: var(--color-text-2); }

/* Responsive */
@media (max-width: 900px) {
  .footer-top {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .footer-columns {
    grid-template-columns: repeat(2, 1fr);
  }

  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
