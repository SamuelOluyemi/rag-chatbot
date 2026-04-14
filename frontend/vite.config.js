// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    rollupOptions: {
      input: "/frontend/index.html", // Only if not in root
    },
  },
});
