import { type Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "orko-accent-start": "var(--orko-accent-start)",
        "orko-accent-end": "var(--orko-accent-end)",
        "orko-bg": "var(--orko-bg)",
        "orko-surface": "var(--orko-surface)",
        "orko-card": "var(--orko-card)",
        "orko-text": "var(--orko-text)",
        "orko-muted": "var(--orko-muted)",
      },
      boxShadow: {
        card: "0px 4px 12px rgba(0, 0, 0, 0.06)",
      },
      borderRadius: {
        xl2: "16px",
      },
    },
  },
  plugins: [],
} satisfies Config;
