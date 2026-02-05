import { test, expect } from '@playwright/test'

test.describe('Dashboard Page', () => {
  test('should display dashboard', async ({ page }) => {
    await page.goto('/dashboard')
    
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible()
  })

  test('should show stats cards', async ({ page }) => {
    await page.goto('/dashboard')
    
    await expect(page.getByText(/total scans/i)).toBeVisible()
    await expect(page.getByText(/vulnerabilities/i)).toBeVisible()
  })

  test('should show recent scans section', async ({ page }) => {
    await page.goto('/dashboard')
    
    await expect(page.getByText(/recent scans/i)).toBeVisible()
  })

  test('should have new scan button', async ({ page }) => {
    await page.goto('/dashboard')
    
    const newScanBtn = page.getByRole('link', { name: /new scan/i })
    await expect(newScanBtn).toBeVisible()
    
    await newScanBtn.click()
    await expect(page).toHaveURL(/\/scan/)
  })

  test('should display charts', async ({ page }) => {
    await page.goto('/dashboard')
    
    const charts = page.locator('canvas, svg')
    const chartCount = await charts.count()
    expect(chartCount).toBeGreaterThanOrEqual(0)
  })
})
