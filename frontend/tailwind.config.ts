import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        studio: {
          bg: "#edf0f6",
          deep: "#f8fafc",
          panel: "#ffffff",
          card: "#f4f6fb",
          input: "#eef1f6",
          gold: "#f5a623",
          goldDeep: "#e08a1e",
          goldDim: "#8a6420",
        },
      },
      boxShadow: {
        glow: "0 0 24px rgba(245,166,35,0.25)",
      },
    },
  },
  plugins: [],
};
export default config;
