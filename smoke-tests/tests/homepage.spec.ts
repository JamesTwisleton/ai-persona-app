import { test, expect } from "@playwright/test";

test.describe("Homepage", () => {
  test("loads with expected content", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await page.goto("/");
    await expect(page).toHaveTitle(/Persona Composer/i);
  });

  test("has navigation links", async ({ page }) => {
    await page.goto("/");
    // Should have a link to explore/discover personas
    const exploreLink = page.getByRole("link", { name: /explore|discover|browse/i });
    await expect(exploreLink).toBeVisible();
  });

  test("has login link when unauthenticated", async ({ page }) => {
    await page.goto("/");
    const loginLink = page.getByRole("link", { name: /log\s*in|sign\s*in/i });
    await expect(loginLink).toBeVisible();
  });
});
