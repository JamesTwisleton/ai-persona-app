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
    const modal = page.locator('[data-testid="display-name-modal"]');
    await expect(modal).toBeVisible();

    // Should have display name input
    const displayNameInput = page.locator('input[id="display_name"]').or(
      page.locator('input[placeholder*="Alex"]')
    );
    await expect(displayNameInput).toBeVisible();

    // Should have submit button specifically in modal
    const submitButton = page.locator('[data-testid="display-name-modal"] button[type="submit"]').or(
      page.locator('text=Welcome to PersonaComposer!').locator('..').locator('button:has-text("Let\'s Go")')
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

    // Submit form - be specific to modal to avoid conflicts
    const submitButton = page.locator('[data-testid="display-name-modal"] button[type="submit"]').or(
      page.locator('text=Welcome to PersonaComposer!').locator('..').locator('button:has-text("Let\'s Go")')
    );
    await submitButton.click();

    // Modal should disappear
    const modal = page.locator('[data-testid="display-name-modal"]');
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

    // Try to access persona creation API directly (should be blocked)
    const apiUrl = process.env.SMOKE_TEST_API_URL || "https://persona-pr-115-be.fly.dev";
    const response = await page.request.post(`${apiUrl}/personas`, {
      headers: { 
        Authorization: `Bearer ${tokenWithoutDisplayName}`,
        "Content-Type": "application/json"
      },
      data: JSON.stringify({
        name: "Test Persona",
        description: "Test description",
        age: 30,
        gender: "Other"
      })
    });
    
    // Should be either 403 (Forbidden) or 422 (Validation Error)
    expect([403, 422].includes(response.status())).toBeTruthy();
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
    const modal = page.locator('[data-testid="display-name-modal"]');
    await expect(modal).not.toBeVisible();

    // Should be able to access protected pages
    await page.goto("/personas");
    await expect(page.locator("body")).not.toContainText("500");
  });
});