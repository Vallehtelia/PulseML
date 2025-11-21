import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const host = env.FRONTEND_HOST ?? "0.0.0.0";
  const port = Number(env.FRONTEND_PORT ?? 3000);

  return {
    plugins: [react()],
    server: {
      host,
      port,
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
  };
});


