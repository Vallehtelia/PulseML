import { forwardRef } from "react";
import type { CSSProperties, InputHTMLAttributes } from "react";

const styles: CSSProperties = {
  width: "100%",
  borderRadius: "0.5rem",
  border: "1px solid var(--color-border)",
  background: "var(--color-surface-alt)",
  padding: "0.55rem 0.75rem",
  color: "var(--color-text)",
};

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ style, ...props }, ref) => (
    <input ref={ref} style={{ ...styles, ...style }} {...props} />
  ),
);

Input.displayName = "Input";

export default Input;


