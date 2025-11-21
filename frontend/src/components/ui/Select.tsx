import { forwardRef } from "react";
import type { CSSProperties, SelectHTMLAttributes } from "react";

const styles: CSSProperties = {
  width: "100%",
  borderRadius: "0.5rem",
  border: "1px solid var(--color-border)",
  background: "var(--color-surface-alt)",
  padding: "0.55rem 0.75rem",
  color: "var(--color-text)",
};

const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(
  ({ children, style, ...props }, ref) => (
    <select ref={ref} style={{ ...styles, ...style }} {...props}>
      {children}
    </select>
  ),
);

Select.displayName = "Select";

export default Select;


