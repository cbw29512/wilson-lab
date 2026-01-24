/**
 * Purpose: Vite configuration for GitHub Pages deployment.
 * Why: GitHub Pages serves this site under /wilson-lab/ (repo name), so assets must use that base path.
 * Next: If repo name changes, update base accordingly.
 */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8055",
    },
  },
plugins: [react()],
  base: "/wilson-lab/",
});
