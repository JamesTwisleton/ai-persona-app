import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ocean: {
          openness: "#8b5cf6",
          conscientiousness: "#3b82f6",
          extraversion: "#f59e0b",
          agreeableness: "#10b981",
          neuroticism: "#ef4444",
        },
      },
    },
  },
  plugins: [],
};
export default config;
