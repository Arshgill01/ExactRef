import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/cases/FS-01");
  await expect(page.getByRole("heading", { name: "Readback yes, one letter wrong" })).toBeVisible();
  await page.getByRole("button", { name: "Replay fixture" }).click();
  await expect(page.getByText("Writable: no")).toBeVisible();
});

test("FS-01 shows the F/S mismatch and blocks a live write", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Readback yes, one letter wrong" })).toBeVisible();
  await expect(page.getByText("Mismatch — do not write")).toBeVisible();
  await expect(page.getByText("First difference at character 6")).toBeVisible();
  await expect(page.getByText("Writable: no")).toBeVisible();

  await page.getByRole("button", { name: "Preview task" }).click();
  await expect(page.getByText("Intended identifier is not in the task.")).toBeVisible();

  await page.getByRole("button", { name: "Place live call" }).click();
  await expect(page.getByRole("heading", { name: "Live create is disabled" })).toBeVisible();
  await page.getByRole("button", { name: "Close" }).click();

  await page.getByRole("button", { name: "Mark independently verified" }).click();
  await expect(page.getByText("A second channel claim is required")).toBeVisible();

  await page.getByLabel("Type the identifier from a second channel").fill("07198SECTIST");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Mark independently verified" }).click();
  await expect(page.getByText("Mismatch — do not write")).toBeVisible();

  await page.getByLabel("Type the identifier from a second channel").fill("07198FECTIST");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Mark independently verified" }).click();
  await expect(page.getByText("Independently verified")).toBeVisible();
  await expect(page.getByText("Writable: yes")).toBeVisible();
});

test("FS-03 stays conversational until a typed second channel", async ({ page }) => {
  await page.getByRole("link", { name: /FS-03/ }).click();
  await page.getByRole("button", { name: "Replay fixture" }).click();
  await expect(page.getByText("Readback confirmed — still unverified")).toBeVisible();
  await expect(page.getByText("Writable: no")).toBeVisible();

  await page.getByLabel("Type the identifier from a second channel").fill("TK-44019");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Mark independently verified" }).click();
  await expect(page.getByText("Independently verified")).toBeVisible();
});

test("FS-04 and FS-05 stay blocked", async ({ page }) => {
  await page.getByRole("link", { name: /FS-04/ }).click();
  await expect(page.getByText("Unknown", { exact: true })).toBeVisible();
  await expect(page.getByText("No verbatim evidence span.")).toBeVisible();

  await page.getByRole("link", { name: /FS-05/ }).click();
  await expect(page.getByText("Mismatch — do not write")).toBeVisible();
  await expect(page.getByText("intended 0, extracted O")).toBeVisible();
});
