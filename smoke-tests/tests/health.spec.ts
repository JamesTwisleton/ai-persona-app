import { test, expect } from "@playwright/test";

const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";

test.describe("Infrastructure health", () => {
  test("backend /health returns 200", async ({ request }) => {
    const response = await request.get(`${apiURL}/health`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("status");
  });

  test("frontend loads HTML", async ({ request }) => {
    const response = await request.get("/");
    expect(response.status()).toBe(200);
    const html = await response.text();
    expect(html).toContain("<!DOCTYPE html");
  });

  test("backend responds within 10s", async ({ request }) => {
    const start = Date.now();
    await request.get(`${apiURL}/health`);
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(10_000);
  });
});
