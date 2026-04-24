import { test, expect } from "@playwright/test";
import { generateSmokeTestToken } from "../lib/auth";
import jwt from "jsonwebtoken";

test.describe("Display Name Modal", () => {
  test("shows modal for user without display name", async ({ page }) => {
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

    const modal = page.locator('[data-testid="display-name-modal"]');
    await expect(modal).toBeVisible({ timeout: 10000 });

    const displayNameInput = modal.locator('input[id="display_name"]').or(
      modal.locator('[data-testid="display-name-input"]')
    );
    await expect(displayNameInput).toBeVisible();

    const submitButton = modal.locator('button[type="submit"]').or(
      modal.locator('[data-testid="display-name-submit"]')
    );
    await expect(submitButton).toBeVisible();
  });

  test("can set display name through modal", async ({ page }) => {
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

    const modal = page.locator('[data-testid="display-name-modal"]');
    const displayNameInput = modal.locator('input[id="display_name"]').or(
      modal.locator('[data-testid="display-name-input"]')
    );
    await displayNameInput.fill("SmokeTestUser");

    const submitButton = modal.locator('button[type="submit"]').or(
      modal.locator('[data-testid="display-name-submit"]')
    );
    await submitButton.click();

    await expect(modal).not.toBeVisible({ timeout: 10000 });
  });

  test("blocks persona creation without display name", async ({ page }) => {
    const JWT_SECRET = process.env.JWT_SECRET;
    if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");

    const now = Math.floor(Date.now() / 1000);
    const tokenWithoutDisplayName = jwt.sign(
      { sub: "smoke-test-no-display", iat: now, exp: now + 3600 },
      JWT_SECRET,
      { algorithm: "HS256" }
    );

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

    expect([403, 422].includes(response.status())).toBeTruthy();
  });

  test("allows normal flow with display name set", async ({ page }) => {
    const token = generateSmokeTestToken();
    await page.goto("/");
    await page.evaluate(
      ([key, val]) => localStorage.setItem(key, val),
      ["ai_focus_groups_token", token]
    );
    await page.reload();

    const modal = page.locator('[data-testid="display-name-modal"]');
    await expect(modal).not.toBeVisible();
  });
});
