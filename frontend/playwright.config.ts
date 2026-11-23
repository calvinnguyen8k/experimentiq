import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  use: { baseURL: "http://127.0.0.1:3100", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    { command: "../backend/.venv/bin/uvicorn tests.e2e_api:app --app-dir ../backend --host 127.0.0.1 --port 8100 --no-access-log",
      url: "http://127.0.0.1:8100/health", reuseExistingServer: false },
    { command: "npm run dev -- --port 3100", url: "http://127.0.0.1:3100",
      env: { NEXT_PUBLIC_API_URL: "http://127.0.0.1:8100", NEXT_TELEMETRY_DISABLED: "1" },
      reuseExistingServer: false, timeout: 120_000 },
  ],
});
