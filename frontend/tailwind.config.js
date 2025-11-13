/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: '#00d9ff',
          blue: '#0066ff',
          purple: '#7c3aed',
          green: '#10b981',
        },
        dark: {
          bg: '#0a0a0f',
          surface: '#111118',
          border: '#1f1f2e',
          hover: '#1a1a25',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
      },
    },
  },
  plugins: [],
}

