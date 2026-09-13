import { expect, test } from "@playwright/test";

test("FS-01 shows the F/S mismatch and blocks a live write", async ({ page }) => {
  await page.goto("/cases/FS-01");
  await expect(page.getByRole("heading", { name: "Readback yes, one letter wrong" })).toBeVisible();
  await expect(page.getByText("Mismatch — do not write")).toBeVisible();
  await expect(page.getByText("First difference at character 6")).toBeVisible();
  await expect(page.getByText("Writable: no")).toBeVisible();

  await page.getByRole("button", { name: "Preview task" }).click();
  await expect(page.getByText("Intended identifier is not in the task.")).toBeVisible();

  await page.getByRole("button", { name: "Place live call" }).click();
  await expect(page.getByRole("heading", { name: "Live create is disabled" })).toBeVisible();
  await page.getByRole("button", { name: "Close" }).click();

  await page.getByLabel("Type the identifier from a second channel").fill("07198SECTIST");
  await page.getByText("I compared this to a written channel").click();
  await page.getByRole("button", { name: "Mark independently verified" }).click();
  await expect(page.getByText("Mismatch — do not write")).toBeVisible();

  await page.getByLabel("Type the identifier from a second channel").fill("07198FECTIST");
  await page.getByRole("button", { name: "Mark independently verified" }).click();
  await expect(page.getByText("Independently verified")).toBeVisible();
  await expect(page.getByText("Writable: yes")).toBeVisible();
});
