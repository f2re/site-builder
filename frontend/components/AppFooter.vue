<script setup lang="ts">
const footerLinks = [
  {
    title: 'Магазин',
    links: [
      { to: '/products', label: 'Каталог товаров' },
      { to: '/cart',     label: 'Корзина'        },
      { to: '/shipping', label: 'Доставка и оплата' },
    ],
  },
  {
    title: 'Информация',
    links: [
      { to: '/blog',     label: 'Блог и новости'   },
      { to: '/about',    label: 'О компании'       },
      { to: '/contact',  label: 'Обратная связь'   },
    ],
  },
  {
    title: 'Поддержка',
    links: [
      { to: '/faq',                         label: 'Вопросы и ответы'              },
      { to: '/returns',                     label: 'Возврат товара'                },
      { to: '/garantiynye-obyazatelstva',   label: 'Гарантийные обязательства'     },
      { to: '/dostavka',                    label: 'Доставка'                      },
      { to: '/politika-konfidentsialnosti', label: 'Политика конфиденциальности'   },
      { to: '/usloviya-soglasheniya',       label: 'Условия соглашения'            },
    ],
  },
]

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="footer__top">
      <div class="container footer__container">
        <!-- Brand -->
        <div class="footer__brand">
          <NuxtLink to="/" class="footer__logo">
            WIFI<span class="footer__logo-accent">OBD</span>
          </NuxtLink>
          <p class="footer__tagline">
            Профессиональное оборудование для диагностики и чип-тюнинга автомобилей.
          </p>
          <div class="footer__socials">
            <a href="#" class="footer__social-link" aria-label="Telegram">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7Z"/>
              </svg>
            </a>
            <a href="#" class="footer__social-link" aria-label="VK">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10Z"/><path d="m9 12 2 2 4-4"/>
              </svg>
            </a>
            <a href="#" class="footer__social-link" aria-label="YouTube">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 2-2 68.39 68.39 0 0 1 15 0 2 2 0 0 1 2 2 24.12 24.12 0 0 1 0 10 2 2 0 0 1-2 2 68.39 68.39 0 0 1-15 0 2 2 0 0 1-2-2Z"/><path d="m10 15 5-3-5-3v6Z"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Links -->
        <div class="footer__grid">
          <div v-for="section in footerLinks" :key="section.title" class="footer__section">
            <h3 class="footer__title">{{ section.title }}</h3>
            <ul class="footer__list">
              <li v-for="link in section.links" :key="link.to">
                <NuxtLink :to="link.to" class="footer__link">{{ link.label }}</NuxtLink>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom -->
    <div class="footer__bottom">
      <div class="container footer__bottom-container">
        <p class="footer__copyright">
          © {{ currentYear }} WifiOBD.shop. Все права защищены.
        </p>
        <div class="footer__payments">
          <div class="footer__payment-card">VISA</div>
          <div class="footer__payment-card">MasterCard</div>
          <div class="footer__payment-card">Mir</div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  margin-top: auto;
}

.footer__top {
  padding: 64px 0;
}

.footer__container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 64px;
}

.footer__brand {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.footer__logo {
  font-size: 28px;
  font-weight: 900;
  color: var(--color-text);
  text-decoration: none;
  letter-spacing: -1px;
}

.footer__logo-accent {
  color: var(--color-accent);
}

.footer__tagline {
  color: var(--color-text-2);
  line-height: 1.6;
  max-width: 320px;
}

.footer__socials {
  display: flex;
  gap: 12px;
}

.footer__social-link {
  width: 40px;
  height: 40px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-2);
  transition: all var(--transition-fast);
}

.footer__social-link:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow-accent);
}

.footer__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.footer__title {
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 24px;
}

.footer__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer__link {
  color: var(--color-text-2);
  text-decoration: none;
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.footer__link:hover {
  color: var(--color-accent);
}

.footer__bottom {
  border-top: 1px solid var(--color-border);
  padding: 24px 0;
  background-color: var(--color-bg-subtle);
}

.footer__bottom-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer__copyright {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.footer__payments {
  display: flex;
  gap: 12px;
}

.footer__payment-card {
  font-size: 10px;
  font-weight: 800;
  color: var(--color-muted);
  border: 1px solid var(--color-border);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}

/* Responsive */
@media (max-width: 1024px) {
  .footer__container {
    grid-template-columns: 1fr;
    gap: 48px;
  }
}

@media (max-width: 640px) {
  .footer__grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  .footer__bottom-container {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}
</style>
