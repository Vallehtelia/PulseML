import type { CSSProperties, ReactNode } from "react";

type Props = {
  title?: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  style?: CSSProperties;
  className?: string;
};

const baseStyle: CSSProperties = {
  borderRadius: "1rem",
  border: "1px solid var(--color-border)",
  background: "var(--color-surface)",
  padding: "1.25rem",
};

const Card = ({ title, description, children, style, className }: Props) => {
  return (
    <section style={{ ...baseStyle, ...style }} className={className}>
      {(title || description) && (
        <header style={{ marginBottom: "1rem" }}>
          {title && <h3 style={{ margin: 0 }}>{title}</h3>}
          {description && (
            <p style={{ margin: "0.25rem 0 0", color: "var(--color-text-secondary)" }}>
              {description}
            </p>
          )}
        </header>
      )}
      {children}
    </section>
  );
};

export default Card;


