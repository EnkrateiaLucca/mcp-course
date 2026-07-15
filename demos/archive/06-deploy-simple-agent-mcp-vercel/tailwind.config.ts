import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f1a",
        panel: "#121826",
        border: "#1f2937",
        accent: "#7c3aed",
      },
    },
  },
  plugins: [],
} satisfies Config;
