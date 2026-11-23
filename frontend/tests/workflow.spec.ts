import { expect, test, Page } from "@playwright/test";
import { readFile } from "node:fs/promises";

async function design(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "Load complete synthetic example" }).click();
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await page.getByRole("button", { name: "Next: Generate experiment design →" }).click();
}
async function statistics(page: Page) {
  await design(page);
  await expect(page.getByRole("button", { name: "Next: Statistical validation →" })).toBeDisabled();
  await page.getByRole("checkbox", { name: /I have reviewed this design/ }).check();
  await page.getByRole("button", { name: "Next: Statistical validation →" }).click();
  await expect(page.getByRole("button", { name: "Calculate sample size" })).toBeDisabled();
  await page.getByRole("checkbox", { name: /I confirm these numerical inputs/ }).check();
  await page.getByRole("button", { name: "Calculate sample size" }).click();
  await expect(page.getByText("Fits your eligible population", { exact: true })).toBeVisible();
}

test("all stages with explicit gates, real calculation and complete Markdown download", async ({ page }, testInfo) => {
  await statistics(page);
  await expect(page.getByText("3,140", { exact: true })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("statistics.png"), fullPage: true });
  await page.getByRole("button", { name: "Next: Review & export →" }).click();
  await expect(page.getByRole("heading", { name: "Review & export", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Download Markdown report" })).toBeDisabled();
  await page.getByRole("checkbox", { name: /I have reviewed the risks/ }).check();
  await page.screenshot({ path: testInfo.outputPath("review.png"), fullPage: true });
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download Markdown report" }).click();
  const download = await downloadPromise;
  const report = await readFile((await download.path())!, "utf8");
  expect(report).toContain("Total: 3140");
  expect(report).toContain("Contamination");
  expect(report).toContain("Intake provenance");
  expect(report).toContain("Draft experiment plan");
  expect(report).toContain("baseline\\_sd: 100");
  expect(report).toContain("critic\\_v1");
  await page.getByRole("button", { name: "Back to statistics" }).click();
  await page.getByLabel("Target power", { exact: true }).fill("0.9");
  await expect(page.getByRole("button", { name: "Next: Review & export →" })).toBeDisabled();
  await expect(page.getByRole("navigation").getByRole("button", { name: /Review & export/ })).toBeDisabled();
  await expect(page.getByText("3,140", { exact: true })).toHaveCount(0);
});

test("mobile full workflow remains navigable and revisiting does not submit again", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await statistics(page);
  await page.getByRole("button", { name: "Next: Review & export →" }).click();
  await expect(page.getByRole("heading", { name: "Review & export", exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: testInfo.outputPath("mobile-review.png"), fullPage: true });
  await page.getByRole("navigation").getByRole("button", { name: /Design proposal/ }).click();
  await expect(page.getByRole("checkbox", { name: /I have reviewed this design/ })).toBeChecked();
  await page.getByRole("checkbox", { name: /I have reviewed this design/ }).uncheck();
  await expect(page.getByRole("navigation").getByRole("button", { name: /Statistical validation/ })).toBeDisabled();
  await expect(page.getByRole("navigation").getByRole("button", { name: /Review & export/ })).toBeDisabled();
});

test("review failure retains calculation and supports retry", async ({ page }) => {
  await statistics(page);
  await page.route("**/api/v1/experiments/review", route => route.fulfill({ status: 503,
    contentType: "application/json", body: JSON.stringify({ error: { message: "Risk review is temporarily unavailable." } }),
  }));
  await page.getByRole("button", { name: "Next: Review & export →" }).click();
  await expect(page.getByRole("alert", { name: "Step could not finish" })).toContainText("temporarily unavailable");
  await expect(page.getByText("3,140", { exact: true })).toBeVisible();
  await page.unroute("**/api/v1/experiments/review");
  await page.getByRole("button", { name: "Next: Review & export →" }).click();
  await expect(page.getByRole("heading", { name: "Review & export", exact: true })).toBeVisible();
});

test("missing baseline cannot calculate and unsupported design cannot proceed", async ({ page }) => {
  await statistics(page);
  await page.getByLabel("Baseline standard deviation", { exact: true }).fill("");
  await expect(page.getByRole("button", { name: "Calculate sample size" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Next: Review & export →" })).toBeDisabled();
  await page.route("**/api/v1/experiments/design", async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.status = "needs_attention"; json.design.design_family = "unsupported";
    await route.fulfill({ response, json });
  });
  await design(page);
  await expect(page.getByRole("checkbox", { name: /I have reviewed this design/ })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Next: Statistical validation →" })).toBeDisabled();
});
