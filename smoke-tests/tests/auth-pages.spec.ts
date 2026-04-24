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
  });

  test("new conversation form loads", async ({ page }) => {
    await page.goto("/conversations/new");
    await expect(page.locator("body")).not.toContainText("500");
  });

  test("user is recognized in navigation", async ({ page }) => {
    await page.goto("/");
    
    // When authenticated, login buttons should not be visible
    // Look for sign in buttons (now uses modal instead of links)
    const signInButton = page.getByRole("button", { name: /log\s*in|sign\s*in/i });
    const loginLink = page.getByRole("link", { name: /log\s*in|sign\s*in/i });
    
    // Neither should be visible when authenticated
    await expect(signInButton).not.toBeVisible();
    await expect(loginLink).not.toBeVisible();
  });
});
