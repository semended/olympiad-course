import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(220 13% 91%)",
        background: "hsl(210 20% 98%)",
        foreground: "hsl(222 47% 11%)",
        card: "hsl(0 0% 100%)"
      }
    }
  },
  plugins: []
};

export default config;
