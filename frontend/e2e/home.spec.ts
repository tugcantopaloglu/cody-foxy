import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('should display the homepage', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Cody Foxy/)
  })

  test('should have a working navigation', async ({ page }) => {
    await page.goto('/')
    
    const dashboardLink = page.getByRole('link', { name: /dashboard/i })
    await expect(dashboardLink).toBeVisible()
    
    const scanLink = page.getByRole('link', { name: /scan/i })
    await expect(scanLink).toBeVisible()
  })

  test('should navigate to scan page', async ({ page }) => {
    await page.goto('/')
    
    await page.getByRole('link', { name: /scan/i }).click()
    await expect(page).toHaveURL(/\/scan/)
  })

  test('should toggle dark mode', async ({ page }) => {
    await page.goto('/')
    
    const themeToggle = page.getByRole('button', { name: /toggle theme/i })
    if (await themeToggle.isVisible()) {
      await themeToggle.click()
      await expect(page.locator('html')).toHaveClass(/dark/)
    }
  })

  test('should be responsive', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    
    const header = page.locator('header')
    await expect(header).toBeVisible()
  })
})
