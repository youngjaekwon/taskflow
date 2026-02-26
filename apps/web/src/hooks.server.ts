import type { Handle, HandleServerError } from '@sveltejs/kit';
import { refreshTokens } from '$lib/server/auth';
import { setAuthCookies, clearAuthCookies } from '$lib/server/cookies';
import { decodeJwtPayload } from '$lib/server/jwt';

export const handle: Handle = async ({ event, resolve }) => {
	const accessToken = event.cookies.get('access_token');
	const refreshToken = event.cookies.get('refresh_token');

	if (accessToken) {
		// JWT payload에서 만료 시간 확인
		const payload = decodeJwtPayload(accessToken);
		const isExpired = payload ? (payload.exp as number) * 1000 < Date.now() : false;

		if (isExpired && refreshToken) {
			// 토큰 리프레시 시도
			try {
				const tokens = await refreshTokens(fetch, refreshToken);
				setAuthCookies(event.cookies, tokens);
				event.locals.accessToken = tokens.access;
			} catch {
				// 리프레시 실패 — 쿠키 삭제
				clearAuthCookies(event.cookies);
				event.locals.accessToken = null;
				event.locals.user = null;
			}
		} else {
			event.locals.accessToken = accessToken;
		}
	} else if (refreshToken) {
		// access token 없지만 refresh token이 있는 경우
		try {
			const tokens = await refreshTokens(fetch, refreshToken);
			setAuthCookies(event.cookies, tokens);
			event.locals.accessToken = tokens.access;
		} catch {
			clearAuthCookies(event.cookies);
			event.locals.accessToken = null;
			event.locals.user = null;
		}
	} else {
		event.locals.accessToken = null;
		event.locals.user = null;
	}

	// accessToken이 있으면 사용자 정보를 JWT에서 추출 (가벼운 방식)
	if (event.locals.accessToken) {
		const payload = decodeJwtPayload(event.locals.accessToken);
		if (payload) {
			event.locals.user = {
				id: String(payload.user_id),
				email: (payload.email as string) || '',
				username: (payload.username as string) || '',
				firstName: (payload.first_name as string) || '',
				lastName: (payload.last_name as string) || '',
				profileImage: (payload.profile_image as string) || null
			};
		} else {
			event.locals.user = null;
		}
	}

	const response = await resolve(event);

	response.headers.set('X-Frame-Options', 'DENY');
	response.headers.set('X-Content-Type-Options', 'nosniff');

	return response;
};

export const handleError: HandleServerError = async ({ error, event }) => {
	const errorId = crypto.randomUUID();

	console.error(`[${errorId}] Server error at ${event.url.pathname}:`, error);

	return {
		message: '예상치 못한 오류가 발생했습니다.',
		errorId
	};
};
