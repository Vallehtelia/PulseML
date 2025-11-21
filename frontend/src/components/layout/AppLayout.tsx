import type { ReactNode } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

type Props = {
  children?: ReactNode;
};

const AppLayout = ({ children }: Props) => {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--color-bg)" }}>
      <Sidebar />
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <Topbar />
        <main style={{ padding: "1.5rem", flex: 1, overflow: "auto" }}>{children}</main>
      </div>
    </div>
  );
};

export default AppLayout;


