import type { Config } from "jest";
import nextJest from "next/jest.js";

const createJestConfig = nextJest({
  dir: "./",
});

const config: Config = {
  coverageProvider: "v8",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^.+\\.module\\.(css|sass|scss)$": "identity-obj-proxy",
  },
  testMatch: ["<rootDir>/src/**/*.test.{ts,tsx}"],
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/types/**",
  ],
  coverageThreshold: {
    global: {
      lines: 80,
    },
  },
};

export default createJestConfig(config);
