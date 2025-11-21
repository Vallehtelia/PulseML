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
            top: "calc(100% + 0.25rem)",
            left: "50%",
            transform: "translateX(-50%)",
            background: "var(--color-surface-alt)",
            border: "1px solid var(--color-border)",
            padding: "0.5rem",
            borderRadius: "0.5rem",
            width: "200px",
            zIndex: 10,
            fontSize: "0.875rem",
          }}
        >
          {label}
        </span>
      )}
    </span>
  );
};

export default Tooltip;


