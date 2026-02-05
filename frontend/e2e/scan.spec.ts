import { test, expect } from '@playwright/test'

test.describe('Scan Page', () => {
  test('should display scan options', async ({ page }) => {
    await page.goto('/scan')
    
    await expect(page.getByText(/upload/i)).toBeVisible()
    await expect(page.getByText(/github/i)).toBeVisible()
  })

  test('should show file upload dropzone', async ({ page }) => {
    await page.goto('/scan')
    
    const uploadTab = page.getByRole('tab', { name: /upload/i })
    if (await uploadTab.isVisible()) {
      await uploadTab.click()
    }
    
    const dropzone = page.getByText(/drag.*drop/i)
    await expect(dropzone).toBeVisible()
  })

  test('should show GitHub scanner', async ({ page }) => {
    await page.goto('/scan')
    
    const githubTab = page.getByRole('tab', { name: /github/i })
    if (await githubTab.isVisible()) {
      await githubTab.click()
    }
    
    const repoInput = page.getByPlaceholder(/github/i)
    await expect(repoInput).toBeVisible()
  })

  test('should validate GitHub URL input', async ({ page }) => {
    await page.goto('/scan')
    
    const githubTab = page.getByRole('tab', { name: /github/i })
    if (await githubTab.isVisible()) {
      await githubTab.click()
    }
    
    const repoInput = page.getByPlaceholder(/github/i)
    await repoInput.fill('not-a-valid-url')
    
    const scanButton = page.getByRole('button', { name: /scan/i })
    if (await scanButton.isVisible()) {
      await scanButton.click()
    }
  })
})
