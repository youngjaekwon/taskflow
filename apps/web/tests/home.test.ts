import { expect, test } from '@playwright/test';

test('홈 페이지 렌더링', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { name: 'TaskFlow' })).toBeVisible();
});

test('비인증 사용자에게 로그인/회원가입 링크 표시', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('link', { name: '로그인' })).toBeVisible();
	await expect(page.getByRole('link', { name: '회원가입' })).toBeVisible();
});

test('로그인 페이지 렌더링', async ({ page }) => {
	await page.goto('/login');
	await expect(page.getByRole('heading', { name: '로그인' })).toBeVisible();
});

test('회원가입 페이지 렌더링', async ({ page }) => {
	await page.goto('/register');
	await expect(page.getByRole('heading', { name: '회원가입' })).toBeVisible();
});

test('보호된 라우트 접근 시 로그인 리다이렉트', async ({ page }) => {
	await page.goto('/orgs');
	await expect(page).toHaveURL(/\/login/);
});
