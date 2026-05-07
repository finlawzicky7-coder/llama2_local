import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: '#0b0d10',
        panel: '#11141a',
        panelborder: '#1d212a',
        ink: '#e6e8ee',
        muted: '#8a93a6',
        accent: '#a78bfa',
        good: '#34d399',
        warn: '#fbbf24',
        bad: '#f87171',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
