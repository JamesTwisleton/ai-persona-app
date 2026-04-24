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
    const signIn = page.getByRole("button", { name: /sign in/i });
    await expect(signIn).toBeVisible();
  });

  test("shows discovery feed content", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState('networkidle');
    
    // Should show either onboarding content or discovery feed
    const hasOnboarding = await page.locator('text=/welcome|get started|how it works/i').isVisible().catch(() => false);
    const hasDiscoveryFeed = await page.locator('[data-testid="discovery-feed"], [class*="feed"], [class*="grid"]').isVisible().catch(() => false);
    const hasPersonaCards = await page.locator('[data-testid="persona-card"], [class*="persona"], [class*="card"]').count() > 0;
    
    // Should have some form of content
    expect(hasOnboarding || hasDiscoveryFeed || hasPersonaCards).toBeTruthy();
  });
});
