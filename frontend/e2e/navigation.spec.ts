import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Mock auth
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ token: 'mock-jwt-token' })
      });
    });
  });

  test('sidebar renders navigation items', async ({ page }) => {
    await page.goto('/chat');
    await expect(page.locator('nav')).toContainText('Chat');
    await expect(page.locator('nav')).toContainText('Pipelines');
    await expect(page.locator('nav')).toContainText('Usage');
    await expect(page.locator('nav')).toContainText('Settings');
  });

  test('navigation works', async ({ page }) => {
    await page.goto('/chat');
    await page.click('nav a:has-text("Usage")');
    await expect(page).toHaveURL(/.*usage.*/);
  });

  test('sidebar shows user email', async ({ page }) => {
    await page.goto('/chat');
    await expect(page.locator('nav')).toContainText('test@financecommander.com');
  });

  test('logout works', async ({ page }) => {
    await page.goto('/chat');
    await page.click('button:has-text("Logout")');
    await expect(page).toHaveURL(/.*login.*/);
  });
});