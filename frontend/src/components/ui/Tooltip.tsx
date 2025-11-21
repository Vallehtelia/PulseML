import { useState } from "react";
import type { ReactNode } from "react";

type Props = {
  label: ReactNode;
  children: ReactNode;
};

const Tooltip = ({ label, children }: Props) => {
  const [visible, setVisible] = useState(false);
  return (
    <span
      style={{ position: "relative", display: "inline-block" }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span
          style={{
            position: "absolute",
            top: "calc(100% + 0.5rem)",
            left: "0",
            background: "var(--color-surface-alt)",
            border: "1px solid var(--color-border)",
            padding: "0.75rem 1rem",
            borderRadius: "0.5rem",
            minWidth: "250px",
            maxWidth: "350px",
            width: "max-content",
            zIndex: 1001,
            fontSize: "0.875rem",
            lineHeight: "1.5",
            whiteSpace: "normal",
            wordWrap: "break-word",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
            pointerEvents: "none",
          }}
        >
          {label}
        </span>
      )}
    </span>
  );
};

export default Tooltip;


