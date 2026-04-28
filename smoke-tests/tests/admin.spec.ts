import { test, expect } from "@playwright/test";
import { injectAuth, authHeader } from "../lib/auth";

const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";
const adminUserId = process.env.SMOKE_TEST_ADMIN_USER_ID;

test.describe("Admin panel", () => {
  test.skip(!adminUserId, "SMOKE_TEST_ADMIN_USER_ID not set — skipping admin tests");

  test("admin page loads", async ({ page }) => {
    await injectAuth(page, adminUserId!);
    await page.goto("/admin");
    await expect(page.locator("body")).not.toContainText("500");
    await expect(page.locator("body")).not.toContainText("Internal Server Error");
  });

  test("GET /admin/personas returns data", async ({ request }) => {
    const headers = authHeader(adminUserId!);
    const res = await request.get(`${apiURL}/admin/personas`, { headers });
    expect(res.status()).toBe(200);
  });

  test("GET /admin/conversations returns data", async ({ request }) => {
    const headers = authHeader(adminUserId!);
    const res = await request.get(`${apiURL}/admin/conversations`, { headers });
    expect(res.status()).toBe(200);
  });
});
