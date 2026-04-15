import { test, expect } from "@playwright/test";
import { authHeader } from "../lib/auth";

const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";

test.describe("Backend API endpoints", () => {
  test("GET /health returns 200", async ({ request }) => {
    const res = await request.get(`${apiURL}/health`);
    expect(res.status()).toBe(200);
  });

  test("GET /personas/public returns array", async ({ request }) => {
    const res = await request.get(`${apiURL}/personas/public`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test("GET /discover returns data", async ({ request }) => {
    const res = await request.get(`${apiURL}/discover`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toBeDefined();
  });

  test("GET /users/me with JWT returns user", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/users/me`, { headers });
    expect(res.status()).toBe(200);
    const user = await res.json();
    expect(user).toHaveProperty("id");
    expect(user).toHaveProperty("email");
  });

  test("GET /personas with JWT returns user personas", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/personas`, { headers });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test("GET /conversations with JWT returns user conversations", async ({ request }) => {
    const headers = authHeader();
    const res = await request.get(`${apiURL}/conversations`, { headers });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
  });
});
