import type { Handle, HandleServerError } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
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
