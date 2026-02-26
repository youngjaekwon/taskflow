import { redirect } from '@sveltejs/kit';
import { logout } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ cookies, fetch }) => {
		const refreshToken = cookies.get('refresh_token');
		if (refreshToken) {
			try {
				await logout(fetch, refreshToken);
			} catch {
				// 로그아웃 실패해도 쿠키는 삭제
			}
		}
		cookies.delete('access_token', { path: '/' });
		cookies.delete('refresh_token', { path: '/' });
		redirect(303, '/login');
	}
};
