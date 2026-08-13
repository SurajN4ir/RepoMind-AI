import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./config/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        surface: "hsl(var(--surface))",
        card: "hsl(var(--card))",
        primary: "hsl(var(--primary))",
        accent: "hsl(var(--accent))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
        border: "hsl(var(--border))",
        ring: "hsl(var(--ring))",
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        glow: "0 0 0 1px hsl(var(--primary) / 0.18), 0 18px 48px hsl(222 47% 5% / 0.22)",
        "glow-accent": "0 0 0 1px hsl(var(--accent) / 0.18), 0 18px 48px hsl(222 47% 5% / 0.22)",
        "glow-lg": "0 0 40px hsl(var(--primary) / 0.25), 0 0 0 1px hsl(var(--primary) / 0.12)",
        card: "0 1px 3px hsl(222 47% 5% / 0.3), 0 8px 24px hsl(222 47% 5% / 0.15)",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": {
            boxShadow: "0 0 0px 0px hsl(var(--primary) / 0)",
          },
          "50%": {
            boxShadow: "0 0 18px 4px hsl(var(--primary) / 0.35)",
          },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
        },
        "gradient-shift": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        "orb-drift": {
          "0%": { transform: "translate(0%, 0%) scale(1)" },
          "33%": { transform: "translate(3%, -4%) scale(1.05)" },
          "66%": { transform: "translate(-2%, 3%) scale(0.97)" },
          "100%": { transform: "translate(0%, 0%) scale(1)" },
        },
        "typing-cursor": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
        "slide-in-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "pulse-glow": "pulse-glow 2.4s ease-in-out infinite",
        float: "float 4s ease-in-out infinite",
        "gradient-shift": "gradient-shift 8s ease infinite",
        "orb-drift": "orb-drift 18s ease-in-out infinite",
        "typing-cursor": "typing-cursor 1s step-end infinite",
        "slide-in-up": "slide-in-up 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "fade-in": "fade-in 0.35s ease forwards",
      },
      backgroundSize: {
        "200%": "200% 200%",
      },
      fontFamily: {
        sans: ["var(--font-ui)", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-code)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      screens: {
        xs: "480px",
      },
    },
  },
  plugins: [],
} satisfies Config;
