import { test, expect } from "@playwright/test";

const isPreview = (process.env.SMOKE_TEST_BASE_URL || "").includes("-pr-");

test.describe("Homepage", () => {
  test("loads with expected content", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await page.goto("/");
    await expect(page).toHaveTitle(/PersonaComposer/i);
  });

  test("has navigation links", async ({ page }) => {
    await page.goto("/");
    const personasLink = page.getByRole("link", { name: /personas/i });
    await expect(personasLink).toBeVisible();
    const conversationsLink = page.getByRole("link", { name: /conversations/i });
    await expect(conversationsLink).toBeVisible();
  });

  test("has sign-in option when unauthenticated", async ({ page }) => {
    test.skip(isPreview, "Preview frontend auto-logins — sign-in button not rendered");
    await page.goto("/");
    // Onboarding page shows "Get Started Free" link for unauthenticated users
    const getStarted = page.getByRole("link", { name: /get started/i });
    await expect(getStarted).toBeVisible();
  });
});
