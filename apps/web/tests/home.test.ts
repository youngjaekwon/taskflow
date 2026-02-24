import { expect, test } from '@playwright/test';

test('홈 페이지 렌더링', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { name: 'TaskFlow' })).toBeVisible();
});

test('카운터 동작', async ({ page }) => {
	await page.goto('/');
	const counter = page.getByText('카운터:');
	await expect(counter).toBeVisible();
});
