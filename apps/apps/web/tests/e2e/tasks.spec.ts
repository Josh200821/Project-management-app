import { test, expect } from "@playwright/test"

test.describe("Task Management", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login")
    await page.getByPlaceholder(/email/i).fill("demo@example.com")
    await page.getByPlaceholder(/password/i).fill("Demo1234!")
    await page.getByRole("button", { name: /sign in/i }).click()
    await page.waitForURL(/dashboard/)
  })

  test("create a new task", async ({ page }) => {
    await page.goto("/projects/platform-rewrite/tasks")
    await page.getByRole("button", { name: /new task/i }).click()
    await page.getByPlaceholder(/task title/i).fill("E2E test task")
    await page.getByRole("button", { name: /create/i }).click()
    await expect(page.getByText("E2E test task")).toBeVisible()
  })

  test("kanban board shows tasks by status", async ({ page }) => {
    await page.goto("/projects/platform-rewrite/board")
    await expect(page.getByText(/to do/i)).toBeVisible()
    await expect(page.getByText(/in progress/i)).toBeVisible()
    await expect(page.getByText(/done/i)).toBeVisible()
  })
})
