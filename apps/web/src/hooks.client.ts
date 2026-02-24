import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({ error }) => {
	const errorId = crypto.randomUUID();

	console.error(`[${errorId}] Client error:`, error);

	return {
		message: '예상치 못한 오류가 발생했습니다.',
		errorId
	};
};
