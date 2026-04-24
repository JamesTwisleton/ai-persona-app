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

    // Wait for either onboarding content or discovery feed to appear
    const onboarding = page.getByText(/welcome|get started|how it works/i);
    const discoveryFeed = page.locator('[data-testid="discovery-feed"]');
    const personaCards = page.locator('[data-testid="persona-card"]');

    await expect(onboarding.or(discoveryFeed).or(personaCards).first()).toBeVisible({ timeout: 15000 });

    const hasOnboarding = await onboarding.first().isVisible();
    const hasDiscoveryFeed = await discoveryFeed.first().isVisible();
    const hasPersonaCards = await personaCards.count() > 0;

    expect(hasOnboarding || hasDiscoveryFeed || hasPersonaCards).toBeTruthy();
  });
});
