/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        md: {
          primary:             "#1565C0",
          "primary-container": "#D3E4FF",
          "on-primary":        "#FFFFFF",
          "on-primary-container": "#001D36",
          secondary:           "#0277BD",
          "secondary-container": "#B3E5FC",
          tertiary:            "#006064",
          surface:             "#FFFFFF",
          "surface-variant":   "#E3F2FD",
          "surface-dim":       "#E8EAF6",
          background:          "#F5F5F5",
          "on-surface":        "#1C1B1F",
          "on-surface-variant":"#49454F",
          outline:             "#79747E",
          "outline-variant":   "#CAC4D0",
          error:               "#B3261E",
          "error-container":   "#F9DEDC",
          "on-error":          "#FFFFFF",
        },
        clinical: {
          normal:   "#1565C0",
          elevated: "#E65100",
          high:     "#B71C1C",
          missing:  "#9E9E9E",
        },
      },
      boxShadow: {
        "elevation-1": "0px 1px 2px rgba(0,0,0,0.3), 0px 1px 3px 1px rgba(0,0,0,0.15)",
        "elevation-2": "0px 1px 2px rgba(0,0,0,0.3), 0px 2px 6px 2px rgba(0,0,0,0.15)",
        "elevation-3": "0px 4px 8px 3px rgba(0,0,0,0.15), 0px 1px 3px rgba(0,0,0,0.3)",
      },
      borderRadius: {
        "xs": "4px",
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "28px",
      },
      fontFamily: {
        sans: ["Inter", "Roboto", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
