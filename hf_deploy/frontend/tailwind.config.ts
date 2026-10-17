import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        studio: {
          bg: "#0a0a0f",
          panel: "#121218",
          card: "#17171f",
          gold: "#f5b942",
          goldDim: "#8a6420",
        },
      },
    },
  },
  plugins: [],
};
export default config;
