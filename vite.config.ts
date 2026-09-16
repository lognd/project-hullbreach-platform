import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// The web frontend lives under web/ so the repo root can hold the Python
// package (src/, tests/) that frob treats as this polyglot repo's Python
// stage; every path below is relative to that root.
export default defineConfig({
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
    proxy: {
      "/api": "http://127.0.0.1:8000",
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
});
