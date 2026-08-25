/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        display: ['Syne', 'sans-serif'],
      },
      colors: {
        cyber: {
          50: '#f0fdf9',
          100: '#ccfbef',
          200: '#99f6e0',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        void: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          850: '#172033',
          900: '#0f172a',
          950: '#080d1a',
        },
        neon: {
          green: '#00ff9d',
          blue: '#00d4ff',
          red: '#ff2d6b',
          purple: '#bf5af2',
          orange: '#ff9f0a',
        }
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(rgba(20,184,166,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(20,184,166,0.03) 1px, transparent 1px)",
        'radial-glow': "radial-gradient(ellipse at center, rgba(20,184,166,0.15) 0%, transparent 70%)",
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(20,184,166,0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(20,184,166,0.9), 0 0 40px rgba(20,184,166,0.3)' },
        }
      },
      boxShadow: {
        'neon': '0 0 10px rgba(20,184,166,0.5), 0 0 40px rgba(20,184,166,0.1)',
        'neon-red': '0 0 10px rgba(255,45,107,0.5), 0 0 40px rgba(255,45,107,0.1)',
        'glass': '0 8px 32px rgba(0,0,0,0.3)',
      }
    },
  },
  plugins: [],
};
