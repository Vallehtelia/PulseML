import type { ReactNode } from "react";
import Button from "./Button";

type ModalProps = {
  title: string;
  open: boolean;
  onClose: () => void;
  children: ReactNode;
};

const Modal = ({ title, open, onClose, children }: ModalProps) => {
  if (!open) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(2, 6, 23, 0.8)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
      }}
    >
      <div
        style={{
          width: "min(600px, 90vw)",
          background: "var(--color-surface)",
          borderRadius: "1rem",
          border: "1px solid var(--color-border)",
          padding: "1.5rem",
        }}
      >
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1rem",
          }}
        >
          <h2 style={{ margin: 0 }}>{title}</h2>
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </header>
        {children}
      </div>
    </div>
  );
};

export default Modal;


