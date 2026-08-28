/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        shield: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          900: '#14532d',
        },
        cyber: {
          navy: '#0B0F19',
          dark: '#0e1626',
          card: '#131D31',
          border: '#1E293B',
          accent: '#3B82F6',
          glow: '#6366F1'
        }
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s infinite ease-in-out',
        'scan-beam': 'scanBeam 2.5s infinite linear',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: 0.8, filter: 'drop-shadow(0 0 15px rgba(59, 130, 246, 0.6))' },
          '50%': { opacity: 1, filter: 'drop-shadow(0 0 25px rgba(99, 102, 241, 0.9))' },
        },
        scanBeam: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        }
      }
    },
  },
  plugins: [],
}
