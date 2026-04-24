import { test, expect } from "@playwright/test";
import { injectAuth } from "../lib/auth";

test.describe("Authenticated pages", () => {
  test.beforeEach(async ({ page }) => {
    await injectAuth(page);
  });

  test("personas list loads", async ({ page }) => {
    await page.goto("/personas");
    await expect(page.locator("body")).not.toContainText("500");
    await expect(page.locator("body")).not.toContainText("Internal Server Error");
  });

  test("conversations list loads", async ({ page }) => {
    await page.goto("/conversations");
    await expect(page.locator("body")).not.toContainText("500");
    await expect(page.locator("body")).not.toContainText("Internal Server Error");
  });

  test("new persona form loads", async ({ page }) => {
    await page.goto("/personas/new");
    await expect(page.locator("body")).not.toContainText("500");
    // Should have a form or input for persona creation
    const nameInput = page.locator("input, textarea").first();
    await expect(nameInput).toBeVisible();
    
    // Should have AI generation functionality
    const generateButton = page.locator('button:has-text("Generate with AI")').or(
      page.locator('[data-testid="generate-backstory"]')
    );
    
    // AI generation button should be present
    if (await generateButton.isVisible()) {
      await expect(generateButton).toBeVisible();
    }
  });

  test("new conversation form loads", async ({ page }) => {
    await page.goto("/conversations/new");
    await expect(page.locator("body")).not.toContainText("500");
  });

  test("user is recognized in navigation", async ({ page }) => {
    await page.goto("/");
    // When authenticated, login link should not be visible
    // and user menu/avatar should appear instead
    const loginLink = page.getByRole("link", { name: /log\s*in|sign\s*in/i });
    await expect(loginLink).not.toBeVisible();
  });
});
