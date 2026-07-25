import { test, expect } from '@playwright/test';
import path from 'path';

const APP_URL = `file://${path.resolve(__dirname, 'app/fg_policy_portal.html')}`;

test.describe('F&G Policy & Annuity Core Automation Suite', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
  });

  test('TC-FG-101-01: Validate Fixed Index Annuity Base Premium & GLWB Rider Calculation', async ({ page }) => {
    // Step 1: fill on #premium-amount
    await page.locator("#premium-amount").fill("15000");
    // Step 2: fill on #applicant-age
    await page.locator("#applicant-age").fill("55");
    // Step 3: select on #rider-type
    await page.locator("#rider-type").selectOption("GLWB_PLUS");
    // Step 4: click on [data-testid='calculate-policy-btn']
    await page.locator("[data-testid='calculate-policy-btn']").click();
    await expect(page.locator("#tier-bonus-result")).toContainText("5%");
    await expect(page.locator("#rider-fee-result")).toContainText("$142.50");
    await expect(page.locator("#accum-value-result")).toContainText("$16,282.50");
  });

  test('TC-FG-102-01: Validate Annuity Policy Issuance Eligibility & Underwriting Rules', async ({ page }) => {
    // Step 1: fill on #applicant-age
    await page.locator("#applicant-age").fill("45");
    // Step 2: select on #applicant-state
    await page.locator("#applicant-state").selectOption("IA");
    // Step 3: fill on #suitability-score
    await page.locator("#suitability-score").fill("85");
    // Step 4: click on [data-testid='submit-eligibility']
    await page.locator("[data-testid='submit-eligibility']").click();
    await expect(page.locator("#status-badge")).toHaveText("APPROVED");
  });
});
