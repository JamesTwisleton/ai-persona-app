import { test, expect } from "@playwright/test";
import { generateSmokeTestToken } from "../lib/auth";
import jwt from "jsonwebtoken";

test.describe("Display Name Modal", () => {
  test("shows modal for user without display name", async ({ page }) => {
    // Create a token for a user without a display name
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");

    const now = Math.floor(Date.now() / 1000);
    const uniqueSub = `smoke-test-no-display-${Date.now()}-${Math.random()}`;
    const tokenWithoutDisplayName = jwt.sign(
      { sub: uniqueSub, iat: now, exp: now + 3600 },
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
    await expect(modal).toBeVisible({ timeout: 10000 });

    // Should have display name input
    const displayNameInput = modal.locator('input[id="display_name"]').or(
      modal.locator('[data-testid="display-name-input"]')
    );
    await expect(displayNameInput).toBeVisible();

    // Should have submit button specifically in modal
    const submitButton = modal.locator('button[type="submit"]').or(
      modal.locator('[data-testid="display-name-submit"]')
    );
    await expect(submitButton).toBeVisible();
  });

  test("can set display name through modal", async ({ page }) => {
    // Setup user without display name
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");

    const now = Math.floor(Date.now() / 1000);
    const uniqueSub = `smoke-test-no-display-${Date.now()}-${Math.random()}`;
    const tokenWithoutDisplayName = jwt.sign(
      { sub: uniqueSub, iat: now, exp: now + 3600 },
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
    const modal = page.locator('[data-testid="display-name-modal"]');
    const displayNameInput = modal.locator('input[id="display_name"]').or(
      modal.locator('[data-testid="display-name-input"]')
    );
    await displayNameInput.fill("SmokeTestUser");

    // Submit form - be specific to modal to avoid conflicts
    const submitButton = modal.locator('button[type="submit"]').or(
      modal.locator('[data-testid="display-name-submit"]')
    );
    await submitButton.click();

    // Modal should disappear
    await expect(modal).not.toBeVisible({ timeout: 10000 });

    // Should be able to access protected features
    await page.goto("/personas");
    await expect(page.locator("body")).not.toContainText("500");
  });

  test("blocks persona creation without display name", async ({ page }) => {
    // Setup user without display name
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");

    const now = Math.floor(Date.now() / 1000);
    const uniqueSub = `smoke-test-no-display-${Date.now()}-${Math.random()}`;
    const tokenWithoutDisplayName = jwt.sign(
      { sub: uniqueSub, iat: now, exp: now + 3600 },
      JWT_SECRET,
      { algorithm: "HS256" }
    );

    await page.goto("/");
    await page.evaluate(
      ([key, val]) => localStorage.setItem(key, val),
      ["ai_focus_groups_token", tokenWithoutDisplayName]
    );

    // Try to access persona creation API directly (should be blocked)
    const apiUrl = (process.env.SMOKE_TEST_API_URL || "https://persona-pr-115-be.fly.dev").replace(/\/$/, "");
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
