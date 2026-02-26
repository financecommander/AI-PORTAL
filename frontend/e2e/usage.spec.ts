import { test, expect } from '@playwright/test';

test.describe('Usage', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ token: 'mock-jwt-token' })
      });
    });

    await page.route('**/usage/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          logs: [
            { timestamp: '2023-01-01', specialist: 'analyst', tokens: 100, cost: 0.01, latency: 500 }
          ]
        })
      });
    });
  });

  test('usage page renders stats', async ({ page }) => {
    await page.goto('/usage');
    await expect(page.locator('text=Total Cost')).toBeVisible();
  });

  test('usage table shows entries', async ({ page }) => {
    await page.goto('/usage');
    await expect(page.locator('table')).toContainText('analyst');
  });

  test('tab switching works', async ({ page }) => {
    await page.goto('/usage');
    await page.click('text=Pipeline Runs');
    await expect(page.locator('text=Pipeline Runs')).toBeVisible();
  });
});