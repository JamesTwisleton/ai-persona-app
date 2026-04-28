import { test, expect } from "@playwright/test";
import { authHeader } from "../lib/auth";

const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";

test.describe("Avatar image generation", () => {
  test("personas include avatar_url field", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/personas`, { headers });
    expect(res.status()).toBe(200);
    const personas = await res.json();
    if (personas.length > 0) {
      const persona = personas[0];
      expect(persona).toHaveProperty("avatar_url");
      expect(persona.avatar_url).toBeTruthy();
    }
  });

  test("public personas from discover include avatar_url", async ({ request }) => {
    const res = await request.get(`${apiURL}/discover`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    const personas = body.personas || [];
    if (personas.length > 0) {
      const persona = personas[0];
      expect(persona).toHaveProperty("avatar_url");
      expect(persona.avatar_url).toBeTruthy();
    }
  });

  test("avatar URL is reachable", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/personas`, { headers });
    expect(res.status()).toBe(200);
    const personas = await res.json();
    const withAvatar = personas.find(
      (p: any) => p.avatar_url && !p.avatar_url.includes("dicebear"),
    );
    if (withAvatar) {
      const avatarRes = await request.get(withAvatar.avatar_url);
      expect([200, 206]).toContain(avatarRes.status());
    }
  });
});
