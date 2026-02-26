import { test, expect } from '@playwright/test';

test.describe('Pipelines', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ token: 'mock-jwt-token' })
      });
    });

    await page.route('**/pipelines/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          pipelines: [{ name: 'lex-intelligence', description: 'Legal research' }]
        })
      });
    });

    await page.route('**/pipelines/run', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          pipeline_id: 'test-id',
          status: 'running'
        })
      });
    });
  });

  test('pipelines page shows cards', async ({ page }) => {
    await page.goto('/pipelines');
    await expect(page.locator('text=lex-intelligence')).toBeVisible();
  });

  test('clicking pipeline shows input', async ({ page }) => {
    await page.goto('/pipelines');
    await page.click('text=lex-intelligence');
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('submitting query shows progress', async ({ page }) => {
    await page.goto('/pipelines');
    await page.click('text=lex-intelligence');
    await page.fill('input[type="text"]', 'Test query');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=running')).toBeVisible();
  });
});