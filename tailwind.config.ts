import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charcoal: "#1b1b1b",
        "warm-gray": "#7d756b",
        cream: "#f5efe6",
        "cream-light": "#faf6ef",
        "footer-bg": "#25211d",
        sage: "#5c6b4f",
        sand: "#c4b59a",
        rose: "#c08080",
      },
      boxShadow: {
        panel: "0 20px 50px rgba(0, 0, 0, 0.08)",
      },
      fontFamily: {
        sans: ["Arial", "Helvetica", "sans-serif"],
      },
      maxWidth: {
        layout: "1440px",
      },
    },
  },
  plugins: [],
};

export default config;
