import { dev } from '$app/environment';
import type { Cookies } from '@sveltejs/kit';

interface TokenPair {
	access: string;
	refresh: string;
}

export function setAuthCookies(cookies: Cookies, tokens: TokenPair): void {
	cookies.set('access_token', tokens.access, {
		path: '/',
		httpOnly: true,
		sameSite: 'lax',
		secure: !dev,
		maxAge: 60 * 30 // 30분
	});
	cookies.set('refresh_token', tokens.refresh, {
		path: '/',
		httpOnly: true,
		sameSite: 'lax',
		secure: !dev,
		maxAge: 60 * 60 * 24 * 7 // 7일
	});
}

export function clearAuthCookies(cookies: Cookies): void {
	cookies.delete('access_token', { path: '/' });
	cookies.delete('refresh_token', { path: '/' });
}
