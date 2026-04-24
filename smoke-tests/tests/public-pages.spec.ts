import { test, expect } from "@playwright/test";

test.describe("Public pages (unauthenticated)", () => {
  test("explore page loads", async ({ page }) => {
    await page.goto("/personas");
    // Should show the explore/discover page without auth
    await expect(page.locator("body")).not.toContainText("500");
    await expect(page.locator("body")).not.toContainText("Internal Server Error");
  });

  test("public persona profile loads if available", async ({ page, request }) => {
    const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";
    const res = await request.get(`${apiURL}/personas/public?limit=1`);
    const personas = await res.json();

    if (!Array.isArray(personas) || personas.length === 0) {
      test.skip();
      return;
    }

    const id = personas[0].unique_id || personas[0].id;
    await page.goto(`/p/${id}`);
    await expect(page.locator("body")).not.toContainText("500");
  });

  test("public conversation loads if available", async ({ page, request }) => {
    const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";
    const res = await request.get(`${apiURL}/discover?limit=1&sort=new&type=conversation`);
    const data = await res.json();
    const conversations = data.conversations || data.items || [];

    if (!Array.isArray(conversations) || conversations.length === 0) {
      test.skip();
      return;
    }

    const id = conversations[0].id;
    await page.goto(`/c/${id}`);
    await expect(page.locator("body")).not.toContainText("500");
  });
});
