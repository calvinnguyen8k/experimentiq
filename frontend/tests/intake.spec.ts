import { expect, test } from "@playwright/test";

test("complete synthetic preset fills applicable fields and reaches intake complete", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByLabel("Experiment objective")).toHaveValue("");
  await page.getByRole("button", { name: "Load complete synthetic example" }).click();
  await expect(page.getByRole("status")).toContainText("fictional demo assumptions");
  await expect(page.getByLabel("Outcome type", { exact: true })).toHaveValue("continuous");
  await expect(page.getByLabel("Baseline mean", { exact: true })).toHaveValue("200");
  await expect(page.getByLabel("Baseline standard deviation", { exact: true })).toHaveValue("100");
  await expect(page.getByLabel("Baseline conversion rate", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Intake complete", { exact: true })).toHaveCount(0);
  const response = page.waitForResponse("**/api/v1/experiments/extract");
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  const result = await (await response).json();
  expect(result.status).toBe("extraction_complete");
  expect(result.questions).toEqual([]);
  expect(result.statistics_status).toBe("not_implemented");
  expect(result.facts.baseline_conversion_rate.value).toBeNull();
  await expect(page.getByText("Intake complete", { exact: true })).toBeVisible();
  await expect(page.getByText("Your input", { exact: true })).toHaveCount(6);
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await expect(page.getByText("Intake complete", { exact: true })).toHaveCount(0);
  await page.getByText("Optional confirmed inputs").click();
  await expect(page.getByLabel("Baseline mean", { exact: true })).toHaveValue("");
});

test("form → FastAPI → mocked OpenAI SDK → validated facts and missing questions", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByText("A few details need your attention")).toBeVisible();
  await expect(page.getByText("100,000", { exact: true })).toBeVisible();
  await expect(page.getByText("0.05", { exact: true })).toBeVisible();
  await expect(page.getByText("What is the baseline mean in the metric's units?")).toBeVisible();
  await expect(page.getByText("What is the baseline standard deviation in the same units?")).toBeVisible();
  await expect(page.getByText("Confirm extraction", { exact: true })).toHaveCount(4);
  await page.screenshot({ path: testInfo.outputPath("desktop-extraction.png"), fullPage: true });
  await page.getByLabel("Experiment objective").fill("A new synthetic conversion experiment for a toy product.");
  await expect(page.getByText("100,000", { exact: true })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "A clearer starting point" })).toBeVisible();
});

test("confirmed conflicting input is retained and conflict displayed", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByText("Optional confirmed inputs").click();
  await page.getByLabel("Eligible population").fill("5000");
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByText("Resolve conflicting assumptions")).toBeVisible();
  await expect(page.getByText("5,000", { exact: true })).toBeVisible();
  await expect(page.getByText("Your input", { exact: true })).toHaveCount(1);
});

test("provider error is actionable and the form stays editable", async ({ page }) => {
  await page.route("**/api/v1/experiments/extract", async (route) => {
    await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({
      error: { code: "llm_unavailable", message: "AI extraction is temporarily unavailable. Please try again later.", request_id: "test-request", fields: [] },
    }) });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByRole("alert", { name: "Extraction could not finish" })).toContainText("temporarily unavailable");
  await expect(page.getByLabel("Experiment objective")).toBeEnabled();
  await expect(page.getByText("100,000", { exact: true })).toHaveCount(0);
});

test("malformed success response is rejected", async ({ page }) => {
  await page.route("**/api/v1/experiments/extract", (route) => route.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify({ status: "success" }),
  }));
  await page.goto("/");
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByRole("alert", { name: "Extraction could not finish" })).toContainText("expected format");
});

test("mobile intake fits the viewport and supports extraction", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByText("A few details need your attention")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: testInfo.outputPath("mobile-extraction.png"), fullPage: true });
});

test("correcting outcome type clears incompatible inputs and resolves the reported conflict", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByText("Optional confirmed inputs").click();
  await page.getByLabel("Primary metric", { exact: true }).fill("mean spending per customer");
  await page.getByLabel("Outcome type", { exact: true }).selectOption("binary");
  await page.getByLabel("Baseline conversion rate", { exact: true }).fill("0.1");
  await expect(page.getByLabel("Baseline mean", { exact: true })).toHaveCount(0);
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByText("Resolve conflicting assumptions")).toBeVisible();
  await page.getByLabel("Outcome type", { exact: true }).selectOption("continuous");
  await expect(page.getByLabel("Baseline conversion rate", { exact: true })).toHaveCount(0);
  await expect(page.getByLabel("Baseline mean", { exact: true })).toHaveValue("");
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByText("A few details need your attention")).toBeVisible();
  await expect(page.getByText("Resolve conflicting assumptions")).toHaveCount(0);
  await expect(page.getByText("Metric wording note", { exact: true })).toBeVisible();
  await expect(page.getByText("What is the baseline standard deviation in the same units?")).toBeVisible();
  await page.getByLabel("Outcome type", { exact: true }).selectOption("binary");
  await expect(page.getByLabel("Baseline conversion rate", { exact: true })).toHaveValue("");
});

test("invalid relative effect inputs identify the exact fields to fix", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Load example with missing data" }).click();
  await page.getByText("Optional confirmed inputs").click();
  await page.getByLabel("Outcome type", { exact: true }).selectOption("continuous");
  await page.getByLabel("Baseline mean", { exact: true }).fill("0");
  await page.getByLabel("Target relative increase", { exact: true }).fill("0.05");
  await page.getByRole("button", { name: "Extract experiment facts" }).click();
  await expect(page.getByRole("alert", { name: "Extraction could not finish" })).toContainText("baseline mean greater than zero");
  await expect(page.getByLabel("Baseline mean", { exact: true })).toHaveAttribute("aria-invalid", "true");
});
