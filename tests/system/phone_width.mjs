// Measures horizontal overflow of the signed-in /me page in real Chromium at 390px.
// Env: E2E_URL, E2E_USER, E2E_PASSWORD, PLAYWRIGHT_CORE (path to playwright-core).
// Prints one JSON line {viewport, scrollWidth, offenders}; the pytest asserts on it.
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE);
const base = process.env.E2E_URL;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
await page.goto(`${base}/login`);
await page.getByLabel("Username").fill(process.env.E2E_USER);
await page.getByLabel("Password").fill(process.env.E2E_PASSWORD);
await page.getByRole("button", { name: /log in|sign in/i }).last().click();
await page.waitForURL((url) => !url.pathname.startsWith("/login"));
await page.goto(`${base}/me`);
await page.waitForSelector("main");
await page.waitForTimeout(800);
const result = await page.evaluate(() => {
  const vw = document.documentElement.clientWidth;
  const offenders = [...document.querySelectorAll("body *")]
    .filter((e) => e.getBoundingClientRect().right > vw + 1)
    .map((e) => e.tagName)
    .slice(0, 5);
  return { viewport: vw, scrollWidth: document.documentElement.scrollWidth, offenders };
});
console.log(JSON.stringify(result));
await browser.close();
