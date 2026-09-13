/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#f8fafc",
          900: "#f1f5f9",
          800: "#ffffff",
          700: "#e2e8f0",
        },
        accent: {
          blue: "#3b82f6",
          purple: "#8b5cf6",
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
