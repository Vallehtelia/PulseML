import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from "react";

type ButtonVariant = "primary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
}

const baseStyle: CSSProperties = {
  padding: "0.6rem 1.25rem",
  borderRadius: "0.65rem",
  fontWeight: 600,
  border: "none",
  cursor: "pointer",
  transition: "opacity 0.2s ease",
};

const variantStyle: Record<ButtonVariant, CSSProperties> = {
  primary: {
    background: "var(--color-primary)",
    color: "#fff",
  },
  ghost: {
    background: "transparent",
    color: "var(--color-text)",
    border: "1px solid var(--color-border)",
  },
  danger: {
    background: "var(--color-danger)",
    color: "#fff",
  },
};

const Button = ({ variant = "primary", children, style, ...props }: ButtonProps) => {
  return (
    <button
      style={{
        ...baseStyle,
        ...variantStyle[variant],
        opacity: props.disabled ? 0.6 : 1,
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;


