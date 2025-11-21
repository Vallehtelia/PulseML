import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Datasets", to: "/datasets" },
  { label: "Training Runs", to: "/training-runs" },
  { label: "AI Assistant (coming soon)", to: "/ai-assistant" },
];

const Sidebar = () => {
  return (
    <aside
      style={{
        width: "240px",
        background: "var(--color-surface)",
        borderRight: "1px solid var(--color-border)",
        minHeight: "100vh",
        padding: "1.5rem 1rem",
      }}
    >
      <div style={{ marginBottom: "2rem" }}>
        <div style={{ fontSize: "1.25rem", fontWeight: 600 }}>PulseML</div>
        <div style={{ color: "var(--color-text-secondary)", fontSize: "0.875rem" }}>
          GPU-powered ML studio
        </div>
      </div>
      <nav style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              padding: "0.75rem 1rem",
              borderRadius: "0.5rem",
              color: "var(--color-text)",
              background: isActive ? "var(--color-primary)" : "transparent",
              fontWeight: isActive ? 600 : 500,
            })}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;


