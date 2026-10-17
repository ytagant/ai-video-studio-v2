import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        studio: {
          bg: "#0a1120",
          deep: "#070d18",
          panel: "#101a2e",
          card: "#152036",
          input: "#0b1322",
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
