/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neo-bg': '#fdfbf7',
        'neo-primary': '#4f46e5',
        'neo-accent': '#ff6b6b',
        'neo-yellow': '#fde047',
        'neo-green': '#4ade80',
        'neo-blue': '#60a5fa',
        'neo-surface': '#ffffff',
        'neo-text': '#111827',
        'neo-border': '#000000',
      },
      boxShadow: {
        'neo-sm': '2px 2px 0px 0px rgba(0,0,0,1)',
        'neo': '4px 4px 0px 0px rgba(0,0,0,1)',
        'neo-lg': '8px 8px 0px 0px rgba(0,0,0,1)',
        'neo-xl': '12px 12px 0px 0px rgba(0,0,0,1)',
        'neo-inset': 'inset 4px 4px 0px 0px rgba(0,0,0,1)',
      },
      borderWidth: {
        'neo': '3px',
        'neo-lg': '4px',
      },
      fontFamily: {
        sans: ['"Inter"', 'sans-serif'],
      },
      borderRadius: {
        'neo': '0.375rem',
        'neo-lg': '0.5rem',
      }
    },
  },
  plugins: [],
}
