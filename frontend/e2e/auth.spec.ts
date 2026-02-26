import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('login page renders', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('invalid domain shows error', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Domain not authorized')).toBeVisible();
  });

  test('valid login redirects to chat', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@financecommander.com');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*chat.*/);
  });

  test('unauthenticated redirects to login', async ({ page }) => {
    await page.goto('/chat');
    await expect(page).toHaveURL(/.*login.*/);
  });

  test('logout clears session', async ({ page }) => {
    // Assume logged in
    await page.goto('/chat');
    await page.click('button:has-text("Logout")');
    await expect(page).toHaveURL(/.*login.*/);
  });
});