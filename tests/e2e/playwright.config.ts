import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 10000, // 10 sec timeout per test for fast feedback
  expect: {
    timeout: 5000
  },
  fullyParallel: false,
  retries: 0, // Retries managed autonomously by AI Self-Healing Engine
  workers: 1,
  reporter: [
    ['html', { outputFolder: '../../reports/playwright-report', open: 'never' }],
    ['list']
  ],
  use: {
    headless: true,
    actionTimeout: 5000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
