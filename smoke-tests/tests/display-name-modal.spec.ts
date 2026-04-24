import { test, expect } from "@playwright/test";
import { generateSmokeTestToken } from "../lib/auth";
import jwt from "jsonwebtoken";

test.describe("Display Name Modal", () => {
  test("shows modal for user without display name", async ({ page }) => {
    // Create a token for a user without a display name
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");
    
    const now = Math.floor(Date.now() / 1000);
    const tokenWithoutDisplayName = jwt.sign(
      { sub: "smoke-test-no-display", iat: now, exp: now + 3600 },
      JWT_SECRET,
      { algorithm: "HS256" }
    );

    // Navigate and set auth without display name
    await page.goto("/");
    await page.evaluate(
      ([key, val]) => localStorage.setItem(key, val),
      ["ai_focus_groups_token", tokenWithoutDisplayName]
    );
    await page.reload();

    // Display name modal should appear
    const modal = page.locator('[data-testid="display-name-modal"]').or(
      page.locator('text=Welcome to PersonaComposer!')
    );
    await expect(modal).toBeVisible();

    // Should have display name input
    const displayNameInput = page.locator('input[id="display_name"]').or(
      page.locator('input[placeholder*="Alex"]')
    );
    await expect(displayNameInput).toBeVisible();

    // Should have submit button
    const submitButton = page.locator('button[type="submit"]').or(
      page.locator('text=Let\'s Go')
    );
    await expect(submitButton).toBeVisible();
  });

  test("can set display name through modal", async ({ page }) => {
    // Setup user without display name
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");
    
    const now = Math.floor(Date.now() / 1000);
    const tokenWithoutDisplayName = jwt.sign(
      { sub: "smoke-test-no-display", iat: now, exp: now + 3600 },
      JWT_SECRET,
      { algorithm: "HS256" }
    );

    await page.goto("/");
    await page.evaluate(
      ([key, val]) => localStorage.setItem(key, val),
      ["ai_focus_groups_token", tokenWithoutDisplayName]
    );
    await page.reload();

    // Fill display name
    const displayNameInput = page.locator('input[id="display_name"]').or(
      page.locator('input[placeholder*="Alex"]')
    );
    await displayNameInput.fill("SmokeTestUser");

    // Submit form
    const submitButton = page.locator('button[type="submit"]').or(
      page.locator('text=Let\'s Go')
    );
    await submitButton.click();

    // Modal should disappear
    const modal = page.locator('[data-testid="display-name-modal"]').or(
      page.locator('text=Welcome to PersonaComposer!')
    );
    await expect(modal).not.toBeVisible({ timeout: 5000 });

    // Should be able to access protected features
    await page.goto("/personas");
    await expect(page.locator("body")).not.toContainText("500");
  });

  test("blocks persona creation without display name", async ({ page }) => {
    // Setup user without display name
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");
    
    const now = Math.floor(Date.now() / 1000);
    const tokenWithoutDisplayName = jwt.sign(
      { sub: "smoke-test-no-display", iat: now, exp: now + 3600 },
      JWT_SECRET,
      { algorithm: "HS256" }
    );

    await page.goto("/");
    await page.evaluate(
      ([key, val]) => localStorage.setItem(key, val),
      ["ai_focus_groups_token", tokenWithoutDisplayName]
    );

    // Try to access persona creation directly (should redirect or show error)
    const response = await page.request.post("/personas", {
      headers: { Authorization: `Bearer ${tokenWithoutDisplayName}` },
      data: {
        name: "Test Persona",
        description: "Test description"
      }
    });
    
    expect(response.status()).toBe(403);
  });

  test("allows normal flow with display name set", async ({ page }) => {
    // Use normal auth injection (user with display name)
    const token = generateSmokeTestToken();
    await page.goto("/");
    await page.evaluate(
      ([key, val]) => localStorage.setItem(key, val),
      ["ai_focus_groups_token", token]
    );
    await page.reload();

    // Should NOT see display name modal
    const modal = page.locator('text=Welcome to PersonaComposer!');
    await expect(modal).not.toBeVisible();

    // Should be able to access protected pages
    await page.goto("/personas");
    await expect(page.locator("body")).not.toContainText("500");
  });
});