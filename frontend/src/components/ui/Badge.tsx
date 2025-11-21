import type { CSSProperties, ReactNode } from "react";

type BadgeVariant = "default" | "success" | "danger" | "warning";

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
}

const baseStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  padding: "0.15rem 0.65rem",
  borderRadius: "999px",
  fontSize: "0.85rem",
  fontWeight: 600,
};

const variantStyle: Record<BadgeVariant, CSSProperties> = {
  default: { background: "var(--color-surface-alt)", color: "var(--color-text)" },
  success: { background: "var(--color-success)", color: "#fff" },
  danger: { background: "var(--color-danger)", color: "#fff" },
  warning: { background: "var(--color-warning)", color: "#000" },
};

const Badge = ({ variant = "default", children }: BadgeProps) => (
  <span style={{ ...baseStyle, ...variantStyle[variant] }}>{children}</span>
);

export default Badge;


