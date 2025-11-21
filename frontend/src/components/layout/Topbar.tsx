import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";

const Topbar = () => {
  const { user, logout } = useAuth();

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "1rem 1.5rem",
        borderBottom: "1px solid var(--color-border)",
        background: "var(--color-surface-alt)",
      }}
    >
      <div>
        <div style={{ fontWeight: 600 }}>PulseML Studio</div>
        <small style={{ color: "var(--color-text-secondary)" }}>
          Track datasets, templates, and training runs
        </small>
      </div>
      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <span style={{ color: "var(--color-text-secondary)", fontSize: "0.9rem" }}>
          {user?.email}
        </span>
        <Button variant="ghost" onClick={logout}>
          Logout
        </Button>
      </div>
    </header>
  );
};

export default Topbar;


