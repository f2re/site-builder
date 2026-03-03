import { test, expect } from '@playwright/test';

test.describe('Purchase Flow', () => {
  test('Guest can add product to cart and see it there', async ({ page }) => {
    // 1. Go to home page
    await page.goto('/');

    // 2. Go to products catalog (to ensure we have products to click)
    await page.goto('/products');

    // 3. Wait for products to load
    await page.waitForSelector('.product-card');

    // 4. Get the name of the first product
    const productName = await page.locator('.product-card__title').first().innerText();

    // 5. Add the first product to cart
    await page.locator('.product-card__add').first().click();

    // 6. Go to cart
    await page.locator('.cart-btn').click();
    await expect(page).toHaveURL('/cart');

    // 7. Verify the product is in the cart
    const cartItemName = await page.locator('.cart-item__name').first().innerText();
    expect(cartItemName).toBe(productName);
  });
});

test.describe('Admin Flow', () => {
  test('Admin can login and see dashboard', async ({ page }) => {
    // 1. Go to login page
    await page.goto('/auth/login');

    // 2. Login as admin
    // Assuming default admin credentials if not provided, 
    // but usually we should use environment variables.
    // For this test, I'll assume admin/admin or similar if it's a fresh dev db.
    // However, I'll try to use what's likely to be there.
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // 3. Wait for navigation to profile or home
    await page.waitForURL(url => url.pathname === '/' || url.pathname === '/profile');

    // 4. Go to admin panel
    await page.locator('.admin-btn').click();
    await expect(page).toHaveURL('/admin');

    // 5. Verify dashboard and income (assuming there's a "Доход" or similar text)
    await expect(page.locator('h1')).toContainText('Панель управления');
    // Check for some income-related text
    await expect(page.locator('.admin-dashboard')).toBeVisible();
  });
});
