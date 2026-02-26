import { test, expect } from '@playwright/test';

test.describe('Chat', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API routes
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ token: 'mock-jwt-token' })
      });
    });

    await page.route('**/specialists/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          specialists: [
            { id: 'financial-analyst', name: 'Financial Analyst', provider: 'anthropic' },
            { id: 'research-assistant', name: 'Research Assistant', provider: 'openai' }
          ]
        })
      });
    });

    await page.route('**/chat/send', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          content: 'Mock response',
          tokens_used: { prompt: 10, completion: 20, total: 30 },
          cost: 0.001
        })
      });
    });
  });

  test('chat page renders specialist selector', async ({ page }) => {
    // Assume logged in or mock
    await page.goto('/chat');
    await expect(page.locator('text=Financial Analyst')).toBeVisible();
  });

  test('clicking specialist shows chat interface', async ({ page }) => {
    await page.goto('/chat');
    await page.click('text=Financial Analyst');
    await expect(page.locator('text=Financial Analyst')).toBeVisible();
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('sending message shows response', async ({ page }) => {
    await page.goto('/chat');
    await page.click('text=Financial Analyst');
    await page.fill('input[type="text"]', 'Hello');
    await page.press('Enter');
    await expect(page.locator('text=Mock response')).toBeVisible();
  });

  // Add more tests as needed
});