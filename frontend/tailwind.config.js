/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#07111f",
        panel: "#0f1b2d",
        accent: "#38bdf8",
        success: "#22c55e",
        danger: "#ef4444"
      }
    }
  },
  plugins: []
};
