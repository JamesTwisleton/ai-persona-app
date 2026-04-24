import jwt from "jsonwebtoken";
import { Page } from "@playwright/test";

const JWT_SECRET = process.env.JWT_SECRET;
const TOKEN_KEY = "ai_focus_groups_token";

export function generateSmokeTestToken(userId?: string): string {
  const id = userId || process.env.SMOKE_TEST_USER_ID;
  if (!id) throw new Error("SMOKE_TEST_USER_ID env var is required");
  if (!JWT_SECRET) throw new Error("JWT_SECRET env var is required");

  const now = Math.floor(Date.now() / 1000);
  return jwt.sign(
    { sub: id, iat: now, exp: now + 3600 },
    JWT_SECRET,
    { algorithm: "HS256" },
  );
}

export async function injectAuth(page: Page, userId?: string): Promise<void> {
  const token = generateSmokeTestToken(userId);
  const baseURL = page.context().browser()?.contexts()[0]?.pages()[0]?.url()
    || process.env.SMOKE_TEST_BASE_URL
    || "https://personacomposer.app";

  // Navigate to the app first so localStorage is scoped to the correct origin
  await page.goto("/");
  await page.evaluate(
    ([key, val]) => localStorage.setItem(key, val),
    [TOKEN_KEY, token],
  );
  await page.reload();
  
  // Handle display name modal if it appears
  const displayNameModal = page.locator('text=Welcome to PersonaComposer!');
  if (await displayNameModal.isVisible({ timeout: 2000 }).catch(() => false)) {
    const displayNameInput = page.locator('input[id="display_name"]').or(
      page.locator('input[placeholder*="Alex"]')
    );
    await displayNameInput.fill("SmokeTestUser");
    const submitButton = page.locator('button[type="submit"]').or(
      page.locator('text=Let\'s Go')
    );
    await submitButton.click();
    await displayNameModal.waitFor({ state: 'hidden', timeout: 5000 });
  }
}

export function authHeader(userId?: string): Record<string, string> {
  const token = generateSmokeTestToken(userId);
  return { Authorization: `Bearer ${token}` };
}
