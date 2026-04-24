import { test, expect } from "@playwright/test";
import { authHeader } from "../lib/auth";

const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";

test.describe("Social features", () => {
  test("public personas include social fields", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/personas/public`, { headers });
    expect(res.status()).toBe(200);
    const personas = await res.json();

    if (!Array.isArray(personas) || personas.length === 0) {
      test.skip();
      return;
    }

    const persona = personas[0];
    expect(persona).toHaveProperty("upvote_count");
    expect(persona).toHaveProperty("view_count");
  });

  test("discover endpoint returns structured data", async ({ request }) => {
    const res = await request.get(`${apiURL}/discover`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toBeDefined();
  });

  test("discover supports sort parameter", async ({ request }) => {
    for (const sort of ["hot", "top", "new"]) {
      const res = await request.get(`${apiURL}/discover?sort=${sort}`);
      expect(res.status()).toBe(200);
    }
  });
});
