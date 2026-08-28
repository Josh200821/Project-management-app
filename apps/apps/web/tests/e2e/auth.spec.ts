import { test, expect } from "@playwright/test"

test.describe("Authentication", () => {
  test("login page renders", async ({ page }) => {
    await page.goto("/login")
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible()
    await expect(page.getByPlaceholder(/email/i)).toBeVisible()
    await expect(page.getByPlaceholder(/password/i)).toBeVisible()
  })

  test("login with valid credentials", async ({ page }) => {
    await page.goto("/login")
    await page.getByPlaceholder(/email/i).fill("demo@example.com")
    await page.getByPlaceholder(/password/i).fill("Demo1234!")
    await page.getByRole("button", { name: /sign in/i }).click()
    await expect(page).toHaveURL(/dashboard/)
  })

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/login")
    await page.getByPlaceholder(/email/i).fill("wrong@example.com")
    await page.getByPlaceholder(/password/i).fill("wrongpassword")
    await page.getByRole("button", { name: /sign in/i }).click()
    await expect(page.getByText(/invalid/i)).toBeVisible()
  })

  test("register new account", async ({ page }) => {
    await page.goto("/register")
    await page.getByPlaceholder(/full name/i).fill("Test User")
    await page.getByPlaceholder(/email/i).fill("newuser@example.com")
    await page.getByPlaceholder(/password/i).fill("Secure1234!")
    await page.getByRole("button", { name: /create account/i }).click()
    await expect(page).toHaveURL(/dashboard/)
  })
})
