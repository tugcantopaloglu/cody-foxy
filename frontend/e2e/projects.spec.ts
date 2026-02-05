import { test, expect } from '@playwright/test'

test.describe('Projects Page', () => {
  test('should display projects page', async ({ page }) => {
    await page.goto('/projects')
    
    await expect(page.getByRole('heading', { name: /projects/i })).toBeVisible()
  })

  test('should show new project button', async ({ page }) => {
    await page.goto('/projects')
    
    const newProjectBtn = page.getByRole('link', { name: /new project/i })
    await expect(newProjectBtn).toBeVisible()
  })

  test('should navigate to new project form', async ({ page }) => {
    await page.goto('/projects')
    
    await page.getByRole('link', { name: /new project/i }).click()
    await expect(page).toHaveURL(/\/projects\/new/)
  })

  test('should have search functionality', async ({ page }) => {
    await page.goto('/projects')
    
    const searchInput = page.getByPlaceholder(/search/i)
    await expect(searchInput).toBeVisible()
  })

  test('should toggle view mode', async ({ page }) => {
    await page.goto('/projects')
    
    const gridBtn = page.getByRole('button', { name: /grid/i })
    const listBtn = page.getByRole('button', { name: /list/i })
    
    if (await gridBtn.isVisible() && await listBtn.isVisible()) {
      await listBtn.click()
      await gridBtn.click()
    }
  })
})

test.describe('New Project Form', () => {
  test('should display project form', async ({ page }) => {
    await page.goto('/projects/new')
    
    await expect(page.getByRole('heading', { name: /create project/i })).toBeVisible()
  })

  test('should have required fields', async ({ page }) => {
    await page.goto('/projects/new')
    
    const nameInput = page.getByLabel(/project name/i)
    await expect(nameInput).toBeVisible()
    await expect(nameInput).toHaveAttribute('required')
  })

  test('should have automation toggles', async ({ page }) => {
    await page.goto('/projects/new')
    
    await expect(page.getByText(/scan on push/i)).toBeVisible()
    await expect(page.getByText(/scan on pull request/i)).toBeVisible()
  })

  test('should have fail threshold selector', async ({ page }) => {
    await page.goto('/projects/new')
    
    await expect(page.getByText(/fail threshold/i)).toBeVisible()
  })
})
