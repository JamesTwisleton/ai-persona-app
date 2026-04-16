import { test, expect } from "@playwright/test";
import { authHeader } from "../lib/auth";

const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";

test.describe("Challenge mode", () => {
  test("GET /conversations returns with challenge fields", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/conversations`, { headers });
    expect(res.status()).toBe(200);
    const conversations = await res.json();
    expect(Array.isArray(conversations)).toBe(true);

    // If any conversations exist, verify challenge-related fields are present
    const challenges = conversations.filter((c: any) => c.is_challenge);
    if (challenges.length > 0) {
      const challenge = challenges[0];
      expect(challenge).toHaveProperty("is_challenge", true);
      expect(challenge).toHaveProperty("status");
    }
  });
});
