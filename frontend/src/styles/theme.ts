export const theme = {
  colors: {
    background: "#020617",
    surface: "#0B1120",
    surfaceAlt: "#111827",
    border: "#1F2937",
    textPrimary: "#E5E7EB",
    textSecondary: "#9CA3AF",
    primary: "#2563EB",
    danger: "#EF4444",
    success: "#10B981",
    warning: "#F59E0B",
  },
  spacing: (factor: number) => `${factor * 0.25}rem`,
} as const;

export type Theme = typeof theme;


