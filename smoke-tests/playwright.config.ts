import { defineConfig } from "@playwright/test";

const baseURL = process.env.SMOKE_TEST_BASE_URL || "https://personacomposer.app";
const apiURL = process.env.SMOKE_TEST_API_URL || "https://api.personacomposer.app";

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? "list" : "html",

  use: {
    baseURL,
    navigationTimeout: 60_000, // Fly machines may need cold-start wake
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
});

export { apiURL };
