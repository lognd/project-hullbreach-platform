import { fileURLToPath, URL } from "node:url";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// The web frontend lives under web/ so the repo root can hold the Python
// package (src/, tests/) that frob treats as this polyglot repo's Python
// stage; every path below is relative to that root.
//
// HULLBREACH_PORT (the API's port) and HULLBREACH_WEB_PORT (this dev
// server's port) come from the shell or the repo-root .env, so a second
// copy of the stack can run beside the first (docs/index.md#operator-
// scripts-and-the-doctor). Defaults: API 8000, website 5173.
export default defineConfig(({ mode }) => {
  const repoRoot = fileURLToPath(new URL(".", import.meta.url));
  const env = { ...loadEnv(mode, repoRoot, "HULLBREACH_"), ...process.env };
  const apiPort = env.HULLBREACH_PORT || "8000";
  const webPort = Number(env.HULLBREACH_WEB_PORT || "5173");
  return {
    root: "web",
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./web/src", import.meta.url)),
      },
    },
    build: {
      outDir: "../dist",
      emptyOutDir: true,
    },
    server: {
      port: webPort,
      strictPort: true,
      proxy: {
        "/api": `http://127.0.0.1:${apiPort}`,
      },
    },
    test: {
      root: ".",
      environment: "jsdom",
      globals: true,
      setupFiles: ["./web/tests/setup.ts"],
      include: ["web/tests/unit/**/*.test.ts", "web/tests/unit/**/*.test.tsx"],
      coverage: {
        provider: "v8",
        reporter: ["text", "html"],
        include: ["web/src/**/*.{ts,tsx}"],
      },
    },
  };
});
